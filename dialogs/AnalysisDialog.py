from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QComboBox, QMessageBox, QTableView,
                             QInputDialog, QApplication, QFrame, QCheckBox, QDesktopWidget, QListWidget)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
import json
from time import sleep
from dialogs.templates.DialogTemplate import hyproDialogTemplate
import hyproicons

# This class produces the dialog and functionality for activating the different analyses in Hypro
# Allows for entering the naming convention for files to be found and processed


class analysisSettings(hyproDialogTemplate):
    analysisSettingsUpdated = pyqtSignal()

    def __init__(self, project, analysis, path):
        super().__init__(300, 250, 'HyPro - Analysis Settings')
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))

        self.currproject = project
        self.analysis = analysis
        self.currpath = path

        self.init_ui()


    def init_ui(self):

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        # Analyses keys
        self.analyses = {'guildline': 'Digital Guildline Salinometer', 'scripps': 'Scripps Dissolved Oxygen',
                         'seal': 'Seal AA3 Nutrients', 'seasave': 'Seasave CTD', 'logsheet': 'Sampling Logsheet'}

        # Set up GUI
        headerLabel = QLabel('<b>' + str(self.analyses[self.analysis]) + '</b>', self)

        prefixLabel = QLabel('File prefix:', self)

        self.prefixEdit = QLineEdit(self)

        runLabel = QLabel('Run number format:', self)

        self.runEdit = QLineEdit(self)

        activateLabel = QLabel('Analysis activated:', self)

        self.activateBox = QCheckBox()

        save = QPushButton('Save', self)
        save.clicked.connect(self.save_function)

        cancel = QPushButton('Cancel', self)
        cancel.clicked.connect(self.cancel_function)

        self.grid_layout.addWidget(headerLabel, 0, 0, 1, 2)

        self.grid_layout.addWidget(prefixLabel, 1, 0)
        self.grid_layout.addWidget(self.prefixEdit, 1, 1)

        self.grid_layout.addWidget(runLabel, 2, 0)
        self.grid_layout.addWidget(self.runEdit, 2, 1)

        self.grid_layout.addWidget(activateLabel, 3, 0)
        self.grid_layout.addWidget(self.activateBox, 3, 1)

        self.grid_layout.addWidget(save, 4, 0)
        self.grid_layout.addWidget(cancel, 4, 1)

        self.populate_fields()

    # Populate fields from current info in the parameters file for the project
    def populate_fields(self):
        with open(self.currpath +  '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        self.prefixEdit.setText(params['analysis_params'][self.analysis]['file_prefix'])
        self.runEdit.setText(params['analysis_params'][self.analysis]['run_format'])
        self.activateBox.setChecked(params['analysis_params'][self.analysis]['activated'])

    # This saves what is written in to the dialog inputs, overwriting the info in parameters
    def save_function(self):
        prefix = self.prefixEdit.text()
        runformat = self.runEdit.text()
        active = self.activateBox.isChecked()

        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        params['analysis_params'][self.analysis]['file_prefix'] = prefix
        params['analysis_params'][self.analysis]['run_format'] = runformat
        params['analysis_params'][self.analysis]['activated'] = active

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

    def cancel_function(self):
        sleep(0.1)
        self.close()
