from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QComboBox, QMessageBox,
                             QDesktopWidget, QTabWidget)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
import serial.tools.list_ports
import hyproicons
import traceback


class valveControl(QWidget):
    analysisSettingsUpdated = pyqtSignal()

    def __init__(self):
        try:
            super().__init__()

            self.setWindowIcon(QtGui.QIcon(':/icon.svg'))

            self.init_ui()

            self.setStyleSheet("""
                QMainWindow {
                    background-color: #fefefe;
                }
                QLabel {
                    font: 14px;
                }
                QComboBox {
                    font: 14px;
                }
                QPushButton {
                    font: 13px;
                }
                QLineEdit {
                    font: 13px;
                }
                QCheckBox:indicator {
                    height: 30px;
                    width: 30px;
                }
                QCheckBox:indicator:unchecked {
                    image: url(':/roundcross.svg');
                }
                QCheckBox:indicator:checked {
                    image: url(':/roundchecked.svg');
                }
                QFrame[square=true] {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 2px;
                }
                QTabWidget {
                    font: 13px;
                }
                                """)
        except Exception:
            print(traceback.print_exc())

    def init_ui(self):
        deffont = QFont('Segoe UI')

        gridlayout = QGridLayout()
        gridlayout.setSpacing(20)

        self.setFont(deffont)
        self.setGeometry(0, 0, 300, 280)
        qtRectangle = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setFixedSize(self.size())
        self.setWindowTitle('HyPro - Vici Valve Control')

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.resize(400, 300)

        self.connectiontab = QWidget()
        self.tabs.addTab(self.connectiontab, 'Connection')

        self.manualcontrol = QWidget()
        self.tabs.addTab(self.manualcontrol, 'Manual')
        self.tabs.setTabEnabled(1, False)

        self.autocontrol = QWidget()
        self.tabs.addTab(self.autocontrol, 'Automate')
        self.tabs.setTabEnabled(2, False)

        gridlayout.addWidget(self.tabs, 0, 0)
        self.setLayout(gridlayout)

        # Connection Tab
        self.connectiontab.layout = QGridLayout()

        comPortLabel = QLabel('Select COM Port:')

        self.comPorts = QComboBox()
        comList = serial.tools.list_ports.comports()
        print(comList)
        #self.comPorts.addItems(comList)

        addressLabel = QLabel('Address:')

        self.address = QLineEdit()

        self.connectbutton = QPushButton('Connect', self)
        self.connectbutton.clicked.connect(self.connectvalve)

        self.connectiontab.layout.addWidget(comPortLabel, 0, 0)
        self.connectiontab.layout.addWidget(self.comPorts, 0, 1)

        self.connectiontab.layout.addWidget(addressLabel, 1, 0)
        self.connectiontab.layout.addWidget(self.address, 1, 1)

        self.connectiontab.layout.addWidget(self.connectbutton, 2, 1)

        self.connectiontab.setLayout(self.connectiontab.layout)

        # Manual control Tab

        self.manualcontrol.layout = QGridLayout()

        # valvepicholder = QLabel(self)
        # valvepic = QPixmap('14portvalve.png')
        # valvepicsized = valvepic.scaled(150, 150)
        # valvepicholder.setPixmap(valvepicsized)

        self.pos1 = QPushButton('1', self)
        self.manualcontrol.layout.addWidget(self.pos1, 0, 9)
        self.pos1.setFixedSize(25, 25)
        # self.pos1.clicked.connect(self.movetoport('01'))

        self.pos2 = QPushButton('2', self)
        self.manualcontrol.layout.addWidget(self.pos2, 1, 5)
        self.pos2.setFixedSize(25, 25)
        # self.pos2.clicked.connect(self.movetoport('02'))

        self.pos3 = QPushButton('3', self)
        self.manualcontrol.layout.addWidget(self.pos3, 3, 2)
        self.pos3.setFixedSize(25, 25)
        # self.pos3.clicked.connect(self.movetoport('03'))

        self.pos4 = QPushButton('4', self)
        self.manualcontrol.layout.addWidget(self.pos4, 7, 0)
        self.pos4.setFixedSize(25, 25)
        # self.pos4.clicked.connect(self.movetoport('04'))


        self.pos5 = QPushButton('5', self)
        self.manualcontrol.layout.addWidget(self.pos5, 12, 0)
        self.pos5.setFixedSize(25, 25)
        # self.pos5.clicked.connect(self.movetoport('05'))

        self.pos6 = QPushButton('6', self)
        self.manualcontrol.layout.addWidget(self.pos6, 15, 2)
        self.pos6.setFixedSize(25, 25)
        # self.pos6.clicked.connect(self.movetoport('06'))

        self.pos7 = QPushButton('7', self)
        self.manualcontrol.layout.addWidget(self.pos7, 17, 5)
        self.pos7.setFixedSize(25, 25)
        # self.pos7.clicked.connect(self.movetoport('07'))

        self.pos8 = QPushButton('8', self)
        self.manualcontrol.layout.addWidget(self.pos8, 18, 9)
        self.pos8.setFixedSize(25, 25)
        # self.pos8.clicked.connect(self.movetoport('08'))

        self.pos9 = QPushButton('9', self)
        self.manualcontrol.layout.addWidget(self.pos9, 17, 13)
        self.pos9.setFixedSize(25, 25)
        # self.pos9.clicked.connect(self.movetoport('09'))

        self.pos10 = QPushButton('10', self)
        self.manualcontrol.layout.addWidget(self.pos10, 15, 16)
        self.pos10.setFixedSize(25, 25)
        # self.pos10.clicked.connect(self.movetoport('10'))

        self.pos11 = QPushButton('11', self)
        self.manualcontrol.layout.addWidget(self.pos11, 12, 18)
        self.pos11.setFixedSize(25, 25)
        # self.pos11.clicked.connect(self.movetoport('11'))

        self.pos12 = QPushButton('12', self)
        self.manualcontrol.layout.addWidget(self.pos12, 7, 18)
        self.pos12.setFixedSize(25, 25)
        # self.pos12.clicked.connect(self.movetoport('12'))

        self.pos13 = QPushButton('13', self)
        self.manualcontrol.layout.addWidget(self.pos13, 3, 16)
        self.pos13.setFixedSize(25, 25)
        # self.pos13.clicked.connect(self.movetoport('13'))

        self.pos14 = QPushButton('14', self)
        self.manualcontrol.layout.addWidget(self.pos14, 1, 13)
        self.pos14.setFixedSize(25, 25)
        # self.pos14.clicked.connect(self.movetoport(14))

        currentPosLabel = QLabel('Current Port:', self)

        self.currentPos = QLabel('?', self)

        self.manualcontrol.layout.addWidget(currentPosLabel, 9, 9, 0, 3)
        self.manualcontrol.layout.addWidget(self.currentPos, 10, 9, 0, 3)

        # self.manualcontrol.layout.addWidget(valvepicholder, 5, 7, 8, 7)

        self.manualcontrol.setLayout(self.manualcontrol.layout)

    def connectvalve(self):

        try:
            comport = str(self.comPorts.currentText())
            address = str(self.address.text())

            try:
                self.serialconn = serial.Serial('%s' % comport, 9600, 8, 'N', 1, timeout=2)
                self.connectbutton.setText('CONNECTED')
                self.tabs.setTabEnabled(1, True)
                self.tabs.setTabEnabled(2, True)

            except Exception:
                messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Unsuccessful connection',
                                         'A connection was unable to be made',
                                         buttons=QtWidgets.QMessageBox.Ok, parent=self)
                messagebox.setIconPixmap(QPixmap(':/exclamation.svg'))
                messagebox.setFont(QFont('Segoe UI'))
                messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
                messagebox.exec_()

                self.connectbutton.setText('CONNECTED')
                self.tabs.setTabEnabled(1, True)
                self.tabs.setTabEnabled(2, True)


        except Exception as e:
            print(e)

    def movetoport(self, number):
        port = number
        try:
            # buffer = self.serialconn.write('/Z GO%s\n'%port.encode('utf-8'))
            print('writing')
        except Exception:
            print('Nope no valve connected m8')
