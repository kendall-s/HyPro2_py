from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pylab import get_current_fig_manager
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QAction, QVBoxLayout, QFileDialog, QApplication,
                             QGridLayout, QLabel, QListWidget, QCheckBox, QPushButton, QAbstractItemView, QFrame)
from PyQt5.QtGui import QFont, QIcon, QImage
import io
import hyproicons, style

class QMainPlotterTemplate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.init_ui()

        self.setStyleSheet(style.stylesheet['normal'])

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


        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')

        exportPlot = QAction(QIcon(':/assets/archivebox.svg'), 'Export Plot', self)
        exportPlot.triggered.connect(self.export_plot)
        fileMenu.addAction(exportPlot)

        copyPlot = QAction(QIcon(':/assets/newdoc.svg'), 'Copy', self)
        copyPlot.triggered.connect(self.copy_plot)
        editMenu.addAction(copyPlot)

        run_list_label = QLabel('Select Run:', self)
        self.run_list = QListWidget(self)
        self.run_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.run_list.setMaximumWidth(120)

        self.show_bad_data = QCheckBox('Show bad data', self)

        self.mark_bad_data = QCheckBox('Mark bad data', self)

        self.apply_button = QPushButton('Apply', self)
        self.apply_button.clicked.connect(self.apply)

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

        self.qvbox_layout.addWidget(run_list_label)
        self.qvbox_layout.addWidget(self.run_list)
        self.qvbox_layout.addWidget(self.show_bad_data)
        self.qvbox_layout.addWidget(self.mark_bad_data)
        self.qvbox_layout.addWidget(self.apply_button)

        self.centralWidget().setLayout(self.grid_layout)

        clicker = self.figure.canvas.mpl_connect("button_press_event", self.on_click)

    def export_plot(self):
        filedialog = QFileDialog.getSaveFileName(None, 'Save Plot', '', '.png')
        if filedialog[0]:
            self.figure.savefig(filedialog[0] + filedialog[1], dpi=400)

    def copy_plot(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, dpi=400)
        QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))

    def on_click(self, event):
        tb = get_current_fig_manager().toolbar
        if event.button == 1 and event.inaxes and tb.mode == '':
            print(event.xdata)

    def apply(self):
        pass