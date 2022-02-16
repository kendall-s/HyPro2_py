from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QDockWidget, QListWidget, QVBoxLayout, QTabWidget,
                             QDesktopWidget, QApplication, QLineEdit, QHBoxLayout, QSplitter, QAction)
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pylab import *
import processing.plotting.QCPlots as qcp
import sys, logging, traceback, os
import json
import hyproicons
import style
import processing.procdata.ProcessSealNutrients as psn
from processing.algo.HyproComplexities import save_proc_settings, load_proc_settings, match_click_to_peak, match_hover_to_peak
from processing.algo import HyproComplexities
from dialogs.TraceSelectionDialog import traceSelection
from processing.algo.Structures import WorkingData, SLKData, CHDData
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate
from processing.plotting.TracePlot import TracePlotter
import pyqtgraph as pg
from processing.procdata.ProcessNutrientsController import processNutrientsController

import cProfile
#background-color: #ededed;

mpl.use('Agg')

# TODO: Finish new implementation of cleaned up testable Nutrients

class processingNutrientsWindow(hyproMainWindowTemplate):

    """
    This is the class that handles the GUI interface for Nutrient processing

    Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad,
                    91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different

    """

    processing_completed = pyqtSignal()
    logging_signal = pyqtSignal(str)
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

        self.standard_plots = {}
        self.custom_plots = {}

        self.perf_mode = perf_mode
        self.ultra_perf_mode = ultra_perf_mode

        self.reverted_history_index = 999

        self.ui_initialised = False
        self.plot_title_appender = ''

        self.actions_list = {'initial_window_start': {}, 'initial_window_size': {}}

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

        # Pull out the data from the files in the directoryR
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
        self.processing_thread = QThread()

        self.nutrient_processing_controller = processNutrientsController(self.file,
                                                                         self.file_path,
                                                                         self.database,
                                                                         self.processing_parameters)
        self.nutrient_processing_controller.moveToThread(self.processing_thread)
        self.processing_thread.started.connect(self.nutrient_processing_controller.startup_routine)
        
        # After startup and subsequent reprocessing, update the UI elements
        self.nutrient_processing_controller.startup_routine_completed.connect(self.update_ui)
        self.nutrient_processing_controller.reprocessing_completed.connect(self.update_ui)
        
        # Set cursor based on what the processing controller is up to
        self.nutrient_processing_controller.thinking.connect(self.loading_cursor)
        self.nutrient_processing_controller.startup_routine_completed.connect(self.reset_cursor)
        self.nutrient_processing_controller.reprocessing_completed.connect(self.reset_cursor)

        self.processing_thread.start()

    def loading_cursor(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def reset_cursor(self):
        QApplication.restoreOverrideCursor()

    def update_ui(self, return_package):
        if return_package:
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
                    qc_cups = self.processing_parameters['nutrient_processing']['qc_sample_names']
                    self.create_custom_qc_tabs(self.view_slk_data.sample_ids, qc_cups)

                    self.actions_list[self.current_nutrient] = []
                    self.actions_list['initial_window_start'][self.current_nutrient] = self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_start']
                    self.actions_list['initial_window_size'][self.current_nutrient] = self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_size']

            self.interactive_routine(trace_redraw=trace_redraw)
        else:
            self.logging_signal.emit('Cannot find any nutrients in the SLK file. Check the naming in parameters?')
            #logging.info('Cannot find any nutrients in the SLK file. Check the naming in parameters?')
            self.processing_thread.quit()
            self.destroy(destroyWindow=True)

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

        # The show call is here as the very last thing - so we do not blind the user with a white screen
        self.show()

    def init_ui(self):
        """
        Initialises all the GUI elements required for the nutrient processing window
        :return:
        """
        try:

            self.setFont(QFont('Segoe UI'))

            self.setWindowModality(Qt.WindowModal)
            self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

            self.grid_layout.setSpacing(0)

            """
            Menu bar 
            """
            mainMenu = self.menuBar()
            fileMenu = mainMenu.addMenu('File')
            self.auto_size = QAction('Auto Zoom', mainMenu, checkable=True)
            fileMenu.addAction(self.auto_size)
            self.find_lat_lons = QAction('Match Lat/Longs', mainMenu, checkable=True)
            fileMenu.addAction(self.find_lat_lons)

            fileMenu.addSeparator()

            reset_inital_windows = QAction('Reset Initial Windows', self)
            fileMenu.addAction(reset_inital_windows)
            reset_inital_windows.triggered.connect(self.reset_initial_windows)
            reset_inital_windows.setEnabled(False)

            replay_processing = QAction('Replay Processing', self)
            fileMenu.addAction(replay_processing)
            replay_processing.triggered.connect(self.replay_processing)
            replay_processing.setEnabled(False)

            if os.path.exists(f'{self.path}/Nutrients/processing/{self.file}_procfile.json'):
                reset_inital_windows.setEnabled(True)
                replay_processing.setEnabled(True)

            editMenu = mainMenu.addMenu('Edit')

            undo_action = QAction('Undo', self)
            editMenu.addAction(undo_action)
            undo_action.triggered.connect(self.undo_action)


            """
            Widgets for UI
            """

            # View splitter + the left and right Vertical Box layouts
            self.view_splitter = QSplitter(Qt.Horizontal)
            self.grid_layout.addWidget(self.view_splitter, 0, 0)

            left_v_widget = QWidget(self)
            left_v_box = QVBoxLayout(self)
            left_v_widget.setLayout(left_v_box)

            self.qc_dock = QDockWidget('QC Tabs')

            self.qc_dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

            right_v_widget = QWidget(self)
            right_v_box = QVBoxLayout(self)
            right_v_widget.setLayout(right_v_box)

            self.qc_dock.setWidget(right_v_widget)

            self.addDockWidget(Qt.RightDockWidgetArea, self.qc_dock)

            # Processing trace
            label_text = f'Processing Nutrient File: {self.file} - Analyte: {self.current_nutrient.capitalize()}'
            self.analysistraceLabel = QLabel(label_text)
            #analysistraceLabel.setProperty('headerText', True)
            self.analysistraceLabel.setStyleSheet('font: 18px Segoe UI; font-weight: 500;')

            left_v_box.addWidget(self.analysistraceLabel)

            if not self.perf_mode:
                pg.setConfigOptions(antialias=True)

            # Creating the trace graphing widget
            self.graph_widget = pg.PlotWidget()

            if self.ultra_perf_mode:
                self.graph_widget.useOpenGL(True)

            label_style = {'color': '#C1C1C1', 'font-size': '11pt', 'font-family': 'Segoe UI'}
            self.graph_widget.setLabel('left', 'A/D Value', **label_style)
            self.graph_widget.setLabel('bottom', 'Time (s)', **label_style)
            self.graph_widget.showGrid(x=True, y=True)

            # Create the vertical line to indicate the mouse position
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

            # This lineedit displays information about the peak which is hovered above
            self.hovered_peak_lineedit = QLineEdit()
            self.hovered_peak_lineedit.setFont(QFont('Segoe UI'))

            left_v_box.addWidget(self.graph_widget)
            left_v_box.addWidget(self.hovered_peak_lineedit)

            trace_control_buttons_widget = QWidget()
            trace_control_buttons_layout = QHBoxLayout()
            trace_control_buttons_layout.setSpacing(20)
            trace_control_buttons_widget.setLayout(trace_control_buttons_layout)
            left_v_box.addWidget(trace_control_buttons_widget)

            trace_control_buttons_layout.addStretch()

            leftonxaxis = QPushButton()
            leftonxaxis.clicked.connect(self.move_camera_left)
            leftonxaxis.setIcon(QIcon(':/assets/greenleftarrow.svg'))
            leftonxaxis.setIconSize(QSize(33, 33))
            leftonxaxis.setProperty('nutrientControls', True)
            leftonxaxis.setFixedWidth(50)
            leftonxaxis.setToolTip('Move left on the X axis')
            leftonxaxis.setCursor(QCursor(Qt.PointingHandCursor))

            rightonxaxis = QPushButton()
            rightonxaxis.clicked.connect(self.move_camera_right)
            rightonxaxis.setIcon(QIcon(':/assets/greenrightarrow.svg'))
            rightonxaxis.setIconSize(QSize(33, 33))
            rightonxaxis.setProperty('nutrientControls', True)
            rightonxaxis.setFixedWidth(50)
            rightonxaxis.setToolTip('Move right on the X axis')
            rightonxaxis.setCursor(QCursor(Qt.PointingHandCursor))

            zoomin = QPushButton()
            zoomin.clicked.connect(self.zoom_in)
            zoomin.setIcon(QIcon(':/assets/zoomin.svg'))
            zoomin.setIconSize(QSize(33, 33))
            zoomin.setProperty('nutrientControls', True)
            zoomin.setFixedWidth(50)
            zoomin.setToolTip('Zoom in')
            zoomin.setCursor(QCursor(Qt.PointingHandCursor))

            zoomout = QPushButton()
            zoomout.clicked.connect(self.zoom_out)
            zoomout.setIcon(QIcon(':/assets/zoomout.svg'))
            zoomout.setIconSize(QSize(33, 33))
            zoomout.setProperty('nutrientControls', True)
            zoomout.setFixedWidth(50)
            zoomout.setToolTip('Zoom out')
            zoomout.setCursor(QCursor(Qt.PointingHandCursor))

            zoomfit = QPushButton()
            zoomfit.clicked.connect(self.zoom_fit)
            zoomfit.setIcon(QIcon(':/assets/expand.svg'))
            zoomfit.setIconSize(QSize(33, 33))
            zoomfit.setProperty('nutrientControls', True)
            zoomfit.setFixedWidth(50)
            zoomfit.setToolTip('Scale to highest peak')
            zoomfit.setCursor(QCursor(Qt.PointingHandCursor))


            trace_control_buttons_layout.addWidget(leftonxaxis)
            trace_control_buttons_layout.addWidget(zoomin)
            trace_control_buttons_layout.addWidget(zoomfit)
            trace_control_buttons_layout.addWidget(zoomout)
            trace_control_buttons_layout.addWidget(rightonxaxis)

            trace_control_buttons_layout.addStretch()

            self.history_list_dock = QDockWidget('History')

            self.history_list = QListWidget()
            self.history_list.itemDoubleClicked.connect(self.history_revert)

            self.history_list_dock.setWidget(self.history_list)

            self.addDockWidget(Qt.RightDockWidgetArea, self.history_list_dock)

            """
            Right Side with QC Tabs
            """

            # self.qctabs_label = QLabel('<b>QC Charts:</b>', )
            # self.qctabs_label.setStyleSheet('font: 17px Segoe UI;')
            # right_v_box.addWidget(self.qctabs_label)

            self.qctabs = QTabWidget()
            right_v_box.addWidget(self.qctabs)

            process_control_buttons = QHBoxLayout()
            process_control_buttons.setSpacing(20)
            #right_v_box.addLayout(process_control_buttons)
            self.grid_layout.addLayout(process_control_buttons, 1, 0)

            process_control_buttons.addStretch()

            ok_but = QPushButton('Proceed')
            ok_but.setFixedHeight(30)
            ok_but.setFixedWidth(125)
            ok_but.clicked.connect(self.proceed)
            ok_but.setProperty('nutrientControls', True)
            ok_but.setStyleSheet("background-color: #0275D8; color: #FFFFFF; font-weight: 500; border: 1px #0275D8;")
            ok_but.setCursor(QCursor(Qt.PointingHandCursor))

            process_control_buttons.addWidget(ok_but)

            cancel_but = QPushButton('Cancel')
            cancel_but.clicked.connect(self.cancel)
            cancel_but.setProperty('nutrientControls', True)
            cancel_but.setFixedHeight(30)
            cancel_but.setFixedWidth(120)
            cancel_but.setStyleSheet("font-weight: 500;")
            cancel_but.setCursor(QCursor(Qt.PointingHandCursor))

            process_control_buttons.addWidget(cancel_but)

            process_control_buttons.addStretch()

            self.view_splitter.addWidget(left_v_widget)

            self.tabifyDockWidget(self.history_list_dock, self.qc_dock)

            self.bootup = True
            self.ui_initialised = True

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

        """
        This is the function which runs when the user presses proceed. Here we store the data as processed
        then iterate to the next nutrient, if there is one.
        """

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

            if not os.path.exists(f'{self.path}/Nutrients/processing'):
                os.mkdir(f'{self.path}/Nutrients/processing')

            with open(f'{self.path}/Nutrients/processing/{self.file}_procfile.json', 'w+') as out_file:
                json.dump(self.actions_list, out_file)

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
            if hasattr(self, 'RMNS_fig'):
                self.RMNS_fig.savefig(f'{self.path}/Nutrients/plot/{self.file}/{self.current_nutrient}_rmns_plot.png',
                                        dpi=300)

            # Resave the processing settings to disk
            save_proc_settings(self.path, self.project, self.processing_parameters)

            # Try to increment the current nutrient - if an index error is raised, there is no more nutrients to process
            self.current_nutrient = self.view_slk_data.active_nutrients[current_nut_index+1]

            self.analysistraceLabel.setText('<b>Processing file: </b>' + str(self.file) +
                                            '   |   <b>Analysis Trace: </b>' + str(self.current_nutrient).capitalize())

            self.view_w_d.analyte = self.current_nutrient
            self.actions_list[self.current_nutrient] = []
            self.history_list.clear()

            self.nutrient_processing_controller.set_current_nutrient(self.current_nutrient)

            self.plot_title_appender = f' - {self.current_nutrient.capitalize()} | {self.file}'

            self.graph_widget.removeItem(self.window_lines)

            self.reset_cursor()
            self.nutrient_processing_controller.re_process()

        except IndexError:
            self.processing_thread.quit()
            time.sleep(0.3)
            logging.info(f'Processing successfully completed for nutrient file - {self.file}')
            self.reset_cursor()
            plt.close('all')
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
            x_point = int(data_coordinates.x())

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
                self.peak_display.saveSig.connect(self.update_from_dialog)
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
                new_window_start_time = x_axis_time - picked_peak_start
                self.add_action('window_start_set', new_window_start_time, win_start)

                new_window_length = win_length - (x_axis_time - (picked_peak_start+win_start))
                self.add_action('window_length_set', new_window_length, win_length)

                self.nutrient_processing_controller.set_window_start(new_window_start_time)
                self.nutrient_processing_controller.set_window_size(new_window_length)

            # If picked point is less than the start of the peak window
            if x_axis_time < (picked_peak_start + win_start):
                new_window_start_time = x_axis_time - picked_peak_start
                self.add_action('window_start_set', new_window_start_time, win_start)

                new_window_length = win_length + ((picked_peak_start+win_start) - x_axis_time)
                self.add_action('window_length_set', new_window_length, win_length)

                self.nutrient_processing_controller.set_window_start(new_window_start_time)
                self.nutrient_processing_controller.set_window_size(new_window_length)

            # If point is actually less than the value given of the peak starts...
            if x_axis_time < picked_peak_start:
                time_offset = picked_peak_start - x_axis_time
                adjusted_peak_starts = [p_s - time_offset for p_s in self.view_slk_data.clean_peak_starts[self.current_nutrient]]
                self.add_action('adjust_peak_starts', time_offset, time_offset)

                self.nutrient_processing_controller.set_clean_peak_starts(adjusted_peak_starts)

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
            # User has clicked past the end of the window
            if x_axis_time > window_end:
                window_end_increase = x_axis_time - window_end
                new_window_length = win_length + window_end_increase + 1
                self.add_action('window_length_set', new_window_length, win_length)
                self.nutrient_processing_controller.set_window_size(win_length + window_end_increase + 1)

            # User has clicked before the end of the peak window
            if window_end > x_axis_time:
                window_end_decrease = window_end - x_axis_time
                new_window_length = win_length - window_end_decrease
                self.add_action('window_length_set', new_window_length, win_length)
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
            self.add_action('add_to_chd', x_axis_time, x_axis_time)
        elif direction == 'left':
            self.nutrient_processing_controller.cut_from_chd(x_axis_time)
            self.add_action('cut_from_chd', x_axis_time, x_axis_time)

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

        #print(f'Key ID pressed: {event.key()}')
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

        elif k_id == Qt.Key_P:
            print(self.actions_list)


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
            print(new_x_min)
            print(new_x_max)

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


    def update_from_dialog(self, updates):
        updated_peak_index = updates['peak_index']

        previous_cup_type = self.view_slk_data.cup_types[updated_peak_index]
        if previous_cup_type != updates['cup_type']:
            self.nutrient_processing_controller.set_one_cup_type(updated_peak_index, updates['cup_type'])
            self.add_action('update_cup_type', updates['cup_type'], previous_cup_type, peak=updated_peak_index)

        previous_dilution = self.view_w_d.dilution_factor[updated_peak_index]
        if previous_dilution != updates['dilution_factor']:
            self.nutrient_processing_controller.set_one_dilution_factor(updated_peak_index, updates['dilution_factor'])
            self.add_action('update_dilution', updates['dilution_factor'], previous_dilution, peak=updated_peak_index)

        numerical_flag = self.REVERSE_FLAG_CONVERTER[updates['quality_flag']]
        previous_flag = self.view_w_d.quality_flag[updated_peak_index]
        if previous_flag != numerical_flag:
            self.nutrient_processing_controller.set_one_quality_flag(updated_peak_index, numerical_flag)
            self.add_action('update_flag', numerical_flag, previous_flag, peak=updated_peak_index)

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
            
            # Logic here is we dynamically create the plot tabs and store them in the dict
            # Structure being {'baseline': {'tab': tab, 'layout': layout, 'fig': fig, 'canvas': canvas}}

            self.standard_plots[qc] = {}

            self.standard_plots[qc]['tab'] = QWidget()
            self.qctabs.addTab(self.standard_plots[qc]['tab'], standard_tabs[qc])

            self.standard_plots[qc]['layout'] = QVBoxLayout()
            self.standard_plots[qc]['tab'].setLayout(self.standard_plots[qc]['layout'])
            self.standard_plots[qc]['fig'] = plt.figure()
            self.standard_plots[qc]['canvas'] = FigureCanvas(self.standard_plots[qc]['fig'])

            if qc == 'baseline' or qc == 'drift':
                self.standard_plots[qc]['plot'] = self.standard_plots[qc]['fig'].add_subplot(211)
                self.standard_plots[qc]['plot2'] = self.standard_plots[qc]['fig'].add_subplot(212)
            else:
                self.standard_plots[qc]['plot'] = self.standard_plots[qc]['fig'].add_subplot(111)

            self.standard_plots[qc]['layout'].addWidget(self.standard_plots[qc]['canvas'])

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
                    self.custom_plots[qc_name] = {}
                    self.custom_plots[qc_name]['tab'] = QWidget()
                    self.qctabs.addTab(self.custom_plots[qc_name]['tab'], qc_name)
                    self.custom_plots[qc_name]['layout'] = QVBoxLayout()
                    self.custom_plots[qc_name]['tab'].setLayout(self.custom_plots[qc_name]['layout'])
                    self.custom_plots[qc_name]['fig'] = plt.figure()
                    self.custom_plots[qc_name]['canvas'] = FigureCanvas(self.custom_plots[qc_name]['fig'])

                    # Slightly different for RMNS - got to create multiple subplots if there are more than 1 lot in the analysis
                    if qc == 'rmns':
                        rmns_list = [x for x in sample_ids_set if qc_samps[qc] in x and x[0:4].lower() != 'test']
                        for i, rmns in enumerate(rmns_list):
                            rmns_name = ''.join(i for i in rmns.replace(" ", "") if not i.isdigit())
                            self.custom_plots[qc_name]['plot'+rmns_name] = self.custom_plots[qc_name]['fig'].add_subplot(len(rmns_list), 1, i+1)
                            self.rmns_plots.append(rmns_name)
                    else:
                        self.custom_plots[qc_name]['plot'] = self.custom_plots[qc_name]['fig'].add_subplot(111)

                    self.custom_plots[qc_name]['layout'].addWidget(self.custom_plots[qc_name]['canvas'])
                    self.qc_tabs_in_existence.append(qc_name)

    def plot_standard_data(self):
        """
        Small function that houses all the calls to the plotting of the standard QC tab plots
        :return:
        """
        qcp.calibration_curve_plot(self.standard_plots['cal_curve']['fig'], self.standard_plots['cal_curve']['plot'],
                                    self.view_w_d.calibrant_medians, self.view_w_d.calibrant_concs,
                                    self.view_w_d.calibrant_flags, self.view_w_d.calibration_coefficients,
                                    self.view_w_d.calibration_r_score, title_append=self.plot_title_appender)
        self.standard_plots['cal_curve']['canvas'].draw()

        analyte_error = self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['cal_error']
        qcp.calibration_error_plot(self.standard_plots['cal_error']['fig'], self.standard_plots['cal_error']['plot'],
                                   self.view_w_d.calibrant_indexes, self.view_w_d.calibrant_residuals, analyte_error,
                                    self.view_w_d.calibrant_flags, title_append=self.plot_title_appender)
        self.standard_plots['cal_error']['canvas'].draw()

        qcp.basedrift_correction_plot(self.standard_plots['baseline']['fig'], self.standard_plots['baseline']['plot'],
                                      self.standard_plots['baseline']['plot2'], 'Baseline', self.view_w_d.baseline_indexes,
                                      self.view_w_d.baseline_corr_percent, self.view_w_d.baseline_medians,
                                      self.view_w_d.baseline_flags, title_append=self.plot_title_appender)
        self.standard_plots['baseline']['canvas'].draw()

        qcp.basedrift_correction_plot(self.standard_plots['drift']['fig'], self.standard_plots['drift']['plot'],
                                      self.standard_plots['drift']['plot2'], 'Drift', self.view_w_d.drift_indexes,
                                      self.view_w_d.drift_corr_percent, self.view_w_d.drift_medians, self.view_w_d.drift_flags,
                                      title_append=self.plot_title_appender)
        self.standard_plots['drift']['canvas'].draw()


        if self.view_w_d.analyte == 'nitrate':
            qcp.recovery_plot(self.standard_plots['recovery']['fig'], self.standard_plots['recovery']['plot'], 
                                self.view_w_d.recovery_indexes, self.view_w_d.recovery_concentrations, 
                                self.view_w_d.recovery_ids, self.view_w_d.recovery_flags, 
                                title_append=self.plot_title_appender)

            self.standard_plots['recovery']['canvas'].draw()

    def plot_custom_data(self):
        """
        Small function to house the calls to the QC tab plots for samples that may or may not be present in the run
        :return:
        """
        # Iterate through the confirmed samples in the run
        for qc in self.qc_tabs_in_existence:
            if qc.lower() == 'rmns':
                for rmns in self.rmns_plots:
                    fig = self.custom_plots['rmns']['fig']
                    plot = self.custom_plots['rmns']['plot'+rmns]
                    concs = getattr(self.view_w_d, "{}".format(rmns + '_concentrations'))
                    indexes = getattr(self.view_w_d, "{}".format(rmns + '_indexes'))
                    flags = getattr(self.view_w_d, "{}".format(rmns + '_flags'))

                    qcp.rmns_plot(fig, plot, indexes, concs, flags, rmns, self.current_nutrient)

                fig.set_tight_layout(tight=True)
                self.custom_plots['rmns']['canvas'].draw()

            else:
                if qc.lower() == 'mdl':
                    qcp.mdl_plot(self.custom_plots['MDL']['fig'], self.custom_plots['MDL']['plot'],
                                self.view_w_d.MDL_indexes, self.view_w_d.MDL_concentrations,
                                self.view_w_d.MDL_flags)

                elif qc.lower() == 'bqc':
                    qcp.bqc_plot(self.custom_plots['BQC']['fig'], self.custom_plots['BQC']['plot'],
                                self.view_w_d.BQC_indexes, self.view_w_d.BQC_concentrations,
                                self.view_w_d.BQC_flags)

                # elif qc.lower() == 'intqc':
                #     qcp.intqc_plot(self.IntQC_fig, self.IntQC_plot, self.view_w_d.)
                    # pass

    def reset_initial_windows(self):
        """
        Used by the menu button to reset the window start and size to what it was the first time the file was
        being processed. This should be ran before replaying processing.
        """
        with open(f'{self.path}/Nutrients/processing/{self.file}_procfile.json') as json_file:
            procfile_data = json.load(json_file)

        if self.current_nutrient in procfile_data['initial_window_start']:
            self.nutrient_processing_controller.set_window_start(procfile_data['initial_window_start'][self.current_nutrient])
            self.nutrient_processing_controller.set_window_size(procfile_data['initial_window_size'][self.current_nutrient])

            self.nutrient_processing_controller.re_process()


    # TODO: this could actually be turned into a class method of the nutrient processing controller.
    def replay_processing(self):
        """
        UI functionality for the replaying of processing steps

        """

        with open(f'{self.path}/Nutrients/processing/{self.file}_procfile.json') as json_file:
            procfile_data = json.load(json_file)

        actions  = procfile_data[self.current_nutrient]

        for action_step in actions:
            self.actions_list[self.current_nutrient].append(action_step)
            self.nutrient_processing_controller.replay_processing_step(action_step)

        self.history_list.clear()
        for action_step in self.actions_list[self.current_nutrient]:
            list_string = self.create_history_string(action_step['action'], action_step['old_value'], action_step['value'])
            self.history_list.addItem(list_string)

        self.nutrient_processing_controller.re_process()

    def add_action(self, action, new_value, old_value, peak=False):
        """
        Provide the functionality to add a action to the current actions list
        """
        if peak:
            obj = {'action': action, 'peak': peak, 'value': new_value, 'old_value': old_value}
        else:
            obj = {'action': action, 'value': new_value, 'old_value': old_value}

        # Our current point in time is at the singularity, meaning we can just append our next action
        if self.reverted_history_index > len(self.history_list):
            self.actions_list[self.current_nutrient].append(obj)
            self.history_list.addItem(self.create_history_string(action, old_value, new_value))
        # Else, we have to remove the steps which we have reverted, then save our new action
        else:
            self.actions_list[self.current_nutrient] = [x for x in self.actions_list[self.current_nutrient][0:self.reverted_history_index]]
            self.actions_list[self.current_nutrient].append(obj)
            self.history_list.clear()
            for action_step in self.actions_list[self.current_nutrient]:
                history_string = self.create_history_string(action_step['action'], action_step['old_value'], action_step['value'])
                self.history_list.addItem(history_string)

    def undo_action(self):
        """
        Undoes the last executed action
        """
        if len(self.actions_list[self.current_nutrient]) > 0:
            last_action = self.actions_list[self.current_nutrient][-1]
            self.actions_list[self.current_nutrient].pop(-1)

            self.nutrient_processing_controller.undo_processing_step(last_action)
            self.nutrient_processing_controller.re_process()

    def history_revert(self):
        """
        Handles determining the actions which need to be reverted in the history tree
        """
        # If the reverted history index is already less than the requested history selection, we should reapply
        # the steps instead of triggering undos
        if self.reverted_history_index < self.history_list.currentIndex().row():
            # Now assign the reverted_history_index to the selected row, because that will be where the history is at
            self.reverted_history_index = self.history_list.currentIndex().row()
            steps_to_reapply = self.actions_list[self.current_nutrient][self.reverted_history_index:]
            for action_step in steps_to_reapply:
                self.nutrient_processing_controller.replay_processing_step(action_step)

            self.history_list.setCurrentRow(self.reverted_history_index)
        # Else, we have available steps to go back on so lets undo them
        else:
            self.reverted_history_index = self.history_list.currentIndex().row()
            steps_to_revert = self.actions_list[self.current_nutrient][self.reverted_history_index:]

            # Lets go back through the steps in reverse order so that they are undone sequentially
            for action_step in reversed(steps_to_revert):
                self.nutrient_processing_controller.undo_processing_step(action_step)

            self.history_list.setCurrentRow(self.reverted_history_index)

        self.nutrient_processing_controller.re_process()


    def create_history_string(self, action, old_value, value):
        """
        Create the semi-human readable string to display in the history list
        """
        list_string = f"{action} ({old_value} ➡ {value})"
        return list_string


    def closeEvent(self, event):
        plt.close('all')
        try:
            self.processing_thread.exit()
            del self.plotted_data
            del self.graph_widget
            self.history_list_dock.close()
            self.qc_dock.close()
        except Exception:
            pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = processingNutrientsWindow('in2018_v01nut001.SLK', 'C:/Users/she384/Documents/HyPro_Dev/in2019_v05/-in2019_v05Data.db', 'C:/Users/she384/Documents/HyPro_Dev', 'in2018_v01')
    sys.exit(app.exec_())

