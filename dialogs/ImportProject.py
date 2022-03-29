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
        import_project_label = QLabel('Browse for a project file:', self)

        self.project_directory = QLineEdit('', self)

        project_directory_button = QPushButton('Browse...', self)
        project_directory_button.clicked.connect(self.browsePath)

        ok_button = QPushButton('Import', self)
        ok_button.clicked.connect(self.importProj)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)

        self.grid_layout.addWidget(import_project_label, 0, 0, 1, 3)
        self.grid_layout.addWidget(self.project_directory, 1, 0, 1, 3)
        self.grid_layout.addWidget(project_directory_button, 1, 3)
        self.grid_layout.addWidget(ok_button, 2, 1)
        self.grid_layout.addWidget(cancel_button, 2, 2)

    def browsePath(self):
        # Browse for an existing 'hypro' project file
        propath = QFileDialog.Options()
        files = QFileDialog.getOpenFileName(self, "Select Project", 'c://', "HyPro Project (*.hypro)")
        if os.path.exists(files[0]):
            # Need to parse the file path to get the folder path. Then we will update the .hypro file with this
            file_buffer = open(files[0])
            read_buffer = csv.reader(file_buffer)
            self.project_file_list = list(read_buffer)
            self.project_directory.setText(files[0])

    def importProj(self):
        project_prefix_str = self.project_file_list[0]
        try:
            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                self.params = json.load(f)

            # First check if the project already exists in the list
            if project_prefix_str[0] not in self.params['projects']:

                # Update the parameters projects file to include project
                # if any(project_prefix_str == x[0] for x in projects) == False:
                prefix = str(project_prefix_str[0])
                type = str(self.project_file_list[1][0])
                path = str(self.project_file_list[2][0])

                new_proj = {'%s' % prefix: {'path': path, 'type': type}}
                self.params['projects'].update(new_proj)
                # Save back to disk
                with open('C:/HyPro/hyprosettings.json', 'w') as file:
                    json.dump(self.params, file)

                # Update the imported .hypro file with the path that it lives in
                file_buffer = open(self.project_directory.text(), 'w')
                file_buffer.write(prefix + '\n')
                file_buffer.write(type + '\n')
                file_buffer.write(os.path.dirname(self.project_directory.text()) + '\n')
                file_buffer.close()

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
