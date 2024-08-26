import os
import pathlib
import platform


def _is_rpi():
    if platform.system() == 'Windows':
        return False
    return os.uname().nodename in ('raspberrypi', 'rpi')


# when present, DDH simulates latitude and longitude values from config.toml
TMP_PATH_GPS_DUMMY = "/tmp/gps_dummy_mode.json"

# when present, DDH simulates speed
TMP_PATH_DDH_BOAT_SPEED_JSON = "/tmp/ddh_boat_speed.json"

# when present, the BLE code on the DDH is disabled
TMP_PATH_DISABLE_BLE = "/tmp/ddh_disabled_ble_file.flag"

# when present, DDH graphs test data
TMP_PATH_GRAPH_TEST_MODE_JSON = '/tmp/ddh_graph_test_mode.json'

# written by DDH to indicate the logger it wants plot for via GUI
TMP_PATH_GRAPH_REQ_JSON = '/tmp/graph_req.json'

# written by real GPS to know the last GPS position
TMP_PATH_GPS_LAST_JSON = "/tmp/gps_last.json"

# written by DDS to tell which BLE interface is using
TMP_PATH_BLE_IFACE = "/tmp/ble_iface_used.json"

# indicates the DDH GUI has been closed pressing the upper-right X
TMP_PATH_GUI_CLOSED_FLAG = "/tmp/gui_closed.flag"

# indicates the DDH GUI wants to force an AWS sync
TMP_PATH_AWS_HAS_WORK_VIA_GUI = "/tmp/ddh_aws_has_something_to_do_via_gui.flag"

# indicates the DDH GUI requested a CNV process
TMP_PATH_CNV_REQUESTED_VIA_GUI = "/tmp/ddh_cnv_requested_via_gui.flag"

# indicates the DDH GUI updated itself (beta)
TMP_PATH_DDH_GOT_UPDATE = "/tmp/ddh_got_update_file.flag"

# indicates the "clear lock out" button has been pressed
# this clears macs, forces a download, etc.
TMP_PATH_DDH_APP_OVERRIDE = "/tmp/ddh_app_override_file.flag"

# internet via
TMP_PATH_INET_VIA = '/tmp/ddh_internet_via.json'


# permanent on DDH, temporary on dev platform
d = '/home/pi/li/' if _is_rpi() else '/tmp'
LI_PATH_DDH_GPS_EXTERNAL = f'{d}/.ddt_gps_external.flag'
LI_PATH_GROUPED_S3_FILE_FLAG = f'{d}/.ddt_this_box_has_grouped_s3_uplink.flag'
LI_PATH_CELL_FW = f'{d}/.fw_cell_ver'
DDH_USES_SHIELD_JUICE4HALT = f'{d}/.ddt_j4h_shield.flag'
DDH_USES_SHIELD_SAILOR = f'{d}/.ddt_sailor_shield.flag'
LI_FILE_ICCID=f'{d}/.iccid'
LI_PATH_TEST_MODE = f'{d}/.ddh_test_mode.flag'
h = str(pathlib.Path.home())
h_ddh = f'{h}/li/ddh' if _is_rpi() else f'{h}/PycharmProjects/ddh'
LI_PATH_DDH_VERSION = f'{h_ddh}/.ddh_version'
LI_PATH_DDH_GPS_CELL_SHIELD_USB4 = f'{d}/.gps_quectel_at_usb4'
LI_PATH_PLOT_DATA_EVEN_OUT_WATER = f'{h_ddh}/.ddh_plt_outside_water'
