import glob
import os
import pathlib
from dds.timecache import its_time_to
from mat.data_converter import default_parameters, DataConverter
from mat.data_file_factory import load_data_file
from mat.tap import convert_tap_file
from mat.utils import linux_ls_by_ext
from utils.logs import lg_cnv as lg
from utils.ddh_shared import (
    send_ddh_udp_gui as _u,
    get_ddh_folder_path_dl_files,
    STATE_DDS_NOTIFY_CONVERSION_ERR,
    STATE_DDS_NOTIFY_CONVERSION_OK,
)
import pandas as pd


"""
code in this file only takes care of LID data files
"""


PERIOD_CNV_SECS = 3600 * 12
BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR = 10.1
DDH_BPSL = BAROMETRIC_PRESSURE_SEA_LEVEL_IN_DECIBAR


_g_files_we_cannot_convert = []
_g_files_already_converted = []
_g_last_nf = 0


def _lid_file_has_sensor_data_type(path, suffix):
    _map = {"_DissolvedOxygen": "DOS", "_Temperature": "TMP", "_Pressure": "PRS"}
    header = load_data_file(path).header()
    return header.tag(_map[suffix])


def _cnv(fol, suf) -> (bool, list):

    # check asked folder (ex: dl_files/e5-fc-4e-94-ed-dd) exists
    if not pathlib.Path(fol).is_dir():
        lg.a("error: folder {} not found".format(fol))
        return False, []

    # check asked suffix (ex: _DissolvedOxygen) exists
    valid_suffixes = ("_DissolvedOxygen", "_Temperature", "_Pressure")
    if suf not in valid_suffixes:
        lg.a("error: unknown suffix {}".format(suf))
        return False, []

    # we only convert LID files
    parameters = default_parameters()
    err_files = []
    all_ok = True
    global _g_files_we_cannot_convert
    lid_files = linux_ls_by_ext(fol, "lid")

    for f in lid_files:
        # do not convert test_files
        if os.path.basename(f).startswith('test'):
            continue
        # do not convert when already have CSV files for this LID file
        _ = "{}{}.csv".format(f.split(".")[0], suf)
        if pathlib.Path(_).is_file():
            global _g_files_already_converted
            s = "debug: skip conversion, file {} already exists"
            if _ not in _g_files_already_converted:
                lg.a(s.format(_))
                _g_files_already_converted.append(_)
            continue

        # do not convert when LID file already known as defective
        if f in _g_files_we_cannot_convert:
            continue

        # -----------------------------
        # try to convert this LID file
        # -----------------------------
        try:
            # skip files not containing this sensor data
            if not _lid_file_has_sensor_data_type(f, suf):
                # s = 'debug: skip conversion, file {} has no {} data'
                # lg.a(s.format(f, suf))
                continue

            DataConverter(f, parameters).convert()
            lg.a("converted file {} for suffix {}".format(f, suf))

            # --------------------------------
            # RN4020: hack for pressure adjust
            # --------------------------------
            if ("_Pressure" in suf) and ("moana" not in f.lower()):
                lg.a("debug: adjusting LI file {}".format(f))
                fp_csv = f[:-4] + "_Pressure.csv"
                df = pd.read_csv(fp_csv)
                c = "Pressure (dbar)"
                df[c] = df["Pressure (dbar)"] - DDH_BPSL
                df[c] = df[c].apply(lambda x: x if x > 0 else 0)
                df.to_csv(fp_csv, index=False)

        except (ValueError, Exception) as ex:

            all_ok = False
            err_files.append(f)
            e = "error: converting file {}, metric {} --> {}"
            lg.a(e.format(f, suf, str(ex)))

            # add to black list of files
            if f not in _g_files_we_cannot_convert:
                e = "warning: ignoring file {} for metric {} from now on"
                lg.a(e.format(f, suf))
                _g_files_we_cannot_convert.append(f)

    return all_ok, err_files


# alias for this function
def convert_lid_to_csv(fol, suf) -> (bool, list):
    return _cnv(fol, suf)


def _cnv_metric(m):
    fol = str(get_ddh_folder_path_dl_files())
    rv, _ = _cnv(fol, m)
    return rv


def _cnv_all_tap_files():
    fol = str(get_ddh_folder_path_dl_files())
    if not fol:
        return []
    if not os.path.isdir(fol):
        return []

    global _g_files_we_cannot_convert
    global _g_files_already_converted
    wildcard = fol + '/**/*.lix'
    ff = glob.glob(wildcard, recursive=True)
    rv_all = 0

    wildcard = fol + '/**/*TAP.csv'
    _g_files_already_converted = glob.glob(wildcard, recursive=True)

    for f_tap in ff:
        # cases no conversion needed
        if not f_tap.endswith('.lix'):
            continue
        f_csv = f_tap[:-4] + '_TAP.csv'
        if f_csv in _g_files_already_converted:
            lg.a(f"debug: skip conversion, file {f_csv} already exists")
            continue
        if f_tap in _g_files_we_cannot_convert:
            continue

        # try to convert it
        rv, _ = convert_tap_file(f_tap, verbose=False)

        # populate lists
        if rv and f_tap not in _g_files_we_cannot_convert:
            lg.a("warning: ignoring file {f_tap} from now on")
            _g_files_we_cannot_convert.append(f_tap)
        rv_all += rv
    return rv_all == 0


def _cnv_serve():

    # detect we have to force a conversion sequence
    fol = str(get_ddh_folder_path_dl_files())
    global _g_last_nf
    ls = glob.glob(f'{fol}/**/*.lid', recursive=True)
    forced = len(ls) != _g_last_nf
    if forced:
        lg.a(f'OK: #LID files {_g_last_nf} -> {len(ls)}, conversion forced')
    _g_last_nf = len(ls)

    # this function does not run always, only from time to time
    if not its_time_to("do_some_conversions", PERIOD_CNV_SECS) and not forced:
        return

    # general banner
    s = f'conversion sequence started'
    lg.a('-' * len(s))
    lg.a(s)

    # error variable
    e = ""

    # this one includes WATER
    s = "some {} .lid files did not convert"
    m = "_DissolvedOxygen"
    rv = _cnv_metric(m)
    if not rv:
        e += "O_"
        lg.a(s.format(m))

    m = "_Temperature"
    rv = _cnv_metric(m)
    if not rv:
        e += "T_"
        lg.a(s.format(m))

    m = "_Pressure"
    rv = _cnv_metric(m)
    if not rv:
        e += "P_"
        lg.a(s.format(m))

    rv = _cnv_all_tap_files()
    if not rv:
        e += 'TAP_'
        lg.a(s.format('_TAP'))

    s = f'conversion sequence finished'
    lg.a(s)
    lg.a('-' * len(s))

    # GUI update
    if e:
        _u("{}/{}".format(STATE_DDS_NOTIFY_CONVERSION_ERR, e))
    else:
        _u("{}/OK".format(STATE_DDS_NOTIFY_CONVERSION_OK))


def cnv_serve():
    try:
        _cnv_serve()
    except (Exception, ) as ex:
        e = 'error: conversion exception ex ->'
        if its_time_to(e, 3600 * 6):
            lg.a(f'{e} {ex}')


if __name__ == '__main__':
    # we are currently inside "ddh/dds" folder
    os.chdir('../dl_files')
    # now we are inside "ddh/dl_files" folder
    print('working directory:', os.getcwd())
    for p in os.listdir():
        if (not os.path.isdir(p)) or p.startswith('ddh'):
            continue
        print(f'doing folder {p}')
        mask = f'{p}/*.csv'
        for f in glob.glob(mask):
            os.unlink(f)
        convert_lid_to_csv(p, '_DissolvedOxygen')
