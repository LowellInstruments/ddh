import asyncio
import os.path

from math import ceil

from bleak.assigned_numbers import AdvertisementDataType
from bleak.backends.bluezdbus.advertisement_monitor import OrPattern

from dds.macs import macs_black, macs_orange
from dds.notifications_v2 import notify_ddh_error_hw_ble
from dds.timecache import is_it_time_to
from mat.ble.ble_mat_utils import ble_mat_get_bluez_version
from utils.ddh_config import dds_get_cfg_monitored_macs, exp_get_use_ble_passive_scanning
from utils.ddh_shared import (
    send_ddh_udp_gui as _u,
    STATE_DDS_BLE_SCAN_FIRST_EVER,
    STATE_DDS_BLE_SCAN, STATE_DDS_BLE_HARDWARE_ERROR, get_mac_from_folder_path,
)
from bleak import BleakScanner, BleakError
from bleak.backends.bluezdbus.scanner import BlueZScannerArgs
from bleak.backends.device import BLEDevice
from utils.logs import lg_dds as lg


PERIOD_BLE_TELL_HW_ERR_SECS = 600
_g_first_ble_scan_ever = True
_g_monitored_macs = dds_get_cfg_monitored_macs()
_g_ble_scan_early_leave = None


# ----------------------------------------------------------------------------
# activate BLE experimental features you NEED (o/wise gives error):
#     - bluez >= v5.65
#     - sudo nano /lib/systemd/system/bluetooth.service
#           ExecStart=/usr/local/libexec/bluetooth/bluetoothd --experimental
#     - sudo systemctl daemon-reload && sudo systemctl restart bluetooth
# ----------------------------------------------------------------------------


# PASSIVE scanning makes loggers relying on SCAN_REQ to detect out-of-water slower
# see https://github.com/hbldh/bleak/issues/1433
_gbv = ble_mat_get_bluez_version()
_g_ble_scan_mode = "passive" if (exp_get_use_ble_passive_scanning() == 1
                                 and _gbv >= '5.65') else "active"

print('-------------------------')
lg.a(f'bluez v.{_gbv} -> BLE scan mode {_g_ble_scan_mode}')
print('-------------------------')


def _ble_is_supported_logger(s):
    logger_types = [
        "DO-2",
        "DO-1",
        "MOANA",
        "MAT-2W",
        "MATP-2W",
        "TDO",
        "TAP1"
    ]
    for t in logger_types:
        if t in s:
            return True


def _ble_scan_banner(_h, _h_desc):
    global _g_first_ble_scan_ever
    if _g_first_ble_scan_ever:
        _u(STATE_DDS_BLE_SCAN_FIRST_EVER)
        _g_first_ble_scan_ever = False
    _u(STATE_DDS_BLE_SCAN)


async def ble_scan(macs_mon, g, _h: int, _h_desc, t=6.0):

    # classify devs
    _all = {}
    _our = {}
    macs_bad = set(macs_black()).union(set(macs_orange()))
    macs_bad = [get_mac_from_folder_path(i) for i in macs_bad]

    def _scan_cb(d: BLEDevice, _):
        mac = d.address.lower()
        # dt: device type 'TDO'
        dt = d.name
        _all[mac] = dt
        if not _ble_is_supported_logger(dt):
            return
        # allows bleak scan to end faster
        if mac in macs_mon and mac not in macs_bad:
            _our[mac] = dt
            global _g_ble_scan_early_leave
            _g_ble_scan_early_leave = mac

    # real code function starts here
    _ble_scan_banner(_h, _h_desc)

    # convert hci format integer to string
    ad = f"hci{_h}"

    try:
        # -------------------------------
        # active or passive BLE scanning
        # -------------------------------
        if _g_ble_scan_mode == 'passive':
            args = BlueZScannerArgs(
                or_patterns=[OrPattern(0, AdvertisementDataType.COMPLETE_LOCAL_NAME, b"ZT-MOANA"),
                             OrPattern(0, AdvertisementDataType.COMPLETE_LOCAL_NAME, b"TDO"),
                             OrPattern(0, AdvertisementDataType.COMPLETE_LOCAL_NAME, b"DO-1"),
                             OrPattern(0, AdvertisementDataType.COMPLETE_LOCAL_NAME, b"DO-2"),
                             ]
            )
            scanner = BleakScanner(_scan_cb, None,
                                   adapter=ad,
                                   scanning_mode=_g_ble_scan_mode,
                                   bluez=args)
        else:
            scanner = BleakScanner(_scan_cb, None,
                                   adapter=ad,
                                   scanning_mode=_g_ble_scan_mode)

        # perform bleak scanning procedure
        global _g_ble_scan_early_leave
        _g_ble_scan_early_leave = None
        await scanner.start()
        for i in range(ceil(t) * 10):
            # * 10 to be able to sleep 100 ms
            await asyncio.sleep(.1)
            if _g_ble_scan_early_leave:
                # lg.a(f"OK: fast scan for {_g_ble_scan_early_leave}")
                break
        await scanner.stop()

        # _our_devs: {'60:77:71:22:ca:6d': 'DO-2', ...}
        if len(_all) > 15:
            s = "debug: crowded BLE environment"
            if is_it_time_to(s, t=3600 * 6):
                lg.a(s)
        return _our

    except (asyncio.TimeoutError, BleakError, OSError) as ex:
        e = "hardware error during scan! {}"
        if is_it_time_to(e, 600):
            lg.a(e.format(ex))
            notify_ddh_error_hw_ble(g)
        _u(STATE_DDS_BLE_HARDWARE_ERROR)
        # wait some time so any GUI can display this
        await asyncio.sleep(5)
        return {}
