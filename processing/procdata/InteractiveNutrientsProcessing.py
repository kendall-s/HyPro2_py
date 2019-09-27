from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QCheckBox, QFrame, QVBoxLayout, QTabWidget,
                             QDesktopWidget, QApplication)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import *
import processing.plotting.QCPlots as qcp
import sys, logging, traceback
import json
import hyproicons
import processing.procdata.ProcessSealNutrients as psn
import processing.readdata.ReadSealNutrients as rsn
from processing.algo.HyproComplexities import load_proc_settings, match_click_to_peak
from dialogs.TraceSelectionDialog import traceSelection
from processing.algo.Structures import WorkingData
from threading import Thread
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate
import cProfile
#background-color: #ededed;

# TODO: Finish new implementation of cleaned up testable Nutrients
# TODO: Reimplement the QC chart tab system to be more L I G H T W E I G H T
# TODO: Re-create style sheet in styles file

class processingNutrientsWindow(hyproMainWindowTemplate):

    """
    Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad,
                    91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different

    """
    def __init__(self, file, database, path, project, interactive=True, rereading=''):
        screenwidth = QDesktopWidget().availableGeometry().width()
        screenheight = QDesktopWidget().availableGeometry().height()
        super().__init__((screenwidth * 0.85), (screenheight * 0.85),
                         'HyPro - Process Nutrient Analysis')

        self.FLAG_COLORS = {1: '#68C968', 2: '#3CB6C9', 3: '#C92724', 4:'#3CB6C9', 5: '#C92724', 6: '#C9852B'}

        self.processing_parameters = load_proc_settings(path, project)

        self.file_path = path + '/' + 'Nutrients' + '/' + file
        self.path = path
        self.project = project
        self.database = database


        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())

        if params['theme'] == 'normal':
            self.COLORS = {'axes.edgecolor': '#000000', 'xtick.color': '#000000', 'ytick.color': '#000000',
                           'axes.facecolor': '#FFFFFF', 'axes.labelcolor': '#000000', 'figure.facecolor': '#FFFFFF',
                            'grid.color': '#000000', 'lines.color': '#191919', 'figure.frameon': False}
        else:
            self.COLORS = {'axes.edgecolor': '#F5F5F5', 'xtick.color': '#F5F5F5', 'ytick.color': '#F5F5F5',
                           'axes.facecolor': '#191919', 'axes.labelcolor': '#F5F5F5', 'figure.facecolor': '#191919',
                           'grid.color': '#F5F5F5', 'lines.color': '#F5F5F5', 'figure.frameon': False}

        self.w_d = WorkingData(file)

        self.slk_data, self.chd_data, self.w_d, self.current_nutrient = rsn.get_data_routine(self.file_path,
                                                                                             self.w_d,
                                                                                             self.processing_parameters,
                                                                                             self.database)
        self.w_d = psn.processing_routine(self.slk_data, self.chd_data, self.w_d, self.processing_parameters,
                                          self.current_nutrient)

        if interactive:
            self.init_ui()

            thread = Thread(target=self.draw_data, args=(self.chd_data, self.w_d, self.current_nutrient))
            thread.start()
            thread.join()


            st = time.time()

            self.create_standard_qc_tabs()

            qc_cups = self.processing_parameters['nutrientprocessing']['qcsamplenames']
            self.create_custom_qc_tabs(self.slk_data.sample_ids, qc_cups)

            self.plot_data()
            print('QCTabs: ' + str(time.time() - st))
        else:
            sys.exit()


    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))
            self.setWindowModality(Qt.WindowModal)
            self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

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
            leftonxaxis.setIconSize(QSize(33, 33))
            leftonxaxis.setProperty('icons', True)
            leftonxaxis.setFixedWidth(50)

            rightonxaxis = QPushButton()
            rightonxaxis.clicked.connect(self.move_camera_right)
            rightonxaxis.setIcon(QIcon(':/assets/greenrightarrow.svg'))
            rightonxaxis.setIconSize(QSize(33, 33))
            rightonxaxis.setProperty('icons', True)
            rightonxaxis.setFixedWidth(50)

            zoomin = QPushButton()
            zoomin.clicked.connect(self.zoom_in)
            zoomin.setIcon(QIcon(':/assets/zoomin.svg'))
            zoomin.setIconSize(QSize(33, 33))
            zoomin.setProperty('icons', True)
            zoomin.setFixedWidth(50)

            zoomout = QPushButton()
            zoomout.clicked.connect(self.zoom_out)
            zoomout.setIcon(QIcon(':/assets/zoomout.svg'))
            zoomout.setIconSize(QSize(33, 33))
            zoomout.setProperty('icons', True)
            zoomout.setFixedWidth(50)

            zoomfit = QPushButton()
            zoomfit.clicked.connect(self.zoom_fit)
            zoomfit.setIcon(QIcon(':/assets/expand.svg'))
            zoomfit.setIconSize(QSize(33, 33))
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
            with mpl.rc_context(rc=self.COLORS):
                self.tracefigure = plt.figure(figsize=(6, 4))
                self.tracefigure.set_tight_layout(tight=True)
                #self.tracefigure.set_facecolor('#f9fcff')
                self.tracecanvas = FigureCanvas(self.tracefigure)
                self.tracecanvas.setParent(self)
                self.tracetoolbar = NavigationToolbar(self.tracecanvas, self)
                self.tracetoolbar.locLabel.hide()
                self.main_trace = self.tracefigure.add_subplot(111)

            # Setting everything into the layout
            self.grid_layout.addWidget(tracelabelframe, 0, 0, 1, 11)
            self.grid_layout.addWidget(self.analysistraceLabel, 0, 0, 1, 3, Qt.AlignCenter)

            self.grid_layout.addWidget(qclabelframe, 0, 11, 1, 5)
            self.grid_layout.addWidget(self.qctabsLabel, 0, 11, 1, 1, Qt.AlignCenter)

            self.grid_layout.addWidget(traceframe, 1, 0, 20, 11)
            self.grid_layout.addWidget(self.tracecanvas, 1, 0, 17, 11)
            self.grid_layout.addWidget(self.tracetoolbar, 18, 0, 1, 5)

            self.grid_layout.addWidget(qctabsframe, 1, 11, 19, 5)
            self.grid_layout.addWidget(self.qctabs, 1, 11, 19, 5)

            self.grid_layout.addWidget(self.auto_size, 20, 0, Qt.AlignCenter)

            self.grid_layout.addWidget(buttonsframe, 19, 3, 2, 5)

            self.grid_layout.addWidget(leftonxaxis, 19, 3, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(rightonxaxis, 19, 4, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomfit, 19, 5, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomin, 19, 6, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomout, 19, 7, 2, 1, Qt.AlignHCenter)

            self.grid_layout.addWidget(self.underwayfile, 19, 0, Qt.AlignCenter)

            self.grid_layout.addWidget(okcanframe, 20, 11, 1, 5)

            self.grid_layout.addWidget(okbut, 20, 12, 1, 2, Qt.AlignJustify)
            self.grid_layout.addWidget(cancelbut, 20, 13, 1, 2, Qt.AlignJustify)


            # Connect the mouse interaction to the trace plot so we can click and select peaks on it
            clicker = self.tracefigure.canvas.mpl_connect("button_press_event", self.on_click)

            self.bootup = True

            self.show()

        except Exception:
            print(traceback.print_exc())


    def draw_data(self, chd_data, w_d, current_nutrient):
        st = time.time()

        if len(self.main_trace.lines) == 0:
            #self.main_trace.set_facecolor('#fcfdff')
            self.main_trace.grid(alpha=0.1)
            self.main_trace.set_xlabel('Time (s)')
            self.main_trace.set_ylabel('A/D Value')

            self.main_trace.plot(range(len(chd_data.ad_data[current_nutrient])), chd_data.ad_data[current_nutrient],
                                 linewidth = 0.75, label='trace', color='#F5F5F5')

            self.main_trace.set_xlim(0, len(chd_data.ad_data[current_nutrient]))
            self.main_trace.set_ylim(0, max(chd_data.ad_data[current_nutrient])*1.1)

        if len(self.main_trace.lines) > 1:
            del self.main_trace.lines[1:]
            del self.main_trace.artists[1:]

        for i, x in enumerate(w_d.time_values):
            self.main_trace.plot(x, w_d.window_values[i], color=self.FLAG_COLORS[w_d.quality_flag[i]], linewidth=2.5, label='top')

        #self.main_trace.plot(w_d.time_values, w_d.window_values, linewidth=0.25, color='#68C968', marker='o')

        self.baseline = self.main_trace.plot(w_d.baseline_peak_starts[:], w_d.baseline_medians[1:-1], linewidth=1, color="#d69f20", label='baseline')
        self.main_trace.plot(w_d.drift_peak_starts[:], w_d.raw_drift_medians[:], linewidth=1, label='drift')

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
        #print(event.key())
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
        if event.key() == 82: # R Imitates changing peak windows etc, for testing optimisation of processing and draw

            random_modifier = np.random.randint(low=10, high=50)
            random_modifier2 = np.random.randint(low=2, high=30)
            print(random_modifier)
            print(random_modifier2)

            self.processing_parameters['nutrientprocessing']['processingpars'][self.current_nutrient]['windowStart'] = random_modifier
            self.processing_parameters['nutrientprocessing']['processingpars'][self.current_nutrient]['windowSize'] = random_modifier
            self.w_d.quality_flag = [self.w_d.quality_flag[i] if x not in [4,5] else 1 for i, x in enumerate(self.w_d.quality_flag)]
            self.w_d = psn.processing_routine(self.slk_data, self.chd_data, self.w_d, self.processing_parameters,
                                              self.current_nutrient)
            self.draw_data(self.chd_data, self.w_d, self.current_nutrient)
            self.tracecanvas.draw()

            self.plot_data()

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


    def create_standard_qc_tabs(self):
        standard_tabs = {'cal_curve': 'Calibration', 'cal_error': 'Cal Error', 'baseline': 'Baseline Corr', 'drift': 'Drift Corr'}
        with mpl.rc_context(rc=self.COLORS):
            for qc in standard_tabs:
                setattr(self, "{}".format(qc + str('_tab')), QWidget())
                self.qctabs.addTab(getattr(self, "{}".format(qc + str('_tab'))), str(standard_tabs[qc]))
                setattr(self, "{}".format(qc + str('_lout')), QVBoxLayout())
                getattr(self, "{}".format(qc + str('_tab'))).setLayout(getattr(self, "{}".format(qc + str('_lout'))))
                setattr(self, "{}".format(qc + str('_fig')), plt.figure())
                setattr(self, "{}".format(qc + str('_canvas')), FigureCanvas(getattr(self, "{}".format(qc + str('_fig')))))
                if qc == 'baseline' or qc == 'drift':
                    setattr(self, "{}".format(qc + str('_plot')),getattr(self, "{}".format(qc + str('_fig'))).add_subplot(211))
                    setattr(self, "{}".format(qc + str('_plot2')),getattr(self, "{}".format(qc + str('_fig'))).add_subplot(212))
                else:
                    setattr(self, "{}".format(qc + str('_plot')), getattr(self, "{}".format(qc + str('_fig'))).add_subplot(111))
                getattr(self, "{}".format(qc + str('_lout'))).addWidget(getattr(self, "{}".format(qc + str('_canvas'))))


    def create_custom_qc_tabs(self, sample_ids, qc_samps):
        self.qc_tabs_in_existence = []
        sample_ids_set = set(sample_ids)
        with mpl.rc_context(rc=self.COLORS):
            for qc in qc_samps:
                #print(qc_samps[qc])
                if not qc == 'driftsample':
                    if any(qc_samps[qc] in s_id for s_id in sample_ids_set):
                        setattr(self, "{}".format(qc + str('_tab')), QWidget())
                        self.qctabs.addTab(getattr(self, "{}".format(qc + str('_tab'))), str(qc_samps[qc]))
                        setattr(self, "{}".format(qc + str('_lout')), QVBoxLayout())
                        getattr(self, "{}".format(qc + str('_tab'))).setLayout(getattr(self, "{}".format(qc + str('_lout'))))
                        setattr(self, "{}".format(qc + str('_fig')), plt.figure())
                        setattr(self, "{}".format(qc + str('_canvas')), FigureCanvas(getattr(self, "{}".format(qc + str('_fig')))))
                        setattr(self, "{}".format(qc + str('_plot')), getattr(self, "{}".format(qc + str('_fig'))).add_subplot(111))
                        getattr(self, "{}".format(qc + str('_lout'))).addWidget(getattr(self, "{}".format(qc + str('_canvas'))))
                        self.qc_tabs_in_existence.append(qc)

    def plot_data(self):
        print(self.COLORS)
        qcp.calibration_curve_plot(self.COLORS, self.cal_curve_fig, self.cal_curve_plot,
                                   self.w_d.calibrant_medians, self.w_d.calibrant_concs, self.w_d.calibrant_flags, 1)
        self.cal_curve_canvas.draw()
        analyte_error = self.processing_parameters['nutrientprocessing']['processingpars'][self.current_nutrient]['calerror']
        qcp.calibration_error_plot(self.COLORS, self.cal_error_fig, self.cal_error_plot,
                                   self.w_d.calibrant_concs, self.w_d.calibrant_residuals, analyte_error,
                             self.w_d.calibrant_flags)
        self.cal_error_canvas.draw()
        qcp.basedrift_correction_plot(self.COLORS, self.baseline_fig, self.baseline_plot,
                                      self.baseline_plot2, 'Baseline', self.w_d.baseline_indexes,
                                     self.w_d.baseline_corr_percent, self.w_d.baseline_medians, self.w_d.baseline_flags)
        self.baseline_canvas.draw()

        qcp.basedrift_correction_plot(self.COLORS, self.drift_fig, self.drift_plot,
                                      self.drift_plot2, 'Drift', self.w_d.drift_indexes,
                                      self.w_d.drift_corr_percent, self.w_d.drift_medians, self.w_d.drift_flags)
        self.drift_canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = processingNutrientsWindow('in2018_v01nut001.SLK', '', 'C:/Users/she384/Documents/HyPro_Dev', 'in2018_v01')
    sys.exit(app.exec_())

