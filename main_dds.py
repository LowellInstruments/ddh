#!/usr/bin/env python3
from multiprocessing import Process
import threading
import time
import os
import uuid
from api.api_utils import get_ip_vpn
from dds.aws import aws_serve
from dds.ble import ble_interact_all_loggers
from dds.ble_scan import ble_scan
from dds.cnv import cnv_serve
from dds.gps import (
    gps_wait_for_first_frame_at_boot,
    gps_measure,
    gps_configure_shield,
    gps_clock_sync_if_so,
    gps_tell_vessel_name,
    gps_hw_error_get,
    gps_did_we_ever_clock_sync,
    gps_print_trying_clock_sync_at_boot,
    gps_hw_error_parse,
    gps_power_cycle_if_so,
    gps_know_hat_firmware_version,
)
from dds.macs import dds_create_folder_macs_color, dds_macs_color_show_at_boot
from dds.net import net_serve
from dds.rbl import rbl_loop
from dds.sqs import (
    dds_create_folder_sqs,
    sqs_serve,
    sqs_msg_ddh_booted,
    sqs_msg_ddh_alive, sqs_msg_ddh_alarm_crash, sqs_msg_ddh_needs_update
)
from dds.lef import dds_create_folder_lef
from dds.ble_utils_dds import (
    ble_apply_debug_hooks_at_boot,
    ble_show_monitored_macs,
    ble_op_conditions_met,
    ble_tell_gui_antenna_type,
    ble_check_antenna_up_n_running, dds_tell_software_update, dds_check_bluez_version,
)
from dds.timecache import its_time_to
from mat.linux import linux_app_write_pid_to_tmp, linux_is_process_running
from mat.ble.ble_mat_utils import (
    ble_mat_get_antenna_type,
    ble_mat_bluetoothctl_power_cycle
)
from rpc.rpc_rx import th_srv_cmd
from rpc.rpc_tx import th_cli_notify
from utils.ddh_shared import (
    dds_check_conf_json_file,
    dds_get_macs_from_json_file,
    PID_FILE_DDS,
    dds_create_folder_dl_files,
    dds_create_folder_logs,
    dds_ensure_proper_working_folder,
    dds_check_we_have_box_env_info,
    PID_FILE_DDS_CONTROLLER,
    NAME_EXE_DDS_CONTROLLER,
    NAME_EXE_DDS, dds_get_json_vessel_name,
)
from settings import ctx
from utils.logs import (
    lg_dds as lg,
    dds_log_tracking_add,
    dds_log_core_start_at_boot
)
import setproctitle


def main_dds():

    dds_tell_software_update()
    dds_check_we_have_box_env_info()
    dds_ensure_proper_working_folder()
    dds_create_folder_macs_color()
    dds_create_folder_sqs()
    dds_create_folder_lef()
    dds_create_folder_dl_files()
    dds_create_folder_logs()
    dds_log_core_start_at_boot()
    dds_check_conf_json_file()
    dds_macs_color_show_at_boot()
    m_j = dds_get_macs_from_json_file()
    dds_check_bluez_version()

    ble_show_monitored_macs()
    ble_apply_debug_hooks_at_boot()
    ble_mat_bluetoothctl_power_cycle()

    # detecting and selecting Bluetooth antenna
    h, h_d = ble_mat_get_antenna_type()

    # seems boot process is going well
    setproctitle.setproctitle(NAME_EXE_DDS)
    linux_app_write_pid_to_tmp(PID_FILE_DDS)

    # GPS boot stage
    rv = gps_configure_shield()
    if not rv:
        gps_power_cycle_if_so(forced=True)
        gps_configure_shield()
    gps_wait_for_first_frame_at_boot()
    gps_know_hat_firmware_version()

    # GPS first stage
    g = gps_measure()
    if g:
        lat, lon, tg, speed = g
        gps_clock_sync_if_so(tg)
        sqs_msg_ddh_booted(lat, lon)

    # do nothing if we never had a GPS clock sync
    gps_print_trying_clock_sync_at_boot()
    lat = ''
    lon = ''
    while not gps_did_we_ever_clock_sync():
        g = gps_measure()
        if g:
            lat, lon, tg, speed = g
            if gps_clock_sync_if_so(tg):
                break
        time.sleep(5)

    if sqs_msg_ddh_needs_update(lat, lon):
        s = 'warning: this DDH needs an update'
        lg.a('-' * len(s))
        lg.a(s)
        lg.a('-' * len(s))

    # Rockblocks stuff is slow, launch its loop as a thread
    th = threading.Thread(target=rbl_loop)
    th.start()

    # =============
    # main loop
    # =============

    while 1:

        # old GPS hats may need power ON / OFF + GPS on
        gps_power_cycle_if_so()
        gps_configure_shield()

        # other stages
        cnv_serve()
        aws_serve()
        sqs_serve()
        net_serve()

        # GPS stage
        gps_tell_vessel_name()
        g = gps_measure()
        _ge = gps_hw_error_get(g)
        if gps_hw_error_parse(_ge):
            time.sleep(1)
            continue
        lat, lon, tg, speed = g
        dds_log_tracking_add(lat, lon, tg)
        gps_clock_sync_if_so(tg)

        # send SQS ping
        sqs_msg_ddh_alive(lat, lon)

        # check we do Bluetooth or not
        ble_tell_gui_antenna_type(h, h_d)
        if not ble_check_antenna_up_n_running(lat, lon, h):
            continue
        if not ble_op_conditions_met(speed):
            continue

        # BLE stage
        args = [g, h, h_d]
        det = ctx.ael.run_until_complete(ble_scan(*args))
        args = [det, m_j, g, h, h_d]
        ctx.ael.run_until_complete(ble_interact_all_loggers(*args))


def _alarm_dds_crash(n):
    if n == 0:
        return
    if its_time_to('tell_dds_child_crash', 3600):
        vs = dds_get_json_vessel_name()
        box_sn = os.getenv("DDH_BOX_SERIAL_NUMBER")
        prj = os.getenv("DDH_BOX_PROJECT_NAME")
        ip_vpn = get_ip_vpn()
        u = str(uuid.uuid4())[:5]
        s = f'DDH just crashed, check it: '
        s += f'BOAT {vs} PRJ {prj} SN{box_sn} IP_VPN {ip_vpn} CODE {n} ID {u}'
        sqs_msg_ddh_alarm_crash(s)


def controller_main_dds():
    s = NAME_EXE_DDS_CONTROLLER
    p = PID_FILE_DDS_CONTROLLER
    setproctitle.setproctitle(s)
    linux_app_write_pid_to_tmp(p)
    lg.a("=== {} started ===".format(s))

    while 1:
        # the GUI KILLs this process when desired
        lg.a("=== {} launching child ===".format(s))
        p = Process(target=main_dds)
        p.start()
        p.join()
        _alarm_dds_crash(p.exitcode)
        lg.a("=== {} waits child ===".format(s))
        time.sleep(5)


if __name__ == "__main__":

    # -----------------
    # run DDS software
    # -----------------
    if not linux_is_process_running(NAME_EXE_DDS_CONTROLLER):
        controller_main_dds()
    else:
        e = "not launching {}, already running at python level"
        print(e.format(NAME_EXE_DDS_CONTROLLER))
