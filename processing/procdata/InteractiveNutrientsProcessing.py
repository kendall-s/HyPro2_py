from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QGridLayout, QCheckBox, QFrame, QVBoxLayout,
                             QMainWindow, QTabWidget, QDesktopWidget, QApplication)
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import *
import processing.plotting.QCPlots as qcp
import sys, logging, traceback
import hyproicons
import processing.procdata.ProcessSealNutrients as psn
import processing.readdata.ReadSealNutrients as rsn
from processing.algo.HyproComplexities import load_proc_settings, match_click_to_peak, determineSurvey
from dialogs.TraceSelectionDialog import traceSelection
from processing.algo.Structures import WorkingData
from threading import Thread
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate

#background-color: #ededed;

# TODO: Finish new implementation of cleaned up testable Nutrients
# TODO: clean up style sheet, move across into style file
# TODO: Shift some of the calculative parts into the processnutrients script. Keep this slim and focused on GUI proc

class processingNutrientsWindow(hyproMainWindowTemplate):

    """
    Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad,
                    91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different


    """

    def __init__(self, file, database, path, project, interactive=True, rereading=''):
        screenwidth = QDesktopWidget().availableGeometry().width()
        screenheight = QDesktopWidget().availableGeometry().height()
        super().__init__((screenwidth - (screenwidth * 0.1)), (screenheight - (screenheight * 0.1)),
                         'HyPro - Process Nutrient Analysis')

        self.FLAG_COLORS = {1: '#68C968', 2: '#3CB6C9', 3: '#C92724', 4:'#3CB6C9', 5: '#C92724', 6: '#C9852B'}

        self.processing_parameters = load_proc_settings(path, project)

        self.file_path = path + '/' + 'Nutrients' + '/' + file
        self.path = path
        self.project = project
        self.database = database


        self.w_d = WorkingData(file)

        self.slk_data, self.chd_data, self.w_d, self.current_nutrient = rsn.get_data_routine(self.file_path,
                                                                                             self.w_d,
                                                                                             self.processing_parameters,
                                                                                             self.database)

        self.w_d = psn.processing_routine(self.slk_data, self.w_d, self.processing_parameters, self.current_nutrient)

        if interactive:
            self.init_ui()

            thread = Thread(target=self.draw_data, args=(self.chd_data, self.w_d, self.current_nutrient))
            thread.start()
            thread.join()

            self.setStyleSheet("""
    
                 QMainWindow {
                     background-color: #ebeff2;
                     border: 0px solid #bababa;   
                 }
                 QLabel {
                     font: 14px;
                 }
                 QLabel[hidetheme=true] {
                     color: #fefefe;
                 }
                 QListWidget {
                     font: 14px;
                 }
                 QPushButton {
                     font: 14px;
                 }
                 QPushButton[icons=true] {
                     color: #222222;
                     border: 1px solid #ededed;
                     border-radius: 5px;
                     font: 15px;   
                 }
                 QPushButton[icons=true]:hover {
                     color: #222222;
                     border: 2px solid #C7E6FF;
                     background: #E0F0FF;
                     font: 15px;
                 }
                 QPushButton[icons=true]:pressed{
                     border: 1px solid #8f98a8;
                     color: #222222;
                     background-color: #78C6FF;
                     font: 15px;
                     border-style: inset;
                 }
                 QPushButton[clear=true] {
                     background-color: #fefefe;
                 }
                 QTabWidget QWidget {
                     font: 14px;
                     border: 0px;
                     background-color: #f9fcff;
                 }
                 QCheckBox {
                     font: 13px;
                 }
                 QFrame[dashboardframe=true] {
                     background-color: #f9fcff;
                 }
                 QFrame[dashboardframe2=true] {
                     background-color: #f9fcff;
                     padding: 20px;
                 }
                 QFrame[headerframe=true]{
                     background-color: #ddeaff;
                 }
                 QFrame[buttonsframe=true] {
                     background-color: #f9fcff;
                     border: 1px solid #ddeaff;
                     border-radius: 3px;
                     
                 }
                 QLabel[headertext=true]{
                     color: #222222;
                     font: 18px;
                     font-weight: bold;  
                 }
                                 """)
        else:
            sys.exit()


    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))
            self.setWindowModality(QtCore.Qt.WindowModal)

            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            self.analysistraceLabel = QLabel('Analysis Trace:')
            self.analysistraceLabel.setProperty('headertext', True)

            tracelabelframe = QFrame()
            tracelabelframe.setProperty('headerframe', True)
            tracelabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            tracelabelframeshadow.setBlurRadius(6)
            tracelabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            tracelabelframeshadow.setYOffset(2)
            tracelabelframeshadow.setXOffset(3)
            tracelabelframe.setGraphicsEffect(tracelabelframeshadow)

            traceframe = QFrame()
            traceframe.setProperty('dashboardframe', True)
            traceframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            traceframeshadow.setBlurRadius(6)
            traceframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            traceframeshadow.setYOffset(2)
            traceframeshadow.setXOffset(3)
            traceframe.setGraphicsEffect(traceframeshadow)

            self.qctabsLabel = QLabel('QC Charts:',)
            self.qctabsLabel.setProperty('headertext', True)

            qclabelframe = QFrame()
            qclabelframe.setProperty('headerframe', True)
            qclabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qclabelframeshadow.setBlurRadius(6)
            qclabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qclabelframeshadow.setYOffset(2)
            qclabelframeshadow.setXOffset(3)
            qclabelframe.setGraphicsEffect(qclabelframeshadow)

            self.qctabs = QTabWidget()

            qctabsframe = QFrame()
            qctabsframe.setProperty('dashboardframe', True)
            qctabsframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qctabsframeshadow.setBlurRadius(6)
            qctabsframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qctabsframeshadow.setYOffset(3)
            qctabsframeshadow.setXOffset(3)
            qctabsframe.setGraphicsEffect(qctabsframeshadow)

            buttonsframe = QFrame()
            buttonsframe.setFixedHeight(60)
            #buttonsframe.setFixedWidth(300)
            buttonsframe.setProperty('buttonsframe', True)

            self.auto_size = QCheckBox('Auto zoom')

            leftonxaxis = QPushButton()
            leftonxaxis.clicked.connect(self.move_camera_left)
            leftonxaxis.setIcon(QIcon(':/assets/greenleftarrow.svg'))
            leftonxaxis.setIconSize(QtCore.QSize(33, 33))
            leftonxaxis.setProperty('icons', True)
            leftonxaxis.setFixedWidth(50)

            rightonxaxis = QPushButton()
            rightonxaxis.clicked.connect(self.move_camera_right)
            rightonxaxis.setIcon(QIcon(':/assets/greenrightarrow.svg'))
            rightonxaxis.setIconSize(QtCore.QSize(33, 33))
            rightonxaxis.setProperty('icons', True)
            rightonxaxis.setFixedWidth(50)

            zoomin = QPushButton()
            zoomin.clicked.connect(self.zoom_in)
            zoomin.setIcon(QIcon(':/assets/zoomin.svg'))
            zoomin.setIconSize(QtCore.QSize(33, 33))
            zoomin.setProperty('icons', True)
            zoomin.setFixedWidth(50)

            zoomout = QPushButton()
            zoomout.clicked.connect(self.zoom_out)
            zoomout.setIcon(QIcon(':/assets/zoomout.svg'))
            zoomout.setIconSize(QtCore.QSize(33, 33))
            zoomout.setProperty('icons', True)
            zoomout.setFixedWidth(50)

            zoomfit = QPushButton()
            zoomfit.clicked.connect(self.zoom_fit)
            zoomfit.setIcon(QIcon(':/assets/expand.svg'))
            zoomfit.setIconSize(QtCore.QSize(33, 33))
            zoomfit.setProperty('icons', True)
            zoomfit.setFixedWidth(50)

            self.underwayfile = QCheckBox('Find Lat/Longs')

            okcanframe = QFrame()
            okcanframe.setMinimumHeight(40)
            okcanframe.setProperty('dashboardframe2', True)
            okcanframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            okcanframeshadow.setBlurRadius(6)
            okcanframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            okcanframeshadow.setYOffset(2)
            okcanframeshadow.setXOffset(3)
            okcanframe.setGraphicsEffect(okcanframeshadow)

            okbut = QPushButton('Proceed')
            okbut.setFixedHeight(25)
            okbut.setFixedWidth(100)
            okbut.clicked.connect(self.proceed)
            okbut.setProperty('icons', True)

            cancelbut = QPushButton('Cancel')
            cancelbut.clicked.connect(self.cancel)
            cancelbut.setProperty('icons', True)
            cancelbut.setFixedHeight(25)
            cancelbut.setFixedWidth(95)

            # Initialise the trace figure for plotting to
            self.tracefigure = plt.figure(figsize=(6, 4))
            self.tracefigure.set_tight_layout(tight=True)
            self.tracefigure.set_facecolor('#f9fcff')
            self.tracecanvas = FigureCanvas(self.tracefigure)
            self.tracecanvas.setParent(self)
            self.tracetoolbar = NavigationToolbar(self.tracecanvas, self)
            self.tracetoolbar.locLabel.hide()

            # Setting everything into the layout
            self.grid_layout.addWidget(tracelabelframe, 0, 0, 1, 11)
            self.grid_layout.addWidget(self.analysistraceLabel, 0, 0, 1, 3, QtCore.Qt.AlignCenter)

            self.grid_layout.addWidget(qclabelframe, 0, 11, 1, 5)
            self.grid_layout.addWidget(self.qctabsLabel, 0, 11, 1, 1, QtCore.Qt.AlignCenter)

            self.grid_layout.addWidget(traceframe, 1, 0, 20, 11)
            self.grid_layout.addWidget(self.tracecanvas, 1, 0, 17, 11)
            self.grid_layout.addWidget(self.tracetoolbar, 18, 0, 1, 5)

            self.grid_layout.addWidget(qctabsframe, 1, 11, 19, 5)
            self.grid_layout.addWidget(self.qctabs, 1, 11, 19, 5)

            self.grid_layout.addWidget(self.auto_size, 20, 0, QtCore.Qt.AlignCenter)

            self.grid_layout.addWidget(buttonsframe, 19, 3, 2, 5)

            self.grid_layout.addWidget(leftonxaxis, 19, 3, 2, 1, QtCore.Qt.AlignHCenter)
            self.grid_layout.addWidget(rightonxaxis, 19, 4, 2, 1, QtCore.Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomfit, 19, 5, 2, 1, QtCore.Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomin, 19, 6, 2, 1, QtCore.Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomout, 19, 7, 2, 1, QtCore.Qt.AlignHCenter)

            self.grid_layout.addWidget(self.underwayfile, 19, 0, QtCore.Qt.AlignCenter)

            self.grid_layout.addWidget(okcanframe, 20, 11, 1, 5)

            self.grid_layout.addWidget(okbut, 20, 12, 1, 2, QtCore.Qt.AlignJustify)
            self.grid_layout.addWidget(cancelbut, 20, 13, 1, 2, QtCore.Qt.AlignJustify)

            self.main_trace = self.tracefigure.add_subplot(111)

            # Connect the mouse interaction to the trace plot so we can click and select peaks on it
            clicker = self.tracefigure.canvas.mpl_connect("button_press_event", self.on_click)

            self.bootup = True

            self.show()

        except Exception:
            print(traceback.print_exc())


    def draw_data(self, chd_data, w_d, current_nutrient):
        st = time.time()

        if len(self.main_trace.lines) == 0:
            self.main_trace.set_facecolor('#fcfdff')
            self.main_trace.grid(color="#0a2b60", alpha=0.1)
            self.main_trace.set_xlabel('Time (s)')
            self.main_trace.set_ylabel('A/D Value')

        #self.main_trace.set_xlim(self.xmin, self.xmax)
        #self.main_trace.set_ylim(self.ymin, self.ymax)

            self.main_trace.plot(range(len(chd_data.ad_data[current_nutrient])), chd_data.ad_data[current_nutrient], linewidth = 0.75, color='#1b2535')

            self.main_trace.set_xlim(0, len(chd_data.ad_data[current_nutrient]))
            self.main_trace.set_ylim(0, max(chd_data.ad_data[current_nutrient])*1.1)


        if len(self.main_trace.lines) > 2:
            del self.main_trace.lines[1:]

        for i, x in enumerate(w_d.time_values):
            self.main_trace.plot(x, w_d.window_values[i], color=self.FLAG_COLORS[w_d.quality_flag[i]], linewidth=2.5)

        #self.main_trace.plot(w_d.time_values[current_nutrient], w_d.window_values[current_nutrient], linewidth=0, color='#68C968', marker='o')

        self.main_trace.plot(w_d.baseline_peak_starts[:], w_d.baseline_medians[1:-1], linewidth=1, color="#d69f20")
        self.main_trace.plot(w_d.drift_peak_starts[:], w_d.raw_drift_medians[:], linewidth = 1)
        self.tracecanvas.draw()
        ft = time.time()

        print('Draw time: ' + str(ft-st))

        print(str(len(self.main_trace.lines)) + str(' Lines on Main Trace'))

    def create_plot_tabs(self):

        self.calibrant_curve_tab()
        self.calibrant_error_tab()
        self.baseline_correction_tab()
        self.drift_correction_tab()

    def store_data(self):
        pass
        psn.pack_data(self.slk_data, self.w_d, self.database)


    def proceed(self):
        self.main_trace.cla()
        self.tracecanvas.draw()

        self.store_data(self.w_d)

        index = self.slk_data.active_nutrients.index(self.current_nutrient)
        try:
            self.current_nutrient = self.slk_data.active_nutrients[index+1]
            self.process_data(self.file_path, '', self.path, self.project, self.current_nutrient, self.slk_data, self.chd_data)
        except IndexError:
            print('Processing completed')
            self.close()

    def cancel(self):
        self.close()

    # Manages the clicking
    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            x_axis_time = int(event.xdata)
            exists, peak_index = match_click_to_peak(x_axis_time, self.slk_data, self.current_nutrient)
            if exists:
                self.peak_display = traceSelection(self.slk_data.sample_ids[peak_index],
                                                   self.slk_data.cup_types[peak_index],
                                                   (peak_index+1),
                                                   self.w_d.corr_window_medians[peak_index],
                                                   self.w_d.calculated_concentrations[peak_index],
                                                   self.w_d.quality_flag[peak_index],
                                                   self.w_d.dilution_factor[peak_index], 'Trace')
                self.peak_display.setStart.connect(lambda: self.movepeakstart(x_axis_time, peak_index))


    def movepeakstart(self, x, i):

        thread = Thread(target=self.process_data, args=(self.current_nutrient, self.slk_data, self.chd_data, self.w_d))
        thread.start()

    # Manages the key pressing
    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() == 65: # A
            self.move_camera_left()
        if event.key() == 68: # D
            self.move_camera_right()
        if event.key() == 87: # W
            self.zoom_in()
        if event.key() == 88: # X
            self.zoom_out()
        if event.key() == 83: # S
            self.zoom_fit()

        if event.key() == 81:
            if self.auto_size.isChecked():
                self.autosize.setChecked(False)
            else:
                self.auto_size.setChecked(True)

    def move_camera_left(self):
        xmin, xmax = self.main_trace.get_xbound()
        ten_percent = (xmax-xmin) * 0.1
        if xmin > 0 - 100:
            self.main_trace.set_xlim(xmin - ten_percent, xmax - ten_percent)
            self.tracecanvas.draw()
        if self.auto_size.isChecked():
            self.zoom_fit()

    def move_camera_right(self):
        xmin, xmax = self.main_trace.get_xbound()
        ten_percent = (xmax - xmin) * 0.1
        if xmax < len(self.chd_data.ad_data[self.current_nutrient]) + 100:
            self.main_trace.set_xlim(xmin + ten_percent, xmax + ten_percent)
            self.tracecanvas.draw()
        if self.auto_size.isChecked():
            self.zoom_fit()

    def zoom_in(self):
        ymin, ymax = self.main_trace.get_ybound()
        xmin, xmax = self.main_trace.get_xbound()
        ytenpercent = ymax * 0.1
        xtenpercent = (xmax - xmin) * 0.15
        if ymax > min(self.chd_data.ad_data[self.current_nutrient]) * 2 and xtenpercent < (xmax - xmin) / 2:
            self.main_trace.set_ylim(ymin, ymax - ytenpercent)
            self.main_trace.set_xlim(xmin + xtenpercent, xmax - xtenpercent)
        self.tracecanvas.draw()

    def zoom_out(self):
        ymin, ymax = self.main_trace.get_ybound()
        xmin, xmax = self.main_trace.get_xbound()
        ytenpercent = ymax * 0.1
        xtenpercent = (xmax - xmin) * 0.15
        if ymax < max(self.chd_data.ad_data[self.current_nutrient]) + 500:
            self.main_trace.set_ylim(ymin, ymax + ytenpercent)
            self.main_trace.set_xlim(xmin - xtenpercent, xmax + xtenpercent)
        else:
            if xmin > 0 and xmax < len(self.chd_data.ad_data[self.current_nutrient]):
                self.main_trace.set_xlim(xmin - xtenpercent, xmax + xtenpercent)
        self.tracecanvas.draw()

    def zoom_fit(self):
        try:
            ymin, ymax = self.main_trace.get_ybound()
            xmin, xmax = self.main_trace.get_xbound()
            maxheight = max(self.chd_data.ad_data[self.current_nutrient][int(xmin): int(xmax)])
            self.main_trace.set_ylim(ymin, maxheight * 1.02)
            self.tracecanvas.draw()
        except Exception as e:
            print(e)

    def calibrant_curve_tab(self):

        self.cal_curve_tab = QWidget()
        self.qctabs.addTab(self.cal_curve_tab, 'Cal Curve')
        self.cal_curve_tab.layout = QVBoxLayout()

        cc_plot = qcp.calibrationCurve(self.w_d.analyte, self.w_d.calibrant_medians_minuszero,
                                       self.w_d.calibrant_concentations)

        #self.cal_curve_plotted = qcp.calibrationCurve(self.currentnut, self.finalcaladvals, self.cc,
        #                                            self.fittoplot, self.r_value, self.calibrantflags)
        #self.cal_curve_tab.layout.addWidget(self.calcurveplotted)
        self.cal_curve_tab.setLayout(self.cal_curve_tab.layout)

    def calibrant_error_tab(self):

        self.cal_error_tab = QWidget()
        self.qctabs.addTab(self.cal_error_tab, 'Cal Error')
        self.cal_error_tab.layout = QVBoxLayout()

        self.cal_error_tab.setLayout(self.cal_error_tab.layout)

    def baseline_correction_tab(self):

        self.baseline_corr_tab = QWidget()
        self.qctabs.addTab(self.baseline_corr_tab, 'Baseline Correction')
        self.baseline_corr_tab.layout = QVBoxLayout()


        self.baseline_corr_tab.setLayout(self.baseline_corr_tab.layout)

    def drift_correction_tab(self):

        self.drift_corr_tab = QWidget()
        self.qctabs.addTab(self.drift_corr_tab, 'Drift Correction')
        self.drift_corr_tab.layout = QVBoxLayout()

        self.baseline_corr_tab.setLayout(self.drift_corr_tab.layout)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = processingNutrientsWindow('in2018_v01nut001.SLK', '', 'C:/Users/she384/Documents/HyPro_Dev', 'in2018_v01')
    sys.exit(app.exec_())

