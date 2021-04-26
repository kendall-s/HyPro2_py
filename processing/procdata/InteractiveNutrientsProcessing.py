from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QCheckBox, QFrame, QVBoxLayout, QTabWidget,
                             QDesktopWidget, QApplication, QLineEdit)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pylab import *
import processing.plotting.QCPlots as qcp
import sys, logging, traceback, os
import json
import hyproicons
import style
import processing.procdata.ProcessSealNutrients as psn
from processing.algo.HyproComplexities import load_proc_settings, match_click_to_peak, match_hover_to_peak
from processing.algo import HyproComplexities
from dialogs.TraceSelectionDialog import traceSelection
from processing.algo.Structures import WorkingData, SLKData, CHDData
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate
from processing.plotting.TracePlot import TracePlotter
import pyqtgraph as pg
from processing.procdata.ProcessNutrientsController import processNutrientsController

import cProfile
#background-color: #ededed;




# TODO: Finish new implementation of cleaned up testable Nutrients
# TODO: Reimplement the QC chart tab system to be more L I G H T W E I G H T
# TODO: Re-create style sheet in styles file


class processingNutrientsWindow(hyproMainWindowTemplate):

    """
    This is the class that handles the GUI interface for Nutrient processing

    Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad,
                    91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different

    """

    processing_completed = pyqtSignal()
    aborted = pyqtSignal()

    def __init__(self, file, database, path, project, interactive=True, rereading=False, perf_mode=False,
                 ultra_perf_mode=False):
        screenwidth = QDesktopWidget().availableGeometry().width()
        screenheight = QDesktopWidget().availableGeometry().height()
        super().__init__((screenwidth * 0.85), (screenheight * 0.85), 'HyPro - Process Nutrient Analysis')

        # Set flagging colours
        self.FLAG_COLORS = {1: '#68C968', 2: '#45D4E8', 3: '#C92724', 4:'#3CB6C9', 5: '#C92724', 6: '#DC9530',
                            91: '#9CCDD6', 92: '#F442D9', 8: '#3CB6C9'}

        self.FLAG_CONVERTER = {1 : 'Good', 2 : 'Suspect', 3 : 'Bad', 4 : 'Shape Sus', 5 : 'Shape Bad',
                               91 : 'CalError Sus', 92 : 'CalError Bad', 8 : 'Dup Diff'}
        self.REVERSE_FLAG_CONVERTER = {x : y for y, x in self.FLAG_CONVERTER.items()}

        # Load in the processing parameters
        self.processing_parameters = load_proc_settings(path, project)


        self.file_path = path + '/' + 'Nutrients' + '/' + file
        self.file = file
        self.path = path
        self.project = project
        self.database = database
        self.interactive = interactive
        self.rereading = rereading

        self.perf_mode = perf_mode
        self.ultra_perf_mode = ultra_perf_mode

        self.ui_initialised = False
        self.plot_title_appender = ''

        self.actions_list = []

        # General HyPro settings, use for setting theme of window
        with open('C:/HyPro/hyprosettings.json', 'r') as temp:
            params = json.loads(temp.read())
        # Load up theme for window
        if params['theme'] == 'normal':
            plt.style.use(style.mplstyle['normal'])
            self.theme = 'normal'
        else:
            plt.style.use(style.mplstyle['dark'])
            self.theme = 'dark'

        # Holds all the calculation data
        self.view_w_d = WorkingData(file)
        self.view_slk_data = SLKData(file)
        self.view_chd_data = CHDData(file)
        self.current_nutrient = 'none yet'

        # Pull out the data from the files in the directory
        try:
            # Start the nutrient processisng QObject in a different thread, this will handle all the data side
            self.start_nutrient_processing_thread()

        except TypeError:
            logging.error(f'Formatting error in .SLK file. Processing aborted.')
            traceback.print_exc()

        except FileNotFoundError:
            logging.error('Could not find the nutrient file, is it in the right spot? Does a Nutrient folder exist?')

        except IndexError:
            logging.error('HyPro could not find any nutrients! Please check the spelling of your analyte names')

    def start_nutrient_processing_thread(self):
        self.thread = QThread()

        self.nutrient_processing_controller = processNutrientsController(self.file,
                                                                         self.file_path,
                                                                         self.database,
                                                                         self.processing_parameters)
        self.nutrient_processing_controller.moveToThread(self.thread)
        self.thread.started.connect(self.nutrient_processing_controller.startup_routine)
        self.nutrient_processing_controller.startup_routine_completed.connect(self.update_ui)

        self.nutrient_processing_controller.reprocessing_completed.connect(self.update_ui)

        self.nutrient_processing_controller.thinking.connect(self.loading_cursor)
        self.nutrient_processing_controller.startup_routine_completed.connect(self.reset_cursor)
        self.nutrient_processing_controller.reprocessing_completed.connect(self.reset_cursor)

        self.thread.start()

    def loading_cursor(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def reset_cursor(self):
        QApplication.restoreOverrideCursor()

    def update_ui(self, return_package):
        trace_redraw = True
        self.current_nutrient, self.view_slk_data, self.view_chd_data, self.view_w_d = return_package

        self.plot_title_appender = f' - {self.current_nutrient.capitalize()} | {self.file}'

        if self.view_w_d == None:
            self.aborted.emit()

        if not self.interactive:
            self.store_data()
            self.close()
            return

        if not self.ui_initialised:
            trace_redraw = False
            self.init_ui()
            if self.view_w_d == None:
                time.sleep(0.3)
                self.close()
            else:
                self.create_standard_qc_tabs()
                qc_cups = self.processing_parameters['nutrientprocessing']['qcsamplenames']
                self.create_custom_qc_tabs(self.view_slk_data.sample_ids, qc_cups)

        self.interactive_routine(trace_redraw=trace_redraw)


    def interactive_routine(self, trace_redraw=True):
        """
        Routine called every time the data has been reprocessed, this will redraw all as necessary.
        :return:
        """

        self.draw_data(self.view_chd_data, self.view_w_d, self.current_nutrient, trace_redraw)

        st = time.time()

        self.plot_standard_data()
        self.plot_custom_data()
        print('QCTabs: ' + str(time.time() - st))

    def init_ui(self):
        """
        Initialises all the GUI elements required for the nutrient processing window
        :return:
        """
        try:

            self.setFont(QFont('Segoe UI'))

            self.setWindowModality(Qt.WindowModal)
            self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
            #self.showMaximized()
            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            editMenu = mainMenu.addMenu('Edit')

            label_text = f'<b>Processing File:</b> {self.file}  |  <b>Analysis Trace:</b> {self.current_nutrient.capitalize()}'
            self.analysistraceLabel = QLabel(label_text)
            self.analysistraceLabel.setProperty('headertext', True)
            self.analysistraceLabel.setStyleSheet("font: 16px; font-family: Segoe UI;")

            tracelabelframe = QFrame()
            tracelabelframe.setProperty('nutrientHeadFrame', True)
            tracelabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            tracelabelframeshadow.setBlurRadius(6)
            tracelabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            tracelabelframeshadow.setYOffset(2)
            tracelabelframeshadow.setXOffset(3)
            tracelabelframe.setGraphicsEffect(tracelabelframeshadow)

            traceframe = QFrame()
            traceframe.setProperty('nutrientFrame', True)
            traceframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            traceframeshadow.setBlurRadius(6)
            traceframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            traceframeshadow.setYOffset(2)
            traceframeshadow.setXOffset(3)
            traceframe.setGraphicsEffect(traceframeshadow)

            self.qctabsLabel = QLabel('<b>QC Charts:</b>',)
            self.qctabsLabel.setProperty('headertext', True)

            qclabelframe = QFrame()
            qclabelframe.setProperty('nutrientHeadFrame', True)
            qclabelframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qclabelframeshadow.setBlurRadius(6)
            qclabelframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qclabelframeshadow.setYOffset(2)
            qclabelframeshadow.setXOffset(3)
            qclabelframe.setGraphicsEffect(qclabelframeshadow)

            self.qctabs = QTabWidget()

            qctabsframe = QFrame()
            qctabsframe.setProperty('nutrientFrame', True)
            qctabsframeshadow = QtWidgets.QGraphicsDropShadowEffect()
            qctabsframeshadow.setBlurRadius(6)
            qctabsframeshadow.setColor(QtGui.QColor('#e1e6ea'))
            qctabsframeshadow.setYOffset(3)
            qctabsframeshadow.setXOffset(3)
            qctabsframe.setGraphicsEffect(qctabsframeshadow)

            buttonsframe = QFrame()
            buttonsframe.setFixedHeight(60)
            #buttonsframe.setFixedWidth(300)
            buttonsframe.setProperty('nutrientButtonFrame', True)

            self.auto_size = QCheckBox('Auto zoom')

            leftonxaxis = QPushButton()
            leftonxaxis.clicked.connect(self.move_camera_left)
            leftonxaxis.setIcon(QIcon(':/assets/greenleftarrow.svg'))
            leftonxaxis.setIconSize(QSize(33, 33))
            leftonxaxis.setProperty('nutrientControls', True)
            leftonxaxis.setFixedWidth(50)

            rightonxaxis = QPushButton()
            rightonxaxis.clicked.connect(self.move_camera_right)
            rightonxaxis.setIcon(QIcon(':/assets/greenrightarrow.svg'))
            rightonxaxis.setIconSize(QSize(33, 33))
            rightonxaxis.setProperty('nutrientControls', True)
            rightonxaxis.setFixedWidth(50)

            zoomin = QPushButton()
            zoomin.clicked.connect(self.zoom_in)
            zoomin.setIcon(QIcon(':/assets/zoomin.svg'))
            zoomin.setIconSize(QSize(33, 33))
            zoomin.setProperty('nutrientControls', True)
            zoomin.setFixedWidth(50)

            zoomout = QPushButton()
            zoomout.clicked.connect(self.zoom_out)
            zoomout.setIcon(QIcon(':/assets/zoomout.svg'))
            zoomout.setIconSize(QSize(33, 33))
            zoomout.setProperty('nutrientControls', True)
            zoomout.setFixedWidth(50)

            zoomfit = QPushButton()
            zoomfit.clicked.connect(self.zoom_fit)
            zoomfit.setIcon(QIcon(':/assets/expand.svg'))
            zoomfit.setIconSize(QSize(33, 33))
            zoomfit.setProperty('nutrientControls', True)
            zoomfit.setFixedWidth(50)

            self.find_lat_lons = QCheckBox('Find Lat/Longs')

            okcanframe = QFrame()
            okcanframe.setMinimumHeight(40)
            okcanframe.setProperty('nutrientFrame2', True)
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
            okbut.setProperty('nutrientControls', True)

            cancelbut = QPushButton('Cancel')
            cancelbut.clicked.connect(self.cancel)
            cancelbut.setProperty('nutrientControls', True)
            cancelbut.setFixedHeight(25)
            cancelbut.setFixedWidth(95)

            if not self.perf_mode:
                pg.setConfigOptions(antialias=True)

            self.graph_widget = pg.PlotWidget()

            if self.ultra_perf_mode:
                self.graph_widget.useOpenGL(True)

            label_style = {'color': '#C1C1C1', 'font-size': '10pt', 'font-family': 'Segoe UI'}
            self.graph_widget.setLabel('left', 'A/D Value', **label_style)
            self.graph_widget.setLabel('bottom', 'Time (s)', **label_style)
            self.graph_widget.showGrid(x=True, y=True)

            self.vertical_line = pg.InfiniteLine(angle=90, movable=False)
            self.vertical_line.setZValue(10)

            self.graph_widget.addItem(self.vertical_line, ignoreBounds=True)

            if self.theme == 'normal':
                self.graph_widget.setBackground('w')
                graph_pen = pg.mkPen(color=(25, 25, 30), width=1.2)
            else:
                self.graph_widget.setBackground((25, 25, 25))
                graph_pen = pg.mkPen(color=(211, 211, 211), width=1.2)

            # This is the plot that holds the signal trace
            self.plotted_data = self.graph_widget.plot(pen=graph_pen)
            self.plotted_data.scene().sigMouseClicked.connect(self.on_click)
            self.plotted_data.scene().sigMouseMoved.connect(self.move_crosshair)
            # These are for holding the lines representing the drift and baseline across the run
            baseline_pen = pg.mkPen(color=('#d69f20'), width=2)
            self.baseline_plotted = self.graph_widget.plot(pen=baseline_pen)

            drift_pen = pg.mkPen(color=('#c6c600'), width=2)
            self.drift_plotted = self.graph_widget.plot(pen=drift_pen)

            self.hovered_peak_lineedit = QLineEdit()
            self.hovered_peak_lineedit.setFont(QFont('Segoe UI'))

            # Setting everything into the layout
            self.grid_layout.addWidget(tracelabelframe, 0, 0, 1, 11)
            self.grid_layout.addWidget(self.analysistraceLabel, 0, 1, 1, 5)

            self.grid_layout.addWidget(qclabelframe, 0, 11, 1, 5)
            self.grid_layout.addWidget(self.qctabsLabel, 0, 11, 1, 1, Qt.AlignCenter)

            self.grid_layout.addWidget(traceframe, 1, 0, 20, 11)
            self.grid_layout.addWidget(self.graph_widget, 1, 0, 17, 11)

            self.grid_layout.addWidget(self.hovered_peak_lineedit, 18, 0, 1, 11)

            self.grid_layout.addWidget(qctabsframe, 1, 11, 19, 5)
            self.grid_layout.addWidget(self.qctabs, 1, 11, 19, 5)

            self.grid_layout.addWidget(self.auto_size, 20, 0, Qt.AlignCenter)

            self.grid_layout.addWidget(buttonsframe, 19, 3, 2, 5)

            self.grid_layout.addWidget(leftonxaxis, 19, 3, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(rightonxaxis, 19, 4, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomfit, 19, 5, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomin, 19, 6, 2, 1, Qt.AlignHCenter)
            self.grid_layout.addWidget(zoomout, 19, 7, 2, 1, Qt.AlignHCenter)

            self.grid_layout.addWidget(self.find_lat_lons, 19, 0, Qt.AlignCenter)

            self.grid_layout.addWidget(okcanframe, 20, 11, 1, 5)

            self.grid_layout.addWidget(okbut, 20, 12, 1, 2, Qt.AlignJustify)
            self.grid_layout.addWidget(cancelbut, 20, 13, 1, 2, Qt.AlignJustify)

            self.bootup = True
            self.ui_initialised = True

            self.show()

        except Exception:
            print(traceback.print_exc())

    def draw_data(self, chd_data, w_d, current_nutrient, trace_redraw):
        """
        Draws the relevant data to the figures that are already initialised in init_ui. Removes lines on each call of
        this function so that memory and performance are preserved.
        :param chd_data:
        :param w_d:
        :param current_nutrient:
        :return:
        """
        st = time.time()

        self.plotted_data.setData(range(len(chd_data.ad_data[current_nutrient])), chd_data.ad_data[current_nutrient])

        if trace_redraw:
            self.graph_widget.removeItem(self.window_lines)
            del self.window_lines

        self.window_lines = TracePlotter(w_d.time_values, w_d.window_values, w_d.quality_flag)
        self.graph_widget.addItem(self.window_lines)

        self.baseline_plotted.setData(w_d.baseline_peak_starts, w_d.baseline_medians[1:-1])
        self.drift_plotted.setData(w_d.drift_peak_starts, w_d.raw_drift_medians)

        ft = time.time()

        print('Draw time: ' + str(ft-st))

    def store_data(self):
        psn.pack_data(self.view_slk_data, self.view_w_d, self.database, self.file_path)

    def proceed(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)
        # TODO: switch data storage to the controller
        self.store_data()

        # If the matching lat/lons check box is active assume the file is a underway one. Pull out samples and
        # find the latitude and longitudes that correspond
        if self.find_lat_lons.isChecked():
            print('Checked')
            try:
                complete = psn.match_lat_lons_routine(self.path, self.project, self.database, self.current_nutrient,
                                                      self.processing_parameters, self.view_w_d, self.view_slk_data)
            except Exception:
                print(traceback.print_exc())

        current_nut_index = self.view_slk_data.active_nutrients.index(self.current_nutrient)

        try:
            if self.current_nutrient == 'nitrate':
                recovery_tab_index = self.qctabs.indexOf(self.recovery_tab)
                self.qctabs.removeTab(recovery_tab_index)

            if not os.path.exists(f'{self.path}/Nutrients/plot'):
                os.mkdir(f'{self.path}/Nutrients/plot')

            if not os.path.exists(f'{self.path}/Nutrients/plot/{self.file}'):
                os.mkdir(f'{self.path}/Nutrients/plot/{self.file}')

            self.drift_fig.savefig(f'{self.path}/Nutrients/plot/{self.file}/{self.current_nutrient}_drift_plot.png',
                                   dpi=300)
            self.baseline_fig.savefig(f'{self.path}/Nutrients/plot/{self.file}/{self.current_nutrient}_baseline_plot.png',
                                      dpi=300)
            self.cal_curve_fig.savefig(f'{self.path}/Nutrients/plot/{self.file}/{self.current_nutrient}_cal_curve_plot.png',
                                      dpi=300)
            self.cal_error_fig.savefig(f'{self.path}/Nutrients/plot/{self.file}/{self.current_nutrient}_cal_error_plot.png',
                                      dpi=300)

            # Try to increment the current nutrient - if an index error is raised, there is no more nutrients to process
            self.current_nutrient = self.view_slk_data.active_nutrients[current_nut_index+1]

            self.analysistraceLabel.setText('<b>Processing file: </b>' + str(self.file) +
                                            '   |   <b>Analysis Trace: </b>' + str(self.current_nutrient).capitalize())


            self.view_w_d.analyte = self.current_nutrient

            self.nutrient_processing_controller.set_current_nutrient(self.current_nutrient)

            self.plot_title_appender = f' - {self.current_nutrient.capitalize()} | {self.file}'

            self.graph_widget.removeItem(self.window_lines)

            QApplication.restoreOverrideCursor()
            self.nutrient_processing_controller.re_process()

        except IndexError:
            print('Processing completed')
            logging.info(f'Processing successfully completed for nutrient file - {self.file}')

            self.processing_completed.emit()
            self.close()

    def cancel(self):
        plt.close('all')
        self.close()

    def move_crosshair(self, event):
        data_coordinates = self.plotted_data.getViewBox().mapSceneToView(event)
        self.vertical_line.setPos(data_coordinates.x())
        x_point = data_coordinates.x()
        #exists, peak_index = match_click_to_peak(x_point, self.view_slk_data, self.current_nutrient, self.view_w_d.adjusted_peak_starts)
        exists, peak_index = match_hover_to_peak(x_point, self.view_slk_data, self.current_nutrient, self.view_w_d.time_values)

        if len(peak_index) > 0:
            peak_index = peak_index[0]
            self.hovered_peak_lineedit.setText(f'Peak #{peak_index+1} | Sample ID: {self.view_slk_data.sample_ids[peak_index]} | Cup Type: {self.view_slk_data.cup_types[peak_index]} | Conc: {round(self.view_w_d.calculated_concentrations[peak_index], 3)} | Corr A/D: {round(self.view_w_d.corr_window_medians[peak_index], 1)} | Raw A/D: {self.view_w_d.raw_window_medians[peak_index]} | Time: {self.view_slk_data.raw_timestamps[peak_index]}')
        else:
            self.hovered_peak_lineedit.setText('No peak')

    def on_click(self, event):
        """
        Handles mouse clicks into the plot
        :param event:
        :return:
        """
        # Get the clicked coordinates, convert to the plotted data values
        trace_coordinates = event.scenePos()
        data_coordinates = self.plotted_data.getViewBox().mapSceneToView(trace_coordinates)

        if event.button() == 1:
            x_point = data_coordinates.x()
            exists, peak_index = match_click_to_peak(x_point,
                                                     self.view_slk_data,
                                                     self.current_nutrient,
                                                     self.view_slk_data.clean_peak_starts)

            if exists:
                self.peak_display = traceSelection(self.view_slk_data.sample_ids[peak_index],
                                                   self.view_slk_data.cup_types[peak_index],
                                                   (peak_index+1),
                                                   self.view_w_d.corr_window_medians[peak_index],
                                                   self.view_w_d.calculated_concentrations[peak_index],
                                                   self.view_w_d.quality_flag[peak_index],
                                                   self.view_w_d.dilution_factor[peak_index], 'Trace')

                self.peak_display.setStart.connect(lambda: self.move_peak_start(x_point, peak_index))
                self.peak_display.setEnd.connect(lambda: self.move_peak_end(x_point, peak_index))
                self.peak_display.saveSig.connect(lambda: self.update_from_dialog)
                self.peak_display.peakShiftLeft.connect(lambda: self.shift_trace(x_point, 'left'))
                self.peak_display.peakShiftRight.connect(lambda: self.shift_trace(x_point, 'right'))

    def move_peak_start(self, x_axis_time, peak_index):
        """
        Moves the peak window start point to where ever the user clicked on the screen
        :param x_axis_time:
        :param peak_index:
        :return:
        """
        x_axis_time = x_axis_time + 1

        picked_peak_start = int(self.nutrient_processing_controller.get_peak_starts()[peak_index])

        win_start = int(self.nutrient_processing_controller.get_window_start())
        win_length = int(self.nutrient_processing_controller.get_window_size())

        # If picked point is less than the end of the peak window i.e. valid
        if x_axis_time < (picked_peak_start + win_start + win_length):

            # If picked point is further along than the current peak window
            if x_axis_time > (picked_peak_start + win_start):
                window_start_time = x_axis_time - picked_peak_start
                new_window_length = win_length - (x_axis_time - (picked_peak_start+win_start))
                self.nutrient_processing_controller.set_window_start(window_start_time)
                self.nutrient_processing_controller.set_window_size(new_window_length)

            # If picked point is less than the start of the peak window
            if x_axis_time < (picked_peak_start + win_start):
                window_start_time = x_axis_time - picked_peak_start
                new_window_length = win_length + ((picked_peak_start+win_start) - x_axis_time)
                self.nutrient_processing_controller.set_window_start(window_start_time)
                self.nutrient_processing_controller.set_window_size(new_window_length)

            # If point is actually less than the value given of the peak starts...
            if x_axis_time < picked_peak_start:
                time_offset = picked_peak_start - x_axis_time
                adjusted_peak_starts = [p_s - time_offset for p_s in self.view_slk_data.peak_starts]
                self.nutrient_processing_controller.set_peak_starts(adjusted_peak_starts)

            self.nutrient_processing_controller.re_process()

    def move_peak_end(self, x_axis_time, peak_index):
        """
        Moves the peak end after a user has clicked into a spot on the trace and pressed move end
        :param x_axis_time:
        :param peak_index:
        :return:
        """
        picked_peak_start = int(self.view_slk_data.peak_starts[self.current_nutrient][peak_index])
        win_start = int(self.nutrient_processing_controller.get_window_start())
        win_length = int(self.nutrient_processing_controller.get_window_size())

        if x_axis_time > (picked_peak_start + win_start):

            window_end = picked_peak_start + win_start + win_length

            if x_axis_time > window_end:
                window_end_increase = x_axis_time - window_end
                self.nutrient_processing_controller.set_window_size(win_length + window_end_increase + 1)

            if window_end > x_axis_time:
                window_end_decrease = window_end - x_axis_time
                self.nutrient_processing_controller.set_window_size(win_length - window_end_decrease)

            self.nutrient_processing_controller.re_process()

    def shift_trace(self, x_axis_time, direction):
        """
        Function for physically shifting the whole trace by 3 time points. Used to realign the trace if necessary
        :param x_axis_time:
        :param direction:
        :return:
        """
        if direction == 'right':
            self.nutrient_processing_controller.add_to_chd(x_axis_time)
        elif direction == 'left':
            self.nutrient_processing_controller.cut_from_chd(x_axis_time)

        self.nutrient_processing_controller.re_process()

    def keyPressEvent(self, event):
        """
        Handles keyboard button presses and completes functions accordingly
        :param event:
        :return:
        """
        k_id = event.key()
        mods = event.modifiers()

        window_start = int(self.nutrient_processing_controller.get_window_start())
        window_size = int(self.nutrient_processing_controller.get_window_size())

        print(f'Key ID pressed: {event.key()}')
        if k_id == Qt.Key_A: # Assign A to move left
            self.move_camera_left()
        elif k_id == Qt.Key_D: # Assign D to move right
            self.move_camera_right()
        elif k_id == Qt.Key_W:
            # Assign W to zoom in
            self.zoom_in()
        elif k_id == Qt.Key_X:
            # Assign X to zoom out
            self.zoom_out()
        elif k_id == Qt.Key_S:
            # Assign S to zoom fit
            self.zoom_fit()
        elif k_id == Qt.Key_Q:
            # Toggle the zoom toggle
            if self.auto_size.isChecked():
                self.auto_size.setChecked(False)
            else:
                self.auto_size.setChecked(True)
        elif k_id == Qt.Key_N:
            # Iterate through the QC tabs
            curr_tab = self.qctabs.currentIndex()
            if curr_tab == (len(self.qctabs)-1):
                self.qctabs.setCurrentIndex(0)
            else:
                self.qctabs.setCurrentIndex(curr_tab+1)

        elif k_id == Qt.Key_Z:
            if mods == Qt.ShiftModifier:
                # If SHIFT is combo'd then lets just move the start left, keeping the end in the same place
                self.nutrient_processing_controller.set_window_start(window_start - 2)
                self.nutrient_processing_controller.set_window_size(window_size + 2)

            elif mods == Qt.AltModifier:
                # If ALT is combo'd then lets shrink the window from the left side
                self.nutrient_processing_controller.set_window_start(window_start + 2)
                self.nutrient_processing_controller.set_window_size(window_size - 2)

            else:
                # Shift the peak windows to the right
                self.nutrient_processing_controller.set_window_start(window_start - 2)
                self.nutrient_processing_controller.re_process()

            self.nutrient_processing_controller.re_process()

        elif k_id == Qt.Key_C:
            if mods == Qt.ShiftModifier:
                # If SHIFT is combo'd then lets extend the window to the right
                self.nutrient_processing_controller.set_window_size(window_size + 2)
                self.nutrient_processing_controller.re_process()

            elif mods == Qt.AltModifier:
                # If ALT is combo'd then lets shrink the window from the right side
                self.nutrient_processing_controller.set_window_size(window_size - 2)
                self.nutrient_processing_controller.re_process()

            else:
                self.nutrient_processing_controller.set_window_start(window_start + 2)
                self.nutrient_processing_controller.re_process()

            self.nutrient_processing_controller.re_process()

        # Below is only meant to be used for DEVELOPMENT PURPOSES, used to inject random values into peak picking
        # to check how the software responds, used to check speed of processing and robustness
        elif k_id == Qt.Key_R: # R Imitates changing peak windows etc, for testing optimisation of processing and draw
            random_modifier = np.random.randint(low=15, high=45)
            self.nutrient_processing_controller.set_window_start(random_modifier)
            self.nutrient_processing_controller.set_window_size(random_modifier)

            reset_flags = [self.view_w_d.quality_flag[i] if x not in [4,5] else 1 for i, x in enumerate(self.view_w_d.quality_flag)]
            self.nutrient_processing_controller.set_quality_flags(reset_flags)

            self.nutrient_processing_controller.re_process()

    def move_camera_left(self):
        """
        Shifts the camera to the left on a button press, happy balance of movement seems to be 6.5% of the current
        X axis range. Also will dynamically zoom to the tallest peak if the Auto Zoom checkbox is ticked
        :return:
        """
        result = HyproComplexities.move_camera_calc(self.graph_widget)
        if result:
            new_x_min, new_x_max = result
            self.graph_widget.setXRange(new_x_min, new_x_max)

            if self.auto_size.isChecked():
                self.zoom_fit()

    def move_camera_right(self):
        """
        Shifts the camera to the right on a button press. See shift camera left for more detail
        :return:
        """
        ad_max = len(self.view_chd_data.ad_data[self.current_nutrient])
        result = HyproComplexities.move_camera_calc(self.graph_widget, right=True, ad_max=ad_max)
        if result:
            new_x_min, new_x_max = result
            self.graph_widget.setXRange(new_x_min, new_x_max)

            if self.auto_size.isChecked():
                self.zoom_fit()

    def zoom_in(self):
        """
        Zooms in on the plot, zooms on both the X and Y
        :return:
        """
        ad_min = min(self.view_chd_data.ad_data[self.current_nutrient])
        res = HyproComplexities.zoom(self.graph_widget, ad_min=ad_min)
        if res:
            new_x_min, new_x_max, new_y_min, new_y_max = res

            if new_y_min < 0:
                new_y_min = 0

            self.graph_widget.setXRange(new_x_min, new_x_max)
            self.graph_widget.setYRange(new_y_min, new_y_max)

    def zoom_out(self):
        """
        Zooms out on the plot, zooms out on both the X and Y
        :return:
        """
        ad_max = max(self.view_chd_data.ad_data[self.current_nutrient])

        res = HyproComplexities.zoom(self.graph_widget, ad_max=ad_max, out=True)
        if res:
            new_x_min, new_x_max, new_y_min, new_y_max = res
            if new_y_min < 0:
                new_y_min = 0
            self.graph_widget.setXRange(new_x_min, new_x_max)
            self.graph_widget.setYRange(new_y_min, new_y_max)

    def zoom_fit(self):
        """
        Used to zoom to the height of the tallest peak in the current view, adds a little extra so the top isn't
        in line with the plot top
        :return:
        """
        # Used to zoom to the tallest peak plus a little extra so it isn't touch the top
        trace_state = self.graph_widget.getViewBox().state
        x_min = trace_state['viewRange'][0][0]
        x_max = trace_state['viewRange'][0][1]
        y_min = trace_state['viewRange'][1][0]
        y_max = trace_state['viewRange'][1][1]

        if x_min < 0:
            x_min = 0
        if y_min < 0:
            y_min = 0

        max_height = max(self.view_chd_data.ad_data[self.current_nutrient][int(x_min): int(x_max)])

        y_min = 0

        self.graph_widget.setYRange(y_min, max_height * 1.02)

    def validate_cup_type(self):
        #TODO: add cuptype validation logic here
        pass

    def update_from_dialog(self, updates):
        updated_peak_index = updates['peak_index']
        self.nutrient_processing_controller.set_one_cup_type(updated_peak_index, updates['cup_type'])
        self.nutrient_processing_controller.set_one_dilution_factor(updated_peak_index, updates['dilution_factor'])

        numerical_flag = self.REVERSE_FLAG_CONVERTER[updates['quality_flag']]
        self.nutrient_processing_controller.set_one_quality_flag(updated_peak_index, numerical_flag)

        self.nutrient_processing_controller.re_process()

    def create_standard_qc_tabs(self):
        """
        This function creates all the QTabs that hold the QC plots which are integral to the correct processing of
        an analysis, this includes Drift, Baseline, Calibration curve and calibration errors
        :return:
        """
        standard_tabs = {'cal_curve': 'Calibration', 'cal_error': 'Cal Error', 'baseline': 'Baseline Corr', 'drift': 'Drift Corr'}

        if self.view_w_d.analyte == 'nitrate':
            standard_tabs = {'cal_curve': 'Calibration', 'cal_error': 'Cal Error', 'recovery': 'NOx Recovery',
                             'baseline': 'Baseline Corr', 'drift': 'Drift Corr'}

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
        """
        Creates all the QTabs for holding the QC plots which come from samples that may or may not be present in an
        analytical run, this includes RMNS, MDL, internal QC or BQC
        :param sample_ids:
        :param qc_samps:
        :return:
        """
        self.qc_tabs_in_existence = []
        self.rmns_plots = []

        sample_ids_set = set(sample_ids)
        sample_ids_set_loop = [x for x in sample_ids_set]
        # Got to remove the samples that have a TEST in their sample name
        for s_id in sample_ids_set_loop:
            if 'test' in s_id.lower():
                sample_ids_set.remove(s_id)

        # Iterate through the potential QC samples to create their plot tab
        for qc in qc_samps:
            if qc == 'driftcheck':
                # Ignore the drift check QC sample
                pass
            else:
                check_sample_id_list = [(qc_samps[qc] in s_id) for s_id in sample_ids_set]
                if any(check_sample_id_list):
                    # If the QC sample was in the sample ID set then create its plot tab
                    qc_name = ''.join(i for i in qc_samps[qc].replace(" ", "") if not i.isdigit())
                    setattr(self, "{}".format(qc_name + '_tab'), QWidget())

                    self.qctabs.addTab(getattr(self, "{}".format(qc_name + '_tab')), str(qc_samps[qc]))
                    setattr(self, "{}".format(qc_name + '_lout'), QVBoxLayout())
                    getattr(self, "{}".format(qc_name + '_tab')).setLayout(getattr(self, "{}".format(qc_name + '_lout')))
                    setattr(self, "{}".format(qc_name + '_fig'), plt.figure())
                    setattr(self, "{}".format(qc_name + '_canvas'), FigureCanvas(getattr(self, "{}".format(qc_name + '_fig'))))

                    # Slightly different for RMNS - got to create multiple subplots if there are more than 1 lot in the analysis
                    if qc == 'rmns':
                        rmns_list = [x for x in sample_ids_set if qc_samps[qc] in x and x[0:4].lower() != 'test']
                        for i, rmns in enumerate(rmns_list):
                            rmns_name = ''.join(i for i in rmns.replace(" ", "") if not i.isdigit())
                            setattr(self, (rmns_name+'_plot'), getattr(self, "{}".format(qc_name+'_fig')).add_subplot(len(rmns_list), 1, i+1))
                            self.rmns_plots.append(rmns_name)
                    else:
                        setattr(self, "{}".format(qc_name + str('_plot')), getattr(self, "{}".format(qc_name + '_fig')).add_subplot(111))
                    getattr(self, "{}".format(qc_name + str('_lout'))).addWidget(getattr(self, "{}".format(qc_name + str('_canvas'))))
                    self.qc_tabs_in_existence.append(qc_name)

    def plot_standard_data(self):
        """
        Small function that houses all the calls to the plotting of the standard QC tab plots
        :return:
        """
        qcp.calibration_curve_plot(self.cal_curve_fig, self.cal_curve_plot,
                                   self.view_w_d.calibrant_medians, self.view_w_d.calibrant_concs,
                                   self.view_w_d.calibrant_flags, self.view_w_d.calibration_coefficients,
                                   self.view_w_d.calibration_r_score, title_append=self.plot_title_appender)
        self.cal_curve_canvas.draw()

        analyte_error = self.processing_parameters['nutrientprocessing']['processingpars'][self.current_nutrient]['calerror']
        qcp.calibration_error_plot(self.cal_error_fig, self.cal_error_plot,
                                   self.view_w_d.calibrant_indexes, self.view_w_d.calibrant_residuals, analyte_error,
                                    self.view_w_d.calibrant_flags, title_append=self.plot_title_appender)
        self.cal_error_canvas.draw()

        qcp.basedrift_correction_plot(self.baseline_fig, self.baseline_plot,
                                      self.baseline_plot2, 'Baseline', self.view_w_d.baseline_indexes,
                                      self.view_w_d.baseline_corr_percent, self.view_w_d.baseline_medians,
                                      self.view_w_d.baseline_flags, title_append=self.plot_title_appender)
        self.baseline_canvas.draw()

        qcp.basedrift_correction_plot(self.drift_fig, self.drift_plot,
                                      self.drift_plot2, 'Drift', self.view_w_d.drift_indexes,
                                      self.view_w_d.drift_corr_percent, self.view_w_d.drift_medians, self.view_w_d.drift_flags,
                                      title_append=self.plot_title_appender)
        self.drift_canvas.draw()


        if self.view_w_d.analyte == 'nitrate':
            qcp.recovery_plot(self.recovery_fig, self.recovery_plot, self.view_w_d.recovery_indexes,
                              self.view_w_d.recovery_concentrations, self.view_w_d.recovery_ids,
                              self.view_w_d.recovery_flags, title_append=self.plot_title_appender)

            self.recovery_canvas.draw()

    def plot_custom_data(self):
        """
        Small function to house the calls to the QC tab plots for samples that may or may not be present in the run
        :return:
        """
        # Iterate through the confirmed samples in the run
        for qc in self.qc_tabs_in_existence:
            if qc.lower() == 'rmns':
                for rmns in self.rmns_plots:
                    plot = getattr(self, "{}".format(rmns + '_plot'))
                    concs = getattr(self.view_w_d, "{}".format(rmns + '_concentrations'))
                    indexes = getattr(self.view_w_d, "{}".format(rmns + '_indexes'))
                    flags = getattr(self.view_w_d, "{}".format(rmns + '_flags'))

                    qcp.rmns_plot(self.RMNS_fig, plot, indexes, concs, flags, rmns, self.current_nutrient)
                getattr(self, "{}".format(qc + '_fig')).set_tight_layout(tight=True)
                getattr(self, "{}".format(qc + '_canvas')).draw()

            else:
                if qc.lower() == 'mdl':
                    qcp.mdl_plot(self.MDL_fig, self.MDL_plot, self.view_w_d.MDL_indexes, self.view_w_d.MDL_concentrations,
                                 self.view_w_d.MDL_flags)

                elif qc.lower() == 'bqc':
                    qcp.bqc_plot(self.BQC_fig, self.BQC_plot, self.view_w_d.BQC_indexes, self.view_w_d.BQC_concentrations,
                                 self.view_w_d.BQC_flags)

                # elif qc.lower() == 'intqc':
                #     qcp.intqc_plot(self.IntQC_fig, self.IntQC_plot, self.view_w_d.)
                    # pass

    def closeEvent(self, event):
        plt.close('all')
        del self.plotted_data
        del self.graph_widget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = processingNutrientsWindow('in2018_v01nut001.SLK', 'C:/Users/she384/Documents/HyPro_Dev/in2019_v05/-in2019_v05Data.db', 'C:/Users/she384/Documents/HyPro_Dev', 'in2018_v01')
    sys.exit(app.exec_())

