import datetime
import json
import os
import shlex
import socket
import time
import shutil
import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QMovie
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QWidget,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
)
from gpiozero import Button

from ddh.db.db_his import DBHis
from ddh.graph import process_n_graph
from ddh.utils_net import net_get_my_current_wlan_ssid
from dds.ble_utils_dds import ble_get_cc26x2_recipe_file_rerun_flag
from mat.ble.ble_mat_utils import DDH_GUI_UDP_PORT
from mat.utils import linux_is_rpi
import subprocess as sp
from utils.ddh_shared import (
    dds_get_json_vessel_name,
    STATE_DDS_BLE_SCAN,
    STATE_DDS_SOFTWARE_UPDATED,
    STATE_DDS_BLE_DOWNLOAD,
    STATE_DDS_BLE_DOWNLOAD_OK,
    STATE_DDS_BLE_DOWNLOAD_WARNING,
    STATE_DDS_BLE_DOWNLOAD_ERROR,
    STATE_DDS_BLE_HARDWARE_ERROR,
    STATE_DDS_BLE_DISABLED,
    STATE_DDS_BLE_APP_GPS_ERROR_POSITION,
    STATE_DDS_BLE_APP_GPS_ERROR_SPEED,
    STATE_DDS_NOTIFY_GPS_BOOT,
    STATE_DDS_BLE_DOWNLOAD_PROGRESS,
    STATE_DDS_BLE_SERVICE_INACTIVE,
    STATE_DDS_BLE_ANTENNA,
    STATE_DDS_NOTIFY_NET_VIA,
    STATE_DDS_NOTIFY_CLOUD_BUSY,
    STATE_DDS_NOTIFY_CLOUD_LOGIN,
    STATE_DDS_NOTIFY_CLOUD_OK,
    STATE_DDS_NOTIFY_CLOUD_ERR,
    STATE_DDS_NOTIFY_CONVERSION_ERR,
    STATE_DDS_NOTIFY_CONVERSION_OK,
    STATE_DDS_NOTIFY_BOAT_NAME,
    STATE_DDS_NOTIFY_GPS,
    STATE_DDS_GPS_POWER_CYCLE,
    STATE_DDS_NOTIFY_GPS_CLOCK,
    STATE_DDS_NOTIFY_GPS_NUM_SAT,
    STATE_DDS_NOTIFY_HISTORY,
    STATE_DDS_BLE_LOW_BATTERY,
    STATE_DDS_BLE_RUN_STATUS,
    ddh_get_folder_path_res,
    ddh_get_settings_json_file,
    dds_get_json_mac_dns,
    get_ddh_commit,
    dds_get_serial_number_of_macs_from_json_file,
    STATE_DDS_BLE_SCAN_FIRST_EVER,
    STATE_DDS_BLE_ERROR_MOANA_PLUGIN, STATE_DDS_BLE_DOWNLOAD_ERROR_GDO, STATE_DDS_BLE_ERROR_RUN,
    STATE_DDS_REQUEST_GRAPH, ddh_get_absolute_application_path, g_graph_test_mode,
    STATE_DDS_BLE_DOWNLOAD_ERROR_TP_SENSOR, ddh_get_db_history_file, STATE_DDS_BLE_NO_ASSIGNED_LOGGERS,
)
from utils.logs import lg_gui as lg

STR_NOTE_PURGE_BLACKLIST = "Purge all loggers' lock-out time?"
STR_NOTE_GPS_BAD = "Skipping logger until valid GPS fix is obtained"
_g_ts_gui_boot = time.perf_counter()
_g_ts_gui_expire_icon = 0
PERIOD_SHOW_LOGGER_DL_OK_SECS = 300
PERIOD_SHOW_LOGGER_DL_ERROR_SECS = 300
PERIOD_SHOW_LOGGER_DL_WARNING_SECS = 60
PERIOD_SHOW_BLE_APP_GPS_ERROR_POSITION = 60


def gui_setup_view(my_win):
    """fills window with titles and default contents"""
    a = my_win
    a.setupUi(a)
    a.setWindowTitle("Lowell Instruments' Deck Data Hub")
    a.tabs.setTabIcon(0, QIcon("ddh/gui/res/icon_info.png"))
    a.tabs.setTabIcon(1, QIcon("ddh/gui/res/icon_setup.png"))
    a.tabs.setTabIcon(2, QIcon("ddh/gui/res/icon_exclamation.png"))
    a.tabs.setTabIcon(3, QIcon("ddh/gui/res/icon_history.ico"))
    a.tabs.setTabIcon(4, QIcon("ddh/gui/res/icon_tweak.png"))
    a.tabs.setTabIcon(5, QIcon("ddh/gui/res/icon_graph.ico"))
    a.setWindowIcon(QIcon("ddh/gui/res/icon_lowell.ico"))
    a.lbl_brightness.setPixmap(QPixmap("ddh/gui/res/bright.png"))
    a.lbl_boat.setPixmap(QPixmap("ddh/gui/res/img_boat.png"))
    a.lbl_net.setPixmap(QPixmap("ddh/gui/res/img_wireless_color.png"))
    a.lbl_cloud_img.setPixmap(QPixmap("ddh/gui/res/upcloud.png"))
    ship = dds_get_json_vessel_name()
    a.lbl_boat_txt.setText(ship)
    a.setCentralWidget(a.tabs)
    a.tabs.setCurrentIndex(0)

    # info: lat, lon, time
    fmt = "{}\n{}"
    a.lbl_gps.setText(fmt.format("-", "-"))

    # cloud: aws, cell
    a.lbl_cloud_txt.setText("-")
    a.bar_dl.setVisible(False)

    # load default values for edit tab
    a.btn_load_current.animateClick()

    # load git commit display
    dc = "version: {}".format(get_ddh_commit())
    a.lbl_commit.setText(dc)

    # checkboxes rerun flag
    rerun_flag = ble_get_cc26x2_recipe_file_rerun_flag()
    a.chk_rerun.setChecked(rerun_flag)

    return a


def gui_center_window(my_app):
    """on RPi, DDH app uses full screen"""
    a = my_app

    if linux_is_rpi():
        # rpi is 800 x 480
        a.showFullScreen()
        return

    qr = a.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    a.move(300, 200)
    a.setFixedWidth(1024)
    a.setFixedHeight(768)


def gui_manage_graph_test_files():
    a = ddh_get_absolute_application_path()
    d0 = a + '/dl_files/00-00-00-00-00-00'
    d1 = a + '/dl_files/11-22-33-44-55-66'
    d2 = a + '/dl_files/99-99-99-99-99-99'
    d3 = a + '/dl_files/55-55-55-55-55-55'
    t0 = a + '/tests/00-00-00-00-00-00'
    t1 = a + '/tests/11-22-33-44-55-66'
    t2 = a + '/tests/99-99-99-99-99-99'
    t3 = a + '/tests/55-55-55-55-55-55'
    shutil.rmtree(d0, ignore_errors=True)
    shutil.rmtree(d1, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)
    shutil.rmtree(d3, ignore_errors=True)
    if g_graph_test_mode():
        shutil.copytree(t0, d0)
        shutil.copytree(t1, d1)
        shutil.copytree(t2, d2)
        shutil.copytree(t3, d3)
        lg.a('copied logger graph test folders')


def gui_populate_history_tab(my_app):
    """
    fills history table on history tab
    """

    a = my_app
    a.tbl_his.clear()
    db = DBHis(ddh_get_db_history_file())
    r = db.get_all(15)

    for i, h in enumerate(r):
        e = h["e"]
        e = "success" if e == "ok" else e
        try:
            lat = "{:+6.4f}".format(float(h["lat"]))
            lon = "{:+6.4f}".format(float(h["lon"]))
            dt = datetime.datetime.fromtimestamp(int(h["sws_time"]))
            t = dt.strftime("%b %d %H:%M")
            s = "{} on {} at {}, {}".format(e, t, lat, lon)

            # set values to cells
            a.tbl_his.setItem(i, 0, QTableWidgetItem(str(h["SN"])))
            a.tbl_his.setItem(i, 1, QTableWidgetItem(s))

        except (Exception,):
            lg.a("error: history frame {}".format(h))

    # redistribute columns with
    h = a.tbl_his.horizontalHeader()
    h.resizeSection(0, 150)
    h.setSectionResizeMode(1, QHeaderView.Stretch)

    # column labels
    labels = ["logger", "result"]
    a.tbl_his.setHorizontalHeaderLabels(labels)


def gui_ddh_populate_note_tab_dropdown(my_app):
    """fills dropdown list in note tab"""

    a = my_app
    a.lst_macs_note_tab.clear()

    j = dds_get_serial_number_of_macs_from_json_file()
    for each in j:
        a.lst_macs_note_tab.addItem(each)


def gui_ddh_populate_graph_dropdown_sn(my_app):
    """fills logger serial number dropdown list in graph tab"""

    a = my_app
    a.cb_g_sn.clear()

    if g_graph_test_mode():
        a.cb_g_sn.addItem('SNtest000')
        a.cb_g_sn.addItem('SNtest111')
        a.cb_g_sn.addItem('SNtest999')
        a.cb_g_sn.addItem('SNtest555')
        return

    j = dds_get_serial_number_of_macs_from_json_file()
    for each in j:
        a.cb_g_sn.addItem('SN' + each)


def gui_setup_buttons(my_app):
    """link buttons and labels clicks and signals"""
    a = my_app

    # hidden buttons
    if not linux_is_rpi():
        a.btn_adv_sms.setEnabled(True)

    # clicks in BLE text, boat image, brightness...
    a.lbl_ble.mousePressEvent = a.click_lbl_ble
    a.lbl_brightness.mousePressEvent = a.click_lbl_brightness
    a.lbl_brightness_txt.mousePressEvent = a.click_lbl_brightness
    a.lbl_uptime.mousePressEvent = a.click_lbl_uptime
    a.lbl_boat.mousePressEvent = a.click_lbl_boat_pressed
    a.lbl_boat.mouseReleaseEvent = a.click_lbl_boat_released
    a.lbl_cloud_img.mousePressEvent = a.click_lbl_cloud_img
    a.lbl_commit.mousePressEvent = a.click_lbl_commit_pressed
    a.lbl_commit.mouseReleaseEvent = a.click_lbl_commit_released
    a.lbl_date.mousePressEvent = a.click_lbl_datetime_pressed
    a.lbl_date.mouseReleaseEvent = a.click_lbl_datetime_released
    a.lbl_net.mousePressEvent = a.click_lbl_net_pressed
    a.lbl_net.mouseReleaseEvent = a.click_lbl_net_released

    # buttons' connections
    a.btn_known_clear.clicked.connect(a.click_btn_clear_known_mac_list)
    a.btn_see_all.clicked.connect(a.click_btn_clear_see_all_macs)
    a.btn_see_cur.clicked.connect(a.click_btn_see_macs_in_current_json_file)
    a.btn_arrow.clicked.connect(a.click_btn_arrow_move_entries)
    a.btn_setup_apply.clicked.connect(a.click_btn_apply_write_json_file)
    a.btn_dl_purge.clicked.connect(a.click_btn_purge_dl_folder)
    a.btn_his_purge.clicked.connect(a.click_btn_purge_his_db)
    a.btn_adv_purge_lo.clicked.connect(a.click_btn_adv_purge_lo)
    a.btn_load_current.clicked.connect(a.click_btn_load_current_json_file)
    a.btn_note_yes.clicked.connect(a.click_btn_note_yes)
    a.btn_note_no.clicked.connect(a.click_btn_note_no)
    a.btn_note_yes_specific.clicked.connect(a.click_btn_note_yes_specific)
    a.chk_rerun.toggled.connect(a.click_chk_rerun)
    a.cb_s3_uplink_type.activated.connect(a.click_cb_s3_uplink_type)
    a.btn_adv_sms.clicked.connect(a.click_btn_adv_sms)

    # graph stuff
    a.btn_g_reset.clicked.connect(a.click_graph_btn_reset)
    a.btn_g_next_haul.clicked.connect(a.click_graph_btn_next_haul)
    a.cb_g_sn.activated.connect(a.click_graph_listview_logger_sn)
    a.cb_g_cycle_haul.activated.connect(a.click_graph_lbl_haul_types)
    a.cb_g_paint_zones.activated.connect(a.click_graph_btn_paint_zones)


def gui_hide_edit_tab(ui):
    # find tab ID, index and keep ref
    p = ui.tabs.findChild(QWidget, "tab_setup")
    i = ui.tabs.indexOf(p)
    ui.tab_edit_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)


def gui_hide_advanced_tab(ui):
    # find tab ID, index and keep ref
    p = ui.tabs.findChild(QWidget, "tab_advanced")
    i = ui.tabs.indexOf(p)
    ui.tab_recipe_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)


def gui_hide_graph_tab(ui):

    if not linux_is_rpi():
        return
    if os.path.exists('/home/pi/li/.ddh_graph_enabler.json'):
        return
    # find tab ID, index and keep ref
    p = ui.tabs.findChild(QWidget, "tab_graph")
    i = ui.tabs.indexOf(p)
    ui.tab_graph_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)


def gui_show_graph_tab(ui):
    icon = QIcon("ddh/gui/res/icon_graph.ico")
    ui.tabs.addTab(ui.tab_graph_wgt_ref, icon, " Graphs")
    p = ui.tabs.findChild(QWidget, "tab_graph")
    i = ui.tabs.indexOf(p)
    ui.tabs.setCurrentIndex(i)


def gui_show_edit_tab(ui):
    icon = QIcon("ddh/gui/res/icon_setup.png")
    ui.tabs.addTab(ui.tab_edit_wgt_ref, icon, " Setup")
    p = ui.tabs.findChild(QWidget, "tab_setup")
    i = ui.tabs.indexOf(p)
    ui.tabs.setCurrentIndex(i)


def gui_show_advanced_tab(ui):
    icon = QIcon("ddh/gui/res/icon_tweak.png")
    ui.tabs.addTab(ui.tab_recipe_wgt_ref, icon, " Advanced")
    p = ui.tabs.findChild(QWidget, "tab_advanced")
    i = ui.tabs.indexOf(p)
    ui.tabs.setCurrentIndex(i)


def gui_hide_note_tab(ui):
    p = ui.tabs.findChild(QWidget, "tab_note")
    i = ui.tabs.indexOf(p)
    ui.tab_note_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)


def gui_hide_maps_tab(ui):
    p = ui.tabs.findChild(QWidget, "tab_map")
    i = ui.tabs.indexOf(p)
    ui.tab_map_wgt_ref = ui.tabs.widget(i)
    ui.tabs.removeTab(i)


def gui_show_note_tab_delete_black_macs(ui):
    icon = QIcon("ddh/gui/res/icon_exclamation.png")
    ui.tabs.addTab(ui.tab_note_wgt_ref, icon, " Note")
    ui.lbl_note.setText(STR_NOTE_PURGE_BLACKLIST)
    p = ui.tabs.findChild(QWidget, "tab_note")
    i = ui.tabs.indexOf(p)
    ui.tabs.setCurrentIndex(i)


def dict_from_list_view(l_v):
    """grab listview entries 'name mac' and build a dict"""
    d = dict()
    n = l_v.count()
    for _ in range(n):
        it = l_v.item(_)
        pair = it.text().split()
        d[pair[0]] = pair[1]
    return d


def gui_setup_buttons_rpi(my_app):
    """link raspberry buttons with callback functions"""

    a = my_app
    if not linux_is_rpi():
        # no box buttons so bye
        return

    def button1_pressed_cb():
        lg.a("debug: low-level utils_gui detect pressed button 1")
        a.keyPressEvent(ButtonPressEvent(Qt.Key_1))

    def button2_pressed_cb():
        lg.a("debug: low-level utils_gui detect pressed button 2")
        a.keyPressEvent(ButtonPressEvent(Qt.Key_2))

    def button3_pressed_cb():
        lg.a("debug: low-level utils_gui detect pressed button 3")
        a.keyPressEvent(ButtonPressEvent(Qt.Key_3))

    a.button1 = Button(16, pull_up=True, bounce_time=0.05)
    a.button2 = Button(20, pull_up=True, bounce_time=0.05)
    a.button3 = Button(21, pull_up=True, bounce_time=0.05)
    a.button1.when_pressed = button1_pressed_cb
    a.button2.when_pressed = button2_pressed_cb
    a.button3.when_pressed = button3_pressed_cb


def gui_add_to_history_database(mac, e, lat, lon, t):
    sn = dds_get_json_mac_dns(mac)
    db = DBHis(ddh_get_db_history_file())
    db.add(mac, sn, e, lat, lon, t)


def gui_confirm_by_user(s):
    """ask user to press OK or CANCEL"""

    m = QMessageBox()
    m.setIcon(QMessageBox.Information)
    m.setWindowTitle("warning")
    m.setText(s)
    choices = QMessageBox.Ok | QMessageBox.Cancel
    m.setStandardButtons(choices)
    return m.exec_() == QMessageBox.Ok


def _parse_addr(my_app, addr):
    ip, _ = addr
    if ip == "127.0.0.1":
        my_app.lbl_ip.setText("local DDH")
    else:
        my_app.lbl_ip.setText("remote DDH")


def _gui_update_icon(my_app, ci, ct):
    if ci:
        fol_res = str(ddh_get_folder_path_res())
        ci = "{}/{}".format(fol_res, ci)
        my_app.lbl_ble_img.setPixmap(QPixmap(ci))
    if ct:
        my_app.lbl_ble.setText(ct)


def _parse_udp(my_app, s, ip="127.0.0.1"):

    a = my_app
    global _g_ts_gui_expire_icon
    i = int(time.perf_counter()) % 4

    f, v = s.split("/")
    # lg.a('UDP | parsing \'{}/{}\''.format(f, v))

    # variables for big icon and text
    ci = ""
    ct = ""

    # -------------------
    # BLE service states
    # -------------------
    if f in (STATE_DDS_BLE_SCAN, STATE_DDS_BLE_SCAN_FIRST_EVER):
        ct = "searching for loggers"
        ci = "blue{}.png".format(i)

    elif f == STATE_DDS_SOFTWARE_UPDATED:
        _g_ts_gui_expire_icon = time.perf_counter() + 30
        ct = "DDH updated!"
        ci = "update.png"

    elif f == STATE_DDS_BLE_DOWNLOAD:
        _g_ts_gui_expire_icon = time.perf_counter() + 30
        ct = "downloading {}".format(v)
        ci = "dl2.png"
        a.bar_dl.setValue(0)

    elif f == STATE_DDS_BLE_DOWNLOAD_OK:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "done " + v
        ci = "ok.png"

    elif f == STATE_DDS_BLE_DOWNLOAD_WARNING:
        _g_ts_gui_expire_icon = time.perf_counter() + 30
        ct = "{} retrying".format(v)
        ci = "sand_clock.png"

    elif f == STATE_DDS_BLE_DOWNLOAD_ERROR:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "{} failure".format(v)
        ci = "error.png"

    elif f == STATE_DDS_BLE_DOWNLOAD_ERROR_GDO:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "error oxygen sensor"
        ci = "error.png"

    elif f == STATE_DDS_BLE_DOWNLOAD_ERROR_TP_SENSOR:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "error oxygen TP"
        ci = "error.png"

    elif f == STATE_DDS_BLE_ERROR_RUN:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "error running logger"
        ci = "error.png"

    elif f == STATE_DDS_BLE_HARDWARE_ERROR:
        _g_ts_gui_expire_icon = time.perf_counter() + 10
        ct = "radio restarting"
        ci = "blue_err.png"

    elif f == STATE_DDS_BLE_DISABLED:
        ct = "radio is disabled"
        ci = "blue_dis.png"

    elif f == STATE_DDS_BLE_APP_GPS_ERROR_POSITION:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "need GPS"
        ci = "gps_err.png"
        a.lbl_gps.setText("-")
        a.lbl_gps_sat.setText("-")

    elif f == STATE_DDS_BLE_APP_GPS_ERROR_SPEED:
        _g_ts_gui_expire_icon = time.perf_counter() + 60
        ct = "app resting"
        ci = "blue{}.png".format(i)

    elif f == STATE_DDS_NOTIFY_GPS_BOOT:
        v = int(float(v))
        ct = "waiting GPS {} seconds".format(v)
        ci = "gps_boot{}.png".format(i)

    elif f == STATE_DDS_BLE_DOWNLOAD_PROGRESS:
        v = int(float(v))
        if v == -1:
            a.bar_dl.setVisible(False)
        else:
            if not a.lbl_ble_img_filled:
                ct = "downloading..."
                ci = "dl2.png"
            a.bar_dl.setVisible(True)
            a.bar_dl.setValue(v)

    elif f == STATE_DDS_BLE_SERVICE_INACTIVE:
        ct = "no BLE service"
        ci = "blue_err.png"
        a.lbl_antenna.setText("")

    elif f == STATE_DDS_BLE_ANTENNA:
        a.lbl_antenna.setText(v)

    elif f == STATE_DDS_BLE_ERROR_MOANA_PLUGIN:
        ct = "moana plugin needed"
        ci = "moana_plugin.png"

    # -------------------
    # NET service states
    # -------------------
    elif f == STATE_DDS_NOTIFY_NET_VIA:
        a.lbl_net_txt.setText(v)
        if v in ("wifi", "wi-fi"):
            ssid = net_get_my_current_wlan_ssid()
            a.lbl_net_txt.setText(ssid)

    # -------------------
    # CLOUD states
    # -------------------
    elif f == STATE_DDS_NOTIFY_CLOUD_BUSY:
        a.lbl_cloud_txt.setText("busy")
    elif f == STATE_DDS_NOTIFY_CLOUD_LOGIN:
        a.lbl_cloud_txt.setText("err_login")
    elif f == STATE_DDS_NOTIFY_CLOUD_OK:
        a.lbl_cloud_txt.setText("OK")
    elif f == STATE_DDS_NOTIFY_CLOUD_ERR:
        a.lbl_cloud_txt.setText("error")

    # -------------------
    # CONVERSION states
    # -------------------
    elif f == STATE_DDS_NOTIFY_CONVERSION_ERR:
        a.lbl_cnv.setText("cnv_error")
    elif f == STATE_DDS_NOTIFY_CONVERSION_OK:
        a.lbl_cnv.setText("cnv_ok")

    # -----------
    # GRAPH fields
    # -----------
    elif f == STATE_DDS_REQUEST_GRAPH:
        if ip != "127.0.0.1":
            lg.a("not graphing remote downloads")
            return

        # GRAPH PROCESS
        process_n_graph(a, r='BLE')

    # ----------------------------------
    # other fields that are not states
    # ----------------------------------
    elif f == STATE_DDS_NOTIFY_BOAT_NAME:
        a.lbl_boat_txt.setText(v)

    elif f == STATE_DDS_NOTIFY_GPS:
        a.lbl_gps.setText(v)

    elif f == STATE_DDS_GPS_POWER_CYCLE:
        ct = "wait, power-cycling GPS"
        ci = "gps_power_cycle.png"

    elif f == STATE_DDS_NOTIFY_GPS_CLOCK:
        ct = "syncing GPS time"
        ci = "gps_clock.png"

    elif f == STATE_DDS_NOTIFY_GPS_NUM_SAT:
        _ = "{} GPS satellites".format(v)
        a.lbl_gps_sat.setText(_)

    elif f == STATE_DDS_NOTIFY_HISTORY:
        if v.startswith("add"):
            # history/add&{mac}&{ok|error}&{lat}&{lon}&{t_epoch}
            v = v.split("&")
            gui_add_to_history_database(v[1], v[2], v[3], v[4], v[5])
        gui_populate_history_tab(a)

    elif f == STATE_DDS_BLE_LOW_BATTERY:
        ct = "low battery!"
        ci = "low_battery.png"

    elif f == STATE_DDS_BLE_RUN_STATUS:
        if v == "off":
            ct = "logger stopped & auto-wake OFF"
            ci = "attention.png"

    elif f == STATE_DDS_BLE_NO_ASSIGNED_LOGGERS:
        ct = "no loggers assigned"
        ci = "attention.png"

    else:
        lg.a("UDP | unknown state: {}".format(f))

    # -----------------------
    # update big icon in GUI
    # -----------------------
    now = time.perf_counter()
    if f == STATE_DDS_BLE_SCAN and now < _g_ts_gui_expire_icon:
        # current icon should be 'scan', but it has LOW priority
        # lets show others till they expire
        return

    # GUI main icon and title
    _gui_update_icon(a, ci, ct)

    # progress bar
    if f not in (STATE_DDS_BLE_DOWNLOAD, STATE_DDS_BLE_DOWNLOAD_PROGRESS):
        a.bar_dl.setVisible(False)


# socket gui
_skg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
_skg.settimeout(0.1)
_skg.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_skg.bind(("127.0.0.1", DDH_GUI_UDP_PORT))


def gui_timer_fxn(my_app):
    a = my_app

    i = int(time.perf_counter()) % 4
    a.lbl_date.setText(datetime.datetime.now().strftime("%b %d %H:%M:%S"))

    if a.boat_pressed > 0:
        a.boat_pressed += 1
    if a.commit_pressed > 0:
        a.commit_pressed += 1
    if a.datetime_pressed > 0:
        a.datetime_pressed += 1
    if a.lbl_net_pressed > 0:
        a.lbl_net_pressed += 1

    _u = bytes()
    try:
        while 1:
            _u, addr = _skg.recvfrom(1024)
            _parse_addr(my_app, addr)
            _parse_udp(my_app, _u.decode())
    except socket.timeout:
        pass

    # how long this GUI has been up, it restarts every GUI launch
    _up = datetime.timedelta(seconds=time.perf_counter() - _g_ts_gui_boot)
    a.lbl_uptime.setText("uptime " + str(_up).split(".")[0])

    # force normally show first tab
    _ti = a.tabs.currentIndex()
    _pf = int(time.perf_counter())
    if _ti != 0 and _pf % 1800 == 0:
        a.tabs.setCurrentIndex(0)

    # animate BLE icon
    if a.lbl_ble.text() == "searching for loggers":
        ci = "blue{}.png".format(i)
        fol_res = str(ddh_get_folder_path_res())
        ci = "{}/{}".format(fol_res, ci)
        a.lbl_ble_img.setPixmap(QPixmap(ci))


def _yaml_get_pairs(y) -> dict:
    """gets <mac: logger_name> pairs"""
    try:
        with open(y) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            return data
    except TypeError as te:
        lg.a("error yaml_get_macs")
        raise te


def _check_macs(pairs):
    rv = True
    for i in pairs.keys():
        rv = rv and len(i) == 17
        if not rv:
            e = "bad mac {}".format(i)
            raise ValueError(e)


def gui_yaml_load_pairs(f):
    """gets and checks <mac: logger_name> pairs"""
    try:
        f = f[0]
        if not f.endswith(".yml"):
            return
        m = _yaml_get_pairs(f)
        _check_macs(m)
        return {k.lower(): v for k, v in m.items()}

    except (TypeError, ValueError):
        return None


def gui_gen_ddh_json_content(known, v, f_t, lh):
    """generates ddh.json content"""
    data = dict()
    s = "auto-generated by DDH setup tab, do not edit"
    data["comment-1"] = s
    data["db_logger_macs"] = known
    data["ship_name"] = v
    data["forget_time"] = f_t
    data["metrics"] = [["DOS", "DOT"], ["T", "P"]]

    # [ num of partitions, minutes / partition, minutes total, ...
    # ... format label, how many to jump or skip]
    data["span_dict"] = {
        "h": [5, 15, 60, "%H:%M", 1],
        "d": [48, 30, 1440, "%H", 2],
        "w": [14, 720, 10080, "%m/%d", 2],
        "m": [31, 1440, 43800, "%d", 1],
        "y": [12, 43800, 525600, "%b %y", 1],
    }
    # 'F' for Fahrenheit, 'C' for Celsius
    data["units_temp"] = "F"
    # 'm' for meters of 'f' for fathoms
    data["units_depth"] = "m"
    data["last_haul"] = lh
    data["moving_speed"] = {"min": 0.5, "max": 6}
    return json.dumps(data, indent=4)


def gui_json_get_forget_time_secs():
    j = str(ddh_get_settings_json_file())
    with open(j) as f:
        rv = int(json.load(f)["forget_time"])
        assert rv >= 600
        return rv


def gui_json_set_graph_units():
    j = str(ddh_get_settings_json_file())
    with open(j) as f:
        cfg = json.load(f)
    assert cfg["units_temp"] in "FC"
    assert cfg["units_depth"] in "fm"
    return cfg["units_temp"], cfg["units_depth"]


def gui_json_get_mac_n_name_pairs():
    """gets list of pairs {mac, names} in ddh.json file"""

    j = str(ddh_get_settings_json_file())
    try:
        with open(j) as f:
            cfg = json.load(f)
            # macs not lowered()
            return cfg["db_logger_macs"]
    except TypeError:
        return "error json_get_mac_n_name_pairs()"


def gui_ddh_set_brightness(a):
    if not linux_is_rpi():
        lg.a("not raspberry, no brightness control")
        return

    nc = a.num_clicks_brightness
    assert 1 <= nc <= 10

    # 25.5 is 255 / 10 -> 10%
    v = int(nc * 25.5)

    # special value for lowest click, 10 minimum or pitch black
    one_percent = 10
    if nc == 1:
        v = one_percent

    lg.a("setting brightness to {}".format(v))
    b1 = '/sys/class/backlight/rpi_backlight/brightness"'
    b2 = '/sys/class/backlight/10-0045/brightness"'
    # requires root or $ chmod 777 /sys/class.../backlight
    s1 = 'bash -c "echo {} > {}'.format(str(v), b1)
    s2 = 'bash -c "echo {} > {}'.format(str(v), b2)
    o = sp.DEVNULL
    sp.run(shlex.split(s1), stdout=o, stderr=o)
    sp.run(shlex.split(s2), stdout=o, stderr=o)
    if nc == 1:
        nc = 0.5
    a.lbl_brightness_txt.setText(str(nc * 10) + "%")


def gui_refresh_dl_folder_list(d):
    """gets updated logger folders list"""

    if os.path.isdir(d):
        f_l = [f.path for f in os.scandir(d) if f.is_dir()]
        # remove 'ddh_vessel' folders
        f_l = [f for f in f_l if "ddh" not in f]
        return f_l
    else:
        os.makedirs(d, exist_ok=True)


def map_prototype(app):
    a = app
    p = str(ddh_get_folder_path_res()) + '/300.gif'
    a.gif = QMovie(p)
    a.lbl_map.setMovie(a.gif)
    a.gif.start()


class ButtonPressEvent:
    def __init__(self, code):
        self.code = code

    def key(self):
        return self.code
