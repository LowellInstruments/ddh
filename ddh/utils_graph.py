from functools import lru_cache
from glob import glob
import os
from mat.utils import linux_is_rpi
import pandas as pd
import dateutil.parser as dp
from os.path import basename


_g_ff_t = []
_g_ff_p = []
_g_ff_do = []


# grab all mac folders
def graph_get_fol_list():
    """
    return absolute paths of "dl_files/<mac>" folders
    """
    d = '/home/pi/li/ddh/dl_files'
    if not linux_is_rpi():
        d = '/home/kaz/PycharmProjects/ddh/dl_files'

    if os.path.isdir(d):
        f_l = [f.path for f in os.scandir(d) if f.is_dir()]
        # remove 'ddh_vessel' folders
        return [f for f in f_l if "ddh" not in basename(f)]
    return []


# get graph_req.json from /tmp containing the FULL ABSOLUTE folder path to plot
def graph_get_fol_req_file():
    # file written by DDH plot request
    with open('/tmp/graph_req.json') as f:
        fol = f.read().strip()
    if not os.path.exists(fol):
        raise FileNotFoundError('inexistent plot folder')
    return fol


@lru_cache
def graph_get_data_csv(fol, h, hi) -> dict:
    global _g_ff_t, _g_ff_p, _g_ff_do

    _g_ff_t = sorted(glob("{}/{}".format(fol, "*_Temperature.csv")))
    _g_ff_p = sorted(glob("{}/{}".format(fol, "*_Pressure.csv")))
    _g_ff_do = sorted(glob("{}/{}".format(fol, "*_DissolvedOxygen.csv")))

    # type of haul to plot
    met = ''
    if _g_ff_t:
        if h == 'all hauls':
            _g_ff_t = _g_ff_t
        elif h == 'last haul':
            _g_ff_t = _g_ff_t[-1:]
        else:
            _g_ff_t = [_g_ff_t[hi]]
    if _g_ff_p:
        if h == 'all hauls':
            _g_ff_p = _g_ff_p
        elif h == 'last haul':
            _g_ff_p = _g_ff_p[-1:]
        else:
            _g_ff_p = [_g_ff_p[hi]]
    if _g_ff_do:
        met = 'DO'
        if h == 'all hauls':
            _g_ff_do = _g_ff_do
        elif h == 'last haul':
            _g_ff_do = _g_ff_do[-1:]
        else:
            _g_ff_do = [_g_ff_do[hi]]

    # check metric is set
    if not met:
        return {
            'metric': '',
        }

    # grab values
    s = 'drawing metric {} folder {} hauls {} hi {}'
    print(s.format(met, basename(fol), h, hi))
    if met == 'TP':
        x, t, p = [], [], []
        for f in _g_ff_t:
            print('\tread file', basename(f))
            df = pd.read_csv(f)
            # grab Time (x) values from here
            x += list(df['ISO 8601 Time'])
            t += list(df['Temperature (C)'])
        for f in _g_ff_p:
            print('\tread file', basename(f))
            df = pd.read_csv(f)
            p += list(df['Pressure (dbar)'])

        # convert 2018-11-11T13:00:00.000 --> epoch seconds
        x = [dp.parse('{}Z'.format(i)).timestamp() for i in x]
        return {
            'metric': met,
            'ISO 8601 Time': x,
            'Temperature (C)': t,
            'Pressure (dbar)': p,
        }

    elif met == 'DO':
        x, doc, dot = [], [], []
        for f in _g_ff_do:
            print('\tread file', basename(f))
            df = pd.read_csv(f)
            x += list(df['ISO 8601 Time'])
            doc += list(df['Dissolved Oxygen (mg/l)'])
            dot += list(df['DO Temperature (C)'])

        # convert 2018-11-11T13:00:00.000 --> epoch seconds
        x = [dp.parse('{}Z'.format(i)).timestamp() for i in x]
        return {
            'metric': met,
            'ISO 8601 Time': x,
            'Dissolved C': doc,
            'Dissolved T': dot
        }

    else:
        print('error: graph_get_all_csv() unknown metric')
        assert False
