import os

from mat.utils import linux_is_rpi
from utils.logs import lg_sta as lg
from utils.ddh_shared import get_ddh_folder_path_tweak
import toml

FILE_SAVED_PREFERENCES = f'{get_ddh_folder_path_tweak()}/.saved_preferences.toml'


def _check_preferences_file_exists():
    if not os.path.exists(FILE_SAVED_PREFERENCES):
        lg.a('set brightness value 255 (100% = clicks 9) to preferences file')
        state_save_brightness_clicks(9)
        lg.a('set models index value 0 to preferences file')
        state_save_models_index(0)


def state_get_saved_brightness_clicks():
    if not linux_is_rpi():
        return
    _check_preferences_file_exists()
    with open(FILE_SAVED_PREFERENCES, 'r') as f:
        d = toml.load(f)
        v = d['brightness']
        lg.a(f'read saved brightness clicks = {v} from preferences file')
        return v


def state_get_saved_models_index():
    _check_preferences_file_exists()
    with open(FILE_SAVED_PREFERENCES, 'r') as f:
        d = toml.load(f)
        v = d['models_idx']
        lg.a(f'read saved models index = {v} from preferences file')
        return v


def state_save_brightness_clicks(v):
    d = dict()
    d['brightness'] = v
    with open(FILE_SAVED_PREFERENCES, 'w') as f:
        toml.dump(d, f)
    lg.a(f'saving brightness = {v} to preferences file')


def state_save_models_index(v):
    d = dict()
    d['models_idx'] = v
    with open(FILE_SAVED_PREFERENCES, 'w') as f:
        toml.dump(d, f)
    lg.a(f'saving model index = {v} to preferences file')


def state_ble_init_rv_notes(d: dict):
    d["battery_level"] = 0xFFFF
    d["error"] = ""
    d["crit_error"] = 0
    d["dl_files"] = []
    d["rerun"] = False
    d["gfv"] = ''


def state_ble_logger_ccx26x2r_needs_a_reset(mac):
    mac = mac.replace(':', '-')
    r = get_ddh_folder_path_tweak()

    # checks existence of 'tweak/<mac>.rst' file
    file_path = f'{r}/{mac}.rst'
    rv = os.path.exists(file_path)
    if rv:
        lg.a("debug: logger reset file {} found".format(file_path))
        os.unlink(file_path)
        lg.a("debug: logger reset file {} deleted".format(file_path))
    return rv


class DdhState:
    def __init__(self):
        self.downloading_ble = False
        self.ble_reset_req = 0

    def state_set_downloading_ble(self): self.downloading_ble = 1
    def state_clr_downloading_ble(self): self.downloading_ble = 0
    def state_get_downloading_ble(self): return self.downloading_ble
    def state_set_ble_reset_req(self): self.ble_reset_req = 1
    def state_clr_ble_reset_req(self): self.ble_reset_req = 0
    def state_get_ble_reset_req(self): return self.ble_reset_req


ddh_state = DdhState()
