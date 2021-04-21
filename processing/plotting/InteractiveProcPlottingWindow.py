from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QApplication, QTabWidget, QVBoxLayout, QPushButton,
                             QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from processing.algo.HyproComplexities import find_closest, update_annotation, check_hover
from dialogs.BottleSelectionDialog import bottleSelection
import json
import time
import io
import hyproicons, style

flag_converter = {1 : 'Good', 2 : 'Suspect', 3 : 'Bad', 4 : 'Shape Sus', 5 : 'Shape Bad', 6: 'Cal Bad',
                    91 : 'CalError Sus', 92 : 'CalError Bad', 8 : 'Dup Diff'}

# TODO: This windows code could probably be scaled back and re-use some of the general plotting functionality, there is now some double ups i.e. flagging

class hyproProcPlotWindow(QMainWindow):
    redraw = pyqtSignal()

    def __init__(self, width, height, title, type, ref_ind, depths, full_data):
        super().__init__()

        self.initial_figure_save = True

        self.type = type
        self.working_quality_flags = full_data.quality_flag

        # Reference index back to the full data file of the plotted data. E.g. plotted data point 10 may be data point
        # 12 in the file. len(ref_ind) will always be less than len(values_in_file)
        self.ref_ind = ref_ind
        self.depths = depths
        self.full_data = full_data

        # This index is used to reference back to the full data, with indexes pulled out the ref_ind list variable
        self.referenced_index = 0

        # Set stylesheet to the one selected by the user.
        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        theme = params['theme']
        if params['theme'] == 'normal':
            plt.style.use(style.mplstyle['normal'])
        else:
            plt.style.use(style.mplstyle['dark'])

        # Setup window UI
        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.height_var = height
        self.width_var = width
        self.title = title

        self.setFont(QFont('Segoe UI'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.qv_box_layout = QVBoxLayout()
        self.qv_box_layout.setSpacing(5)

        self.setGeometry(400, 400, self.width_var, self.height_var)

        # Center window on active screen
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(self.title)

        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        self.edit_menu = self.main_menu.addMenu('Edit')

        self.export_sensor_one = QAction(QIcon(':/assets/archivebox.svg'), 'Export Sensor 1 Plot', self)
        self.export_sensor_one.triggered.connect(self.export_sensor_one_plot)
        self.file_menu.addAction(self.export_sensor_one)

        self.export_sensor_two = QAction(QIcon(':/assets/archivebox2.svg'), 'Export Sensor 2 Plot', self)
        self.export_sensor_two.triggered.connect(self.export_sensor_two_plot)
        self.file_menu.addAction(self.export_sensor_two)

        self.export_both_sensor = QAction('Export Both Sensor Plot', self)
        self.export_both_sensor.triggered.connect(self.export_both_sensor_plot)
        self.file_menu.addAction(self.export_both_sensor)

        self.copy_active_plot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
        self.copy_active_plot.setShortcut('Ctrl+C')
        self.copy_active_plot.triggered.connect(self.clipboard_copy_active_plot)
        self.edit_menu.addAction(self.copy_active_plot)

        # Each plot is held within its own tab
        self.tabs = QTabWidget()

        self.proceed = QPushButton('Proceed')
        self.proceed.setFixedWidth(180)
        self.proceed.clicked.connect(self.proceed_proc)

        """
        
        ** Primary Sensor Tab
        
        """
        self.sensor_one_tab = QWidget()
        self.sensor_one_tab.layout = QVBoxLayout()
        self.tabs.addTab(self.sensor_one_tab, 'Primary Sensor')

        self.sensor_one_figure = plt.figure()
        self.sensor_one_figure.set_tight_layout(tight=True)
        self.sensor_one_canvas = FigureCanvas(self.sensor_one_figure)
        self.sensor_one_canvas.setParent(self)
        self.sensor_one_canvas.mpl_connect('pick_event', self.on_pick)
        self.sensor_one_canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.sensor_one_tab.layout.addWidget(self.sensor_one_canvas)
        self.sensor_one_tab.setLayout(self.sensor_one_tab.layout)

        self.sensor_one_plot = self.sensor_one_figure.add_subplot(211)
        self.sensor_one_plot.set_title(f'Primary Sensor | {type} Error: CTD - Bottle')
        self.sensor_one_plot.set_xlabel('Deployment/Bottle')
        self.sensor_one_plot.set_ylabel('Error (CTD - Bottle)')
        self.sensor_one_plot.grid(alpha=0.1, zorder=0)

        self.sensor_one_plot_anno = self.sensor_one_plot.annotate("", xy=(0, 0), xycoords="data", zorder=5)
        self.sensor_one_plot_anno.set_visible(False)

        self.sensor_one_depth_plot = self.sensor_one_figure.add_subplot(212)
        self.sensor_one_depth_plot.set_xlabel('Error (CTD - Bottle)')
        self.sensor_one_depth_plot.set_ylabel('Pressure (db)')
        self.sensor_one_depth_plot.grid(alpha=0.1, zorder=0)
        self.sensor_one_depth_plot.invert_yaxis()

        self.sensor_one_depth_plot_anno = self.sensor_one_depth_plot.annotate("", xy=(0, 0), xycoords="data", zorder=5)
        self.sensor_one_depth_plot_anno.set_visible(False)

        """
        
        ** Secondary Sensor Tab **
        
        """
        self.sensor_two_tab = QWidget()
        self.sensor_two_tab.layout = QVBoxLayout()
        self.tabs.addTab(self.sensor_two_tab, 'Secondary Sensor')

        self.sensor_two_figure = plt.figure()
        self.sensor_two_figure.set_tight_layout(tight=True)
        self.sensor_two_canvas = FigureCanvas(self.sensor_two_figure)
        self.sensor_two_canvas.setParent(self)
        self.sensor_two_figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.sensor_two_canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.sensor_two_tab.layout.addWidget(self.sensor_two_canvas)
        self.sensor_two_tab.setLayout(self.sensor_two_tab.layout)

        self.sensor_two_plot = self.sensor_two_figure.add_subplot(211)
        self.sensor_two_plot.set_title(f'Secondary Sensor | {type} Error: CTD - Bottle')
        self.sensor_two_plot.set_xlabel('Deployment/Bottle')
        self.sensor_two_plot.set_ylabel('Error (CTD - Bottle)')
        self.sensor_two_plot.grid(alpha=0.1, zorder=0)

        self.sensor_two_plot_anno = self.sensor_two_plot.annotate("", xy=(0, 0), xycoords="data", zorder=5)
        self.sensor_two_plot_anno.set_visible(False)

        self.sensor_two_depth_plot = self.sensor_two_figure.add_subplot(212)
        self.sensor_two_depth_plot.set_xlabel('Error (CTD - Bottle)')
        self.sensor_two_depth_plot.set_ylabel('Pressure (db)')
        self.sensor_two_depth_plot.grid(alpha=0.1, zorder=0)
        self.sensor_two_depth_plot.invert_yaxis()

        self.sensor_two_depth_plot_anno = self.sensor_two_depth_plot.annotate("", xy=(0, 0), xycoords="data", zorder=5)
        self.sensor_two_depth_plot_anno.set_visible(False)

        """ 
        
        ** Both Sensors Tab **
        
        """
        self.both_sensor_tab = QWidget()
        self.both_sensor_tab.layout = QVBoxLayout()
        self.tabs.addTab(self.both_sensor_tab, 'Both Sensors')

        self.both_sensor_figure = plt.figure()
        self.both_sensor_figure.set_tight_layout(tight=True)
        self.both_sensor_canvas = FigureCanvas(self.both_sensor_figure)
        self.both_sensor_canvas.setParent(self)

        self.both_sensor_tab.layout.addWidget(self.both_sensor_canvas)
        self.both_sensor_tab.setLayout(self.both_sensor_tab.layout)

        self.both_sensor_plot = self.both_sensor_figure.add_subplot(111)
        self.both_sensor_plot.set_title(f'Both Sensors | {type} Error: CTD - Bottle')
        self.both_sensor_plot.set_xlabel('Deployment/Bottle')
        self.both_sensor_plot.set_ylabel('Error (CTD - Bottle)')
        self.both_sensor_plot.grid(alpha=0.1, zorder=0)

        # self.both_sensor_depth_plot = self.both_sensor_figure.add_subplot(212)
        # self.both_sensor_depth_plot.set_xlabel('Error (CTD - Bottle)')
        # self.both_sensor_depth_plot.set_ylabel('Pressure (db)')
        # self.both_sensor_depth_plot.grid(alpha=0.1, zorder=0)
        # self.both_sensor_depth_plot.invert_yaxis()

        """
        
        ** Profile Plot **
        
        """

        self.profile_tab = QWidget()
        self.profile_tab.layout = QVBoxLayout()
        self.tabs.addTab(self.profile_tab, 'Profile')

        self.profile_figure = plt.figure()
        self.profile_figure.set_tight_layout(tight=True)
        self.profile_canvas = FigureCanvas(self.profile_figure)
        self.profile_canvas.setParent(self)
        self.profile_canvas.mpl_connect('pick_event', self.on_pick)
        self.profile_canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.profile_tab.layout.addWidget(self.profile_canvas)
        self.profile_tab.setLayout(self.profile_tab.layout)

        self.profile_plot = self.profile_figure.add_subplot(111)
        self.profile_plot.set_title(f'{type} Depth Profile')
        self.profile_plot.set_xlabel('Oxygen Concentration (uM)')
        self.profile_plot.set_ylabel('Pressure (dbar)')
        self.profile_plot.grid(alpha=0.1, zorder=0)
        self.profile_plot.invert_yaxis()

        self.profile_plot_anno = self.profile_plot.annotate("", xy=(0, 0), xycoords="data", zorder=5)
        self.profile_plot_anno.set_visible(False)

        # Add tabs to window layout
        self.qv_box_layout.addWidget(self.tabs)
        self.qv_box_layout.addWidget(self.proceed)

        self.centralWidget().setLayout(self.qv_box_layout)

        self.setStyleSheet(style.stylesheet[theme])

        self.show()

    def proceed_proc(self):
        time.sleep(0.2)
        self.close()

    def export_sensor_one_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sensor_one_figure.savefig(filedialog[0] + filedialog[1], dpi=300)

    def export_sensor_two_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.sensor_two_figure.savefig(filedialog[0] + filedialog[1], dpi=300)

    def export_both_sensor_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.both_sensor_figure.savefig(filedialog[0] + filedialog[1], dpi=300)

    def clipboard_copy_active_plot(self):
        buffer = io.BytesIO()
        current_tab = self.tabs.currentIndex()

        if current_tab == 0:
            self.sensor_one_figure.savefig(buffer, dpi=300)
        if current_tab == 1:
            self.sensor_two_figure.savefig(buffer, dpi=300)
        if current_tab == 2:
            self.both_sensor_figure.savefig(buffer, dpi=300)
        if current_tab == 3:
            self.profile_figure.savefig(buffer, dpi=300)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def on_pick(self, event):
        plotted_data_index = event.ind[0]
        self.referenced_index = self.ref_ind[plotted_data_index]

        if self.type == 'Oxygen':
            concentration = round(self.full_data.oxygen_mols[self.referenced_index], 3)
            analyte = 'oxygen'
        elif self.type == 'Salinity':
            concentration = self.full_data.salinity[self.referenced_index]
            analyte = 'salinity'

        self.picked_bottle_dialog = bottleSelection(self.full_data.file, self.full_data.deployment[self.referenced_index],
                                          self.full_data.rosette_position[self.referenced_index],
                                          self.full_data.bottle_id[self.referenced_index],
                                          concentration, self.full_data.quality_flag[self.referenced_index], analyte)

        self.picked_bottle_dialog.saveSig.connect(self.update_flag)

    def update_flag(self, update_inputs):
        rev_flag_converter = {x: y for y, x in flag_converter.items()}
        numeric_flag = rev_flag_converter[update_inputs[0]]
        self.working_quality_flags[self.referenced_index] = numeric_flag

        self.initial_figure_save = True
        self.redraw.emit()

    def on_hover(self, event):

        x_data = event.xdata
        y_data = event.ydata
        xy_data = (x_data, y_data)
        if event.inaxes == self.profile_plot:
            check_result = check_hover(event, self.profile_plot)
            if check_result:
                x_point, y_point, xy_points = check_result
                index = find_closest(xy_data, xy_points)
                new_text = f'Bottle ID: {str(self.full_data.bottle_id[self.ref_ind[index]])}'
                update_annotation(self.profile_plot_anno, x_point[index], y_point[index], new_text,
                                  self.profile_plot, self.profile_canvas)

        elif event.inaxes == self.sensor_one_plot:
            check_result = check_hover(event, self.sensor_one_plot)
            if check_result:
                x_point, y_point, xy_points = check_result
                # Lambda function gets index of value closest to picked X data point (thanks SO)
                index = min(range(len(x_point)), key=lambda i: abs(x_point[i] - x_data))

                picked_deployment = self.full_data.deployment[self.ref_ind[index]]
                picked_rosette_pos = self.full_data.rosette_position[self.ref_ind[index]]
                picked_depth = self.depths[index]

                new_text = f'{picked_deployment}/{picked_rosette_pos}'
                update_annotation(self.sensor_one_plot_anno, x_point[index], y_point[index], new_text,
                                  self.sensor_one_plot, self.sensor_one_canvas)

                for line in self.sensor_one_depth_plot.get_lines():
                    if line.get_gid() == 'picking_line':
                        x_depth_point = line.get_xdata(orig=True)[index]

                update_annotation(self.sensor_one_depth_plot_anno, x_depth_point, picked_depth, new_text,
                                  self.sensor_one_depth_plot, self.sensor_one_canvas)

        elif event.inaxes == self.sensor_two_plot:
            check_result = check_hover(event, self.sensor_two_plot)
            if check_result:
                x_point, y_point, xy_points = check_result
                # Lambda function gets index of value closest to picked X data point (thanks SO)
                index = min(range(len(x_point)), key=lambda i: abs(x_point[i] - x_data))

                picked_deployment = self.full_data.deployment[self.ref_ind[index]]
                picked_rosette_pos = self.full_data.rosette_position[self.ref_ind[index]]
                picked_depth = self.depths[index]

                new_text = f'{picked_deployment}/{picked_rosette_pos}'
                update_annotation(self.sensor_two_plot_anno, x_point[index], y_point[index], new_text,
                                  self.sensor_two_plot, self.sensor_two_canvas)

                for line in self.sensor_two_depth_plot.get_lines():
                    if line.get_gid() == 'picking_line':
                        x_depth_point = line.get_xdata(orig=True)[index]

                update_annotation(self.sensor_two_depth_plot_anno, x_depth_point, picked_depth, new_text,
                                  self.sensor_two_depth_plot, self.sensor_two_canvas)