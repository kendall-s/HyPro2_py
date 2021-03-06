from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QAction, QVBoxLayout, QFileDialog, QApplication,
                             QGridLayout, QLabel, QListWidget, QCheckBox, QPushButton, QAbstractItemView, QFrame)
from PyQt5.QtGui import QFont, QIcon, QImage
import io, json, sqlite3
import hyproicons, style
from dialogs.TraceSelectionDialog import traceSelection
from dialogs.BottleSelectionDialog import bottleSelection

class QMainPlotterTemplate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        theme = params['theme']

        if params['theme'] == 'normal':
            plt.style.use(style.mplstyle['normal'])
        else:
            plt.style.use(style.mplstyle['dark'])

        self.init_ui()

        self.setStyleSheet(style.stylesheet[theme])

    def init_ui(self):
        self.setFont(QFont('Segoe UI'))

        self.setGeometry(0, 0, 780, 820)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle('HyPro - Plotting Window')

        self.qvbox_layout = QVBoxLayout()
        self.qvbox_frame_holder = QFrame()
        self.qvbox_frame_holder.setLayout(self.qvbox_layout)
        self.grid_layout = QGridLayout()

        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        self.edit_menu = self.main_menu.addMenu('Edit')

        export = QAction(QIcon(':/assets/archivebox.svg'), 'Export Plot', self)
        export.triggered.connect(self.export_plot)
        self.file_menu.addAction(export)

        copy = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
        copy.triggered.connect(self.copy_plot)
        self.edit_menu.addAction(copy)

        self.run_list_label = QLabel('Select Run:', self)
        self.run_list = QListWidget(self)
        self.run_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.run_list.setMaximumWidth(120)

        self.show_bad_data = QCheckBox('Show bad data', self)

        self.mark_bad_data = QCheckBox('Mark bad data', self)

        self.apply_button = QPushButton('Apply', self)

        self.figure = plt.figure()
        self.figure.set_tight_layout(tight=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)

        self.main_plot = self.figure.add_subplot(111)

        for x in self.main_plot.get_xticklabels():
            x.set_fontsize(12)
        for y in self.main_plot.get_yticklabels():
            y.set_fontsize(12)

        self.grid_layout.addWidget(self.canvas, 0, 1)
        self.grid_layout.addWidget(self.qvbox_frame_holder, 0, 0)

        self.qvbox_layout.addWidget(self.run_list_label)
        self.qvbox_layout.addWidget(self.run_list)
        self.qvbox_layout.addWidget(self.show_bad_data)
        self.qvbox_layout.addWidget(self.mark_bad_data)
        self.qvbox_layout.addWidget(self.apply_button)

        self.centralWidget().setLayout(self.grid_layout)

    def export_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=300)

    def copy_plot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=300)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def base_on_pick(self, event, database, runs, peak_nums, nutrient=None, oxygen=None, salinity=None):
        plotted_data_index = event.ind[0]
        picked_run_number = runs[plotted_data_index]
        picked_peak_number = peak_nums[plotted_data_index]

        conn = sqlite3.connect(database)

        if nutrient:
            c = conn.cursor()
            c.execute('SELECT * FROM %sData WHERE runNumber = ? and peakNumber = ?' % nutrient,
                      (picked_run_number, picked_peak_number))
            data = list(c.fetchall())[0]
            conn.close()
            self.picked_peak_dialog = traceSelection(data[2], data[1], data[3], data[5], data[6], data[10], data[11], 'Plot')

        else:
            c = conn.cursor()
            if oxygen:
                c.execute('SELECT * from oxygenData WHERE deployment = ? and rosettePosition = ?', (picked_run_number,
                                                                                                    picked_peak_number))
                data = list(c.fetchall())[0]
                conn.close()
                self.picked_bottle_dialog = bottleSelection(data[0], data[15], data[16], data[4], round(data[9], 3), data[14])

            elif salinity:
                c.execute('SELECT * from salinityData WHERE deployment = ? and rosettePosition = ?', (picked_run_number,
                                                                                                    picked_peak_number))
                data = list(c.fetchall())[0]
                conn.close()
                self.picked_bottle_dialog = bottleSelection(data[0], data[10], data[11], data[2], data[6], data[9])