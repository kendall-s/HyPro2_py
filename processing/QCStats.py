from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QGridLayout, QDesktopWidget, QTableWidget, QComboBox,
                             QLineEdit)
import sqlite3
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *
from time import sleep
import traceback
import statistics
import hyproicons

"""
Implemented from a long standing QC stat generator originally written for the Matlab HyPro

Isn't fully working anymore for this version of HyPro...
"""


class statsDialog(QWidget):
    def __init__(self, project, database):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))

        self.currproj = project

        self.db = database

        self.nutrientconvert = {'Nitrate': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate',
                                'Nitrite': 'nitrite', 'Ammonia': 'ammonia'}

        self.init_ui()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #fefefe;
            }
            QLabel {
                font: 14px;
            }
            QListWidget {
                font: 14px;
            }
            QPushButton {
                font: 13px;
            }
            QTableWidget {
                font: 13px;
            }
            QComboBox {
                font: 13px;
            }
            QLineEdit {
                font: 13px;
            }
                            """)

    def init_ui(self):
        try:
            deffont = QFont('Segoe UI')

            # self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

            gridlayout = QGridLayout()
            gridlayout.setSpacing(20)

            self.setWindowModality(QtCore.Qt.ApplicationModal)

            self.setFont(deffont)
            self.setGeometry(0, 0, 670, 300)
            qtRectangle = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
            # self.setFixedSize(self.size())
            self.setWindowTitle('HyPro - View QC Stats')

            statsHeader = QLabel('Select QC to view:', self)

            self.qcDropdown = QComboBox(self)
            self.qcDropdown.addItems(['RMNS', 'MDL'])

            self.nutrientDropdown = QComboBox(self)
            self.nutrientDropdown.addItems(['Nitrate', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])

            minimumlabel = QLabel('Minimum:', self)
            self.minimum = QLineEdit('', self)

            maximumlabel = QLabel('Maximum:', self)
            self.maximum = QLineEdit('', self)

            meanlabel = QLabel('Mean:', self)
            self.mean = QLineEdit('', self)

            medianlabel = QLabel('Median:', self)
            self.median = QLineEdit('', self)

            stdevlabel = QLabel('StDev:')
            self.stdev = QLineEdit('', self)

            stdevmin = QLabel('Min StDev:', self)
            self.stdevmin = QLineEdit('', self)

            stdevmax = QLabel('Max StDev:', self)
            self.stdevmax = QLineEdit('', self)

            stdevmean = QLabel('Mean StDev:', self)
            self.stdevmean = QLineEdit('', self)

            stdevmedian = QLabel('Median StDev:', self)
            self.stdevmedian = QLineEdit('', self)

            view = QPushButton('View Stats', self)
            view.clicked.connect(self.viewstats)

            close = QPushButton('Close', self)
            close.clicked.connect(self.close)

            gridlayout.addWidget(statsHeader, 0, 0)
            gridlayout.addWidget(self.nutrientDropdown, 1, 0)
            gridlayout.addWidget(self.qcDropdown, 1, 1)
            gridlayout.addWidget(minimumlabel, 2, 0)
            gridlayout.addWidget(self.minimum, 3, 0)
            gridlayout.addWidget(maximumlabel, 2, 1)
            gridlayout.addWidget(self.maximum, 3, 1)
            gridlayout.addWidget(meanlabel, 2, 2)
            gridlayout.addWidget(self.mean, 3, 2)
            gridlayout.addWidget(medianlabel, 2, 3)
            gridlayout.addWidget(self.median, 3, 3)
            gridlayout.addWidget(stdevlabel, 2, 4)
            gridlayout.addWidget(self.stdev, 3, 4)
            gridlayout.addWidget(stdevmin, 4, 0)
            gridlayout.addWidget(self.stdevmin, 5, 0)
            gridlayout.addWidget(stdevmax, 4, 1)
            gridlayout.addWidget(self.stdevmax, 5, 1)
            gridlayout.addWidget(stdevmean, 4, 2)
            gridlayout.addWidget(self.stdevmean, 5, 2)
            gridlayout.addWidget(stdevmedian, 4, 3)
            gridlayout.addWidget(self.stdevmedian, 5, 3)
            gridlayout.addWidget(view, 6, 3)
            gridlayout.addWidget(close, 6, 4)

            self.setLayout(gridlayout)
        except Exception as e:
            print(e)

    def closewindow(self):
        sleep(0.2)
        self.close()

    def viewstats(self):
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            qc = str(self.qcDropdown.currentText()) + '%'

            c.execute('''SELECT * from %sData WHERE sampleID LIKE ?''' % self.nutrientconvert[
                str(self.nutrientDropdown.currentText())], (qc,))
            data = list(c.fetchall())
            c.close()

            run = [x[0] for x in data]
            conc = [x[6] for x in data]

            runset = list(set(run))

            minconc = min(conc)
            maxconc = max(conc)
            meanconc = statistics.mean(conc)
            medianconc = statistics.median(conc)
            stdevconc = statistics.stdev(conc)

            perrunconcs = []
            perrunstdevlist = []
            for x in runset:
                for i, y in enumerate(run):
                    if x == y:
                        perrunconcs.append(conc[i])
                #print(x)
                #print(statistics.mean(perrunconcs))
                perrunstdev = statistics.stdev(perrunconcs)
                perrunstdevlist.append(perrunstdev)

            minstdev = min(perrunstdevlist)
            maxstdev = max(perrunstdevlist)
            meanstdev = statistics.mean(perrunstdevlist)
            medianstdev = statistics.median(perrunstdevlist)

            self.minimum.setText(str(round(minconc, 3)))
            self.maximum.setText(str(round(maxconc, 3)))
            self.mean.setText(str(round(meanconc, 3)))
            self.median.setText(str(round(medianconc, 3)))
            self.stdev.setText(str(round(stdevconc, 3)))
            self.stdevmin.setText(str(round(minstdev, 3)))
            self.stdevmax.setText(str(round(maxstdev, 3)))
            self.stdevmean.setText(str(round(meanstdev, 3)))
            self.stdevmedian.setText(str(round(medianstdev, 3)))

        except Exception:
            print(traceback.print_exc())

    def saveedit(self):
        print('saving')
