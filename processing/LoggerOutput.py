from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
import logging
import time
import json
import os

# Modified QPlainTextEdit to act as a logger output and catch the logger calls

class QTextEditLogger(QtWidgets.QWidget, logging.Handler):

    append_text = pyqtSignal(str)

    def __init__(self, parent, log_path):
        super().__init__()
        self.log_path = log_path

        self.widget = QtWidgets.QPlainTextEdit()
        self.widget.setProperty('output', True)
        self.widget.setReadOnly(True)
        self.widget.setFont(QFont('Segoe UI'))

        #self.append_text.connect(self.widget.appendPlainText



    def start_up(self):
        with open('C:/HyPro/hyprosettings.json', 'r') as temp:
            params = json.loads(temp.read())
        self.active_processor = params['activeprocessor']

        try:
            with open(self.log_path, mode='r+') as file:
                self.append_text.emit(file.read()[-8000:])

        except IOError:
            with open(self.log_path, mode='w+') as file:
                file.close()

        self.widget.appendPlainText(' . . . ')

    def update_text_box(self, message):
        self.widget.appendPlainText(message)
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())

    def emit(self, record):
        msg = self.format(record)
        current_time = time.strftime('%d/%m %H:%M:%S', time.localtime(time.time()))[:-3]
        self.output = current_time + ' | ' + self.active_processor + ': ' + msg
        time.sleep(0.01)
        self.append_text.emit(self.output)
        try:
            with open(self.log_path, mode='a+') as file:
                file.write(self.output + '\n')
        except Exception:
            print(Exception)
            pass

    def clear(self):
        self.widget.clear()
        self.append_text.emit('. . .')

    def gettext(self):
        text = self.widget.toPlainText()
        return text
