from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox
from PyQt5.QtGui import QPixmap, QFont, QIcon
import json
import hyproicons
import style

class hyproMessageBoxTemplate(QMessageBox):
    def __init__(self, title, short_text, type,long_text=None):
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
            self.setIconPixmap(QPixmap(':/assets/.svg'))

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
