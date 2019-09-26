from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QComboBox, QMessageBox, QTableView,
                             QInputDialog, QApplication, QFrame, QCheckBox, QDesktopWidget, QListWidget)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
import json
from time import sleep
import hyproicons

# This class produces the dialog and functionality for activating the different analyses in Hypro
# Allows for entering the naming convention for files to be found and processed


class analysisSettings(QWidget):
    analysisSettingsUpdated = pyqtSignal()

    def __init__(self, project, analysis, path):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))

        self.currproject = project
        self.analysis = analysis
        self.currpath = path

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
                font: 14px;
            }
            QLineEdit {
                font: 14px;
            }
            QCheckBox:indicator {
                height: 30px;
                width: 30px;
                background-color: #ededed;
                border: 2px solid #cccccc;
                border-radius: 7px;
            }
            QCheckBox:indicator:hover {
                background-color: #f7f7f7;
                border: 2px solid #c6dbff;
            }
            QCheckBox:indicator:pressed {
                height: 27px;
                width: 27px;
                border: 2px solid #8294b5; 
            }
            QCheckBox:indicator:unchecked {
                image: url(':/assets/roundcross.svg');
            }
            QCheckBox:indicator:checked {
                image: url(':/assets/roundchecked.svg');
            }
            QFrame[square=true] {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 2px;
            }
                            """)

    def init_ui(self):
        deffont = QFont('Segoe UI')
        self.setFont(deffont)

        gridlayout = QGridLayout()
        gridlayout.setSpacing(20)

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setGeometry(0, 0, 300, 250)
        qtRectangle = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setFixedSize(self.size())
        self.setWindowTitle('HyPro - Guildline Salinity Settings')

        # Analyses keys
        self.analyses = {'guildline': 'Digital Guildline Salinometer', 'scripps': 'Scripps Dissolved Oxygen',
                         'seal': 'Seal AA3 Nutrients', 'seasave': 'Seasave CTD', 'logsheet': 'Sampling Logsheet'}

        # Set up GUI
        headerLabel = QLabel('<b>' + str(self.analyses[self.analysis]) + '</b>', self)
        #headerLabel.setFont(deffont)

        prefixLabel = QLabel('File prefix:')
        prefixLabel.setFont(deffont)

        self.prefixEdit = QLineEdit(self)
        self.prefixEdit.setFont(deffont)

        runLabel = QLabel('Run number format:')
        runLabel.setFont(deffont)

        self.runEdit = QLineEdit(self)
        self.runEdit.setFont(deffont)

        activateLabel = QLabel('Analysis activated:')
        activateLabel.setFont(deffont)

        self.activateBox = QCheckBox()

        save = QPushButton('Save', self)
        save.setFont(deffont)
        save.clicked.connect(self.savefunction)

        cancel = QPushButton('Cancel', self)
        cancel.setFont(deffont)
        cancel.clicked.connect(self.cancelfunction)

        gridlayout.addWidget(headerLabel, 0, 0, 1, 2)

        gridlayout.addWidget(prefixLabel, 1, 0)
        gridlayout.addWidget(self.prefixEdit, 1, 1)

        gridlayout.addWidget(runLabel, 2, 0)
        gridlayout.addWidget(self.runEdit, 2, 1)

        gridlayout.addWidget(activateLabel, 3, 0)
        gridlayout.addWidget(self.activateBox, 3, 1)

        gridlayout.addWidget(save, 4, 0)
        gridlayout.addWidget(cancel, 4, 1)

        self.setLayout(gridlayout)

        self.populatefields()

    # Populate fields from current info in the parameters file for the project
    def populatefields(self):
        with open(self.currpath +  '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        self.prefixEdit.setText(params['analysisparams'][self.analysis]['filePrefix'])
        self.runEdit.setText(params['analysisparams'][self.analysis]['runFormat'])
        self.activateBox.setChecked(params['analysisparams'][self.analysis]['activated'])

    # This saves what is written in to the dialog inputs, overwriting the info in parameters
    def savefunction(self):
        prefix = self.prefixEdit.text()
        runformat = self.runEdit.text()
        active = self.activateBox.isChecked()

        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        params['analysisparams'][self.analysis]['filePrefix'] = prefix
        params['analysisparams'][self.analysis]['runFormat'] = runformat
        params['analysisparams'][self.analysis]['activated'] = active

        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
            json.dump(params, file)

        self.analysisSettingsUpdated.emit()

        messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                 "Settings saved",
                                 buttons=QtWidgets.QMessageBox.Ok, parent=self)
        messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
        messagebox.setFont(QFont('Segoe UI'))
        messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
        messagebox.exec_()
        sleep(0.2)

        self.close()

    def cancelfunction(self):
        sleep(0.1)
        self.close()
