import threading
import time
from signal import pause
from gpiozero import Button
from mat.utils import linux_is_rpi
from utils.ddh_config import exp_get_new_side_buttons
from utils.ddh_shared import (
    send_ddh_udp_gui as _u,
    STATE_DDS_PRESSED_BUTTON_2,
    STATE_DDS_PRESSED_BUTTON_1,
)


new_or_old = exp_get_new_side_buttons()



TIME_LO_S = .5
TIME_DB_S = .001
g_last_t = 0


def _th_gpio_box_buttons():
    if not linux_is_rpi():
        return

    def _cb():
        t = time.perf_counter()
        global g_last_t
        if t > g_last_t + TIME_LO_S:
            g_last_t = t
            return True

    def button1_pressed_cb():
        if _cb():
            _u(STATE_DDS_PRESSED_BUTTON_1)

    def button2_pressed_cb():
        if _cb():
            _u(STATE_DDS_PRESSED_BUTTON_2)

    def button3_pressed_cb():
        pass

    b1 = Button(16, pull_up=True, bounce_time=TIME_DB_S)
    b2 = Button(20, pull_up=True, bounce_time=TIME_DB_S)
    b3 = Button(21, pull_up=True, bounce_time=TIME_DB_S)
    b1.when_pressed = button1_pressed_cb
    b2.when_pressed = button2_pressed_cb
    b3.when_pressed = button3_pressed_cb
    pause()



MS_100 = (1 / 10)
MS_10 = (1 / 100)
MS_1 = (1 / 1000)

PIN_BTN_1 = 16
PIN_BTN_2 = 20
PIN_BTN_3 = 21
if new_or_old == 1:
    b1 = Button(PIN_BTN_1, pull_up=True, bounce_time=MS_1)
    b2 = Button(PIN_BTN_2, pull_up=True, bounce_time=MS_1)
    b3 = Button(PIN_BTN_3, pull_up=True, bounce_time=MS_1)


def button1_pressed_cb():
    print('.')
    time.sleep(MS_10)
    global b1
    if b1.is_pressed:
        _u(STATE_DDS_PRESSED_BUTTON_1)

def button2_pressed_cb():
    time.sleep(MS_10)
    global b2
    if b2.is_pressed:
        _u(STATE_DDS_PRESSED_BUTTON_2)


def button3_pressed_cb():
    time.sleep(MS_10)
    global b3
    if b3.is_pressed:
        pass


def _th_gpio_box_buttons_new():
    global b1
    global b2
    global b3
    b1.when_pressed = button1_pressed_cb
    b2.when_pressed = button2_pressed_cb
    b3.when_pressed = button3_pressed_cb
    pause()


def dds_create_buttons_thread():
    if new_or_old == 1:
        print('creating NEW buttons thread')
        bth = threading.Thread(target=_th_gpio_box_buttons_new)
        bth.start()
    else:
        print('creating OLD buttons thread')
        bth = threading.Thread(target=_th_gpio_box_buttons)
        bth.start()