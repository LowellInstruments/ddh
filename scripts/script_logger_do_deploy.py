#!/usr/bin/env python3
import asyncio

import sys
import subprocess as sp
import yaml
import os
from mat.utils import PrintColors as PC
from script_logger_do_deploy_utils import (
    set_script_cfg_file,
    deploy_logger,
    get_script_cfg_file,
    ble_scan,
)

# ---------------------------------
# issues RUN command or not at end
# ---------------------------------
g_flag_run = False
g_flag_sensor = True


def _screen_clear():
    sp.run("clear", shell=True)


def _print_cwd():
    print("\ncurrent working directory ->", os.getcwd())


def _screen_separation():
    print("\n\n")


def _menu_get():
    return input("\t-> ")


def _check_cwd():
    _print_cwd()
    if not os.getcwd().endswith("scripts"):
        e = "--> current working directory must be folder containing this script"
        print(e)
        assert False


def _get_macs_to_sn_file_path():
    p = os.getcwd()
    p = p + "/../settings/_li_all_macs_to_sn.yml"
    return p


def _list_monitored_macs():
    p = _get_macs_to_sn_file_path()
    with open(p, "r") as f:
        lines = f.readlines()
        for n, i in enumerate(lines):
            if n == 0:
                print("\nmonitored macs\n--------------\n", p)
            if i.startswith("#") or len(i) < 5:
                continue
            if ":" in i:
                print(i.replace("\n", ""))


def _menu_build(_sr: dict, n: int):

    # -------------------------------------------------
    # dictionary <- import macs from '_macs_to_sn.yml'
    # -------------------------------------------------
    ddh_d = {}
    try:
        path = _get_macs_to_sn_file_path()
        with open(path) as f:
            ddh_d = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError as ex:
        print(ex)

    # detect errors
    if not ddh_d:
        e = "error -> importing _macs_to_sn.yml"
        print(PC.FAIL + e + PC.ENDC)
        return
    # convert to lower-case
    ddh_d = dict((k.lower(), v) for k, v in ddh_d.items())

    # --------------------------------------------------
    # filters scan results: only MACS in our dictionary
    # --------------------------------------------------
    d = {}
    i = 0
    for each_sr in _sr:
        mac, rssi = each_sr
        if mac not in ddh_d:
            continue

        # --------------------------------------------------------
        # builds menu of up to 'n' entries d[#i]: (mac, sn, rssi)
        # --------------------------------------------------------
        sn = str(ddh_d[mac])
        d[i] = (mac, sn, rssi)
        i += 1
        if i == n - 1:
            break

    return d


def _menu_display(d: dict, cfg: dict):
    print("scan done!")
    print("\nchoose an option:")
    print("\ts) scan for macs nearby")
    print("\tl) list monitored macs in file li_all_macs_to_sn.yml")
    print("\tr) toggle RUN flag, current value is {}".format(g_flag_run))
    print("\ti) set DO interval, current value is {}".format(cfg["DRI"]))
    print("\td) set DEPLOYMENT, current value is {}".format(cfg["DFN"]))
    print("\to) check oxygen sensor, current value is {}".format(g_flag_sensor))
    print("\tq) quit")
    if not d:
        return

    # print found macs with number
    for k, v in d.items():
        s = "\t{}) deploy {} -> SN {} -> rssi {}"
        print(s.format(k, v[0], v[1], v[2]))


ael = asyncio.new_event_loop()
asyncio.set_event_loop(ael)


def _menu_execute(_m, _c, cfg):

    global g_flag_run
    global g_flag_sensor

    # _c: user choice
    if _c == "q":
        print("bye!")
        sys.exit(0)

    if _c == "s":
        # re-scan
        return

    if _c == "l":
        _list_monitored_macs()
        return

    if _c == "r":
        # toggle
        g_flag_run = not g_flag_run
        return

    if _c == "o":
        # toggle
        g_flag_sensor = not g_flag_sensor
        return

    if _c == "d":
        # ------------------------
        # set new deployment name
        # ------------------------
        i = str(input("\t\t enter new deployment -> "))
        if len(i) != 3:
            print("invalid input: must be 3 letters long")
            return
        cfg["DFN"] = i
        set_script_cfg_file(cfg)
        return

    if _c == "i":
        # --------------------
        # set new DO interval
        # --------------------
        try:
            i = int(input("\t\t enter new interval -> "))
        except ValueError:
            print("invalid input: must be number")
            return
        valid = (30, 60, 300, 600, 900, 3600, 7200)
        if i not in valid:
            print("invalid interval: must be {}".format(valid))
            return
        cfg["DRI"] = i
        set_script_cfg_file(cfg)
        return

    # --------------------------------------------
    # safety check, logger menu keys are integers
    # --------------------------------------------
    if not str(_c).isnumeric():
        print(PC.WARNING + "\tunknown option" + PC.ENDC)
        return
    _c = int(_c)
    if _c >= len(_m):
        print(PC.WARNING + "\tbad option" + PC.ENDC)
        return

    # safety check, SN length
    mac, sn = _m[_c][0], _m[_c][1]
    if len(sn) != 7:
        e = "\terror: got {}, but serial numbers must be 7 digits long"
        print(PC.FAIL + e.format(sn) + PC.ENDC)
        return

    # =====================================
    # call main routine logger preparation
    # =====================================
    print(PC.OKBLUE + "\n\tdeploying logger {}...".format(mac) + PC.ENDC)
    rv = ael.run_until_complete(deploy_logger(mac, sn, g_flag_run, g_flag_sensor))

    # show green or red success
    _ = "\n\t========================"
    s_ok = PC.OKGREEN + _ + "\n\tsuccess {}" + _ + PC.ENDC
    s_nok = PC.FAIL + _ + "\n\terror {}" + _ + PC.ENDC
    s = s_ok if rv == 0 else s_nok
    print(s.format(mac))


if __name__ == "__main__":
    _screen_clear()
    _check_cwd()

    while True:
        cfg = get_script_cfg_file()

        # --------------
        # BLE scan
        # --------------
        sr = ael.run_until_complete(ble_scan())

        m = _menu_build(sr, 10)
        _menu_display(m, cfg)
        c = _menu_get()

        # -----------------
        # BLE deployment
        # -----------------

        _menu_execute(m, c, cfg)
        _screen_separation()
