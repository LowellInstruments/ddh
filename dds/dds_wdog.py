import socket
import subprocess as sp
import time


# total time is these 2 multiplied so 60, 60 is 1 hour
CHECKS_MAX_MISSED = 60
CHECKS_INTER_TIME = 60
WATCHDOG_ADDRESS = ("127.0.0.1", 44444)


_skg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_skg.settimeout(1)
_skg.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_skg.bind(WATCHDOG_ADDRESS)



def dds_wdog(max_wd_feeds_missed=CHECKS_MAX_MISSED):
    # give child some time to boot
    time.sleep(10)

    f = 0
    while 1:
        print(f)
        try:
            # don't do it too often
            time.sleep(CHECKS_INTER_TIME)
            rv = sp.run('ps -aux | grep -w main_dds | grep -v grep', shell=True)
            if rv.returncode:
                return 1
            _skg.recvfrom(1024)
            f = 0
        except socket.timeout:
            f += 1
            if f == max_wd_feeds_missed:
                return 2


def dds_feed_watchdog():
    _skf = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _skf.sendto(b'cookie', WATCHDOG_ADDRESS)


if __name__ == '__main__':
    dds_wdog()
