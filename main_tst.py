from mat.ble.ble_mat_utils import ble_mat_disconnect_all_devices_ll
from mat.ble.bleak.cc26x2r import BleCC26X2
from utils.ddh_shared import (
    ael
)


async def ble_tst(mac):

    lc = BleCC26X2()
    rv = await lc.connect(mac)
    if rv:
        raise Exception(f'error: connecting to {mac}, aborting')
    print(f"connected to {mac}")

    n = 100
    for i in range(n):
        print(f'sending MTS command {i + 1} / {n}')
        rv = await lc.cmd_mts()
        if rv:
            raise Exception(f'error: sending command MTS, aborting')
        print(f'sending FRM command {i + 1} / {n}')
        rv = await lc.cmd_frm()
        if rv:
            raise Exception(f'error: sending command FRM, aborting')

    await lc.disconnect()


if __name__ == "__main__":
    ble_mat_disconnect_all_devices_ll()
    m = "F0:5E:CD:25:A2:5F"
    _args = [m]
    ael.run_until_complete(ble_tst(*_args))
