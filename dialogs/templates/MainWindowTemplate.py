from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
import json

import hyproicons, style

class hyproMainWindowTemplate(QMainWindow):
    def __init__(self, width, height, title):
        super().__init__()

        self.setWindowIcon(QIcon(':/assets/icon.svg'))

        self.height_var = height
        self.width_var = width
        self.title = title

        self.setFont(QFont('Segoe UI'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)

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

        self.centralWidget().setLayout(self.grid_layout)

        # Set stylesheet to the one selected by the user.
        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        theme = params['theme']
        self.setStyleSheet(style.stylesheet[theme])
