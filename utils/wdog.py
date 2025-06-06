import pathlib

import time
import os


DOG_GUI = '/tmp/dog_gui.txt'
DOG_GUI_EN = '/tmp/dog_gui_en.txt'



# ---------------------------
# a watchdog for the DDH GUI
# ---------------------------


def gui_dog_is_enabled():
    return os.path.exists(DOG_GUI_EN)


def gui_dog_disable():
    if os.path.exists(DOG_GUI_EN):
        os.unlink(DOG_GUI_EN)


def gui_dog_enable():
    pathlib.Path(DOG_GUI_EN).touch(exist_ok=True)


def gui_dog_clear():
    # fresh start
    if os.path.exists(DOG_GUI):
        os.unlink(DOG_GUI)


def gui_dog_touch():
    # written by main_ddh
    with open(DOG_GUI, 'w') as f:
        now = int(time.perf_counter())
        f.write(str(now))


def gui_dog_get():
    # read by main_ddh_controller
    try:
        with open(DOG_GUI) as f:
            return int(f.readline())
    except (Exception, ):
        # disabled
        return 0


if __name__ == '__main__':
    time.sleep(3)
    gui_dog_touch()
    v = gui_dog_get()
    print(v)
