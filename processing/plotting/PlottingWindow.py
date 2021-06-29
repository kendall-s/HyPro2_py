from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5.QtWidgets import (QMainWindow, QWidget, QAction, QVBoxLayout, QFileDialog, QApplication,
                             QGridLayout, QLabel, QListWidget, QCheckBox, QPushButton, QAbstractItemView, QFrame)
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5.QtCore import pyqtSignal
import io, json, sqlite3
import hyproicons, style
from dialogs.TraceSelectionDialog import traceSelection
from dialogs.BottleSelectionDialog import bottleSelection

# Set the matplotlib backend to be more stable with PyQt integration
mpl.use('Agg')

class QMainPlotterTemplate(QMainWindow):

    need_update = pyqtSignal()

    def __init__(self, database):
        super().__init__()

        self.database = database

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

        # Center window on active screen
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
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

        copy_report = QAction('Copy 4Report', self)
        copy_report.triggered.connect(self.copy_plot_report)
        self.edit_menu.addAction(copy_report)

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
        self.grid_layout.setColumnStretch(1, 2)
        self.grid_layout.addWidget(self.qvbox_frame_holder, 0, 0)

        self.qvbox_layout.addWidget(self.run_list_label)
        self.qvbox_layout.addWidget(self.run_list)
        self.qvbox_layout.addWidget(self.show_bad_data)
        self.qvbox_layout.addWidget(self.mark_bad_data)
        self.qvbox_layout.addWidget(self.apply_button)

        self.centralWidget().setLayout(self.grid_layout)

    def closeEvent(self, event):
        plt.close('all')

    def export_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=300)

    def copy_plot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=300)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def copy_plot_report(self):
        self.figure.set_size_inches(8.3, 7)
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=100)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def base_on_pick(self, event, runs, peak_nums, nutrient=None, oxygen=None, salinity=None):
        plotted_data_index = event.ind[0]
        picked_run_number = runs[plotted_data_index]
        picked_peak_number = peak_nums[plotted_data_index]

        conn = sqlite3.connect(self.database)

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
                self.picked_bottle_dialog = bottleSelection(data[0], data[15], data[16], data[4], round(data[9], 3),
                                                            data[14], analyte='oxygen')

            elif salinity:
                c.execute('SELECT * from salinityData WHERE deployment = ? and rosettePosition = ?', (picked_run_number,
                                                                                                    picked_peak_number))
                data = list(c.fetchall())[0]
                conn.close()
                self.picked_bottle_dialog = bottleSelection(data[0], data[10], data[11], data[2], data[6],
                                                            data[9], analyte='salinity')

            self.picked_bottle_dialog.saveSig.connect(self.update_flag)
        conn.close()

    def update_flag(self, update_inputs):
        # tuple update_inputs: new_flag, file, deployment, rosette, bottle_id, analyte
        id_or_label = {'oxygen': 'ID', 'salinity': 'Label'}
        flag_conversion = {'Good': 1, 'Suspect': 2, 'Bad': 3}

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Little bit messy. String formatting either the Salinity or Oxygen table, along with changing the column
        # header based on either table.
        # Might change the tuple to a named tuple or a dict to make this more readable?
        c.execute("""UPDATE %sData 
                SET flag=?
                WHERE runNumber=? and deployment=? and rosettePosition=? and bottle%s=?"""
                % (update_inputs[5], id_or_label[update_inputs[5]]),
                (flag_conversion[update_inputs[0]], update_inputs[1], update_inputs[2], update_inputs[3],
                 update_inputs[4]))

        conn.commit()
        conn.close()

        self.need_update.emit()