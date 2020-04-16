from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QApplication, QTabWidget, QVBoxLayout, QPushButton,
                             QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QImage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from dialogs.BottleSelectionDialog import bottleSelection
import json
import time
import io
import hyproicons, style

flag_converter = {1 : 'Good', 2 : 'Suspect', 3 : 'Bad', 4 : 'Shape Sus', 5 : 'Shape Bad', 6: 'Cal Bad',
                    91 : 'CalError Sus', 92 : 'CalError Bad', 8 : 'Dup Diff'}

class hyproProcPlotWindow(QMainWindow):
    redraw = pyqtSignal()

    def __init__(self, width, height, title, type, ref_ind, full_data):
        super().__init__()

        self.type = type
        self.working_quality_flags = full_data.quality_flag

        # Reference index back to the full data file of the plotted data. E.g. plotted data point 10 may be data point
        # 12 in the file. Len(ref_ind) will always be less than Len(values_in_file)
        self.ref_ind = ref_ind
        self.full_data = full_data

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

        self.sensor_one_tab.layout.addWidget(self.sensor_one_canvas)
        self.sensor_one_tab.setLayout(self.sensor_one_tab.layout)

        self.sensor_one_plot = self.sensor_one_figure.add_subplot(211)
        self.sensor_one_plot.set_title(f'Primary Sensor | {type} Error: CTD - Bottle')
        self.sensor_one_plot.set_xlabel('Deployment/Bottle')
        self.sensor_one_plot.set_ylabel('Error (CTD - Bottle)')
        self.sensor_one_plot.grid(alpha=0.1, zorder=0)

        self.sensor_one_depth_plot = self.sensor_one_figure.add_subplot(212)
        self.sensor_one_depth_plot.set_xlabel('Error (CTD - Bottle)')
        self.sensor_one_depth_plot.set_ylabel('Pressure (db)')
        self.sensor_one_depth_plot.grid(alpha=0.1, zorder=0)
        self.sensor_one_depth_plot.invert_yaxis()

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

        self.sensor_two_tab.layout.addWidget(self.sensor_two_canvas)
        self.sensor_two_tab.setLayout(self.sensor_two_tab.layout)

        self.sensor_two_plot = self.sensor_two_figure.add_subplot(211)
        self.sensor_two_plot.set_title(f'Secondary Sensor | {type} Error: CTD - Bottle')
        self.sensor_two_plot.set_xlabel('Deployment/Bottle')
        self.sensor_two_plot.set_ylabel('Error (CTD - Bottle)')
        self.sensor_two_plot.grid(alpha=0.1, zorder=0)

        self.sensor_two_depth_plot = self.sensor_two_figure.add_subplot(212)
        self.sensor_two_depth_plot.set_xlabel('Error (CTD - Bottle)')
        self.sensor_two_depth_plot.set_ylabel('Pressure (db)')
        self.sensor_two_depth_plot.grid(alpha=0.1, zorder=0)
        self.sensor_two_depth_plot.invert_yaxis()

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

        self.profile_tab.layout.addWidget(self.profile_canvas)
        self.profile_tab.setLayout(self.profile_tab.layout)

        self.profile_plot = self.profile_figure.add_subplot(111)
        self.profile_plot.set_title(f'{type} Depth Profile')
        self.profile_plot.set_xlabel('Oxygen Concentration (uM)')
        self.profile_plot.set_ylabel('Pressure (dbar)')
        self.profile_plot.grid(alpha=0.1, zorder=0)
        self.profile_plot.invert_yaxis()

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
        referenced_index = self.ref_ind[plotted_data_index]

        if self.type == 'Oxygen':
            concentration = round(self.full_data.oxygen_mols[referenced_index], 3)
        elif self.type == 'Salinity':
            concentration = self.full_data.salinity[referenced_index]

        self.bottle_sel = bottleSelection(self.full_data.file, self.full_data.deployment[referenced_index],
                                          self.full_data.rosette_position[referenced_index],
                                          self.full_data.bottle_id[referenced_index],
                                          concentration, self.full_data.quality_flag[referenced_index])

        self.bottle_sel.saveSig.connect(lambda: self.update_flag(referenced_index))

    def update_flag(self, index):
        rev_flag_converter = {x: y for y, x in flag_converter.items()}
        numeric_flag = rev_flag_converter[self.bottle_sel.flag_box.currentText()]
        self.working_quality_flags[index] = numeric_flag
        print(self.working_quality_flags)

        self.redraw.emit()

