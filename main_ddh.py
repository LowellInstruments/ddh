import os
import signal
import sys
import time
from multiprocessing import Process
from PyQt5.QtWidgets import QApplication
from ddh.gui.main_gui import DDH, on_ctrl_c
from dds.notifications_v2 import notify_error_sw_crash
from mat.linux import (
    linux_app_write_pid_to_tmp,
    linux_is_process_running
)
from mat.utils import linux_is_rpi
from utils.ddh_shared import (
    PID_FILE_DDH,
    NAME_EXE_DDH_CONTROLLER,
    PID_FILE_DDH_CONTROLLER,
    NAME_EXE_DDH,
    ddh_get_gui_closed_flag_file,
    NAME_EXE_BRT,
    ddh_kill_by_pid_file
)
import setproctitle
from utils.logs import lg_gui as lg
from utils.wdog import gui_dog_get, gui_dog_is_enabled
import subprocess as sp


GUI_WD_EXPIRE_SECS = 30
GUI_WD_START_SECS = 30


def main_ddh():
    setproctitle.setproctitle(NAME_EXE_DDH)
    linux_app_write_pid_to_tmp(PID_FILE_DDH)
    assert sys.version_info >= (3, 9)
    signal.signal(signal.SIGINT, on_ctrl_c)
    app = QApplication(sys.argv)
    ex = DDH()
    ex.show()
    sys.exit(app.exec_())


def controller_main_ddh():

    # don't run DDH GUI when BRT range tool is running
    if linux_is_process_running(NAME_EXE_BRT):
        print('brt running, ddh should not')
        return

    # run the DDH GUI child process
    s = NAME_EXE_DDH_CONTROLLER
    p = PID_FILE_DDH_CONTROLLER
    setproctitle.setproctitle(s)
    linux_app_write_pid_to_tmp(p)

    # kill any old son
    ne = NAME_EXE_DDH
    c = (f'(ps -aux | grep -w {ne} | grep -v grep) '
         f'&& echo "kill loose DDH" && killall {ne} && sleep 3')
    sp.run(c, shell=True)

    # maybe left from before
    f = ddh_get_gui_closed_flag_file()
    if os.path.exists(f):
        os.unlink(f)

    # launch DDH son
    lg.a(f"=== {s} started ===")
    lg.a(f"=== {s} launches child ===")
    p = Process(target=main_ddh)
    p.start()

    while 1:
        time.sleep(5)
        kill = 0
        kill_by_wd = 0

        # closed by user
        if os.path.exists(f):
            os.unlink(f)
            lg.a(f"=== debug: user closed {s} ===")
            kill = 1

        # closed by watchdog
        v = gui_dog_get()
        if gui_dog_is_enabled():
            if v > GUI_WD_START_SECS and time.perf_counter() > v + GUI_WD_EXPIRE_SECS:
                # detects hangs of child GUI
                lg.a(f"=== {s} warning: {time.perf_counter()}, {v} child seems crashed ===")
                kill = 1
                kill_by_wd = 1
        else:
            lg.a(f"=== {s} debug: {v} child seems crashed but GUI watchdog is disabled ===")

        # check kill flags
        if kill:
            # in this order or message does not show
            lg.a(f'debug: closing GUI, crontab will relaunch it', show_ts=0)

            # would be more concerning
            if kill_by_wd:
                lg.a(f'warning: DDH watchdog had to intervene')
                notify_error_sw_crash()

            # kills GUI + GUI controller, NOT DDS, crontab will relaunch them
            ddh_kill_by_pid_file()


if __name__ == "__main__":

    if not linux_is_rpi():
        # debug: run without DDH controller
        main_ddh()
        sys.exit(0)

    if not linux_is_process_running(NAME_EXE_DDH_CONTROLLER):
        controller_main_ddh()
    else:
        _s = NAME_EXE_DDH_CONTROLLER
        print(f"not launching {_s}, already running at python level")
