import datetime
import glob
import os
import sys
import time

import numpy
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import QPushButton, QApplication, QCheckBox, QRadioButton
import pyqtgraph as pg
from ddh.utils_graph import graph_get_fol_req_file, \
    graph_get_fol_list, graph_get_data_csv
from os.path import basename


p1 = None
p2 = None


def graph_update_views():
    # used when resizing
    global p1, p2
    p2.setGeometry(p1.vb.sceneBoundingRect())
    p2.linkedViewChanged(p1.vb, p2.XAxis)


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [QTime().addMSecs(value).toString('mm:ss') for value in values]


class SeparateGraphWindow(QtWidgets.QMainWindow):

    def _btn_close_click(self):
        print('closing graph window')
        self.close()

    def _btn_next_logger_click(self):
        self.fol_ls_idx = (self.fol_ls_idx + 1) % self.fol_ls_len
        self.fol = self.fol_ls[self.fol_ls_idx]
        print('\nswitch to folder', basename(self.fol))
        self.haul_len = len(glob.glob('{}/*_Temperature.csv'.format(self.fol)))
        self.hi = -1
        self.graph_all()

    def _btn_next_haul_click(self):
        self.hi = (self.hi + 1) % self.haul_len
        print('haul is', self.hi)
        self.graph_all()

    def _rb_haul_click(self, b):
        if not b.isChecked():
            return

        self.h = b.text()
        self.btn_next_haul.setEnabled(False)
        if self.h == 'one haul':
            self.btn_next_haul.setEnabled(True)
        self.graph_all()

    def __init__(self, *args, **kwargs):
        super(SeparateGraphWindow, self).__init__(*args, **kwargs)

        # ---------------------------------------
        # get requested folder and list of them
        # ---------------------------------------
        self.h = 'last'
        self.fol = graph_get_fol_req_file()
        if not self.fol:
            print('graph: error self.fol empty')
            return
        self.fol_ls = graph_get_fol_list()
        if not self.fol_ls:
            print('graph: no plot folders')
            return
        self.fol_ls_len = len(self.fol_ls)
        self.fol_ls_idx = self.fol_ls.index(self.fol)
        print('start at folder', basename(self.fol))
        self.hi = -1
        self.haul_len = len(glob.glob('{}/*_Temperature.csv'.format(self.fol)))

        # controls
        self.g = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.btn_close = QPushButton('close', self)
        self.btn_next_logger = QPushButton('next logger', self)
        self.btn_next_haul = QPushButton('next haul', self)
        self.btn_close.clicked.connect(self._btn_close_click)
        self.btn_next_logger.clicked.connect(self._btn_next_logger_click)
        self.btn_next_haul.clicked.connect(self._btn_next_haul_click)
        self.rb1 = QRadioButton("all hauls")
        self.rb1.toggled.connect(lambda: self._rb_haul_click(self.rb1))
        self.rb2 = QRadioButton("last haul")
        self.rb2.toggled.connect(lambda: self._rb_haul_click(self.rb2))
        self.rb2.setChecked(True)
        self.rb3 = QRadioButton("one haul")
        self.rb3.toggled.connect(lambda: self._rb_haul_click(self.rb3))

        # layout everything
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(self.btn_close)
        hl.addWidget(self.btn_next_logger)
        hl.addWidget(self.rb1)
        hl.addWidget(self.rb2)
        hl.addWidget(self.rb3)
        hl.addWidget(self.btn_next_haul)
        vl = QtWidgets.QVBoxLayout()
        vl.setSpacing(10)
        vl.addLayout(hl)
        vl.addWidget(self.g)
        wid.setLayout(vl)

    def graph_all(self):
        global p1
        global p2
        if p1:
            p1.clear()
        if p2:
            p2.clear()
        p1 = self.g.plotItem
        self.g.showGrid(x=True, y=True)

        # create the 2nd plot
        p2 = pg.ViewBox()
        p1.showAxis('right')
        p1.scene().addItem(p2)
        p1.getAxis('right').linkToView(p2)
        p2.setXLink(p1)
        graph_update_views()
        p1.vb.sigResized.connect(graph_update_views)
        sty = {"color": "red", "font-size": "20px"}
        p1.setLabel("left", "Temperature (°C)", **sty)
        sty = {"color": "blue", "font-size": "20px"}
        p1.getAxis('right').setLabel("Pressure (dbar)", ** sty)

        # ----------------------------------------
        # grab all this CSV data for this folder
        # ----------------------------------------
        print('self.fol', self.fol)
        print('self.h', self.h)
        print('self.hi', self.hi)

        data = graph_get_data_csv(self.fol, self.h, self.hi)
        if not data:
            return
        # x is the time and is already in seconds
        x = data['ISO 8601 Time']
        t = data['Temperature (C)']
        p = data['Pressure (dbar)']

        # set the title
        fmt = '%b %d %H:%M'
        t1 = datetime.datetime.utcfromtimestamp(x[0]).strftime(fmt)
        t2 = datetime.datetime.utcfromtimestamp(x[-1]).strftime(fmt)
        mac = os.path.basename(self.fol).replace('-', ':')
        title = '{} - {} to {}'.format(mac, t1, t2)
        self.g.setTitle(title, color="black", size="15pt")

        # --------
        # draw it
        # --------
        p1.setYRange(min(t), max(t), padding=0)
        p2.setYRange(min(p), max(p), padding=0)
        self.g.setBackground('w')
        p1.plot(x, t, pen='r')
        pi = pg.PlotCurveItem(x, p, pen='b', hoverable=True)
        p2.addItem(pi)


# to test
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SeparateGraphWindow()
    ex.show()
    sys.exit(app.exec_())
