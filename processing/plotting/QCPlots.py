import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib as mpl
from pylab import *
from matplotlib.ticker import MaxNLocator
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QApplication, QVBoxLayout, QAction, QLabel,
                             QFileDialog, QTabWidget, QGridLayout, QComboBox, QListWidget, QPushButton, QCheckBox)
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5 import QtCore, QtWidgets
import sqlite3, io, json, logging, traceback, statistics
import hyproicons, style
from dialogs.PlotSelectionDialog import plotSelection
from dialogs.TraceSelectionDialog import traceSelection

from processing.plotting.PlottingWindow import QMainPlotterTemplate

mpl.rc('font', family = 'Segoe UI Symbol') # Cast Segoe UI font onto all plot text

# File contains classes to produce various specific plots, all classes that utilise QWidget are apart of the
# nutrient processing workflow
# The other classes using QMainWindow are plots that are called on manually and are then displayed in their
# own window
# TODO: Fix RMNS plot so it still works even if nominal RMNS values are not in the database


class redfieldPlot(QMainPlotterTemplate):
    def __init__(self, database):
        super().__init__()
        self. database = database
        self.populate_runlist()

        self.setWindowTitle('Redfield Ratio Plot')

        self.main_plot.set_title('Redfield Ratio', fontsize=18)
        self.main_plot.set_xlabel('[NOx] (uM)', fontsize=15)
        self.main_plot.set_ylabel('[Phosphate] (uM)', fontsize=15)

        self.main_plot.grid(alpha=0.1)


        self.show()

    def populate_runlist(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('SELECT DISTINCT runNumber FROM nitrateData')
        nitrate_runs = sorted(list(c.fetchall()))
        c.execute('SELECT DISTINCT runNumber FROM phosphateData')
        phosphate_runs = list(c.fetchall())
        c.close()

        for x in nitrate_runs:
            if x in phosphate_runs:
                self.run_list.addItem(str(x[0]))



class generalPlot(QMainPlotterTemplate):
    def __init__(self):
        super().__init__()


        self.show()


class rmnsPlot(QWidget):
    def __init__(self, lot, nutrient, xdata, ydata):
        super().__init__()

        self.lot = lot
        self.nutrient = nutrient
        self.xdata = xdata
        self.ydata = ydata

        self.qvboxlayout = QVBoxLayout()

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.figure.set_facecolor('#f9fcff')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.qvboxlayout.addWidget(self.canvas)
        self.qvboxlayout.addWidget(self.toolbar)
        self.setLayout(self.qvboxlayout)

        self.mainplot = self.figure.add_subplot(111)

        conn = sqlite3.connect('C:/HyPro/Settings/hypro.db')
        c = conn.cursor()
        c.execute('SELECT * from rmnsData')
        rmnsdata = list(c.fetchall())

        lotnames = [x[0] for x in rmnsdata]
        for i, x in enumerate(lotnames):
            if x == self.lot:
                ind = i

        rmns = rmnsdata[ind]

        if self.nutrient == 'silicate':
            rmnsmean = rmns[3]
            rmnsuncertainty = rmns[4]
        if self.nutrient == 'phosphate':
            rmnsmean = rmns[1]
            rmnsuncertainty = rmns[2]
        if self.nutrient == 'nitrate':
            rmnsmean = rmns[5]
            rmnsuncertainty = rmns[6]
        if self.nutrient == 'nitrite':
            rmnsmean = rmns[7]
            rmnsuncertainty = rmns[8]
        if self.nutrient == 'ammonia':
            rmnsmean = rmns[9]
            rmnsuncertainty = rmns[10]

        self.xmin = min(self.xdata) - 1
        self.xmax = max(self.xdata) + 1

        self.mainplot.set_xlim(self.xmin, self.xmax)

        self.mainplot.grid(linewidth=0.5, alpha=0.2)

        self.mainplot.plot((self.xmin, self.xmax), (rmnsmean, rmnsmean), linewidth=1, color='#999da3', linestyle='--')

        if rmnsmean * 0.01 > 0.02:
            self.ymin = rmnsmean * 0.96
            self.ymax = rmnsmean * 1.04

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 0.99, rmnsmean * 0.99), linewidth=1, color='#2baf69')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 1.01, rmnsmean * 1.01), linewidth=1, color='#2baf69')

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 0.98, rmnsmean * 0.98), linewidth=1, color='#c874db')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 1.02, rmnsmean * 1.02), linewidth=1, color='#c874db')

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 0.97, rmnsmean * 0.97), linewidth=1, color='#e56969')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean * 1.03, rmnsmean * 1.03), linewidth=1, color='#e56969')
        else:
            self.ymin = rmnsmean - 0.08
            self.ymax = rmnsmean + 0.08

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean - 0.02, rmnsmean - 0.02), linewidth=1, color='#2baf69')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean + 0.02, rmnsmean + 0.02), linewidth=1, color='#2baf69')

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean - 0.04, rmnsmean - 0.04), linewidth=1, color='#c874db')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean + 0.04, rmnsmean + 0.04), linewidth=1, color='#c874db')

            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean - 0.06, rmnsmean - 0.06), linewidth=1, color='#e56969')
            self.mainplot.plot((self.xmin, self.xmax), (rmnsmean + 0.06, rmnsmean + 0.06), linewidth=1, color='#e56969')

        self.mainplot.set_ylim(self.ymin, self.ymax)

        self.mainplot.plot((self.xmin, self.xmax), (rmnsmean + rmnsuncertainty, rmnsmean + rmnsuncertainty),
                           linewidth=1, color='#6986e5')
        self.mainplot.plot((self.xmin, self.xmax), (rmnsmean - rmnsuncertainty, rmnsmean - rmnsuncertainty),
                           linewidth=1, color='#6986e5')

        self.mainplot.set_title('RMNS %s' % str(self.lot))
        self.mainplot.set_xlabel('Peak Number')
        self.mainplot.set_ylabel('Concentration')

        self.mainplot.plot(self.xdata, self.ydata, mfc='none', linewidth=0.75, linestyle=':', mec="#12ba66",
                           marker='o', markersize=14, color="#25543b")

        self.canvas.draw()



"""
    Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad,
                    91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different
"""

def calibration_curve_plot(style, fig, axes, cal_medians, cal_concs, flags, reproc_count):

    if len(axes.lines) > 0:
        del axes.lines[:]
    else:
        axes.set_title('Calibration Curve')
        axes.set_xlabel('Calibrant Concentrations')
        axes.set_ylabel('A/D Medians')
        axes.grid(alpha=0.4, zorder=1)

    axes.plot(cal_medians, cal_concs, label=reproc_count)
    fig.set_tight_layout(tight=True)

def calibration_error_plot(style, fig, axes, cal, cal_error, analyte_error, flags):

    if len(axes.lines) > 0:
        del axes.lines[1:]
    else:
        axes.set_title('Calibrant Error')
        axes.set_xlabel('Calibrant Concentration')
        axes.set_ylabel('Error from fitted concentration')
        axes.plot([0, max(cal)], [0, 0], lw=1.25, linestyle='--', alpha=0.7, zorder=2, color='#000000')
        axes.grid(alpha=0.4, zorder=1)

    for i, x in enumerate(flags):
        if x == 1:
            colour = "#12ba66"
            size = 6
            mark = 'o'
        if x == 2 or x==4 or x == 91:
            colour = '#63d0ff'
            size = 14
            mark = '+'
        if x == 3 or x == 5 or x == 92:
            colour = "#d11b1b"
            size = 14
            mark = '+'
        try:
            axes.plot(cal[i], cal_error[i], marker=mark, mfc=colour, linewidth=0, markersize=size,
                       color=colour, alpha=0.8)
        except IndexError:
            pass

    axes.plot([0, max(cal)], [analyte_error, analyte_error], color='#5AD3E2', lw=1.25)
    axes.plot([0, max(cal)], [(-1*analyte_error), (-1*analyte_error)], color='#5AD3E2', lw=1.25)

    axes.plot([0, max(cal)], [(2*analyte_error), (2*analyte_error)], color='#C689C8', lw=1.25)
    axes.plot([0, max(cal)], [(-2 * analyte_error), (-2 * analyte_error)], color='#C689C8', lw=1.25)

    fig.set_tight_layout(tight=True)

def basedrift_correction_plot(COLORS, fig, axes1, axes2, type, indexes, correction, medians, flags):
    with mpl.rc_context(rc=COLORS):
        if len(axes1.lines) > 0:
            del axes1.lines[:]
            del axes2.lines[:]
        else:
            axes1.set_title('%s Peak Height' % type)
            axes1.set_xlabel('Peak Number')
            axes1.set_ylabel('Raw Peak Height (A/D)')
            axes1.grid(alpha=0.4, zorder=1)
            axes2.set_title('%s Correction Percentage' % type)
            axes2.set_xlabel('Peak Number')
            axes2.set_ylabel('Percentage of Top Cal (%)')
            axes2.grid(alpha=0.4, zorder=1)

        axes1.plot(indexes, medians, mfc='none', linewidth=1.25, linestyle=':', color="#8C8C8C", alpha=0.9)
        for i, x in enumerate(flags):
            if x == 1:
                colour = "#12ba66"
                size = 14
                mark = 'o'
            elif x == 3:
                colour = '#63d0ff'
                size = 16
                mark = '+'
            elif x == 2:
                colour = "#d11b1b"
                size = 16
                mark = '+'
            else:
                colour = "#d11b1b"
                size = 19
                mark = 'o'
            axes1.plot(indexes[i], medians[i], linewidth=1.25, linestyle=':', mfc='none', mec=colour,
                       marker=mark, markersize=size, color="#25543b")

            axes1.set_ylim(min(medians) * 0.975, max(medians) * 1.025)

        axes2.plot(indexes, correction, lw=1.25, marker='s', ms=8, mfc='none', color='#6986e5')
        fig.set_tight_layout(tight=True)


class calibrationCurve(QWidget):
    def __init__(self, nutrient, caladvals, calconcs, fit, rsq, flags):
        super().__init__()
        deffont = {'fontname': 'Segoe UI'}
        self.nutrient = nutrient
        self.caladvals = caladvals
        self.calconcs = calconcs
        #self.fit = fit
        self.rsq = rsq
        self.flags = flags

        self.qvboxlayout = QVBoxLayout()

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.figure.set_facecolor('#f9fcff')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.qvboxlayout.addWidget(self.canvas)
        self.qvboxlayout.addWidget(self.toolbar)
        self.setLayout(self.qvboxlayout)

        self.mainplot = self.figure.add_subplot(111)

        self.mainplot.set_title('Calibration')
        self.mainplot.set_xlabel('Concentration (uM)')
        self.mainplot.set_ylabel('A/D Value')

        cattle = list(set(self.caladvals))
        #self.mainplot.plot(self.fit(cattle[0:]), cattle[0:], linewidth=0.5, marker='.', color='#292b2d',
        #                   markersize=7, mew=0.5, mec="#295263", mfc='none')

        for i, x in enumerate(self.flags):
            if x == 1:
                colour = "#12ba66"
                size = 14
                mark = 'o'
            if x == 2:
                colour = '#63d0ff'
                size = 16
                mark = '+'
            if x == 3 or x == 6:
                colour = "#d11b1b"
                size = 16
                mark = '+'

            self.mainplot.plot(self.calconcs[i], self.caladvals[i], marker=mark, mfc='none', linewidth=0,
                               markersize=size,
                               color=colour, alpha=0.8)

        self.mainplot.grid(linewidth=0.5, alpha=0.6)

        self.mainplot.text(0.85, 0.1, 'R2:  ' + str(round(self.rsq, 4)), transform=self.mainplot.transAxes)

        self.canvas.draw()


class calibrationError(QWidget):
    def __init__(self, nutrient, cal, calerror, margin, flags):
        super().__init__()
        deffont = {'fontname': 'Segoe UI'}
        self.nutrient = nutrient
        self.cal = cal
        self.calerror = calerror
        self.margin = margin
        self.flags = flags

        self.qvboxlayout = QVBoxLayout()

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.figure.set_facecolor('#f9fcff')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.qvboxlayout.addWidget(self.canvas)
        self.qvboxlayout.addWidget(self.toolbar)
        self.setLayout(self.qvboxlayout)

        self.mainplot = self.figure.add_subplot(111)

        self.mainplot.set_title('Calibration Error')
        self.mainplot.set_xlabel('Peak Number')
        self.mainplot.set_ylabel('Calibration Error (Derived - Standard)')

        self.mainplot.plot([min(self.cal), max(self.cal)], [self.margin, self.margin], linewidth=1, color='#12ba66',
                           alpha=0.8)

        self.mainplot.plot([min(self.cal), max(self.cal)], [self.margin * -1, self.margin * -1], linewidth=1,
                           color='#12ba66', alpha=0.8)

        for i, x in enumerate(self.flags):
            if x == 1:
                colour = "#12ba66"
                size = 6
                mark = 'o'
            if x == 2:
                colour = '#63d0ff'
                size = 14
                mark = '+'
            if x == 3 or x == 6:
                colour = "#d11b1b"
                size = 14
                mark = '+'

            self.mainplot.plot(self.cal[i], self.calerror[i], marker=mark, mfc=colour, linewidth=0,
                               markersize=size,
                               color=colour, alpha=0.8)

        self.mainplot.grid(linewidth=0.5, alpha=0.6)

        self.canvas.draw()


class driftBase(QWidget):
    def __init__(self, indexes, correction, advals, type, flags):
        super().__init__()
        deffont = {'fontname': 'Segoe UI'}

        self.indexes = indexes
        self.correction = correction
        self.advals = advals
        self.type = type
        self.flags = flags

        self.qvboxlayout = QVBoxLayout()

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.figure.set_facecolor('#f9fcff')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.qvboxlayout.addWidget(self.canvas)
        self.qvboxlayout.addWidget(self.toolbar)
        self.setLayout(self.qvboxlayout)

        self.topplot = self.figure.add_subplot(211)

        self.bottomplot = self.figure.add_subplot(212)

        if self.type == 'drift':
            self.topplot.set_title('Drift Peak Heights')
            self.bottomplot.set_title('Drift Correction Percentage')
            self.bottomplot.set_ylabel('Correction Percentage (%)')

        if self.type == 'baseline':
            self.topplot.set_title('Baseline Peak Height')
            self.bottomplot.set_title('Baseline Correction Percentage')
            self.bottomplot.set_ylabel('Percentage of Top Calibrant (%)')

        self.topplot.set_xlabel('Peak Number')
        self.topplot.set_ylabel('Raw Peak Height (A/D Val)')

        self.bottomplot.set_xlabel('Peak Number')

        if indexes:

            peaknums = [x + 1 for x in self.indexes[1:-1]]
            peakheights = [self.advals[x] for x in self.indexes[1:-1]]
            percentcorr = [x * 100 for x in self.correction[1:-1]]
            qflags = [self.flags[x] for x in self.indexes[1:-1]]

            self.topplot.plot(peaknums, peakheights, mfc='none', linewidth=0.75, linestyle=':', color="#25543b",
                              alpha=0.8)

            for i, x in enumerate(qflags):
                if x == 1:
                    colour = "#12ba66"
                    size = 14
                    mark = 'o'
                elif x == 3:
                    colour = '#63d0ff'
                    size = 16
                    mark = '+'
                elif x == 2:
                    colour = "#d11b1b"
                    size = 16
                    mark = '+'
                else:
                    colour = "#d11b1b"
                    size = 19
                    mark = 'o'
                self.topplot.plot(peaknums[i], peakheights[i], mfc='none', linewidth=0.75, linestyle=':', mec=colour,
                                  marker=mark, markersize=size, color="#25543b")

            self.topplot.grid(linewidth=0.5, alpha=0.7)
            self.topplot.set_ylim(min(peakheights) * 0.95, max(peakheights) * 1.05)


            self.bottomplot.plot((-999, 999), (100, 100), color='#12ba66', linewidth=0.75, linestyle=':')

            self.bottomplot.plot(peaknums, percentcorr, color='#6986e5', marker='s', markersize=7, linewidth=0.75,
                                 mfc='none')

            self.bottomplot.grid(linewidth=0.5, alpha=0.7)
            self.bottomplot.set_xlim(0, max(peaknums) + 5)
            self.bottomplot.set_ylim(min(percentcorr) * 0.95, max(percentcorr) * 1.05)

            self.canvas.draw()


class mdlPlot(QWidget):
    def __init__(self, xdata, ydata):
        super().__init__()

        deffont = {'fontname': 'Segoe UI'}

        self.xdata = xdata
        self.ydata = ydata

        self.qvboxlayout = QVBoxLayout()

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.figure.set_facecolor('#f9fcff')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.qvboxlayout.addWidget(self.canvas)
        self.qvboxlayout.addWidget(self.toolbar)
        self.setLayout(self.qvboxlayout)

        self.mainplot = self.figure.add_subplot(111)

        peaknums = [x + 1 for x in self.xdata]

        self.xmin = min(peaknums) - 1
        self.xmax = max(peaknums) + 1

        self.ymin = min(ydata) * 0.5
        self.ymax = max(ydata) * 1.5

        if self.ymin > 0:
            self.ymin = 0

        self.mainplot.set_xlim(self.xmin, self.xmax)
        self.mainplot.set_ylim(self.ymin, self.ymax)

        self.mainplot.grid(linewidth=0.5, alpha=0.2)

        self.mainplot.set_title('MDL')
        self.mainplot.set_xlabel('Peak Number')
        self.mainplot.set_ylabel('Concentration')

        self.mainplot.plot(peaknums, self.ydata, mfc='none', linewidth=0.75, linestyle=':', mec="#12ba66",
                           marker='o', markersize=14, color="#25543b")

        self.canvas.draw()


class saltErrorPlot(QMainWindow):
    def __init__(self, xdata, ydata1, ydata2, maxrp, interactive):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.xdata = xdata
        self.ydata1 = ydata1
        self.ydata2 = ydata2
        self.maxrp = maxrp
        self.interactive = interactive

        self.init_ui()

        self.setStyleSheet(style.stylesheet['normal'])

    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))

            self.setGeometry(0, 0, 600, 870)
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
            self.setWindowModality(QtCore.Qt.ApplicationModal)

            self.setWindowTitle('HyPro - CTD/Bottle Salinity Error')

            self.qvboxlayout = QVBoxLayout()

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Sensor 1 Plot', self)
            exportPlot.triggered.connect(self.exportsens1plot)
            fileMenu.addAction(exportPlot)

            exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Sensor 2 Plot', self)
            exportPlot.triggered.connect(self.exportsens2plot)
            fileMenu.addAction(exportPlot)

            copyPlot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
            copyPlot.triggered.connect(self.copyplot)
            editMenu.addAction(copyPlot)

            self.proceed = QPushButton('Proceed', self)
            self.proceed.clicked.connect(self.proceedprocessing)
            self.proceed.setFixedWidth(180)

            self.tabs = QTabWidget()

            self.sensor1tab = QWidget()
            self.sensor1tab.layout = QVBoxLayout()
            self.tabs.addTab(self.sensor1tab, 'Primary Sensor')

            self.sensor2tab = QWidget()
            self.sensor2tab.layout = QVBoxLayout()
            self.tabs.addTab(self.sensor2tab, 'Secondary Sensor')

            self.bothsenstab = QWidget()
            self.bothsenstab.layout = QVBoxLayout()
            self.tabs.addTab(self.bothsenstab, 'Both Sensors')

            self.sens1figure = plt.figure()
            self.sens1figure.set_tight_layout(tight=True)
            self.sens1canvas = FigureCanvas(self.sens1figure)
            self.sens1canvas.setParent(self)
            # self.sens1toolbar = NavigationToolbar(self.sens1canvas, self)

            self.sensor1tab.layout.addWidget(self.sens1canvas)
            # self.sensor1tab.layout.addWidget(self.sens1toolbar)
            self.sensor1tab.setLayout(self.sensor1tab.layout)

            self.sens2figure = plt.figure()
            self.sens2figure.set_tight_layout(tight=True)
            self.sens2canvas = FigureCanvas(self.sens2figure)
            self.sens2canvas.setParent(self)
            # self.sens2toolbar = NavigationToolbar(self.sens2canvas, self)

            self.sensor2tab.layout.addWidget(self.sens2canvas)
            # self.sensor2tab.layout.addWidget(self.sens2toolbar)
            self.sensor2tab.setLayout(self.sensor2tab.layout)

            self.bothsensfigure = plt.figure()
            self.bothsensfigure.set_tight_layout(tight=True)
            self.bothsenscanvas = FigureCanvas(self.bothsensfigure)
            self.bothsenscanvas.setParent(self)
            self.bothsenstoolbar = NavigationToolbar(self.bothsenscanvas, self)

            self.bothsenstab.layout.addWidget(self.bothsenscanvas)
            self.bothsenstab.layout.addWidget(self.bothsenstoolbar)
            self.bothsenstab.setLayout(self.bothsenstab.layout)

            self.qvboxlayout.addWidget(self.tabs)

            self.qvboxlayout.addWidget(self.proceed, QtCore.Qt.AlignHCenter)

            self.centralWidget().setLayout(self.qvboxlayout)

            self.show()

            sens1plot = self.sens1figure.add_subplot(111)

            sens2plot = self.sens2figure.add_subplot(111)

            bothsensplot = self.bothsensfigure.add_subplot(111)

            # Primary sensor plot
            sens1plot.set_title('Primary Sensor | Salinity Error: CTD - Bottle')
            sens1plot.set_xlabel('Dep/Bottle')
            sens1plot.set_ylabel('Error (CTD - Bottle)')

            sens1plot.plot(self.xdata, self.ydata1, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                           mfc='none', color='#4068ce')
            sens1plot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')
            if max(self.ydata1) < 0:
                sens1plot.set_ylim(-0.01, 0.01)

            sens1plot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)
            sens1plot.grid(color="#0a2b60", alpha=0.1)

            self.sens1canvas.draw()

            labels = sens1plot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 24)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            sens1plot.set_xticklabels(newlabels)

            # Secondary sensor plot
            sens2plot.set_title('Secondary Sensor | Salinity Error: CTD - Bottle')
            sens2plot.set_xlabel('Dep/Bottle')
            sens2plot.set_ylabel('Error (CTD - Bottle)')

            sens2plot.plot(self.xdata, self.ydata2, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                           mfc='none', color='#71ce40')
            sens2plot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')
            if max(self.ydata2) < 0:
                sens2plot.set_ylim(-0.01, 0.01)
            sens2plot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)

            sens2plot.grid(color="#0a2b60", alpha=0.1)

            self.sens2canvas.draw()

            labels = sens2plot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 36)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            sens2plot.set_xticklabels(newlabels)

            # Both sensors plot
            bothsensplot.set_title('Both Sensors | Salinity Error: CTD - Bottle')
            bothsensplot.set_xlabel('Dep/Bottle')
            bothsensplot.set_ylabel('Error (CTD - Bottle)')

            bothsensplot.plot(self.xdata, self.ydata1, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                              mfc='none', color='#4068ce')

            bothsensplot.plot(self.xdata, self.ydata2, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                              mfc='none', color='#71ce40')

            bothsensplot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')
            if max(self.ydata1) < 0:
                bothsensplot.set_ylim(-0.01, 0.01)
            bothsensplot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)

            bothsensplot.grid(color="#0a2b60", alpha=0.1)

            bothsensplot.legend(['Primary Sensor', 'Secondary Sensor'])

            self.bothsenscanvas.draw()

            labels = bothsensplot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 36)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            bothsensplot.set_xticklabels(newlabels)

        except Exception:
            logging.error(traceback.print_exc())

    def exportsens1plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sens1figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def exportsens2plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sens2figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def exportsensduoplot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.bothsensfigure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copyplot(self):
        buffer = io.BytesIO()
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:
            self.sens1figure.savefig(buffer, dpi = 400)
        if current_tab == 1:
            self.sens2figure.savefig(buffer, dpi = 400)
        if current_tab == 2:
            self.bothsensfigure.savefig(buffer, dpi = 400)

        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def proceedprocessing(self):
        self.close()


class oxygenErrorPlot(QMainWindow):
    def __init__(self, xdata, ydata1, ydata2, maxrp, interactive):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.xdata = xdata
        self.ydata1 = ydata1
        self.ydata2 = ydata2
        self.maxrp = maxrp
        self.interactive = interactive

        self.init_ui()

        self.setStyleSheet(style.stylesheet['normal'])

    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))

            self.setGeometry(0, 0, 600, 870)
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
            self.setWindowModality(QtCore.Qt.ApplicationModal)

            self.setWindowTitle('HyPro - CTD/Bottle Oxygen Error')

            self.qvboxlayout = QVBoxLayout()

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            exportPlot1 = QAction(QIcon(':/assets/archivebox.svg'), 'Export Sensor 1 Plot', self)
            exportPlot1.triggered.connect(self.exportsens1plot)
            fileMenu.addAction(exportPlot1)

            exportPlot2 = QAction(QIcon(':/assets/archivebox2.svg'), 'Export Sensor 2 Plot', self)
            exportPlot2.triggered.connect(self.exportsens2plot)
            fileMenu.addAction(exportPlot2)

            exportPlotDuo = QAction('Export Both Sensor Plot', self)
            exportPlotDuo.triggered.connect(self.exportsensduoplot)
            fileMenu.addAction(exportPlotDuo)

            copyPlot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
            copyPlot.triggered.connect(self.copyplot)
            editMenu.addAction(copyPlot)

            self.proceed = QPushButton('Proceed', self)
            self.proceed.clicked.connect(self.proceedprocessing)
            self.proceed.setFixedWidth(180)

            self.tabs = QTabWidget()

            self.sensor1tab = QWidget()
            self.sensor1tab.layout = QVBoxLayout()
            self.tabs.addTab(self.sensor1tab, 'Primary Sensor')

            self.sensor2tab = QWidget()
            self.sensor2tab.layout = QVBoxLayout()
            self.tabs.addTab(self.sensor2tab, 'Secondary Sensor')

            self.bothsenstab = QWidget()
            self.bothsenstab.layout = QVBoxLayout()
            self.tabs.addTab(self.bothsenstab, 'Both Sensors')

            self.sens1figure = plt.figure()
            self.sens1figure.set_tight_layout(tight=True)
            self.sens1canvas = FigureCanvas(self.sens1figure)
            self.sens1canvas.setParent(self)
            # self.sens1toolbar = NavigationToolbar(self.sens1canvas, self)

            self.sensor1tab.layout.addWidget(self.sens1canvas)
            # self.sensor1tab.layout.addWidget(self.sens1toolbar)
            self.sensor1tab.setLayout(self.sensor1tab.layout)

            self.sens2figure = plt.figure()
            self.sens2figure.set_tight_layout(tight=True)
            self.sens2canvas = FigureCanvas(self.sens2figure)
            self.sens2canvas.setParent(self)
            # self.sens2toolbar = NavigationToolbar(self.sens2canvas, self)

            self.sensor2tab.layout.addWidget(self.sens2canvas)
            # self.sensor2tab.layout.addWidget(self.sens2toolbar)
            self.sensor2tab.setLayout(self.sensor2tab.layout)

            self.bothsensfigure = plt.figure()
            self.bothsensfigure.set_tight_layout(tight=True)
            self.bothsenscanvas = FigureCanvas(self.bothsensfigure)
            self.bothsenscanvas.setParent(self)
            self.bothsenstoolbar = NavigationToolbar(self.bothsenscanvas, self)

            self.bothsenstab.layout.addWidget(self.bothsenscanvas)
            self.bothsenstab.layout.addWidget(self.bothsenstoolbar)
            self.bothsenstab.setLayout(self.bothsenstab.layout)

            self.qvboxlayout.addWidget(self.tabs)

            self.qvboxlayout.addWidget(self.proceed, QtCore.Qt.AlignHCenter)

            self.centralWidget().setLayout(self.qvboxlayout)

            self.show()

            sens1plot = self.sens1figure.add_subplot(111)

            sens2plot = self.sens2figure.add_subplot(111)

            bothsensplot = self.bothsensfigure.add_subplot(111)

            # Primary sensor plot
            sens1plot.set_title('Primary Sensor | Oxygen Error: CTD - Bottle')
            sens1plot.set_xlabel('Dep/Bottle')
            sens1plot.set_ylabel('Error (CTD - Bottle)')

            sens1plot.plot(self.xdata, self.ydata1, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                           mfc='none', color='#4068ce')
            sens1plot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')

            #if max(self.ydata1) < 0:
            #    sens1plot.set_ylim(-0.01, 0.01)

            sens1plot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)
            sens1plot.grid(color="#0a2b60", alpha=0.1)

            self.sens1canvas.draw()

            labels = sens1plot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 24)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            sens1plot.set_xticklabels(newlabels)

            # Secondary sensor plot
            sens2plot.set_title('Secondary Sensor | Oxygen Error: CTD - Bottle')
            sens2plot.set_xlabel('Dep/Bottle')
            sens2plot.set_ylabel('Error (CTD - Bottle)')

            sens2plot.plot(self.xdata, self.ydata2, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                           mfc='none', color='#71ce40')
            sens2plot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')

            #if max(self.ydata2) < 0:
            #    sens2plot.set_ylim(-0.01, 0.01)

            sens2plot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)

            sens2plot.grid(color="#0a2b60", alpha=0.1)

            self.sens2canvas.draw()

            labels = sens2plot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 36)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            sens2plot.set_xticklabels(newlabels)

            # Both sensors plot
            bothsensplot.set_title('Both Sensors | Oxygen Error: CTD - Bottle')
            bothsensplot.set_xlabel('Dep/Bottle')
            bothsensplot.set_ylabel('Error (CTD - Bottle)')

            bothsensplot.plot(self.xdata, self.ydata1, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                              mfc='none', color='#4068ce')

            bothsensplot.plot(self.xdata, self.ydata2, linewidth=0.75, linestyle=':', marker='o', markersize=13,
                              mfc='none', color='#71ce40')

            bothsensplot.plot([-9999, 9999], [0, 0], linewidth=1, linestyle='--', color='#a0a0a0')
            #if max(self.ydata1) < 0:
            #    bothsensplot.set_ylim(-0.01, 0.01)

            bothsensplot.set_xlim(min(self.xdata) - 0.1, max(self.xdata) + 0.1)

            bothsensplot.grid(color="#0a2b60", alpha=0.1)

            bothsensplot.legend(['Primary Sensor', 'Secondary Sensor'])

            self.bothsenscanvas.draw()

            labels = bothsensplot.get_xticks().tolist()
            newlabels = []
            for x in labels:
                rpfraction = x % 1
                rp = int(rpfraction * 36)
                newlabel = str(int(x)) + '/' + str(rp)
                newlabels.append(newlabel)
            bothsensplot.set_xticklabels(newlabels)

        except Exception:
            logging.error(traceback.print_exc())

    def exportsens1plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sens1figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def exportsens2plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sens2figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def exportsensduoplot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.bothsensfigure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copyplot(self):
        buffer = io.BytesIO()
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:
            self.sens1figure.savefig(buffer, dpi = 400)
        if current_tab == 1:
            self.sens2figure.savefig(buffer, dpi = 400)
        if current_tab == 2:
            self.bothsensfigure.savefig(buffer, dpi = 400)

        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def proceedprocessing(self):
        self.close()


class rmnsPlotWindow(QMainWindow):
    def __init__(self, project, path, database):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.currproject = project

        self.currpath = path

        self.database = database

        self.nutconverter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                             'Ammonia': 'ammonia'}

        self.rmnscols = {'NOx': 5, 'Phosphate': 1, 'Silicate': 3, 'Nitrite': 7, 'Ammonia': 9}

        self.init_ui()
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                self.params = json.loads(file.read())
        except Exception:
            logging.error("Can't find parameters file")

        self.populatermns()

        self.setStyleSheet("""
            QLabel {
                font: 14px;
            }
            QListWidget {
                font: 14px;
            }
            QPushButton {
                font: 13px;
            }
            QComboBox {
                font: 13px;
            }
            QCheckBox {
                font: 14px;
            }
                            """)

    def init_ui(self):
        try:
            deffont = QFont('Segoe UI')
            self.setGeometry(0, 0, 780, 820)
            self.setFont(deffont)
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())

            self.setWindowTitle('HyPro - RMNS')

            self.gridlayout = QGridLayout()
            self.qvboxlayout = QVBoxLayout()

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Plot', self)
            exportPlot.triggered.connect(self.exportplot)
            fileMenu.addAction(exportPlot)

            copyPlot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
            copyPlot.triggered.connect(self.copyplot)
            editMenu.addAction(copyPlot)

            self.figure = plt.figure()
            self.figure.set_tight_layout(tight=True)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setParent(self)

            nutrientlabel = QLabel('Nutrient', self)
            self.nutrient = QComboBox(self)
            self.nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])
            self.nutrient.currentIndexChanged.connect(self.populatermns)

            rmnstypelabel = QLabel('RMNS Lot', self)
            self.rmnstype = QComboBox(self)
            self.rmnstype.currentIndexChanged.connect(self.populaterunlist)

            runlistlabel = QLabel('Select Run:', self)
            self.runlist = QListWidget(self)
            self.runlist.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.runlist.setMaximumWidth(120)

            self.showbaddata = QCheckBox('Show bad data', self)

            self.markbaddata = QCheckBox('Mark bad data', self)

            self.applybutton = QPushButton('Apply', self)
            self.applybutton.clicked.connect(self.apply)

            self.gridlayout.addWidget(self.canvas, 0, 1)
            self.gridlayout.addLayout(self.qvboxlayout, 0, 0)

            self.qvboxlayout.addWidget(nutrientlabel)
            self.qvboxlayout.addWidget(self.nutrient)

            self.qvboxlayout.addWidget(rmnstypelabel)
            self.qvboxlayout.addWidget(self.rmnstype)

            self.qvboxlayout.addWidget(runlistlabel)
            self.qvboxlayout.addWidget(self.runlist)

            self.qvboxlayout.addWidget(self.showbaddata)
            self.qvboxlayout.addWidget(self.markbaddata)

            self.qvboxlayout.addWidget(self.applybutton)

            self.centralWidget().setLayout(self.gridlayout)

            self.mainplot = self.figure.add_subplot(111)

            self.mainplot.set_title('RMNS', fontsize=18)
            self.mainplot.set_xlabel('Analysis', fontsize=15)
            self.mainplot.set_ylabel('Concentration (uM)', fontsize=15)

            for x in self.mainplot.get_xticklabels():
                x.set_fontsize(12)
            for y in self.mainplot.get_yticklabels():
                y.set_fontsize(12)

            self.mainplot.grid(alpha=0.1)

            self.canvas.draw()

            clicker = self.figure.canvas.mpl_connect("button_press_event", self.on_click)

        except Exception:
            print(traceback.print_exc())

    def populatermns(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nutconverter[nut]
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()
            rmnsnamelength = len(self.params['nutrientprocessing']['qcsamplenames']['rmns'])
            listofrmns = []
            for i, x in enumerate(data):
                if x[1][:rmnsnamelength] == self.params['nutrientprocessing']['qcsamplenames']['rmns']:
                    listofrmns.append(x)
            rmnslots = set([x[1][rmnsnamelength:(rmnsnamelength + 3)] for x in listofrmns])

            self.rmnstype.clear()
            self.rmnstype.addItems(rmnslots)


        except Exception:
            print(traceback.print_exc())

    def populaterunlist(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nutconverter[nut]
            rmns = self.rmnstype.currentText()

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()

            runnums = []
            for i, x in enumerate(data):
                if rmns in x[1]:
                    runnums.append(x[0])

            self.runlist.clear()
            rn = sorted(list(set(runnums)))
            for x in rn:
                self.runlist.addItem(str(x))


        except Exception:
            print(traceback.print_exc())

    def apply(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nutconverter[nut]
            rmns = self.rmnstype.currentText()
            selected = self.runlist.selectedItems()
            selectedruns = [item.text() for item in selected]

            queryq = '?'
            queryplaceruns = ', '.join(queryq for unused in selectedruns)
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                'SELECT peakNumber, runNumber, sampleID, concentration FROM %sData WHERE runNumber IN (%s)' % (
                    nutq, queryplaceruns), (selectedruns))
            data = list(c.fetchall())
            c.close()

            self.runs = []
            self.conctoplot = []
            self.peaknums = []
            sampleid = []
            for x in data:
                if rmns in x[2]:
                    self.peaknums.append(x[0])
                    self.runs.append(x[1])
                    sampleid.append(x[2])
                    self.conctoplot.append(x[3])

            runpeaknumhold = []
            self.runpeaknumtoplot = []
            runs = sorted(set(self.runs))

            for x in runs:
                runpeaknumhold.append(self.runs.count(x))

            for i, x in enumerate(runpeaknumhold):
                for y in range(x):
                    if y > 0:
                        self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                    else:
                        self.runpeaknumtoplot.append(runs[i])

            self.plotit(self.runpeaknumtoplot, self.conctoplot, rmns)

        except Exception:
            print(traceback.print_exc())

    def plotit(self, xdata, ydata, rmnstype):
        try:
            deffont = {'fontname': 'Segoe UI'}
            conn = sqlite3.connect('C:/HyPro/Settings/hypro.db')
            c = conn.cursor()
            c.execute('SELECT * FROM rmnsData')
            data = list(c.fetchall())
            c.close()

            currentrmns = [x for x in data if x[0] in self.rmnstype.currentText()]

            nut = self.nutrient.currentText()
            rmnscertvalue = currentrmns[0][self.rmnscols[nut]]
            rmnsuncertainty = currentrmns[0][self.rmnscols[nut] + 1]

            self.mainplot.clear()

            self.mainplot.plot((-999, 999), (rmnscertvalue, rmnscertvalue), linewidth=0.5, linestyle=':', alpha=0.9,
                               color='#585a5e')
            self.mainplot.plot((-999, 999), (rmnscertvalue + rmnsuncertainty, rmnscertvalue + rmnsuncertainty),
                               linewidth=0.75, alpha=0.9, color='#4286f4')
            self.mainplot.plot((-999, 999), (rmnscertvalue - rmnsuncertainty, rmnscertvalue - rmnsuncertainty),
                               linewidth=0.75, alpha=0.9, color='#4286f4')

            if rmnscertvalue * 0.01 > 0.02:
                self.mainplot.plot((-999, 999), (rmnscertvalue * 1.01, rmnscertvalue * 1.01), linewidth=0.75, alpha=0.9,
                                   color='#2baf69')
                self.mainplot.plot((-999, 999), (rmnscertvalue * 0.99, rmnscertvalue * 0.99), linewidth=0.75, alpha=0.9,
                                   color='#2baf69')

                self.mainplot.plot((-999, 999), (rmnscertvalue * 1.02, rmnscertvalue * 1.02), linewidth=0.75, alpha=0.9,
                                   color='#c874db')
                self.mainplot.plot((-999, 999), (rmnscertvalue * 0.98, rmnscertvalue * 0.98), linewidth=0.75, alpha=0.9,
                                   color='#c874db')

                self.mainplot.plot((-999, 999), (rmnscertvalue * 1.03, rmnscertvalue * 1.03), linewidth=0.75, alpha=0.8,
                                   color='#e56969')
                self.mainplot.plot((-999, 999), (rmnscertvalue * 0.97, rmnscertvalue * 0.97), linewidth=0.75, alpha=0.8,
                                   color='#e56969')

            else:
                self.mainplot.plot((-999, 999), (rmnscertvalue + 0.02, rmnscertvalue + 0.02), linewidth=0.75, alpha=0.9,
                                   color='#2baf69')
                self.mainplot.plot((-999, 999), (rmnscertvalue - 0.02, rmnscertvalue - 0.02), linewidth=0.75, alpha=0.9,
                                   color='#2baf69')

                self.mainplot.plot((-999, 999), (rmnscertvalue + 0.04, rmnscertvalue + 0.04), linewidth=0.75, alpha=0.9,
                                   color='#c874db')
                self.mainplot.plot((-999, 999), (rmnscertvalue - 0.04, rmnscertvalue - 0.04), linewidth=0.75, alpha=0.9,
                                   color='#c874db')

                self.mainplot.plot((-999, 999), (rmnscertvalue + 0.06, rmnscertvalue + 0.06), linewidth=0.75, alpha=0.8,
                                   color='#e56969')
                self.mainplot.plot((-999, 999), (rmnscertvalue - 0.06, rmnscertvalue - 0.06), linewidth=0.75, alpha=0.8,
                                   color='#e56969')

            self.mainplot.set_xlim(min(xdata) - 1, max(xdata) + 1)

            self.mainplot.set_title(
                str(self.nutrient.currentText()) + ' RMNS: ' + str(rmnstype) + ' (' + str(rmnscertvalue) + ' ± ' + str(
                    rmnsuncertainty) + 'µM' + ')', fontsize=18)

            self.mainplot.text(0.05, 0.97, 'Measured Mean: ' + str(round(statistics.mean(ydata), 4)) + 'µM',
                               transform=self.mainplot.transAxes)
            self.mainplot.text(0.05, 0.93,
                               'Measured Standard Deviation: ' + str(round(statistics.stdev(ydata), 4)) + 'µM',
                               transform=self.mainplot.transAxes)

            self.mainplot.set_xlabel('Analysis', fontsize=15)
            self.mainplot.xaxis.set_major_locator(MaxNLocator(integer=True))
            self.mainplot.set_ylabel('Concentration (µM)', fontsize=15)

            self.mainplot.grid(alpha=0.1)
            for x in self.mainplot.get_xticklabels():
                x.set_fontsize(12)
            for y in self.mainplot.get_yticklabels():
                y.set_fontsize(12)

            self.mainplot.plot(xdata, ydata, linewidth=.25, linestyle=':', marker='o', markersize=13, mfc='none',
                               mec="#12ba66", color="#25543b")

            self.canvas.draw()

        except Exception:
            print(traceback.print_exc())

    def exportplot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copyplot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=400)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            xaxis = event.xdata
            yaxis = event.ydata
            self.matchclicktopeak(xaxis, yaxis)

    def matchclicktopeak(self, xval, yval):
        found = False
        for i, x in enumerate(self.runpeaknumtoplot):
            if abs(x - xval) < 0.09: # Check x coords to where was clicked
                if abs(self.conctoplot[i] - yval) < 0.008: # Check y coords to where was clicked if less than threshold
                                                           # then pick this peak
                    runnum = self.runs[i]
                    peaknum = self.peaknums[i]
                    found = True
                    break  # Break here because we've found the peak

        if found:  # Complete rest of function because we've found a peak, pull up the peaks information
            nutq = self.nutconverter[self.nutrient.currentText()]
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                'SELECT sampleID, cupType, correctedAD, concentration, flag, dilution '
                'FROM %sData WHERE runNumber=? AND peakNumber=?' % nutq, (runnum, peaknum))
            data = list(c.fetchall())
            c.close()
            # Display the peak information dialog, no point assigning variables just pull from data call of db
            # aka  in SampleID, CupType, CorrAD, Conc, Flag, Dilution, PlotType
            self.selection = traceSelection(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][5],
                                            'Plot')
            self.selection.show()


class mdlPlotWindow(QMainWindow):
    def __init__(self, project, path, database):

        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.currproject = project

        self.currpath = path

        self.database = database

        self.nutconverter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                             'Ammonia': 'ammonia'}

        self.init_ui()
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                self.params = json.loads(file.read())
        except Exception:
            logging.error("Can't find parameters file")

        self.populaterunlist()

        self.setStyleSheet("""
            QLabel {
                font: 14px;
            }
            QListWidget {
                font: 14px;
            }
            QPushButton {
                font: 13px;
            }
            QComboBox {
                font: 13px;
            }
            QCheckBox {
                font: 14px;
            }
                            """)

    def init_ui(self):
        try:
            deffont = QFont('Segoe UI')
            self.setGeometry(0, 0, 780, 820)
            self.setFont(deffont)
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())

            self.setFont(deffont)

            self.setWindowTitle('HyPro - MDL')

            self.gridlayout = QGridLayout()
            self.qvboxlayout = QVBoxLayout()

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Plot', self)
            exportPlot.triggered.connect(self.exportplot)
            fileMenu.addAction(exportPlot)

            copyPlot = QAction('Copy', self)
            copyPlot.triggered.connect(self.copyplot)
            editMenu.addAction(copyPlot)

            self.figure = plt.figure()
            self.figure.set_tight_layout(tight=True)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setParent(self)

            nutrientlabel = QLabel('Nutrient', self)
            self.nutrient = QComboBox(self)
            self.nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])
            self.nutrient.currentIndexChanged.connect(self.populaterunlist)

            runlistlabel = QLabel('Select Run:', self)
            self.runlist = QListWidget(self)
            self.runlist.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.runlist.setMaximumWidth(120)

            self.showbaddata = QCheckBox('Show bad data', self)

            self.markbaddata = QCheckBox('Mark bad data', self)

            self.applybutton = QPushButton('Apply', self)
            self.applybutton.clicked.connect(self.apply)

            self.gridlayout.addWidget(self.canvas, 0, 1)
            self.gridlayout.addLayout(self.qvboxlayout, 0, 0)

            self.qvboxlayout.addWidget(nutrientlabel)
            self.qvboxlayout.addWidget(self.nutrient)

            self.qvboxlayout.addWidget(runlistlabel)
            self.qvboxlayout.addWidget(self.runlist)

            self.qvboxlayout.addWidget(self.showbaddata)
            self.qvboxlayout.addWidget(self.markbaddata)

            self.qvboxlayout.addWidget(self.applybutton)

            self.centralWidget().setLayout(self.gridlayout)

            self.mainplot = self.figure.add_subplot(111)

            self.secondaryplot = self.mainplot.twinx()

            self.mainplot.set_title('MDL', fontsize=18)

            self.mainplot.set_xlabel('Analysis', fontsize=15)
            self.mainplot.set_ylabel('Concentration (uM)', fontsize=15)

            for x in self.mainplot.get_xticklabels():
                x.set_fontsize(12)
            for y in self.mainplot.get_yticklabels():
                y.set_fontsize(12)

            self.mainplot.grid(alpha=0.1)

            self.canvas.draw()

            clicker = self.figure.canvas.mpl_connect("button_press_event", self.on_click)


        except Exception:
            print(traceback.print_exc())

    def populaterunlist(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nutconverter[nut]

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()

            mdl = self.params['nutrientprocessing']['qcsamplenames']['mdl']
            runnums = []
            for i, x in enumerate(data):
                if mdl in x[1]:
                    runnums.append(x[0])

            self.runlist.clear()
            rn = sorted(list(set(runnums)))
            for x in rn:
                self.runlist.addItem(str(x))


        except Exception:
            print(traceback.print_exc())

    def apply(self):

        nut = self.nutrient.currentText()
        nutq = self.nutconverter[nut]
        selected = self.runlist.selectedItems()
        selectedruns = [item.text() for item in selected]

        mdl = self.params['nutrientprocessing']['qcsamplenames']['mdl']

        queryq = '?'
        queryplaceruns = ', '.join(queryq for unused in selectedruns)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute(
            'SELECT peakNumber, runNumber, sampleID, concentration FROM %sData WHERE runNumber IN (%s)' % (
                nutq, queryplaceruns), (selectedruns))
        data = list(c.fetchall())
        c.close()

        self.runs = []
        self.conctoplot = []
        self.peaknums = []
        sampleid = []
        for x in data:
            if mdl in x[2]:
                self.peaknums.append(x[0])
                self.runs.append(x[1])
                sampleid.append(x[2])
                self.conctoplot.append(x[3])

        runpeaknumhold = []
        self.runpeaknumtoplot = []
        runs = sorted(set(self.runs))

        stdevs = []
        for x in runs:
            conchold = []
            for i, y in enumerate(self.runs):
                if x == y:
                    conchold.append(self.conctoplot[i])
            stdevs.append(statistics.stdev(conchold))

            runpeaknumhold.append(self.runs.count(x))

        for i, x in enumerate(runpeaknumhold):
            for y in range(x):
                if y > 0:
                    self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                else:
                    self.runpeaknumtoplot.append(runs[i])

        self.plotit(self.runpeaknumtoplot, self.conctoplot, runs, stdevs)

    def plotit(self, xdata, ydata, x2data, y2data):
        try:
            deffont = {'fontname': 'Segoe UI'}

            nut = self.nutrient.currentText()

            self.mainplot.clear()
            self.secondaryplot.clear()

            self.mainplot.text(0.05, 0.97, 'Measured Mean: ' + str(round(statistics.mean(ydata), 4)) + 'µM',
                               transform=self.mainplot.transAxes)
            self.mainplot.text(0.05, 0.93,
                               'Measured Standard Deviation: ' + str(round(statistics.stdev(ydata), 4)) + 'µM',
                               transform=self.mainplot.transAxes)

            self.mainplot.set_title(
                str(self.nutrient.currentText()) + ': MDL (µM)', fontsize=18)

            self.mainplot.set_xlabel('Analysis', fontsize=15)
            self.mainplot.xaxis.set_major_locator(MaxNLocator(integer=True))
            self.mainplot.set_ylabel('Concentration (µM)', fontsize=15)

            self.mainplot.set_xlim(min(xdata) - 1, max(xdata) + 1)

            self.mainplot.grid(alpha=0.1)
            for x in self.mainplot.get_xticklabels():
                x.set_fontsize(12)
            for y in self.mainplot.get_yticklabels():
                y.set_fontsize(12)
            for y in self.secondaryplot.get_yticklabels():
                y.set_fontsize(12)

            self.mainplot.plot((-999, 999), (statistics.mean(ydata), statistics.mean(ydata)), linewidth=0.5,
                               linestyle='--', color='#4286f4')

            self.mainplot.plot((-999, 999), ((statistics.stdev(ydata) * 2) + statistics.mean(ydata),
                                             (statistics.stdev(ydata) * 2) + statistics.mean(ydata)), linewidth=0.5,
                               color='#2baf69')

            self.mainplot.plot((-999, 999), (statistics.mean(ydata) - (statistics.stdev(ydata) * 2),
                                             (statistics.mean(ydata) - statistics.stdev(ydata) * 2)), linewidth=0.5,
                               color='#2baf69')

            self.secondaryplot.plot(x2data, y2data, linewidth=0, marker='s', markersize=5, mec='#949fb2', mfc='#949fb2',
                                    alpha=0.8)
            self.secondaryplot.set_ylabel('Standard Deviation per Run (µM)', fontsize=12)

            self.mainplot.plot(xdata, ydata, linewidth=.25, linestyle=':', marker='o', markersize=13, mfc='none',
                               mec="#12ba66", color="#25543b")

            self.canvas.draw()

        except Exception:
            print(traceback.print_exc())

    def exportplot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copyplot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=400)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            xaxis = event.xdata
            yaxis = event.ydata
            print(xaxis)
            print(yaxis)
            self.matchclicktopeak(xaxis, yaxis)

    def matchclicktopeak(self, xval, yval):
        found = False
        for i, x in enumerate(self.runpeaknumtoplot):
            if abs(x - xval) < 0.09:
                if abs(self.conctoplot[i] - yval) < 0.008:
                    runnum = self.runs[i]
                    peaknum = self.peaknums[i]
                    found = True
                    break  # Break here because we've found the peak
        if found:  # Complete rest of function because we've found a peak
            nutq = self.nutconverter[self.nutrient.currentText()]
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                'SELECT sampleID, cupType, correctedAD, concentration, flag, dilution '
                'FROM %sData WHERE runNumber=? AND peakNumber=?' % nutq, (runnum, peaknum))
            data = list(c.fetchall())
            c.close()
            # Display the peak information dialog, no point assigning variables just pull from data call of db
            # aka  in SampleID, CupType, CorrAD, Conc, Flag, Dilution, PlotType
            self.selection = traceSelection(data[0][0], data[0][1], data[0][2], data[0][3], data[0][4], data[0][5],
                                            'Plot')
            self.selection.show()


class redfieldPlot2(QMainWindow):
    def __init__(self, project, path, database):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.currproject = project

        self.currpath = path

        self.database = database

        self.init_ui()

        self.populaterunlist()

        self.setStyleSheet("""
            QLabel {
                font: 14px;
            }
            QListWidget {
                font: 14px;
            }
            QPushButton {
                font: 13px;
            }
            QComboBox {
                font: 13px;
            }
            QCheckBox {
                font: 14px;
            }
                            """)

        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                self.params = json.loads(file.read())
        except Exception:
            logging.error("Can't find parameters file")

    def init_ui(self):

        deffont = QFont('Segoe UI')
        self.setGeometry(0, 0, 780, 820)
        self.setFont(deffont)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setFont(deffont)

        self.setWindowTitle('HyPro - Redfield Ratio')

        self.gridlayout = QGridLayout()
        self.qvboxlayout = QVBoxLayout()

        # *************** Menu bar ************************

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')

        exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Plot', self)
        exportPlot.triggered.connect(self.exportplot)
        fileMenu.addAction(exportPlot)

        copyPlot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
        copyPlot.triggered.connect(self.copyplot)
        editMenu.addAction(copyPlot)

        # *************** UI elements in window created ************************

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        runlistlabel = QLabel('Select Run:', self)
        self.runlist = QListWidget(self)
        self.runlist.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.runlist.setMaximumWidth(120)

        self.showbaddata = QCheckBox('Show bad data', self)

        self.markbaddata = QCheckBox('Mark bad data', self)

        self.applybutton = QPushButton('Apply', self)
        self.applybutton.clicked.connect(self.apply)

        # *************** Position elements in layouts ************************

        self.gridlayout.addWidget(self.canvas, 0, 1)
        self.gridlayout.addLayout(self.qvboxlayout, 0, 0)

        self.qvboxlayout.addWidget(runlistlabel)
        self.qvboxlayout.addWidget(self.runlist)

        self.qvboxlayout.addWidget(self.showbaddata)
        self.qvboxlayout.addWidget(self.markbaddata)

        self.qvboxlayout.addWidget(self.applybutton)

        self.centralWidget().setLayout(self.gridlayout)

        # *************** Make up plot ************************

        self.mainplot = self.figure.add_subplot(111)

        self.mainplot.set_title('Redfield Ratio', fontsize=18)
        self.mainplot.set_xlabel('[NOx] (uM)', fontsize=15)
        self.mainplot.set_ylabel('[Phosphate] (uM)', fontsize=15)

        for x in self.mainplot.get_xticklabels():
            x.set_fontsize(12)
        for y in self.mainplot.get_yticklabels():
            y.set_fontsize(12)

        self.mainplot.grid(alpha=0.1)

        self.canvas.draw()

    def populaterunlist(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('SELECT runNumber FROM nitrateData')
        data = list(c.fetchall())
        c.close()

        sorted_run_numbers = sorted(list(set(data)))
        for x in sorted_run_numbers:
            self.runlist.addItem(str(x[0]))

    def apply(self):
        selected = self.runlist.selectedItems()
        selected_runs = [item.text() for item in selected]
        print(selected_runs)

    def exportplot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copyplot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=400)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))