import datetime
import os
import random

import time

import sys

from dds.ble_dl_tdo import BAT_FACTOR_TDO
from mat.ble.ble_mat_utils import ble_mat_disconnect_all_devices_ll
from mat.ble.bleak.cc26x2r import BleCC26X2
from utils.ddh_shared import (
    ael
)


async def ble_tst_mts():

    # call of the script
    bn = os.path.basename(sys.argv[0])
    mac = sys.argv[1]
    n = int(sys.argv[2])
    if len(sys.argv) != 3:
        raise Exception(f'error: usage {bn} <logger_mac> number_of_iterations')

    # connect to logger
    lc = BleCC26X2()
    rv = await lc.connect(mac)
    if rv:
        raise Exception(f'error: connecting to {mac}, aborting')
    print(f"connected to {mac}")

    # send a lot of commands
    for i in range(n):
        print(f'sending MTS command {i + 1} / {n}')
        rv = await lc.cmd_mts()
        if rv:
            raise Exception(f'error: sending command MTS, aborting')
        print(f'sending FRM command {i + 1} / {n}')
        rv = await lc.cmd_frm()
        if rv:
            raise Exception(f'error: sending command FRM, aborting')

    # bye bye
    await lc.disconnect()


async def ble_tst_conn():
    mac = "D0:2E:AB:D9:29:48"
    lc = BleCC26X2()

    for i in range(100):
        print('connecting...')
        rv = await lc.connect(mac)
        if rv:
            raise Exception(f'error: connecting to {mac}, aborting')
        print(f"connected to {mac}")
        time.sleep(1)
        await lc.disconnect()
        time.sleep(15)
        print('disconnected')


async def ble_tst_dl():
    mac = "D0:2E:AB:D9:29:48"

    # connect to logger
    lc = BleCC26X2()
    rv = await lc.connect(mac)
    if rv:
        raise Exception(f'error: connecting to {mac}, aborting')
    print(f"connected to {mac}")

    # DDH "A" command includes GTM, SWS, DIR
    g = ("+1.111111", "-2.222222", datetime.datetime.now(), 0)
    rv, ls = await lc.cmd_ddh_a(g)
    if rv:
        raise Exception("DDA error listing files: " + str(rv))
    print(f"DIR: {ls}")

    # download file
    for name, size in ls.items():
        if size == 0:
            raise Exception(f'file {name} has zero length')
        print(f"downloading file {name}, size {size}")
        rv = await lc.cmd_dwg(name)
        if rv:
            raise Exception('dwg exception')
        rv, d = await lc.cmd_dwl(int(size))
        if rv:
            raise Exception('dwl exception')
        print(f'file {name}, size {size} downloaded ok')

    # DDH B command
    rv, v = await lc.cmd_ddh_b(rerun=True)
    if rv:
        raise Exception('ddh_b')

    # a: b'__B 200020000000F072022/08/25 12:13:55'
    v = v[17:19] + v[15:17]
    b = int(v, 16)
    b /= BAT_FACTOR_TDO
    print(f'battery level {b} mV')

    await lc.disconnect()
    return 0


async def ble_tst_noah():
    mac = "D0:2E:AB:D9:29:48"

    # connect to logger
    lc = BleCC26X2()
    rv = await lc.connect(mac)
    if rv:
        raise Exception(f'error: connecting to {mac}, aborting')
    print(f"connected to {mac}")


    # run with string
    g = ("+1.111111", "-2.222222", datetime.datetime.now(), 0)
    rv = await lc.cmd_rws(g)
    if rv:
        print('error: could not RWS')

    # stop with string
    rv = await lc.cmd_sws(g)
    if rv:
        raise Exception("SWS error")

    time.sleep(10)

    rv = await lc.cmd_stm()
    if rv:
        raise Exception("STM error")

    await lc.disconnect()
    return 0


if __name__ == "__main__":

    ble_mat_disconnect_all_devices_ll()
    # ael.run_until_complete(ble_tst_mts())
    # ael.run_until_complete(ble_tst_conn())
    # for _ in range(3):
    #     ael.run_until_complete(ble_tst_dl())
    #     r = int(random.random()* 100)
    #     print(f'sleeping {r} seconds after download\n\n')
    #     time.sleep(r)

    for _ in range(3):
        ael.run_until_complete(ble_tst_noah())
        print(f'sleeping {5} seconds after noah test\n\n')
        time.sleep(5)
