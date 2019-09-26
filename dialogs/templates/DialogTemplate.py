from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QComboBox, QMessageBox, QTableView,
                             QInputDialog, QApplication, QFrame, QDesktopWidget, QListWidget, QDialog)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
import json
from time import sleep
import hyproicons, style

# This class produces the dialog and functionality for activating the different analyses in Hypro
# Allows for entering the naming convention for files to be found and processed


class hyproDialogTemplate(QDialog):
    def __init__(self, width, height, title):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))

        self.height = height
        self.width = width
        self.title = title

        self.setFont(QFont('Segoe UI'))

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setGeometry(0, 0, self.width, self.height)
        qtRectangle = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.setWindowTitle(self.title)

        self.setLayout(self.grid_layout)

        # Set stylesheet to the one selected by the user.
        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        theme = params['theme']
        self.setStyleSheet(style.stylesheet[theme])