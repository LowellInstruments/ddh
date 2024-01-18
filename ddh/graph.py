import time
from datetime import datetime
from glob import glob
import json
from PyQt5 import QtCore
from PyQt5.QtCore import QTime, QCoreApplication
import pyqtgraph as pg
from PyQt5.QtGui import QFont
from pyqtgraph.Qt import QtGui
from os.path import basename
from pyqtgraph import LinearRegionItem
from ddh.utils_graph import utils_graph_read_fol_req_file, \
    utils_graph_get_abs_fol_list, process_graph_csv_data, \
    utils_graph_does_exist_fol_req_file, \
    utils_graph_delete_fol_req_file
from mat.utils import linux_is_rpi
from utils.ddh_config import dds_get_json_mac_dns, dds_get_mac_from_sn_from_json_file
from utils.ddh_shared import get_dl_folder_path_from_mac, \
    ddh_get_absolute_application_path, \
    get_number_of_hauls
from utils.logs import lg_gra as lg
from utils.mavg import get_interesting_idx_ma

# to be able to zoom in RPi
pg.setConfigOption('leftButtonPan', False)


# plot objects
p1 = None
p2 = None
p3 = None
just_booted = True


class GraphException(Exception):
    pass


def _axis_room(v: list):
    return .1 * max(v)


def _sty(color):
    return {"color": color, "font-size": "20px", "font-weight": "bold"}


def _get_color_by_label(lbl):
    # google for SVG 1.0 color names
    if 'Temperature' in lbl:
        return 'red'
    if 'Pressure' in lbl:
        return 'blue'
    if 'Depth' in lbl:
        return 'blue'
    if 'DO Concentration' in lbl:
        return 'blue'
    if 'Ax' in lbl:
        return 'limegreen'
    return 'green'


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [QTime().addMSecs(value).toString('mm:ss') for value in values]


class LimitsTypeError(Exception):
    def __init__(self, err='Limits type must be type int or tuple of ints', *args, **kwargs):
        super().__init__(self, err, *args, **kwargs)


class FiniteLinearRegionItem(LinearRegionItem):
    def __init__(self, limits=None, *args, **kwargs):
        super(FiniteLinearRegionItem, self).__init__(*args, **kwargs)
        """Create a new LinearRegionItem.

            Now you can define the shading area. Enjoy!

        ==============  =====================================================================
        **Arguments:**
        limits          A tuple containing the upper and lower bounds prependicular to the orientation.
                        Or a int/float containing the lower bounds prependicular to the orientation.
                        The default value is None.
        ==============  =====================================================================
        """
        self.limit = limits

    def boundingRect(self):
        br = self.viewRect()
        rng = self.getRegion()

        # Infinite with one end close
        if isinstance(self.limit, int):
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(self.limit)
                br.setTop(br.top() + length * self.span[0])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(br.left() + length * self.span[1])
                br.setLeft(self.limit)
        # Finite
        elif isinstance(self.limit, tuple):
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(self.limit[0])
                br.setTop(self.limit[1])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(self.limit[1])
                br.setLeft(self.limit[0])
        elif self.limit is None:
            if self.orientation in ('vertical', LinearRegionItem.Vertical):
                br.setLeft(rng[0])
                br.setRight(rng[1])
                length = br.height()
                br.setBottom(br.top() + length * self.span[1])
                br.setTop(br.top() + length * self.span[0])
            else:
                br.setTop(rng[0])
                br.setBottom(rng[1])
                length = br.width()
                br.setRight(br.left() + length * self.span[1])
                br.setLeft(br.left() + length * self.span[0])
        else:
            raise LimitsTypeError

        br = br.normalized()
        return br


def _graph_check_mac_has_dl_files(mac, fol_ls):
    for i in fol_ls:
        if mac.lower() in i.lower():
            return True
    return False


def _graph_update_views():
    # used when resizing
    global p1, p2, p3
    # for the second line
    p2.setGeometry(p1.vb.sceneBoundingRect())
    p2.linkedViewChanged(p1.vb, p2.XAxis)
    # for the 3+ line
    if p3:
        p3.setGeometry(p1.vb.sceneBoundingRect())
        p3.linkedViewChanged(p1.vb, p3.XAxis)


def _graph_busy_sign_show(a):
    a.lbl_graph_busy.setVisible(True)
    QCoreApplication.processEvents()


def _graph_busy_sign_hide(a):
    a.lbl_graph_busy.setVisible(False)


def _graph_calc_hash_filenames(fol):
    _g_ff_t = sorted(glob("{}/{}".format(fol, "*_Temperature.csv")))
    _g_ff_p = sorted(glob("{}/{}".format(fol, "*_Pressure.csv")))
    _g_ff_do = sorted(glob("{}/{}".format(fol, "*_DissolvedOxygen.csv")))
    _g_ff_tap = sorted(glob("{}/{}".format(fol, "*_TAP.csv")))

    # so we can use cache
    return '\n'.join(_g_ff_t) + '\n'.join(_g_ff_p) +\
        '\n'.join(_g_ff_do) + '\n'.join(_g_ff_tap)


def _process_n_graph(a, r=''):

    # get graph from passed app
    g = a.g

    # benchmark this graphing function
    start_ts = time.perf_counter()

    # get list of absolute local 'dl_files/<mac>' folders
    fol_ls = utils_graph_get_abs_fol_list()
    fol: str

    # get current haul type
    _ht = a.cb_g_cycle_haul.currentText()

    # get zones on / off
    _zt = a.cb_g_paint_zones.currentText()

    # get haul idx
    if a.g_haul_idx is None:
        a.g_haul_idx = -1

    # get reason passed for graph
    if r == 'BLE':
        if not utils_graph_does_exist_fol_req_file():
            raise GraphException('error: no BLE requested folder to graph')
        fol = utils_graph_read_fol_req_file()
        lg.a('selected last BLE download {}'.format(fol))
        utils_graph_delete_fol_req_file()
    else:
        # people pressing graph buttons
        sn = a.cb_g_sn.currentText()
        if not sn:
            raise GraphException('seems no one asked for a graph?')
        if sn.startswith('SN'):
            sn = sn[2:]
        mac = dds_get_mac_from_sn_from_json_file(sn).replace(':', '-')
        if not _graph_check_mac_has_dl_files(mac, fol_ls):
            raise GraphException(f'error: no files for sn {sn} mac {mac}')
        lg.a('selected dropdown sn {} / mac {}'.format(sn, mac))
        fol = get_dl_folder_path_from_mac(mac)
        # fol: 'dl_files/<mac>, is not absolute, make it so
        fol = str(ddh_get_absolute_application_path()) + '/' + str(fol)

    # get number of hauls
    nh = get_number_of_hauls(fol)
    lg.a(f'found {nh} hauls in folder {fol}')
    if r == 'hauls_next':
        # remember this button only active on haul_text == 'single'
        if nh == 0:
            raise GraphException(f'error: no hauls for {fol}')
        a.g_haul_idx = (a.g_haul_idx - 1) % nh
        lg.a(f'button haul index = {a.g_haul_idx} / {nh}')
    if r == 'hauls_labels':
        if _ht == 'single':
            a.btn_g_next_haul.setEnabled(True)
            a.btn_g_next_haul.setVisible(True)
            a.g_haul_idx = -1
        else:
            a.btn_g_next_haul.setEnabled(False)
            a.btn_g_next_haul.setVisible(False)

    # get buttons visible or not conditionally
    a.cb_g_switch_tp.setVisible(False)

    # ----------------------------------------
    # let's CLEAR graph and start from scratch
    # ----------------------------------------
    global p1
    global p2
    global p3
    if p1:
        p1.clear()
    if p2:
        p2.clear()
    if p3:
        p3.clear()
    p1 = g.plotItem

    # grid or not
    g.showGrid(x=True, y=False)

    # ---------
    # 2nd line
    # ---------
    p2 = pg.ViewBox(enableMenu=True)
    p1.showAxis('right')
    p1.scene().addItem(p2)
    p1.getAxis('right').linkToView(p2)
    p2.setXLink(p1)

    # ---------
    # 3rd line
    # ---------
    p3 = pg.ViewBox()
    ax3 = pg.AxisItem('right')
    p1.scene().addItem(p3)
    ax3.linkToView(p3)
    p3.setXLink(p1)
    ax3.setZValue(-10000)

    # connect the thing when resizing
    _graph_update_views()
    p1.vb.sigResized.connect(_graph_update_views)

    # font: TICKS TEXT
    font = QtGui.QFont()
    font.setPixelSize(16)
    font.setBold(True)
    p1.getAxis("bottom").setStyle(tickFont=font)
    p1.getAxis("left").setStyle(tickFont=font)
    p1.getAxis("right").setStyle(tickFont=font)

    # --------------------------
    # PROCESS folder's CSV data
    # --------------------------
    filenames_hash = _graph_calc_hash_filenames(fol)
    data = process_graph_csv_data(fol, filenames_hash, _ht, a.g_haul_idx)
    if not data:
        raise GraphException(f'error: no data in folder {fol}')
    if 'ISO 8601 Time' not in data.keys():
        raise GraphException(f'error: no time data for {fol}')

    # x: time
    x = data['ISO 8601 Time']
    met = data['metric']

    # ----------
    # the title
    # ----------
    fmt = '%b %d %Y %H:%M'
    # choose utcfromtimestamp() / fromtimestamp()
    t1 = datetime.fromtimestamp(x[0]).strftime(fmt)
    t2 = datetime.fromtimestamp(x[-1]).strftime(fmt)
    title = '{} to {}'.format(t1, t2)
    if data['pruned']:
        title += ' (data trimmed)'

    # --------------
    # metric labels
    # --------------
    lbl1, lbl2, lbl3 = '', '', ''
    y1, y2, y3 = [], [], []
    if met == 'TP':
        lbl1 = 'Depth (fathoms) TP'
        lbl2 = 'Temperature (F) TP'
    elif met == 'DO':
        lbl1 = 'DO Concentration (mg/l) DO'
        lbl2 = 'Temperature (F) DO'
    elif met == 'TAP':
        lbl1 = 'Depth (fathoms) TAP'
        lbl2 = 'Temperature (F) TAP'
        lbl3 = 'Ax TAP'
        y3 = data['Ax TAP']
        y4 = data['Ay TAP']
        y5 = data['Az TAP']
    y1 = data[lbl1]
    y2 = data[lbl2]

    # see if we need Depth-axis inverted
    p1.invertY('Depth' in lbl1)

    # colors
    lbl1 = lbl1.replace(' TP', '').replace(' DO', '').replace(' TAP', '')
    lbl2 = lbl2.replace(' TP', '').replace(' DO', '').replace(' TAP', '')
    lbl3 = lbl3.replace(' TP', '').replace(' DO', '').replace(' TAP', '')
    clr_1 = _get_color_by_label(lbl1)
    clr_2 = _get_color_by_label(lbl2)
    clr_3 = _get_color_by_label(lbl3)
    clr_4 = 'magenta'
    lbl1 = lbl1 + ' ─'
    lbl2 = lbl2 + ' - -'
    lbl3 = lbl3 + ' ─'
    pen1 = pg.mkPen(color=clr_1, width=2, style=QtCore.Qt.SolidLine)
    pen2 = pg.mkPen(color=clr_2, width=2, style=QtCore.Qt.DashLine)
    pen3 = pg.mkPen(color=clr_3, width=1, style=QtCore.Qt.SolidLine)
    pen4 = pg.mkPen(color=clr_4, width=2, style=QtCore.Qt.SolidLine)
    p1.getAxis('left').setTextPen(clr_1)
    p1.getAxis('right').setTextPen(clr_2)
    p1.getAxis('bottom').setTextPen('black')

    # avoids small glitch when re-zooming
    g.getPlotItem().enableAutoRange()

    # todo ---> decide: set depth min 0 or modify negative depths values

    # -----------------
    # graph DO loggers
    # -----------------
    if met == 'DO':
        # draw DO and T lines
        p1.setLabel("left", lbl1, **_sty(clr_1))
        p1.getAxis('right').setLabel(lbl2, **_sty(clr_2))
        p1.plot(x, y1, pen=pen1, hoverable=True)
        p2.addItem(pg.PlotCurveItem(x, y2, pen=pen2, hoverable=True))

        # y-axis ranges, bottom-axis label
        p1.setYRange(0, 10, padding=0)
        p2.setYRange(min(y2), max(y2), padding=0)
        p1.getAxis('bottom').setLabel(title, **_sty('black'))

        # alpha, for zones, the lower, the more transparent
        alpha = 85
        if _zt == 'zones OFF':
            return
        g.addItem(FiniteLinearRegionItem(values=(0, 2),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 0, 0, alpha),
                                         movable=False))
        g.addItem(FiniteLinearRegionItem(values=(2, 4),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 170, 6, alpha),
                                         movable=False))
        g.addItem(FiniteLinearRegionItem(values=(4, 6),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(255, 255, 66, alpha),
                                         movable=False))
        g.addItem(FiniteLinearRegionItem(values=(6, 10),
                                         limits=4,
                                         orientation="horizontal",
                                         brush=(176, 255, 66, alpha),
                                         movable=False))

    # -----------------------------------------
    # graph old Temperature / Pressure loggers
    # -----------------------------------------
    if met == 'TP':
        # draw T and D lines
        p1.setLabel("left", lbl1, **_sty(clr_1))
        p1.getAxis('right').setLabel(lbl2, **_sty(clr_2))
        p1.plot(x, y1, pen=pen1, hoverable=True)
        p2.addItem(pg.PlotCurveItem(x, y2, pen=pen2, hoverable=True))

        # y-axis ranges, bottom-axis label
        p1.setYRange(0, max(y1) + _axis_room(y1), padding=0)
        p2.setYRange(min(y2), max(y2), padding=0)
        p1.getAxis('bottom').setLabel(title, **_sty('black'))

    # ------------------
    # graph TAP loggers
    # ------------------
    if met == 'TAP':
        a.cb_g_switch_tp.setVisible(True)
        tap_plot_type = a.cb_g_switch_tp.currentText()

        # type of TAP plot 1/2: T & D vs time, draw lines
        if 'time' in tap_plot_type:
            p1.setLabel("left", lbl1, **_sty(clr_1))
            p1.getAxis('right').setLabel(lbl2, **_sty(clr_2))
            p1.plot(x, y1, pen=pen1, hoverable=True)
            p2.addItem(pg.PlotCurveItem(x, y2, pen=pen2, hoverable=True))

            # y-axis ranges, prevent negative depth values, bottom-axis label
            p1.setYRange(0, max(y1) + _axis_room(y1), padding=0)
            p2.setYRange(min(y2), max(y2), padding=0)
            p1.getAxis('bottom').setLabel(title, **_sty('black'))

            # ------------------------
            # 3rd line: accelerometer
            # ------------------------
            if not linux_is_rpi():
                # add 3rd axis
                # p1.layout.addItem(ax3, 2, 3)
                ax3.setStyle(tickFont=font)
                ax3.setLabel(lbl3, **_sty(clr_3))
                ax3.setTextPen(pen3)

                # get indexes with interesting accelerometer data
                w = 2
                th = 3
                li = get_interesting_idx_ma(y5, w, th)
                print('y5', y5)
                print('li_y5', li)

                # add arrows
                # for i in range(3):
                #     a = pg.ArrowItem(angle=-160, tipAngle=60, headLen=40, tailLen=40, tailWidth=20,
                #                      pen=pen3, brush='r')
                #     a.setPos(x[20 + (i * 10)], y3[20 + (i * 10)],)
                #     p3.addItem(a)

                # add text
                # a = pg.TextItem('alarm', color='orange', border='green', angle=45)
                # a.setPos(x[10], y3[10])
                # a.setFont(QFont('Times', 20))
                # p3.addItem(a)

                # range
                p3.setYRange(0, max(y3), padding=0)

        # type of TAP plot 2/2: T vs D, draw lines
        elif 'Temp' in tap_plot_type:
            p1.getAxis('left').setTextPen(clr_4)
            p1.setLabel("left", 'Depth (fathoms)' + ' ─', **_sty(clr_4))

            # remove whole right axis
            g.getPlotItem().hideAxis('right')

            # in this case, x-ticks are T
            p1.plot(y2, y1, pen=pen4, hoverable=True)

            # y-axis range, prevent negative depth values, bottom axis label
            p1.setYRange(0, max(y1) + _axis_room(y1), padding=0)
            title = f'Temperature (F) {title}'
            p1.getAxis('bottom').setLabel(title, **_sty('black'))

            # or we could set the x-axis label on top
            # a.g.setTitle(e, color="red", size="15pt")

    # statistics: benchmark and number of points
    end_ts = time.perf_counter()
    el_ts = int((end_ts - start_ts) * 1000)
    lg.a(f'graphed {len(x)} {met} points, took {el_ts} ms')


def process_n_graph(a, r=''):
    try:
        # ----------
        # graph it
        # ----------
        _graph_busy_sign_show(a)
        _process_n_graph(a, r)

        # remove any past error
        a.g.setTitle('')

    except GraphException as e:
        # errors such as "no data files to graph"
        a.g.setTitle(e, color="red", size="15pt")
        a.g.getAxis('bottom').setLabel("")

    except (Exception,) as ex:
        # not GraphException, but python errors such as IndexError
        e = 'undefined error, see log'
        a.g.setTitle(e, color="red", size="15pt")
        lg.a("error: graph_embed -> {}".format(ex))
        a.g.getAxis('bottom').setLabel("")

    finally:
        _graph_busy_sign_hide(a)
