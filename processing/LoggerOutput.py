from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
import logging
import time
import json
import os

# Modified QPlainTextEdit to act as a logger output and catch the logger calls

class QTextEditLogger(QtWidgets.QWidget, logging.Handler):

    def __init__(self, parent, log_path):
        super().__init__()

        self.widget = QtWidgets.QPlainTextEdit()
        self.widget.setProperty('output', True)
        self.widget.setReadOnly(True)
        self.widget.setFont(QFont('Segoe UI'))

        with open('C:/HyPro/hyprosettings.json', 'r') as temp:
            params = json.loads(temp.read())
        self.active_processor = params['activeprocessor']

        self.log_path = log_path
        try:
            with open(self.log_path, mode='r+') as file:
                self.widget.appendPlainText(file.read()[-8000:])

        except IOError:
            with open(self.log_path, mode='w+') as file:
                file.close()

        self.widget.appendPlainText(' . . . ')

    def emit(self, record):
        msg = self.format(record)
        currenttime = time.strftime('%d/%m %H:%M:%S', time.localtime(time.time()))[:-3]
        self.output = currenttime + ' | ' + self.active_processor + ': ' + msg
        time.sleep(0.1)
        self.widget.appendHtml(self.output)
        try:
            with open(self.log_path, mode='a+') as file:
                file.write(self.output + '\n')
        except Exception:
            print(Exception)
            pass

    def clear(self):
        self.widget.clear()
        self.widget.appendPlainText(' . . . ')

    def gettext(self):
        text = self.widget.toPlainText()
        return text
