# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer_main.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(800, 480))
        MainWindow.setMaximumSize(QtCore.QSize(800, 480))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.tabs.setFont(font)
        self.tabs.setObjectName("tabs")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_4.setSpacing(12)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSpacing(12)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.img_gps = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_gps.sizePolicy().hasHeightForWidth())
        self.img_gps.setSizePolicy(sizePolicy)
        self.img_gps.setText("")
        self.img_gps.setScaledContents(True)
        self.img_gps.setAlignment(QtCore.Qt.AlignCenter)
        self.img_gps.setObjectName("img_gps")
        self.horizontalLayout_13.addWidget(self.img_gps)
        self.lbl_time_n_pos = QtWidgets.QLabel(self.tab)
        self.lbl_time_n_pos.setText("")
        self.lbl_time_n_pos.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_time_n_pos.setWordWrap(True)
        self.lbl_time_n_pos.setObjectName("lbl_time_n_pos")
        self.horizontalLayout_13.addWidget(self.lbl_time_n_pos)
        self.horizontalLayout_13.setStretch(0, 4)
        self.horizontalLayout_13.setStretch(1, 6)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_13)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_ble = QtWidgets.QLabel(self.tab)
        self.lbl_ble.setText("")
        self.lbl_ble.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_ble.setWordWrap(True)
        self.lbl_ble.setObjectName("lbl_ble")
        self.gridLayout.addWidget(self.lbl_ble, 0, 1, 2, 1)
        self.bar_dl = QtWidgets.QProgressBar(self.tab)
        self.bar_dl.setProperty("value", 0)
        self.bar_dl.setAlignment(QtCore.Qt.AlignCenter)
        self.bar_dl.setTextVisible(True)
        self.bar_dl.setObjectName("bar_dl")
        self.gridLayout.addWidget(self.bar_dl, 2, 1, 1, 1)
        self.img_ble = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_ble.sizePolicy().hasHeightForWidth())
        self.img_ble.setSizePolicy(sizePolicy)
        self.img_ble.setMaximumSize(QtCore.QSize(16777215, 150))
        self.img_ble.setText("")
        self.img_ble.setScaledContents(True)
        self.img_ble.setAlignment(QtCore.Qt.AlignCenter)
        self.img_ble.setObjectName("img_ble")
        self.gridLayout.addWidget(self.img_ble, 0, 0, 3, 1)
        self.gridLayout.setColumnStretch(0, 4)
        self.gridLayout.setColumnStretch(1, 6)
        self.horizontalLayout_8.addLayout(self.gridLayout)
        self.horizontalLayout_8.setStretch(0, 1)
        self.horizontalLayout_8.setStretch(1, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setSpacing(12)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.img_net = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_net.sizePolicy().hasHeightForWidth())
        self.img_net.setSizePolicy(sizePolicy)
        self.img_net.setMaximumSize(QtCore.QSize(16777215, 150))
        self.img_net.setText("")
        self.img_net.setScaledContents(True)
        self.img_net.setAlignment(QtCore.Qt.AlignCenter)
        self.img_net.setObjectName("img_net")
        self.horizontalLayout_7.addWidget(self.img_net)
        self.lbl_net_n_ftp = QtWidgets.QLabel(self.tab)
        self.lbl_net_n_ftp.setText("")
        self.lbl_net_n_ftp.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_net_n_ftp.setWordWrap(True)
        self.lbl_net_n_ftp.setObjectName("lbl_net_n_ftp")
        self.horizontalLayout_7.addWidget(self.lbl_net_n_ftp)
        self.horizontalLayout_7.setStretch(0, 4)
        self.horizontalLayout_7.setStretch(1, 6)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.img_plt = QtWidgets.QLabel(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_plt.sizePolicy().hasHeightForWidth())
        self.img_plt.setSizePolicy(sizePolicy)
        self.img_plt.setMaximumSize(QtCore.QSize(16777215, 150))
        self.img_plt.setText("")
        self.img_plt.setScaledContents(True)
        self.img_plt.setAlignment(QtCore.Qt.AlignCenter)
        self.img_plt.setObjectName("img_plt")
        self.horizontalLayout_15.addWidget(self.img_plt)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.lbl_plot = QtWidgets.QLabel(self.tab)
        self.lbl_plot.setText("")
        self.lbl_plot.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_plot.setWordWrap(True)
        self.lbl_plot.setObjectName("lbl_plot")
        self.verticalLayout_5.addWidget(self.lbl_plot)
        self.horizontalLayout_15.addLayout(self.verticalLayout_5)
        self.horizontalLayout_15.setStretch(0, 4)
        self.horizontalLayout_15.setStretch(1, 6)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 1)
        self.horizontalLayout_10.addLayout(self.verticalLayout_4)
        self.tabs.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.layoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.layoutWidget_2.setGeometry(QtCore.QRect(0, 0, 781, 411))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.vl_3 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.vl_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.vl_3.setContentsMargins(0, 0, 0, 0)
        self.vl_3.setSpacing(0)
        self.vl_3.setObjectName("vl_3")
        self.lbl_plt_bsy = QtWidgets.QLabel(self.tab_2)
        self.lbl_plt_bsy.setGeometry(QtCore.QRect(335, 130, 100, 101))
        font = QtGui.QFont()
        font.setPointSize(64)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.lbl_plt_bsy.setFont(font)
        self.lbl_plt_bsy.setStyleSheet("")
        self.lbl_plt_bsy.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lbl_plt_bsy.setTextFormat(QtCore.Qt.RichText)
        self.lbl_plt_bsy.setScaledContents(True)
        self.lbl_plt_bsy.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_plt_bsy.setWordWrap(True)
        self.lbl_plt_bsy.setObjectName("lbl_plt_bsy")
        self.lbl_plt_msg = QtWidgets.QLabel(self.tab_2)
        self.lbl_plt_msg.setGeometry(QtCore.QRect(110, 220, 551, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.lbl_plt_msg.setFont(font)
        self.lbl_plt_msg.setStyleSheet("background: lightyellow;")
        self.lbl_plt_msg.setFrameShape(QtWidgets.QFrame.Box)
        self.lbl_plt_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_plt_msg.setWordWrap(True)
        self.lbl_plt_msg.setObjectName("lbl_plt_msg")
        self.tabs.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(12, 12, 12, 12)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem)
        self.img_boat = QtWidgets.QLabel(self.tab_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.img_boat.sizePolicy().hasHeightForWidth())
        self.img_boat.setSizePolicy(sizePolicy)
        self.img_boat.setMaximumSize(QtCore.QSize(150, 150))
        self.img_boat.setText("")
        self.img_boat.setPixmap(QtGui.QPixmap("../../../.designer/backup/res/img_boatname.png"))
        self.img_boat.setScaledContents(True)
        self.img_boat.setObjectName("img_boat")
        self.horizontalLayout_11.addWidget(self.img_boat)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem1)
        self.lbl_boatname = QtWidgets.QLabel(self.tab_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(8)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_boatname.sizePolicy().hasHeightForWidth())
        self.lbl_boatname.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setKerning(False)
        self.lbl_boatname.setFont(font)
        self.lbl_boatname.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_boatname.setObjectName("lbl_boatname")
        self.horizontalLayout_11.addWidget(self.lbl_boatname)
        self.lbl_ver = QtWidgets.QLabel(self.tab_3)
        self.lbl_ver.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_ver.setObjectName("lbl_ver")
        self.horizontalLayout_11.addWidget(self.lbl_ver)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_11.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_11)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tbl_his = QtWidgets.QTableWidget(self.tab_3)
        self.tbl_his.setEnabled(True)
        self.tbl_his.setStyleSheet("font: 19pt \"Ubuntu\";")
        self.tbl_his.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tbl_his.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tbl_his.setShowGrid(True)
        self.tbl_his.setRowCount(5)
        self.tbl_his.setColumnCount(3)
        self.tbl_his.setObjectName("tbl_his")
        self.tbl_his.horizontalHeader().setDefaultSectionSize(230)
        self.tbl_his.horizontalHeader().setHighlightSections(False)
        self.tbl_his.horizontalHeader().setMinimumSectionSize(80)
        self.tbl_his.verticalHeader().setVisible(False)
        self.tbl_his.verticalHeader().setDefaultSectionSize(36)
        self.tbl_his.verticalHeader().setHighlightSections(False)
        self.horizontalLayout_4.addWidget(self.tbl_his)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.setStretch(0, 3)
        self.verticalLayout_3.setStretch(1, 1)
        self.verticalLayout_3.setStretch(2, 5)
        self.horizontalLayout_12.addLayout(self.verticalLayout_3)
        self.tabs.addTab(self.tab_3, "")
        self.tab_setup = QtWidgets.QWidget()
        self.tab_setup.setObjectName("tab_setup")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.tab_setup)
        self.horizontalLayout_6.setContentsMargins(18, -1, 18, -1)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_see_all = QtWidgets.QPushButton(self.tab_setup)
        self.btn_see_all.setObjectName("btn_see_all")
        self.horizontalLayout_3.addWidget(self.btn_see_all)
        self.btn_see_cur = QtWidgets.QPushButton(self.tab_setup)
        self.btn_see_cur.setObjectName("btn_see_cur")
        self.horizontalLayout_3.addWidget(self.btn_see_cur)
        self.btn_known_clear = QtWidgets.QPushButton(self.tab_setup)
        self.btn_known_clear.setObjectName("btn_known_clear")
        self.horizontalLayout_3.addWidget(self.btn_known_clear)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.lst_mac_org = QtWidgets.QListWidget(self.tab_setup)
        font = QtGui.QFont()
        font.setFamily("Open Sans")
        font.setPointSize(18)
        self.lst_mac_org.setFont(font)
        self.lst_mac_org.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.lst_mac_org.setObjectName("lst_mac_org")
        self.verticalLayout.addWidget(self.lst_mac_org)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.btn_arrow = QtWidgets.QPushButton(self.tab_setup)
        self.btn_arrow.setObjectName("btn_arrow")
        self.horizontalLayout_5.addWidget(self.btn_arrow)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.lst_mac_dst = QtWidgets.QListWidget(self.tab_setup)
        self.lst_mac_dst.setObjectName("lst_mac_dst")
        self.verticalLayout.addWidget(self.lst_mac_dst)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 10)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 10)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        spacerItem6 = QtWidgets.QSpacerItem(144, 397, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem7)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.tab_setup)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lne_vessel = QtWidgets.QLineEdit(self.tab_setup)
        self.lne_vessel.setObjectName("lne_vessel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lne_vessel)
        self.label_3 = QtWidgets.QLabel(self.tab_setup)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lne_forget = QtWidgets.QLineEdit(self.tab_setup)
        self.lne_forget.setObjectName("lne_forget")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lne_forget)
        self.label_5 = QtWidgets.QLabel(self.tab_setup)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.btn_load_current = QtWidgets.QPushButton(self.tab_setup)
        self.btn_load_current.setObjectName("btn_load_current")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.btn_load_current)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.lbl_setup_result = QtWidgets.QLabel(self.tab_setup)
        self.lbl_setup_result.setText("")
        self.lbl_setup_result.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_setup_result.setObjectName("lbl_setup_result")
        self.verticalLayout_2.addWidget(self.lbl_setup_result)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem8)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_4 = QtWidgets.QLabel(self.tab_setup)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.btn_setup_apply = QtWidgets.QPushButton(self.tab_setup)
        self.btn_setup_apply.setObjectName("btn_setup_apply")
        self.gridLayout_2.addWidget(self.btn_setup_apply, 1, 1, 1, 1)
        self.btn_dl_purge = QtWidgets.QPushButton(self.tab_setup)
        self.btn_dl_purge.setObjectName("btn_dl_purge")
        self.gridLayout_2.addWidget(self.btn_dl_purge, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.tab_setup)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.tab_setup)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 2, 0, 1, 1)
        self.btn_his_purge = QtWidgets.QPushButton(self.tab_setup)
        self.btn_his_purge.setObjectName("btn_his_purge")
        self.gridLayout_2.addWidget(self.btn_his_purge, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem9)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 3)
        self.verticalLayout_2.setStretch(2, 1)
        self.verticalLayout_2.setStretch(3, 1)
        self.verticalLayout_2.setStretch(5, 1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.setStretch(0, 10)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 10)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)
        self.tabs.addTab(self.tab_setup, "")
        self.horizontalLayout.addWidget(self.tabs)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), _translate("MainWindow", " Information"))
        self.lbl_plt_bsy.setText(_translate("MainWindow", "??????"))
        self.lbl_plt_msg.setText(_translate("MainWindow", "msg_plt"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_2), _translate("MainWindow", " Plots"))
        self.lbl_boatname.setText(_translate("MainWindow", "<boatname>"))
        self.lbl_ver.setText(_translate("MainWindow", "DDH vX.YY.ZZ"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_3), _translate("MainWindow", " History"))
        self.btn_see_all.setText(_translate("MainWindow", "see all"))
        self.btn_see_cur.setText(_translate("MainWindow", "see current"))
        self.btn_known_clear.setText(_translate("MainWindow", "clear"))
        self.btn_arrow.setText(_translate("MainWindow", "???"))
        self.label.setText(_translate("MainWindow", "vessel name"))
        self.label_3.setText(_translate("MainWindow", "forget time (s)"))
        self.label_5.setText(_translate("MainWindow", "current ones"))
        self.btn_load_current.setText(_translate("MainWindow", "load"))
        self.label_4.setText(_translate("MainWindow", "restart DDH"))
        self.btn_setup_apply.setText(_translate("MainWindow", "apply"))
        self.btn_dl_purge.setText(_translate("MainWindow", "purge"))
        self.label_6.setText(_translate("MainWindow", "files folder"))
        self.label_7.setText(_translate("MainWindow", "history tab"))
        self.btn_his_purge.setText(_translate("MainWindow", "purge"))
        self.tabs.setTabText(self.tabs.indexOf(self.tab_setup), _translate("MainWindow", " Setup"))
