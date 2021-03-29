# https://pythonspot.com/pyqt5-file-dialog/
# http://www.qtcentre.org/threads/20895-PyQt4-Want-to-connect-a-window-s-close-button
# https://pythonprogramminglanguage.com/pyqt5-window-flags/
# https://stackoverflow.com/questions/23617112/how-to-process-only-new-unprocessed-files-in-linux

from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QFileDialog)
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
import os, logging, traceback, json
from time import sleep
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
# Class for the functionality and interface for creating a new project


class createNewProject(hyproDialogTemplate):

    new_project_created = pyqtSignal()

    def __init__(self):
        super().__init__(650, 150, 'HyPro - Create New Project')

        self.init_ui()

        self.show()

    def init_ui(self):
        project_type_label = QLabel('Project Type', self)

        self.project_type = QComboBox(self)
        self.project_type.addItems(['CTD', 'Shore'])

        project_directory_label = QLabel('Project directory:')

        self.project_directory = QLineEdit('', self)

        project_directory_but = QPushButton('Browse...')
        project_directory_but.clicked.connect(self.browsePath)

        project_prefix_label = QLabel('Project Name \nand File Prefix:')

        self.project_prefix = QLineEdit('', self)

        okbut = QPushButton('Create', self)
        okbut.clicked.connect(self.createProj)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(project_type_label, 0, 1)
        self.grid_layout.addWidget(self.project_type, 0, 2)

        self.grid_layout.addWidget(project_directory_label, 1, 0)
        self.grid_layout.addWidget(self.project_directory, 1, 1, 1, 2)
        self.grid_layout.addWidget(project_directory_but, 1, 3)

        self.grid_layout.addWidget(project_prefix_label, 2, 0)
        self.grid_layout.addWidget(self.project_prefix, 2, 1, 1, 3)

        self.grid_layout.addWidget(okbut, 3, 1)
        self.grid_layout.addWidget(cancelbut, 3, 2)

    # Creating the project function, lengthy because it checks if there is already an existing project
    # with the same name. This also creates the correct directories and the project file
    def createProj(self):
        try:
            self.project_directorystr = str(self.project_directory.text())
            self.project_prefix_str = str(self.project_prefix.text())
            self.project_type_str = str(self.project_type.currentText())

            if (self.project_directorystr != '') & (self.project_prefix_str != ''):

                if os.path.exists(self.project_directory.text()):

                    project_directorystr = str(self.project_directory.text())

                    with open('C:/HyPro/hyprosettings.json', 'r') as f:
                        self.params = json.load(f)

                    continue_create_proj = True
                    for x in self.params['projects'].keys():
                        if self.project_prefix_str == x:
                            messagebox = hyproMessageBoxTemplate('Error',
                                                                 'There is already a project with that name, please '
                                                                 'choose a different name for the project.', 'error')
                            continue_create_proj = False

                    if continue_create_proj:

                        new_proj = {'%s' % self.project_prefix_str: {'path': project_directorystr, 'type': self.project_type_str}}

                        self.params['projects'].update(new_proj)

                        #self.params['activeproject'] = project_prefixstr

                        # Write project info back to disk
                        with open('C:/HyPro/hyprosettings.json', 'w') as file:
                            json.dump(self.params, file)

                        # Create directories for the project
                        if not os.path.exists((project_directorystr + "/Nutrients")):
                            os.makedirs((project_directorystr + "/Nutrients"))
                        if not os.path.exists((project_directorystr + "/Salinity")):
                            os.makedirs((project_directorystr + "/Salinity"))
                        if not os.path.exists((project_directorystr + "/Oxygen")):
                            os.makedirs((project_directorystr + "/Oxygen"))
                        if not os.path.exists((project_directorystr + "/CTD")):
                            os.makedirs((project_directorystr + "/CTD"))
                        if not os.path.exists((project_directorystr + "/Sampling")):
                            os.makedirs((project_directorystr + "/Sampling"))

                        # Make weird little hack 'hypro' file, used for when a project needs to be imported
                        filebuffer = open(project_directorystr + '/' + self.project_prefix_str + '.hypro', 'w')
                        filebuffer.write(self.project_prefix_str + '\n')
                        filebuffer.write(self.project_type_str + '\n')
                        filebuffer.write(project_directorystr + '\n')
                        filebuffer.close()


                        messagebox = hyproMessageBoxTemplate('Success', 'A new project was successfully created.',
                                                             'success')
                        sleep(0.4)
                        self.close()
                        sleep(0.5)
                        self.new_project_created.emit()

                    else:
                        messagebox = hyproMessageBoxTemplate('Error',
                                                             'There is already a project with that name, please choose '
                                                             'a different name for the project.', 'error')
                else:
                    messagebox = hyproMessageBoxTemplate('Error', 'Provided path does not exist', 'error')

            else:
                messagebox = hyproMessageBoxTemplate('Error', 'Fields are empty, please fill them in.', 'information')

        except Exception as e:
            logging.error(traceback.print_exc())

    def browsePath(self):
        propath = QFileDialog.Options()
        files = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.project_directory.setText(files)
        self.project_directory.setReadOnly(True)

    def cancel(self):
        self.close()
