from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QMessageBox,
                             QFileDialog, )
import csv, os, json, logging, traceback
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from dialogs.templates.DialogTemplate import hyproDialogTemplate
import time
# GUI and functionality for importing an existing project into Hypro, ie copying a project from the ship pc to your
# pc and now opening it up and continuing processing data with it


class importProject(hyproDialogTemplate):
    def __init__(self):
        super().__init__(450, 150, 'HyPro - Import Project')

        self.init_ui()

        self.show()

    def init_ui(self):
        importprojlabel = QLabel('Browse for a project file:', self)

        self.projdirec = QLineEdit('', self)

        projdirecbut = QPushButton('Browse...', self)
        projdirecbut.clicked.connect(self.browsePath)

        okbut = QPushButton('Import', self)
        okbut.clicked.connect(self.importProj)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(importprojlabel, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.projdirec, 1, 0, 1, 3)
        self.grid_layout.addWidget(projdirecbut, 1, 3)
        self.grid_layout.addWidget(okbut, 2, 1)
        self.grid_layout.addWidget(cancelbut, 2, 2)

    def browsePath(self):
        # Browse for an existing 'hypro' project file
        propath = QFileDialog.Options()
        files = QFileDialog.getOpenFileName(self, "Select Project", 'c://', "HyPro Project (*.hypro)")
        if os.path.exists(files[0]):
            filebuffer = open(files[0])
            readbuffer = csv.reader(filebuffer)
            self.filelist = list(readbuffer)
            self.projdirec.setText(files[0])

    def importProj(self):
        projprefixstr = self.filelist[0]
        try:
            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                self.params = json.load(f)
            # Update the parameters projects file to include project
            # if any(projprefixstr == x[0] for x in projects) == False:
            prefix = str(projprefixstr[0])
            type = str(self.filelist[1][0])
            path = str(self.filelist[2][0])

            newproj = {'%s' % prefix: {'path': path}, 'type': type}
            self.params['projects'].update(newproj)
            # Save back to disk
            with open('C:/HyPro/hyprosettings.json', 'w') as file:
                json.dump(self.params, file)

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                     "An existing project was successfully imported.",
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()

            time.sleep(0.5)

            self.close()

        except Exception:
            logging.error(traceback.print_exc())

    def cancel(self):
        print('Cancel')
        self.close()
