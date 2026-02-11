import os
import pathlib
import sys
import time
from os.path import exists
import serial

from dds.gps_measure import gps_power_cycle_ddc
from mat.quectel import detect_quectel_usb_ports
from scripts.script_ddc import (
    cb_gps_dummy, cb_quit, cb_gps_external, cb_crontab_ddh,
    get_crontab,
    cb_graph_demo, cb_provision_ddh,
    cb_kill_ddh, ddh_run_check, cb_calibrate_display, sh,
    cb_test_mode, is_rpi, VP_QUECTEL, p_w, p_e, c_e, p_i,
    check_aws_run
)
from scripts.script_nadv import main_nadv
from utils.ddh_config import _get_config_file_path, cfg_load_from_file
from utils.ddh_shared import get_ddh_folder_path_settings
from utils.find_usb_port_auto import find_n_list_all_usb_port_automatically
from utils.flag_paths import (
    LI_PATH_GPS_DUMMY,
    LI_PATH_DDH_GPS_EXTERNAL,
    TMP_PATH_GRAPH_TEST_MODE_JSON, LI_PATH_TEST_MODE,
)
import subprocess as sp
from mat.utils import PrintColors as PC


# cwd() is ddh folder here
h = str(pathlib.Path.home())
p = 'li/ddh' if is_rpi() else 'PycharmProjects/ddh'
path_script_deploy_dox = f'{h}/{p}/scripts/run_script_deploy_logger_dox.sh'
path_script_deploy_tdo = f'{h}/{p}/scripts/run_script_deploy_logger_tdo.sh'
path_script_scan_li = f'{h}/{p}/scripts/run_script_scan_li.sh'


# variables for errors and warnings
g_e = None
g_w = None
g_i = None


def _p(s):
    print(s)


def _ddh_show_issues_error():
    if g_e:
        p_e('\nthe following can prevent DDH from starting')
        PC.R(g_e)


def _ddh_show_issues_warning():
    if g_w:
        p_w('\nplease notice')
        PC.Y(g_w)


def _ddh_show_issues_info():
    if g_i:
        p_i('\nmiscellaneous info')
        PC.B(g_i)


def cb_ddh_show_issues():
    _p('')
    _ddh_show_issues_error()
    _ddh_show_issues_warning()
    _ddh_show_issues_info()
    input()


def cb_test_gps_quectel():
    try:
        if not is_rpi():
            p_e('no Rpi for GPS quectel test')
            return
        if sh(f'lsusb | grep {VP_QUECTEL}') == 0:
            port_usb_gps, _ = detect_quectel_usb_ports()
            timeout_gps_test = 60
            till = time.perf_counter() + timeout_gps_test
            ser = serial.Serial(port_usb_gps, 115200,
                                timeout=.1, rtscts=True, dsrdtr=True)

            print(f'\n-- GPS Quectel test will last {timeout_gps_test} seconds --')
            time.sleep(1)
            while time.perf_counter() < till:
                line = ser.readline()
                if line:
                    print(line)
            ser.close()
        else:
            p_e('no testing GPS USB puck')
    except (Exception,) as ex:
        p_e(str(ex))


def cb_list_quectel_usb_ports():
    ls = find_n_list_all_usb_port_automatically(VP_QUECTEL)
    print('\tlist of Quectel USB ports')
    for i in ls:
        print(f'\t{i}')
    input()


def _p_e(param):
    pass


# CSQ: cell signal quality
def cb_get_csq():
    rv = detect_quectel_usb_ports()
    if not rv:
        _p_e('could not detect quectel USB ports for CSQ')
        time.sleep(2)
        return
    _, p_ctl = rv

    till = time.perf_counter() + 1
    b = bytes()
    ser = None
    try:
        ser = serial.Serial(p_ctl, 115200, timeout=.1, rtscts=True, dsrdtr=True)
        ser.write(b'AT+CSQ \r')
        time.sleep(.5)
        while time.perf_counter() < till:
            b += ser.read()
        ser.close()
    except (Exception,):
        _p_e('error working with serial port on CSQ')
        if ser and ser.is_open:
            ser.close()
        input()
        return

    # +CSQ: 19,99 among other lines
    try:
        # _p_e(f'CSQ b = {b}')
        v = b.split(b'+CSQ: ')[1].split(b',')[0]
        # _p_e(f'CSQ v = {v}')
        v = int(v.decode())
    except (Exception,) as ex:
        _p_e(f'exception on CSQ {ex}')
        input()
        return

    # page 81 datasheet EG25
    s = ''
    if v == 0:
        s = '< -113 dBm'
    elif v == 1:
        s = '-111 dBm'
    elif 2 <= v <= 30:
        s = f'{-113 + (2 * v)} dBm'
    elif v == 31:
        s = '> -51 dBm'
    elif v == 99:
        s = 'not detectable'
    elif v == 100:
        s = '< -116 dBm'
    elif v == 101:
        s = '-115 dBm'
    elif 102 <= v <= 190:
        s = f'{-114 + (1 * v)} dBm'
    elif v == 191:
        s = '> -25 dBm'
    elif v == 199:
        s = 'not detectable'
    _p(f'cell signal quality {s} (lowest is -115 dBm)')
    input()


def cb_get_gsq():
    # get the USB ports
    ls_ports_gps_ctl = detect_quectel_usb_ports()
    if not ls_ports_gps_ctl:
        _p_e('could not detect quectel USB ports for CSQ')
        time.sleep(2)
        return
    p_gps, p_ctl = ls_ports_gps_ctl


    # let the user decide
    print('\nQUESTION: Do you want to power-cycle GPS shield? (y/n) -> ', end='')
    question = input().lower()
    if question in ('y', 'yes'):
        gps_power_cycle_ddc(p_ctl)


    # open 2 ports
    os.system('clear')
    ser = serial.Serial(p_gps, 115200, timeout=.1)
    ser_ctl = serial.Serial(p_ctl, 115200, timeout=1)

    # ensure GPS output is activated, this code is same as gps_power_cycle()
    try:
        print('trying to reactivate GPS')
        ser_ctl.write(b'AT+QGPSEND\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.write(b'AT+QGPSDEL=1\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.write(b'AT+QGPS=1\r')
        time.sleep(.1)
        rv = ser_ctl.read_all()
        print(rv)
        ser_ctl.reset_input_buffer()
        time.sleep(1)
    except (Exception, ) as ex:
        print(f'error: gps_power_cycle_ddc {ex}')
    finally:
        if ser_ctl and ser_ctl.is_open:
            ser_ctl.close()

    # starts GPS signal quality loop
    while 1:

        # get a lot of GPS bytes
        os.system('clear')
        print('GPS quality test running, please wait some seconds\n')
        bb = ser.read_all()
        ser.reset_input_buffer()

        # we only keep GPRMC / GPGSV lines
        ls_gps = bb.split(b'\r\n')
        ls_rmc = [i for i in ls_gps if i and i.startswith(b'$GPRMC') and i[-3] == 42]
        ls_gsv = [i for i in ls_gps if i and i.startswith(b'$GPGSV') and i[-3] == 42]
        line_rmc = ''
        if ls_rmc:
            line_rmc = ls_rmc[-1].decode()
        print(ls_rmc)
        print(ls_gsv)

        # parse line GPRMC
        s = '\n'
        last_lat_lon = ''
        last_time = ''
        if not line_rmc:
            s += "RMC --> none\n"
        else:
            g = line_rmc.split(',')
            # g: ['$GPRMC', '145557.00', 'A', '4136.603719', 'N', '07036.560277', 'W', ...]
            if g[2] == 'A':
                def toDD(s):
                    d = float(s[:-7])
                    m = float(s[-7:]) / 60
                    return d + m

                last_lat_lon = (toDD(g[3]), g[4], toDD(g[5]), g[6])
                last_time = f'{g[1][0:2]}:{g[1][2:4]}:{g[1][4:6]}'
                s += f'RMC --> {last_lat_lon}    {last_time}\n'
            else:
                s += "RMC --> ,,,,\n"

        print(s, end='')
        s = ''

        # wait for the first frame of the GPGSV set
        d = {}
        for i in ls_gsv:
            f = i.decode().split(',')
            # 1    = Total number of messages of this type in this cycle
            # 2    = Message number
            # 3    = Total number of SVs in view
            # 4    = SV PRN number
            # 5    = Elevation in degrees, 90 maximum
            # 6    = Azimuth, degrees from true north, 000 to 359
            # 7    = SNR, 00-99 dB (null when not tracking)
            # 8-11 = Information about second SV, same as field 4-7
            # 12-15= Information about third SV, same as field 4-7
            # 16-19= Information about fourth SV, same as field 4-7
            mn = f[2]
            for j in range(4, 17, 4):
                try:
                    s_id = f[j]
                    s_snr = f[j + 3]
                    d[s_id] = s_snr
                except:
                    pass

        n = len(d)
        if d:
            # d: {'1': {'04': '26', '05': '35', '06': '34', '09': '32'},
            #     '2': {'11': '30', '12': '35', '19': '30', '21': '34'},
            #     '3': {'25': '30', '29': '30', '13': '', '17': ''}}
            d = {k: v for k, v in d.items() if v}
            m = len(d)
            s += f'GSV --> {n} satellites, {n - m} of which reporting no SNR\n'
            s += '\n[ id ] snr     (max 99)\n'
            s += '-----------------------\n'
            for k, v in d.items():
                s += f'[ {k} ] snr {v} '
                s += ('#' * int(v)) + '\n'

        print(s)
        time.sleep(3)




def cb_test_buttons():
    try:
        if not is_rpi():
            p_e('no Rpi for buttons test')
            return
        from scripts.script_test_box_buttons import main_test_box_buttons
        main_test_box_buttons()
    except (Exception,) as ex:
        p_e(str(ex))


def cb_run_brt():
    c = '/home/pi/li/ddh/run_brt.sh'
    rv = sp.run(c, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    if rv.returncode:
        print(f'BRT error: {rv.stderr}')
        input()


def cb_run_nadv():
    main_nadv()


def cb_run_deploy_dox():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_deploy_dox)
    except (Exception,) as ex:
        p_e(f'{ex} running deploy_dox')


def cb_run_deploy_tdo():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_deploy_tdo)
    except (Exception,) as ex:
        p_e(f'{ex} running deploy_tdo')


def cb_run_scan_li():
    try:
        # do this or this script's prompts fail
        sp.run(path_script_scan_li)
    except (Exception,) as ex:
        p_e(f'{ex} running scan_li')


def cb_edit_brt_cfg_file():
    p_cfg = f'{h}/Downloads/cfg_brt_nadv.toml'
    if not os.path.exists(p_cfg):
        sp.run(f'cp scripts/cfg_brt_nadv_template.toml {p_cfg}')
    sp.call(['nano', p_cfg],
            stdin=sys.stdin, stdout=sys.stdout)


def cb_edit_ddh_config_file():
    sp.call(['nano', _get_config_file_path()],
            stdin=sys.stdin, stdout=sys.stdout)


def _check_aws_credentials():
    c = cfg_load_from_file()
    f = c['credentials']
    for k, v in f.items():
        if not v:
            if 'custom' not in k:
                # 0 is bad
                return 0
    return check_aws_run(f)


def cb_print_check_all_keys(verbose=True):
    path_w = '/etc/wireguard/wg0.conf'
    if is_rpi():
        c = f'sudo ls {path_w}'
        rv = sp.run(c, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        w = rv.returncode == 0
    else:
        w = os.path.exists(path_w)
    a = os.path.exists(f'{h}/.ssh/authorized_keys')
    c = _check_aws_credentials()
    m = os.path.exists(f'{get_ddh_folder_path_settings()}/all_macs.toml')

    rv = w and a and c and m

    if rv:
        return rv

    if verbose and not w:
        p_e('missing wireguard VPN conf file')
    if verbose and not a:
        p_i('missing SSH authorized keys file')
    if verbose and not c:
        p_e('missing ddh/settings/config.toml credentials section')
    if verbose and not m:
        p_e('missing ddh/settings/all_macs.toml file')

    if verbose:
        input()
    return 0


def cb_is_ddh_running():
    rh = sp.run('ps aux | grep -w main_ddh | grep -v grep > /dev/null',
                shell=True).returncode == 0
    rs = sp.run('ps aux | grep -w main_dds | grep -v grep > /dev/null',
                shell=True).returncode == 0
    return int(rh and rs)


# --------------
# main DCC loop
# --------------


def cb_ddh_show_help():
    _p('test mode    -> prefixes downloaded filenames with "testfile_"')
    _p('GPS dummy    -> GPS is simulated, it uses position in config.toml')
    _p('GPS USB puck -> GPS source is a GPS USB puck, not a RPi shield')
    _p('crontab      -> automatically starts or not DDH app upon boot')
    # _p('kill DDH     -> forces DDH app to quit')
    _p('graph demo   -> the DDH plotting tab will use simulated data')
    _p('credentials  -> checks the DDH has all the passwords to run OK')
    _p('GPS shield   -> tests the GPS shield, not the GPS USB puck')
    _p('side buttons -> tests the DDH real side buttons to be working')
    _p('BLE range    -> tests how well a logger\'s signal reaches the DDH')
    _p('deploy DOX   -> prepares a DO-1 or DO-2 logger for deployment')
    _p('deploy TDO   -> prepares a TDO logger for deployment')
    _p('detect LI    -> detects BLE Lowell Instruments loggers around')
    _p('cell quality -> tests how good cell reception is')
    _p('GPS quality  -> tests how good GPS reception is')
    # _p('calibrate    -> tunes the DDH touch display')
    _p('see issues   -> check any potential DDH conflict or misconfiguration')
    input()


def main_ddc():
    # clearing error log file
    c_e()

    while 1:
        os.system('clear')
        print('\nDDC\n---')

        # -------------------------
        # check everything at once
        # -------------------------
        global g_e
        global g_w
        global g_i
        _, g_e, g_w, g_i = ddh_run_check()

        # get flags
        fgd = 1 if exists(LI_PATH_GPS_DUMMY) else 0
        fge = 1 if exists(LI_PATH_DDH_GPS_EXTERNAL) else 0
        fcd = get_crontab('ddh')
        fgt = 1 if exists(TMP_PATH_GRAPH_TEST_MODE_JSON) else 0
        fdk = cb_print_check_all_keys(verbose=False)
        fdr = cb_is_ddh_running()
        ftm = 1 if exists(LI_PATH_TEST_MODE) else 0

        # create options
        d = {
            '0': (f"0) set test mode     [{ftm}]", cb_test_mode),
            '1': (f"1) set GPS dummy     [{fgd}]", cb_gps_dummy),
            '2': (f"2) set GPS USB puck  [{fge}]", cb_gps_external),
            '3': (f"3) set crontab       [{fcd}]", cb_crontab_ddh),
            # '4': (f"4) kill DDH app      [{fdr}]", cb_kill_ddh),
            '5': (f"5) set graph demo    [{fgt}]", cb_graph_demo),
            '6': (f"6) check all keys    [{fdk}]", cb_print_check_all_keys),
            '7': (f"7) test GPS shield", cb_test_gps_quectel),
            '8': (f"8) test side buttons", cb_test_buttons),
            'r': (f"r) run BLE range tool", cb_run_brt),
            # 'e': (f"e) edit BLE range tool", cb_edit_brt_cfg_file),
            'o': (f"o) deploy logger DOX", cb_run_deploy_dox),
            't': (f"t) deploy logger TDO", cb_run_deploy_tdo),
            'b': (f"b) detect LI loggers around", cb_run_scan_li),
            # 'u': (f"u) list Quectel USB ports", cb_list_quectel_usb_ports),
            's': (f"s) get cell signal quality (beta)", cb_get_csq),
            'g': (f"g) get GPS  signal quality", cb_get_gsq),
            'i': (f"i) ~ see issues ~", cb_ddh_show_issues),
            'h': (f"h) help", cb_ddh_show_help),
            'q': (f"q) quit", cb_quit)
        }

        # show menu
        for k, v in d.items():
            if 'issues' in v[0]:
                # color of the 'see issues' entry
                if g_e:
                    PC.R(f'\t{v[0]}')
                elif g_w:
                    PC.Y(f'\t{v[0]}')
                elif g_i:
                    PC.B(f'\t{v[0]}')
                else:
                    PC.G(f'\t{v[0]}')

            # normal entry
            else:
                print(f'\t{v[0]}')

        # get user input
        c = input('\nenter your choice > ')
        try:
            os.system('clear')
            print(f'you selected:\n\t{d[c][0]}')
            time.sleep(.5)

            # -----------------
            # hidden options
            # -----------------
            if c == 'p':
                cb_provision_ddh()
            elif c == 'k':
                cb_edit_ddh_config_file()
            elif c == 'c':
                cb_calibrate_display()
            elif c == 'u':
                cb_list_quectel_usb_ports()
            else:
                _, cb = d[c]
                cb()

        except (Exception,):
            p_e(f'invalid menu option {c}')
            time.sleep(1)


if __name__ == "__main__":
    main_ddc()
