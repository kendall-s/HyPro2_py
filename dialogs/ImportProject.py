import csv
import json
import logging
import os
import time
import traceback

from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QFileDialog)

from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate

"""
Allows a user to import the .hypro project file which then adds that project path and name to the known projects on
a users computer
"""


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

            # First check if the project already exists in the list
            if projprefixstr[0] not in self.params['projects']:

                # Update the parameters projects file to include project
                # if any(projprefixstr == x[0] for x in projects) == False:
                prefix = str(projprefixstr[0])
                type = str(self.filelist[1][0])
                path = str(self.filelist[2][0])

                newproj = {'%s' % prefix: {'path': path, 'type': type}}
                self.params['projects'].update(newproj)
                # Save back to disk
                with open('C:/HyPro/hyprosettings.json', 'w') as file:
                    json.dump(self.params, file)

                messagebox = hyproMessageBoxTemplate('Success',
                                                     'An existing project was successfully imported.',
                                                     'success')

                time.sleep(0.5)

                self.close()
            else:
                messagebox = hyproMessageBoxTemplate('Error',
                                                     'A project with that name already exists in the known project list.',
                                                     'error')
        except Exception:
            logging.error(traceback.print_exc())

    def cancel(self):
        print('Cancel')
        self.close()
