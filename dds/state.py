from mat.ble.ble_mat_utils import ble_mat_get_antenna_type_v2


class DdhState:
    def __init__(self):
        self.ble_antenna_i, self.ble_antenna_s = ble_mat_get_antenna_type_v2()


ddh_state = DdhState()
