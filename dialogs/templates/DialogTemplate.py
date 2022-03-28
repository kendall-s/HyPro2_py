import json

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QGridLayout, QApplication, QDialog)

import style, hyproicons

"""
This class is the basis for the majority of dialogs in HyPro. It sets up some basic functionality, layout and styling
"""


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
