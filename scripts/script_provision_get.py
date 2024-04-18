#!/usr/bin/env python3


import os
import pathlib
import re
import shutil
import subprocess as sp
import time

import requests
import toml


DDN_PRV_PORT = 9001
DDN_ADDR = '0.0.0.0'
# DDN_ADDR = 'ddn.lowellinstruments.com'
HOME = str(pathlib.Path.home())
PBF = f'{HOME}/.ddh_prov_req.toml'


def _p(s):
    print(f'[ PRV ] {s}')


def _sh(c):
    rv = sp.run(c, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)
    return rv.returncode


def _is_rpi():
    return _sh('cat /proc/cpuinfo | grep aspberry') == 0


def extract_filename_from_content_disposition_header(cd):
    # src: codementor, downloading-files-from-urls-in-python-77q3bs0un
    if not cd:
        return None
    s = re.findall('filename=(.+)', cd)
    if len(s) == 0:
        return None
    return s[0].replace('"', '')


def req(url):
    try:
        rsp = requests.get(url, timeout=5)
        rsp.raise_for_status()
    except (Exception, ):
        pass
    else:
        return rsp


def get_files_from_server(pr, sn, ip, addr=DDN_ADDR, port=DDN_PRV_PORT):
    url = f'http://{addr}:{port}/ddh_provision/v1?prj={pr}&sn={sn}&ip={ip}'
    rsp = req(url)
    if rsp and rsp.status_code == 200:
        h = rsp.headers.get('content-disposition')
        fn = extract_filename_from_content_disposition_header(h)
        dst = f'/tmp/{fn}'
        with open(dst, 'wb') as f:
            f.write(rsp.content)
        return dst


def _read_provision_bootstrap_file():
    with open(PBF, 'r') as f:
        c = toml.load(f)
    pr = c['provision']['boat_prj']
    sn = c['provision']['boat_sn']
    ip = c['provision']['vpn_ip']
    _p(f'read provision request file: prj {pr} sn {sn} ip {ip}')
    return pr, sn, ip


def get_provision_ddh(a=DDN_ADDR):
    """
    # example bootstrap provision file /home/pi/.ddh_prov_req.toml'
    [provision]
    vpn_ip="1.2.3.4"
    boat_sn="1234567"
    boat_prj="kaz"
    """

    try:
        # pr, sn, ip = _read_provision_bootstrap_file()
        pr, sn, ip = 'kaz', '7777777', '1.2.3.4'
        dst = get_files_from_server(pr, sn, ip, a)
        if not dst:
            print('error get_files_from_server')
            return
        if not _is_rpi():
            return
        _sh(f'unzip -o {dst}')
        #     d = '/home/pi/li/ddh/settings'
        #     p = f'{FOL_ANSWER}/config.toml'
        #     _p(f'moving {p} to DDH settings folder')
        #     _sh(f'mv {p} {d}')
        #     p = f'{FOL_ANSWER}/all_macs.toml'
        #     _p(f'moving {p} to DDH settings folder')
        #     _sh(f'mv {p} {d}')
        #     p = f'{FOL_ANSWER}/wg0.conf'
        #     _p(f'moving {p} to wireguard settings folder')
        #     d = '/etc/wireguard'
        #     _sh(f"sudo mv {p} {d}")
        #     _p('restarting DDH wireguard service')
        #     _sh("sudo systemctl restart wg-quick@wg0.service")
        #     _p('enabling DDH wireguard service')
        #     _sh("sudo systemctl enable wg-quick@wg0.service")
        #
        #     # get rid of the file so only executes once
        #     # os.unlink(PBF)
    except (Exception, ) as ex:
        # such as "no bootstrap provision file"
        _p(f'\nexception provision_ddh -> {str(ex)}')
    finally:
        # see any message
        time.sleep(5)


if __name__ == '__main__':
    get_provision_ddh()
    # provision('0.0.0.0')
