#!/usr/bin/env python3


from multiprocessing import Process
import threading
import time
from dds.aws import aws_serve
from dds.ble import ble_interact_all_loggers
from dds.ble_scan import ble_scan
from dds.cnv import cnv_serve
from dds.gps import (
    gps_boot_wait_first,
    gps_measure,
    gps_configure_shield,
    gps_clock_sync_if_so,
    gps_tell_vessel_name,
    gps_check_for_errors,
    gps_did_we_ever_clock_sync,
    gps_banner_clock_sync_at_boot,
    gps_power_cycle_if_so,
    gps_know_hat_firmware_version,
)
from dds.macs import dds_create_folder_macs_color, dds_macs_color_show_at_boot
from dds.net import net_serve
from dds.notifications import notify_boot, notify_error_sw_crash, notify_ddh_needs_sw_update, \
    notify_ddh_alive
from dds.rbl import rbl_loop
from dds.sqs import (
    dds_create_folder_sqs,
    sqs_serve,
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
from utils.ddh_config import dds_check_cfg_has_box_info, \
    dds_get_cfg_monitored_macs
from utils.ddh_shared import (
    PID_FILE_DDS,
    dds_create_folder_dl_files,
    dds_create_folder_logs,
    dds_ensure_proper_working_folder,
    PID_FILE_DDS_CONTROLLER,
    NAME_EXE_DDS_CONTROLLER,
    NAME_EXE_DDS, ael,
)
from utils.logs import (
    lg_dds as lg,
    dds_log_tracking_add,
    dds_log_core_start_at_boot
)
import setproctitle


def main_dds():

    dds_tell_software_update()
    dds_check_cfg_has_box_info()
    dds_ensure_proper_working_folder()
    dds_create_folder_macs_color()
    dds_create_folder_sqs()
    dds_create_folder_lef()
    dds_create_folder_dl_files()
    dds_create_folder_logs()
    dds_log_core_start_at_boot()
    dds_macs_color_show_at_boot()
    m_j = dds_get_cfg_monitored_macs()
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
    gps_boot_wait_first()
    gps_know_hat_firmware_version()

    # GPS first stage
    g = gps_measure()
    if g:
        lat, lon, tg, speed = g
        gps_clock_sync_if_so(tg)
        notify_boot(g)

    # do nothing if we never had a GPS clock sync
    gps_banner_clock_sync_at_boot()
    while not gps_did_we_ever_clock_sync():
        g = gps_measure()
        if g:
            lat, lon, tg, speed = g
            if gps_clock_sync_if_so(tg):
                break
        time.sleep(1)

    if notify_ddh_needs_sw_update(g):
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

        # tell GUI
        gps_tell_vessel_name()

        # old GPS hats may need power ON / OFF + GPS on
        gps_power_cycle_if_so()
        gps_configure_shield()

        # other stages
        cnv_serve()
        aws_serve()
        sqs_serve()
        net_serve()

        # GPS stage
        g = gps_measure()
        if gps_check_for_errors(g):
            time.sleep(1)
            continue
        lat, lon, tg, speed = g
        dds_log_tracking_add(lat, lon, tg)
        gps_clock_sync_if_so(tg)

        # send SQS ping
        notify_ddh_alive(g)

        # check we do Bluetooth or not
        ble_tell_gui_antenna_type(h, h_d)

        if not ble_check_antenna_up_n_running(g, h):
            # note: ensure hciconfig is installed
            continue
        if not ble_op_conditions_met(speed):
            continue

        # BLE scan stage
        args = [m_j, g, h, h_d]
        det = ael.run_until_complete(ble_scan(*args))
        print('scan complete')

        # BLE download stage
        args = [det, m_j, g, h, h_d]
        ael.run_until_complete(ble_interact_all_loggers(*args))


def _alarm_dds_crash(n):
    if n == 0:
        return
    if its_time_to('tell_dds_child_crash', 3600):
        notify_error_sw_crash()


def controller_main_dds():
    s = NAME_EXE_DDS_CONTROLLER
    p = PID_FILE_DDS_CONTROLLER
    setproctitle.setproctitle(s)
    linux_app_write_pid_to_tmp(p)
    lg.a("=== {} started ===".format(s))

    while 1:
        # GUI KILLs this process when desired
        lg.a(f"=== {s} launching child ===")
        p = Process(target=main_dds)
        p.start()
        p.join()
        _alarm_dds_crash(p.exitcode)
        lg.a(f"=== {s} waits child, exitcode {p.exitcode} ===")
        time.sleep(5)


if __name__ == "__main__":

    # --------------------
    # run DDS controller
    # --------------------

    if not linux_is_process_running(NAME_EXE_DDS_CONTROLLER):
        controller_main_dds()
    else:
        e = "not launching {}, already running at python level"
        print(e.format(NAME_EXE_DDS_CONTROLLER))
