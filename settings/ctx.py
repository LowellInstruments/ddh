import asyncio
from utils.ddh_shared import send_ddh_udp_gui, check_gps_dummy_mode

# ---------------------------------------------------------
# this file allows for fine tweaking DDH software behavior
# ---------------------------------------------------------


# to send updates to GUI
_u = send_ddh_udp_gui


# AWS / SQS enabled or not
aws_en = True
sqs_en = True


# BLE: enabled or not + switch capability
ble_en = True
sw_ble_en = True


# rockblocks: enabled or not
rbl_en = False


# GPS configuration
g_gps_is_external = False


# SMS enabled, False, since it is beta
sms_en = False


# debug hooks :)
hook_gps_dummy_measurement = check_gps_dummy_mode()
hook_gps_error_measurement_forced = False
hook_ble_purge_black_macs_on_boot = False
hook_ble_purge_this_mac_dl_files_folder = False
hook_ble_scan_cc26x2r_sim = False


# for asynchronous Bleak BLE
ael = asyncio.get_event_loop()


class BLEAppException(Exception):
    pass
