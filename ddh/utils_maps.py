import datetime
import glob
import os
import requests
from PyQt5.QtGui import QMovie

from dds.state import state_get_saved_models_index
from mat.utils import linux_is_rpi
from utils.ddh_shared import (
    ddh_get_folder_path_res,
)
from utils.logs import lg_gui as lg


def gui_populate_maps_tab(my_app):
    addr_ddn_api = 'ddn.lowellinstruments.com'
    port_ddn_api = 9000
    deg = 'F'

    # create names for maps
    fol = str(ddh_get_folder_path_res())
    now = str(datetime.datetime.now().strftime('%Y%m%d'))
    fg_dtm = f"{fol}/{now}_{deg}_dtm.gif"
    fg_gom = f"{fol}/{now}_{deg}_gom.gif"
    fg_mab = f"{fol}/{now}_{deg}_mab.gif"
    got_dtm = got_gom = got_mab = False

    # delete any previous (not today's) map gifs
    for i in glob.glob(f"{fol}/*.gif"):
        if 'error_maps' in i:
            continue
        if i in (fg_dtm, fg_gom, fg_mab):
            # do not delete today's maps
            continue
        lg.a(f'deleting old model gif file {i}')
        os.unlink(i)

    # when developing, delete even today's maps
    if not linux_is_rpi():
        lg.a('debug: developing, delete even today\'s models gif files')
        for i in glob.glob(f"{fol}/*.gif"):
            if 'error_maps' in i:
                continue
            os.unlink(i)

    # get DTM map from DDN
    t = 5
    if not os.path.exists(fg_dtm):
        lg.a(f"requesting today's DTM model file {fg_dtm}")
        url = f'http://{addr_ddn_api}:{port_ddn_api}/dtm?t={now}&deg={deg}'
        try:
            rsp = requests.get(url, timeout=t)
            rsp.raise_for_status()
            with open(fg_dtm, 'wb') as f:
                f.write(rsp.content)
                got_dtm = True
                lg.a('OK: got DTM model file')
        except (Exception,) as err:
            lg.a(f'error: DTM models request -> {err}')
    else:
        got_dtm = True
        lg.a(f"re-using today's DTM forecast model file {fg_dtm}")

    # get GOM map from DDN
    if not os.path.exists(fg_gom):
        lg.a(f"requesting today's GOM model file {fg_gom}")
        t = 5
        url = f'http://{addr_ddn_api}:{port_ddn_api}/gom?t={now}&deg={deg}'
        try:
            rsp = requests.get(url, timeout=t)
            rsp.raise_for_status()
            with open(fg_gom, 'wb') as f:
                f.write(rsp.content)
                got_gom = True
                lg.a('OK: got GOM model file')
        except (Exception,) as err:
            lg.a(f'error: GOM models request -> {err}')
    else:
        got_gom = True
        lg.a(f"re-using today's GOM forecast model file {fg_gom}")

    # get MAB map from DDN
    if not os.path.exists(fg_mab):
        lg.a(f"requesting today's MAB model file {fg_mab}")
        t = 5
        url = f'http://{addr_ddn_api}:{port_ddn_api}/mab?t={now}&deg={deg}'
        try:
            rsp = requests.get(url, timeout=t)
            rsp.raise_for_status()
            with open(fg_mab, 'wb') as f:
                f.write(rsp.content)
                got_mab = True
                lg.a('OK: got MAB model file')
        except (Exception,) as err:
            lg.a(f'error: MAB models request -> {err}')
    else:
        got_mab = True
        lg.a(f"re-using today's MAB forecast map file {fg_mab}")

    # calculate how many good maps we have
    my_app.n_good_maps = int(got_dtm) + int(got_gom) + int(got_mab)
    if my_app.n_good_maps > 1:
        my_app.btn_map_next.setVisible(True)

    # check user preferences
    n = state_get_saved_models_index()
    if n == 0 and got_dtm:
        lg.a(f'loading model DTM preferred by user = {n}')
        fp = fg_dtm
    elif n == 1 and got_gom:
        lg.a(f'loading model GOM preferred by user = {n}')
        fp = fg_gom
    elif n == 2 and got_mab:
        lg.a(f'loading model MAB preferred by user = {n}')
        fp = fg_mab
    # fallback
    else:
        if got_dtm:
            lg.a(f'loading default model DTM')
            fp = fg_dtm
        elif got_gom:
            lg.a(f'loading default model GOM')
            fp = fg_gom
        elif got_mab:
            lg.a(f'loading default model MAB')
            fp = fg_mab
        else:
            fp = f"{fol}/error_maps.gif"

    # load the models picture
    a = my_app
    a.gif_map = QMovie(fp)
    a.lbl_map.setMovie(a.gif_map)
    a.gif_map.start()
    a.map_filename = fp

