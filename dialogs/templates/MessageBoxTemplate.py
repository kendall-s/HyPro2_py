from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QFont, QIcon
import json
import style, hyproicons

"""
Template for the message box, extends QMessagebox and provides shorthand functionality for showing certain icons and 
messages.
"""


class hyproMessageBoxTemplate(QMessageBox):
    def __init__(self, title, short_text, type, long_text=None):
        super().__init__()

        self.setWindowIcon(QIcon(':/assets/icon.svg'))
        self.setFont(QFont('Segoe UI'))

        self.setWindowTitle(title)

        if type == 'success':
            self.setIconPixmap(QPixmap(':/assets/success.svg'))
        elif type == 'about':
            self.setIconPixmap(QPixmap(':/assets/questionmark.svg'))
        elif type == 'information':
            self.setIconPixmap(QPixmap(':/assets/exclamation.svg'))
        elif type == 'error':
            self.setIconPixmap(QPixmap(':/assets/cross.svg'))
        elif type == 'delete':
            self.setIconPixmap(QPixmap(':/assets/trash.svg'))

        self.setText(short_text)
        self.setInformativeText(long_text)

        ok_but = self.addButton(QMessageBox.Ok)
        ok_but.setProperty('msgBox', True)

        # Set stylesheet to the one selected by the user.
        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        theme = params['theme']
        self.setStyleSheet(style.stylesheet[theme])

        self.exec_()
