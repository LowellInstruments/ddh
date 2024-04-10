import time

import pyqtgraph as pg
from pathlib import Path
import psutil
import glob
import os
import pathlib
import shutil
import sys
from PyQt5.QtCore import QTimer, Qt, QCoreApplication
from PyQt5.QtWidgets import QMainWindow
import ddh.gui.designer_main as d_m
from ddh.db.db_his import DbHis
from ddh.graph import process_n_graph
from ddh.utils_gui import (
    gui_hide_edit_tab,
    gui_hide_note_tab,
    gui_populate_history_tab,
    gui_ddh_set_brightness,
    gui_setup_view,
    gui_setup_buttons,
    gui_center_window,
    gui_dict_from_list_view,
    gui_show_edit_tab,
    gui_json_get_forget_time_secs,
    STR_NOTE_PURGE_BLACKLIST,
    gui_confirm_by_user,
    gui_show_note_tab_delete_black_macs,
    gui_timer_fxn,
    gui_ddh_populate_note_tab_dropdown,
    gui_hide_advanced_tab,
    gui_show_advanced_tab,
    gui_hide_graph_tab,
    gui_show_graph_tab, gui_ddh_populate_graph_dropdown_sn, gui_manage_graph_test_files,
    gui_hide_map_tab
)

from dds.emolt import this_box_has_grouped_s3_uplink
from dds.notifications import notify_via_sms
from dds.timecache import its_time_to
from mat.linux import linux_is_process_running
from mat.utils import linux_is_rpi
from rpc.rpc_rx import th_srv_notify
from rpc.rpc_tx import th_cli_cmd
from utils.ddh_config import (dds_get_cfg_vessel_name, dds_get_cfg_logger_mac_from_sn,
                              ddh_get_cfg_gear_type, cfg_load_from_file, dds_get_cfg_flag_ble_en,
                              cfg_save_to_file, dds_get_cfg_monitored_pairs, ddh_get_cfg_maps_en)
from utils.ddh_shared import (
    get_ddh_folder_path_dl_files,
    ddh_get_gui_closed_flag_file,
    dds_kill_by_pid_file,
    get_ddh_folder_path_macs_black,
    NAME_EXE_DDS,
    send_ddh_udp_gui,
    ddh_get_disabled_ble_flag_file,
    ddh_get_app_override_flag_file,
    dds_get_aws_has_something_to_do_via_gui_flag_file,
    STATE_DDS_BLE_SERVICE_INACTIVE,
    dds_get_ddh_got_an_update_flag_file,
    STATE_DDS_SOFTWARE_UPDATED,
    ddh_get_db_history_file, ddh_kill_by_pid_file, get_ddh_toml_all_macs_content, set_ddh_rerun_flag_li,
    clr_ddh_rerun_flag_li, dds_get_cnv_requested_via_gui_flag_file
)

from utils.logs import lg_gui as lg  # noqa: E402
import subprocess as sp  # noqa: E402

from utils.tmp_paths import LI_PATH_GROUPED_S3_FILE_FLAG

_g_flag_ble_en = dds_get_cfg_flag_ble_en()


class DDH(QMainWindow, d_m.Ui_MainWindow):
    def __init__(self):
        super(DDH, self).__init__()
        gui_setup_view(self)
        gui_setup_buttons(self)
        gui_center_window(self)

        # ------------------------
        # you want GUI logs or not
        # ------------------------
        lg.are_enabled(True)

        # gui: appearance
        self.cbox_gear_type.addItems(["fixed", "mobile"])
        self.cb_s3_uplink_type.addItems(["raw", "group"])
        self.bright_idx = 2
        self.tab_edit_hide = True
        self.tab_advanced_hide = True
        self.tab_graph_hide = True
        self.tab_edit_wgt_ref = None
        self.tab_map_wgt_ref = None
        self.tab_note_wgt_ref = None
        self.tab_recipe_wgt_ref = None
        self.tab_graph_wgt_ref = None
        self.key_pressed = None
        self.num_clicks_brightness = 10
        self.lbl_ble_img_filled = False
        self.boat_pressed = 0
        self.commit_pressed = 0
        self.datetime_pressed = 0
        self.lbl_net_pressed = 0
        self.gif_map = None

        gui_hide_edit_tab(self)
        gui_hide_advanced_tab(self)
        gui_hide_note_tab(self)
        gui_populate_history_tab(self)
        gui_ddh_set_brightness(self)
        gui_ddh_populate_note_tab_dropdown(self)
        gui_ddh_populate_graph_dropdown_sn(self)

        # maps tab
        if not ddh_get_cfg_maps_en():
            gui_hide_map_tab(self)

        # s3 uplink type field
        if this_box_has_grouped_s3_uplink():
            self.cb_s3_uplink_type.setCurrentIndex(1)

        # -----------
        # graph tab
        # -----------
        self.g = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.g_haul_idx = None

        # graph layout
        self.lay_g_h2.addWidget(self.g)
        self.g.setBackground('w')
        self.btn_g_next_haul.setEnabled(False)
        self.btn_g_next_haul.setVisible(False)
        self.lbl_graph_busy.setVisible(False)
        self.cb_g_switch_tp.setVisible(False)

        # graph test mode
        gui_manage_graph_test_files()

        # timer to update GUI fields
        self.tg = QTimer()
        self.tg.timeout.connect(self._tg_fxn)
        self.tg.start(1000)

        # timer to measure RPi temperature
        self.tt = QTimer()
        self.tt.timeout.connect(self._tt_fxn)
        if linux_is_rpi():
            self.tt.start(1000)

        # timer BLE service alive
        self.tb = QTimer()
        self.tb.timeout.connect(self._tb_fxn)
        self.tb.start(30000)

        # check if we had an update, also done at DDS
        file_flag = dds_get_ddh_got_an_update_flag_file()
        if os.path.exists(file_flag):
            send_ddh_udp_gui(STATE_DDS_SOFTWARE_UPDATED)

        # new, run RPC threads for DDH GUI
        # th_srv_notify()
        # th_cli_cmd()

        # indicate
        lg.a("OK: DDH GUI finished booting")

    def _tg_fxn(self):
        gui_timer_fxn(self)

    def _tt_fxn(self):

        # measure RAM usage of DDH box
        m = psutil.virtual_memory()
        if int(m.percent) > 75:
            ma = m.available / 1e9
            s = "debug: {:.2f}% GB of RAM used, {:.2f} GB available"
            lg.a(s.format(m.percent, ma))

        # measure temperature of DDH box, tell when too high
        self.tt.stop()
        c = "/usr/bin/vcgencmd measure_temp"
        rv = sp.run(c, shell=True, stderr=sp.PIPE, stdout=sp.PIPE)

        try:
            ans = rv.stdout
            if ans:
                # ans: b"temp=30.1'C"
                ans = ans.replace(b"\n", b"")
                ans = ans.replace(b"'C", b"")
                ans = ans.replace(b"temp=", b"")
                ans = float(ans.decode())
                if ans > 55:
                    lg.a(f"debug: box temperature {ans} degrees Celsius")

        except (Exception,) as ex:
            lg.a("error: getting vcgencmd -> {}".format(ex))

        # 600 seconds = 10 minutes
        self.tt.start(600000)

    @staticmethod
    def _tb_fxn():
        if not linux_is_process_running(NAME_EXE_DDS):
            if its_time_to('tell_BLE_dead', 1800):
                lg.a("warning: BLE service seems dead")
            send_ddh_udp_gui(STATE_DDS_BLE_SERVICE_INACTIVE)

    def click_btn_clear_known_mac_list(self):
        self.lst_mac_org.clear()
        self.lst_mac_dst.clear()

    def click_btn_see_all_macs(self):
        """loads (mac, name) pairs from all macs config section"""

        self.lst_mac_org.clear()
        pp = get_ddh_toml_all_macs_content()
        for m, n in pp.items():
            s = "{}  {}".format(m, n)
            self.lst_mac_org.addItem(s)

    def click_btn_see_monitored_macs(self):
        """loads (mac, name) pairs from config file"""

        self.lst_mac_org.clear()
        pp = dds_get_cfg_monitored_pairs()
        for m, n in pp.items():
            s = "{}  {}".format(m, n)
            self.lst_mac_org.addItem(s)

    def click_btn_arrow_move_entries(self):
        """move items in upper box to lower box"""

        ls = self.lst_mac_org.selectedItems()
        o = dict()
        for i in ls:
            pair = i.text().split()
            o[pair[0]] = pair[1]

        # dict from all items in lower box
        b = self.lst_mac_dst
        d_b = gui_dict_from_list_view(b)
        d_b.update(o)

        # update lower box
        self.lst_mac_dst.clear()
        for m, n in d_b.items():
            s = "{}  {}".format(m, n)
            self.lst_mac_dst.addItem(s)

    def click_btn_apply_write_json_file(self):
        """creates a config file"""

        l_v = self.lst_mac_dst
        pairs = gui_dict_from_list_view(l_v)
        # pairs: {'11:22:33:44:55:66': '1234567'}

        # input: forget_time
        try:
            t = int(self.lne_forget.text())
        except ValueError:
            t = 0
        self.lne_forget.setText(str(t))

        # input: vessel name
        ves = self.lne_vessel.text()

        # last haul graph type
        lhf = self.cbox_gear_type.currentIndex()

        if t < 600:
            self.lbl_setup_result.setText("bad forget_time")
            return
        if not ves:
            self.lbl_setup_result.setText("bad vessel name")
            return

        save_cfg = cfg_load_from_file()
        save_cfg['behavior']["forget_time"] = t
        save_cfg['behavior']['ship_name'] = ves
        save_cfg['behavior']['gear_type'] = lhf
        save_cfg['monitored_macs'] = pairs
        cfg_save_to_file(save_cfg)

        # we seem good to go
        s = "restarting DDH..."
        self.lbl_setup_result.setText(s)
        lg.a("closing by save config button")

        # bye, bye DDS
        dds_kill_by_pid_file(only_child=False)
        ddh_kill_by_pid_file(only_child=False)

        # bye, bye DDH
        sys.stderr.close()
        os._exit(0)

    def click_lbl_ble(self, _):
        # sequence: press key, depress, click
        k = self.key_pressed
        self.key_pressed = None
        # lg.a('key pressed is {}'.format(k))

        if k == "m":
            self.showMinimized()

        elif k == "b":
            global _g_flag_ble_en
            _g_flag_ble_en ^= 1
            s = "enabled" if _g_flag_ble_en else "disabled"
            lg.a("BLE {} by keypress".format(s))
            flag = ddh_get_disabled_ble_flag_file()
            if _g_flag_ble_en:
                pathlib.Path(flag).touch()
            else:
                if os.path.isfile(flag):
                    os.unlink(flag)

        elif k == "e":
            teh = self.tab_edit_hide = not self.tab_edit_hide
            gui_hide_edit_tab(self) if teh else gui_show_edit_tab(self)

        elif k == "q":
            p = ddh_get_gui_closed_flag_file()
            pathlib.Path.touch(p, exist_ok=True)
            dds_kill_by_pid_file()
            lg.a("closing by keypress 'q'")
            sys.stderr.close()
            os._exit(0)

    @staticmethod
    def click_lbl_uptime(_):
        p = ddh_get_gui_closed_flag_file()
        pathlib.Path.touch(p, exist_ok=True)
        dds_kill_by_pid_file()
        lg.a("closing by lbl_uptime clicked")
        sys.stderr.close()
        os._exit(0)

    def click_lbl_brightness(self, _):
        # no shift key, adjust DDH brightness
        v = (self.num_clicks_brightness + 1) % 11
        self.num_clicks_brightness = 1 if v == 0 else v
        gui_ddh_set_brightness(self)

    @staticmethod
    def click_btn_purge_dl_folder():
        """deletes contents in 'download files' folder"""

        d = str(get_ddh_folder_path_dl_files())
        lg.a("pressed btn_purge_dl_folder")
        s = "sure to delete dl_files folder?"
        if not gui_confirm_by_user(s):
            return

        try:
            if "dl_files" not in str(d):
                return
            shutil.rmtree(str(d), ignore_errors=True)
        except OSError as e:
            lg.a("error {} : {}".format(d, e))

    def click_btn_adv_purge_lo(self):
        gui_show_note_tab_delete_black_macs(self)

    def click_btn_sms(self):
        s: str
        if its_time_to('sms', 3600):
            s = 'sending'
            notify_via_sms('sms')
        else:
            s = 'already sent'
        self.btn_sms.setText(s)
        QCoreApplication.processEvents()
        time.sleep(2)
        self.btn_sms.setText("tech support")

    def click_btn_purge_his_db(self):
        """deletes contents in history database"""

        s = "sure to purge history?"
        if gui_confirm_by_user(s):
            db = DbHis(ddh_get_db_history_file())
            db.delete_all()
        gui_populate_history_tab(self)

    def click_btn_load_current_json_file(self):
        """updates EDIT tab from current config file"""

        ves = dds_get_cfg_vessel_name()
        f_t = gui_json_get_forget_time_secs()
        lhf = ddh_get_cfg_gear_type()
        self.lne_vessel.setText(ves)
        self.lne_forget.setText(str(f_t))
        # set index of the JSON dropdown list
        self.cbox_gear_type.setCurrentIndex(lhf)

    def click_btn_note_yes_specific(self):
        s = self.lbl_note.text()

        # only affects purge_macs note, not BLE GPS one
        if s == STR_NOTE_PURGE_BLACKLIST:
            try:
                p = get_ddh_folder_path_macs_black()
                n = self.lst_macs_note_tab.count()

                for i in range(n):
                    if not self.lst_macs_note_tab.item(i).isSelected():
                        continue

                    sn = self.lst_macs_note_tab.item(i).text()
                    mac = dds_get_cfg_logger_mac_from_sn(sn)
                    if mac:
                        mac = mac.replace(":", "-")
                        mask = "{}/{}@*".format(p, mac)
                        ff = glob.glob(mask)
                        for f in ff:
                            os.unlink(f)
                            s = "debug: clear lock-out selective for {}"
                            lg.a(s.format(f))
                    else:
                        lg.a("warning: could not clear lock-out selective")

            except (OSError, Exception) as ex:
                lg.a("error: {}".format(ex))
                return

        lg.a("pressed note button 'OK'")
        flag = ddh_get_app_override_flag_file()
        pathlib.Path(flag).touch()
        lg.a("BLE op conditions override set as 1")
        gui_hide_note_tab(self)
        self.tabs.setCurrentIndex(0)

    def click_btn_note_yes(self):
        s = self.lbl_note.text()

        # only affects purge_macs note, not BLE GPS one
        if s == STR_NOTE_PURGE_BLACKLIST:
            try:
                p = get_ddh_folder_path_macs_black()
                mask = "{}/*".format(p)
                ff = glob.glob(mask)
                for f in ff:
                    os.unlink(f)
                    s = "warning: debug lock-out all for {}"
                    lg.a(s.format(f))

            except (OSError, Exception) as ex:
                lg.a("error: {}".format(ex))
                return

        lg.a("pressed note button specific 'OK'")
        flag = ddh_get_app_override_flag_file()
        pathlib.Path(flag).touch()
        lg.a("BLE op conditions override set as 1")
        gui_hide_note_tab(self)
        self.tabs.setCurrentIndex(0)

    def click_btn_note_no(self):
        gui_hide_note_tab(self)
        self.tabs.setCurrentIndex(0)
        lg.a("pressed note button 'CANCEL'")

    def closeEvent(self, ev):
        ev.accept()
        p = ddh_get_gui_closed_flag_file()
        pathlib.Path.touch(p, exist_ok=True)
        dds_kill_by_pid_file()
        lg.a("closing by clicking upper-right X")
        sys.stderr.close()
        os._exit(0)

    def keyPressEvent(self, ev):
        self.key_pressed = None
        known_keys = (
            Qt.Key_1,
            Qt.Key_2,
            Qt.Key_3,
            Qt.Key_B,
            Qt.Key_M,
            Qt.Key_W,
            Qt.Key_E,
            Qt.Key_Q,
            Qt.Key_I,
        )
        if ev.key() not in known_keys:
            lg.a("warning: unknown keypress {}".format(ev.key()))
            return

        # ------------------------------
        # identify keyboard key pressed
        # ------------------------------
        if ev.key() == Qt.Key_1:
            lg.a("debug: main_gui detect pressed button 1")

        elif ev.key() == Qt.Key_2:
            lg.a("debug: main_gui detect pressed button 2")
            gui_show_note_tab_delete_black_macs(self)
            return

        elif ev.key() == Qt.Key_3:
            lg.a("debug: main_gui detect pressed button 3")

        elif ev.key() == Qt.Key_M:
            self.key_pressed = "m"

        elif ev.key() == Qt.Key_B:
            self.key_pressed = "b"

        elif ev.key() == Qt.Key_E:
            self.key_pressed = "e"

        elif ev.key() == Qt.Key_Q:
            self.key_pressed = "q"

        elif ev.key() == Qt.Key_I:
            self.key_pressed = "i"

        elif ev.key() == Qt.Key_W:
            self.key_pressed = "w"

    def click_lbl_boat_pressed(self, _):
        self.boat_pressed = 1

    def click_lbl_boat_released(self, _):
        if self.boat_pressed >= 2:
            teh = self.tab_edit_hide = not self.tab_edit_hide
            gui_hide_edit_tab(self) if teh else gui_show_edit_tab(self)
        self.boat_pressed = 0

    def click_lbl_commit_pressed(self, _):
        self.commit_pressed = 1

    def click_lbl_commit_released(self, _):
        if self.commit_pressed >= 2:
            trh = self.tab_advanced_hide = not self.tab_advanced_hide
            gui_hide_advanced_tab(self) if trh else gui_show_advanced_tab(self)
        self.commit_pressed = 0

    def click_lbl_datetime_pressed(self, _):
        self.datetime_pressed = 1

    def click_lbl_datetime_released(self, _):
        if self.datetime_pressed >= 2:
            self.showMinimized()
        self.datetime_pressed = 0

    def click_lbl_net_pressed(self, _):
        # ------------------------
        # lbl_net is the NET icon
        # lbl_net_txt is the text
        # -------------------------
        self.lbl_net_pressed = 1

    def click_lbl_net_released(self, _):
        if self.lbl_net_pressed >= 2:
            tgh = self.tab_graph_hide = not self.tab_graph_hide
            gui_hide_graph_tab(self) if tgh else gui_show_graph_tab(self)
        self.lbl_net_pressed = 0

    def click_cb_s3_uplink_type(self, _):
        s = self.cb_s3_uplink_type.currentText()
        p = LI_PATH_GROUPED_S3_FILE_FLAG
        if s == 'raw':
            os.unlink(p)
        if s == 'group':
            Path(p).touch(exist_ok=True)

    def click_lbl_cloud_img(self, _):
        self.lbl_cloud_txt.setText("checking")
        flag = dds_get_aws_has_something_to_do_via_gui_flag_file()
        pathlib.Path(flag).touch()
        lg.a("user clicked cloud icon")

    def click_lbl_cnv(self, _):
        self.lbl_cnv.setText("checking")
        flag = dds_get_cnv_requested_via_gui_flag_file()
        pathlib.Path(flag).touch()
        lg.a("user clicked lbl_cnv")

    def click_chk_rerun(self, _):
        if self.chk_rerun.isChecked():
            set_ddh_rerun_flag_li()
        else:
            clr_ddh_rerun_flag_li()

    def click_graph_btn_reset(self):
        self.g.getPlotItem().enableAutoRange()
        process_n_graph(self)

    def click_graph_listview_logger_sn(self, _):
        process_n_graph(self)

    def click_graph_btn_next_haul(self):
        process_n_graph(self, r='hauls_next')

    def click_graph_lbl_haul_types(self, _):
        process_n_graph(self, r='hauls_labels')

    def click_graph_btn_paint_zones(self, _):
        process_n_graph(self)

    def click_graph_cb_switch_tp(self, _):
        process_n_graph(self)


def on_ctrl_c(signal_num, _):
    p = ddh_get_gui_closed_flag_file()
    pathlib.Path.touch(p, exist_ok=True)
    lg.a("closing DDS by ctrl + c")
    dds_kill_by_pid_file()
    lg.a("closing DDH by ctrl + c")
    lg.a(f"received exactly signal number {signal_num}")
    os._exit(0)
