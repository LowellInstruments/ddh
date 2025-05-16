import threading
import time
from signal import pause
from gpiozero import Button
from mat.utils import linux_is_rpi
from utils.ddh_config import exp_get_new_side_buttons, exp_get_custom_side_buttons_debounce_time
from utils.ddh_shared import (
    send_ddh_udp_gui as _u,
    STATE_DDS_PRESSED_BUTTON_2,
    STATE_DDS_PRESSED_BUTTON_1, STATE_DDS_PRESSED_BUTTON_3,
)


# old based on config.toml flag
# new_or_old = exp_get_new_side_buttons()
new_or_old = 1


TIME_DB_S = .001
TIME_LO_S = .5
g_last_t = 0
MS_100 = (1 / 10)
MS_10 = (1 / 100)
MS_1 = (1 / 1000)
PIN_BTN_1 = 16
PIN_BTN_2 = 20
PIN_BTN_3 = 21


# custom debounce time
cdt = exp_get_custom_side_buttons_debounce_time()
if cdt == 1:
    cdt = .1
elif cdt == 2:
    cdt = .01
else:
    cdt = .001


def _th_gpio_box_buttons():
    # if not linux_is_rpi():
    #     return

    if new_or_old == 1:
        print(f'new buttons thread using cdt = {cdt}')
        b1 = Button(PIN_BTN_1, pull_up=True, bounce_time=cdt)
        b2 = Button(PIN_BTN_2, pull_up=True, bounce_time=cdt)
        b3 = Button(PIN_BTN_3, pull_up=True, bounce_time=cdt)
    else:
        b1 = Button(PIN_BTN_1, pull_up=True, bounce_time=TIME_DB_S)
        b2 = Button(PIN_BTN_2, pull_up=True, bounce_time=TIME_DB_S)
        b3 = Button(PIN_BTN_3, pull_up=True, bounce_time=TIME_DB_S)

    def _cb():
        t = time.perf_counter()
        global g_last_t
        if t > g_last_t + TIME_LO_S:
            g_last_t = t
            return True

    # v0 old ones
    def b1_cb_v0():
        if _cb():
            _u(STATE_DDS_PRESSED_BUTTON_1)

    def b2_cb_v0():
        if _cb():
            _u(STATE_DDS_PRESSED_BUTTON_2)

    def b3_cb_v0():
        pass

    # v1 new ones
    def b1_cb_v1():
        time.sleep(MS_10)
        if b1.is_pressed:
            _u(STATE_DDS_PRESSED_BUTTON_1)

    def b2_cb_v1():
        time.sleep(MS_10)
        if b2.is_pressed:
            _u(STATE_DDS_PRESSED_BUTTON_2)

    def b3_cb_v1():
        for i in range(50):
            # half second
            time.sleep(MS_10)
            if not b3.is_pressed:
                return
        _u(STATE_DDS_PRESSED_BUTTON_3)

    if new_or_old == 1:
        b1.when_pressed = b1_cb_v1
        b2.when_pressed = b2_cb_v1
        b3.when_pressed = b3_cb_v1
    else:
        b1.when_pressed = b1_cb_v0
        b2.when_pressed = b2_cb_v0
        b3.when_pressed = b3_cb_v0

    pause()


def dds_create_buttons_thread():
    print(f'creating buttons thread v{new_or_old}')
    bth = threading.Thread(target=_th_gpio_box_buttons)
    bth.start()


if __name__ == '__main__':
    dds_create_buttons_thread()
