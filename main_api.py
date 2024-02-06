#!/usr/bin/env python3

import datetime
import pathlib
import shutil
import setproctitle
from api.api_utils import get_git_commit_mat_local, \
    get_ip_vpn, get_ip_wlan, get_ip_cell, \
    get_running, get_crontab_ddh, shell, \
    set_crontab, \
    get_git_commit_ddh_local, \
    get_ble_state, get_gps, get_logger_mac_reset_files, get_versions, api_get_full_ddh_config_file_path, \
    linux_app_write_pid_to_tmp, linux_is_rpi
from utils.ddh_config import dds_get_cfg_vessel_name, dds_get_cfg_box_sn, dds_get_cfg_box_project
from utils.logs import (
    lg_api as lg,
)
import uvicorn
from fastapi import FastAPI, UploadFile, File
import os
from fastapi.responses import FileResponse
import concurrent.futures


DDH_PORT_API = 8000
NAME_EXE_API = "main_api"
PID_FILE_API = "/tmp/{}.pid".format(NAME_EXE_API)


app = FastAPI()


def _get_ddh_folder_path_dl_files():
    # where is the file main_api.py
    p = pathlib.Path(__file__).parent.resolve()
    return p + '/dl_files'


@app.get('/ping')
async def ep_ping():
    d = {
        "ping": "OK",
        "ip_vpn": get_ip_vpn(),
        "ip_wlan": get_ip_wlan(),
        "vessel": dds_get_cfg_vessel_name(),
        "is_rpi": linux_is_rpi()
    }
    return d


ep = 'upload_conf'


@app.post(f"/{ep}")
async def api_upload_conf(file: UploadFile = File(...)):
    if not file.filename == 'config.toml':
        return {ep: 'error_name'}

    # accept the upload and save it to /tmp folder
    uploaded_name = f'/tmp/{file.filename}'
    try:
        with open(uploaded_name, "wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except (Exception, ):
        return {ep: 'error_uploading'}

    # overwrite DDH configuration only on DDH boxes
    if not linux_is_rpi():
        return {ep: 'no_install_not_Rpi'}

    p = api_get_full_ddh_config_file_path()
    rv = shell(f'cp {uploaded_name} {p}')
    if rv.returncode:
        return {ep: 'error_installing'}

    # response back
    return {ep: 'OK'}


@app.get('/info')
async def api_get_info():
    def _th(cb):
        # src: stackoverflow 6893968
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(cb)
            return future.result()

    d = {
        'info': "OK",
        "ip_vpn": _th(get_ip_vpn),
        "ip_wlan": _th(get_ip_wlan),
        "ip_cell": _th(get_ip_cell),
        "gps": _th(get_gps),
        "ble_state": _th(get_ble_state),
        "boat_prj": _th(dds_get_cfg_box_project),
        "boat_sn": _th(dds_get_cfg_box_sn),
        "boat_name": _th(dds_get_cfg_vessel_name),
        "running": _th(get_running),
        "crontab": _th(get_crontab_ddh),
        "mac_reset_files": _th(get_logger_mac_reset_files),
        "versions": _th(get_versions),
        "commit_mat": _th(get_git_commit_mat_local),
        "commit_ddh": _th(get_git_commit_ddh_local),
    }
    return d


@app.get('/logs_get')
async def ep_logs_get():
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    vn = dds_get_cfg_vessel_name()
    vn = vn.replace(' ', '')
    file_name = 'logs_{}_{}.zip'.format(vn, now)
    # zip ONLY .log files
    c = 'zip -r {} logs/*.log'.format(file_name)
    rv = shell(c)
    if rv.returncode == 0:
        c = 'mv {} logs/'.format(file_name)
        rv = shell(c)
        if rv.returncode == 0:
            p = 'logs/' + file_name
            fr = FileResponse(path=p, filename=file_name)
            return fr


@app.get("/conf_get")
async def ep_conf_get():
    # prepare the zip file name
    vn = dds_get_cfg_vessel_name()
    vn = vn.replace(' ', '')
    file_name = 'conf_{}.zip'.format(vn)

    # zip it, -o flag overwrites if already exists
    p = '/tmp/{file_name}'
    cf = api_get_full_ddh_config_file_path()
    rv = shell(f'zip -o {p} {cf}')

    # send it as response
    if rv.returncode == 0:
        return FileResponse(path=p, filename=file_name)


@app.get("/dl_files_get")
async def ep_dl_files_get():
    vn = dds_get_cfg_vessel_name()
    vn = vn.replace(' ', '')
    file_name = 'dl_files_{}.zip'.format(vn)

    # zip it, -o flag overwrites if already exists
    s = _get_ddh_folder_path_dl_files()
    lg.a(f'cwd is {os.getcwd()}, getting files from {s}')
    p = '/tmp/' + file_name
    c = 'zip -ro {} {}'.format(p, s)
    rv = shell(c)

    # send it as response
    if rv.returncode == 0:
        return FileResponse(path=p, filename=file_name)


def _ep_update(_ep, c):
    if not linux_is_rpi():
        return {ep: 'not RPi, not updating DDH'}
    rv = shell(c)
    return {_ep: 'OK' if rv.returncode == 0 else 'error'}


@app.get('/update_ddt')
async def ep_update_ddt():
    return _ep_update('update_ddt', 'cd ../ddt && git pull')


@app.get('/update_ddh')
async def ep_update_ddh():
    return _ep_update('update_ddh', 'cd scripts && ./pop_ddh.sh')


@app.get('/update_mat')
async def ep_update_mat():
    return _ep_update('update_mat', 'cd scripts && ./pop_mat.sh')


@app.get('/kill_ddh')
async def ep_kill_ddh():
    d = dict()
    for i in ('main_ddh', 'main_ddh_controller',
              'main_dds', 'main_dds_controller'):
        rv = shell(f'killall {i}')
        s = rv.stderr.decode().replace('\n', '')
        if rv.returncode == 0:
            s = 'OK'
        d[i] = s
    return d


@app.get('/kill_api')
async def ep_kill_api():
    shell('killall main_api')
    # does not matter, won't answer
    return {'kill_api': 'OK'}


@app.get("/cron_ena")
async def ep_crontab_enable():
    if not linux_is_rpi():
        return {'cron_ena': 'not RPi, not enabling crontab'}
    set_crontab(1)
    return {'cron_ena': get_crontab_ddh()}


@app.get("/cron_dis")
async def ep_crontab_disable():
    if not linux_is_rpi():
        return {'cron_dis': 'not RPi, not disabling crontab'}
    set_crontab(0)
    return {'cron_dis': get_crontab_ddh()}


def main_api():
    # docs at http://0.0.0.0/port/docs
    setproctitle.setproctitle(NAME_EXE_API)
    linux_app_write_pid_to_tmp(PID_FILE_API)
    uvicorn.run(app, host="0.0.0.0", port=DDH_PORT_API)


if __name__ == "__main__":
    main_api()
