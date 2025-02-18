import threading
import time
from signal import pause
from gpiozero import Button
from mat.utils import linux_is_rpi
from utils.ddh_shared import (
    send_ddh_udp_gui as _u,
    STATE_DDS_PRESSED_BUTTON_2,
    STATE_DDS_PRESSED_BUTTON_1,
)
import RPi.GPIO as GPIO


def _th_gpio_box_buttons_old():
    if not linux_is_rpi():
        return

    def button1_pressed_cb():
        _u(STATE_DDS_PRESSED_BUTTON_1)

    def button2_pressed_cb():
        _u(STATE_DDS_PRESSED_BUTTON_2)

    def button3_pressed_cb():
        pass

    b1 = Button(16, pull_up=True, bounce_time=0.1)
    b2 = Button(20, pull_up=True, bounce_time=0.1)
    b3 = Button(21, pull_up=True, bounce_time=0.1)
    b1.when_pressed = button1_pressed_cb
    b2.when_pressed = button2_pressed_cb
    b3.when_pressed = button3_pressed_cb
    pause()


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


def _th_gpio_box_buttons_new():
    def b1_cb(_):
        _u(STATE_DDS_PRESSED_BUTTON_1)

    def b2_cb(_):
        _u(STATE_DDS_PRESSED_BUTTON_2)

    def b3_cb(_):
        pass

    GPIO.setwarnings(False)
    # use physical pin numbering
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    t_bounce_ms = 1000
    GPIO.add_event_detect(
        36,
        GPIO.FALLING,
        callback=b1_cb,
        bouncetime=t_bounce_ms
    )
    GPIO.add_event_detect(
        38,
        GPIO.FALLING,
        callback=b2_cb,
        bouncetime=t_bounce_ms
    )
    # GPIO.add_event_detect(
    #     40,
    #     GPIO.FALLING,
    #     callback=b3_cb,
    #     bouncetime=t_bounce_ms
    # )


def dds_create_buttons_thread():
    bth = threading.Thread(target=_th_gpio_box_buttons)
    bth.start()
