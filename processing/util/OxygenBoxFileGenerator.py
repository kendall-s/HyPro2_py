from PyQt5.QtWidgets import (QPushButton, QAbstractItemView, QLabel, QListWidget, QCheckBox)
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
import sqlite3
import os
import logging

# Small GUI dialog that provides information and functionality when a peak is clicked on the trace of
# nutrient processing
"""
Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad, 
                91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different
"""

"""
A short utility for generating oxygen analysis box files. These simple text files are read in by the oxygen instrument
and allow analysis to be much faster as all sample information is automatically read from the box file.
"""


class generateBoxFile(hyproDialogTemplate):

    def __init__(self, database, path, project):
        super().__init__(240, 500, 'HyPro - Box File Generator')

        self.database = database
        self.path = path
        self.project = project

        self.init_ui()

        self.get_deloyments_available()

    def init_ui(self):

        title_label = QLabel('<b>Box File Generator</b>')

        self.rp_descending = QCheckBox('RP Descending Order')
        self.rp_descending.setChecked(True)

        deployments_available_label = QLabel('Deployments Available:')

        self.deployments_available = QListWidget(self)
        self.deployments_available.setSelectionMode(QAbstractItemView.ExtendedSelection)

        generate_box_file = QPushButton('Generate Box File')
        generate_box_file.clicked.connect(self.generate_box)

        self.grid_layout.addWidget(title_label, 0, 0)
        self.grid_layout.addWidget(self.rp_descending, 1, 0)
        self.grid_layout.addWidget(deployments_available_label, 2, 0)
        self.grid_layout.addWidget(self.deployments_available, 3, 0)
        self.grid_layout.addWidget(generate_box_file, 4, 0)

    def generate_box(self, external_data=None):

        """
        A box file is a simple text file and looks like the following:
        101
        1
        1
        1
        1
        user
        33    144    16.3
        29    143    15.6
        and so on ...

        At the top is the station number and cast. CSIRO just uses deployment and keeps incrementing, so just increment
        station number. i.e. 101, 201, 301 = deps 1, 2 and 3
        Then four 1s, read the manual what these are for can't remember
        Then the user operating, hypro puts its name for now.
        Then the bottle data, which is rosette position, bottle number and oxygen sample temp
        """


        if not external_data:
            data = self.get_logsheet_data()
        else:
            data = external_data

        initial_deployment = data[0][0]
        print(initial_deployment)
        if int(initial_deployment) < 10:
            initial_deployment_fmt = '0' + str(initial_deployment)
        else:
            initial_deployment_fmt = initial_deployment

        if self.make_folder():
            with open(f'{self.path}/Oxygen/BoxFiles/0{initial_deployment_fmt}01.box', mode='w+') as file:
                # Write weird box file header
                file.write(f'{initial_deployment}01\t\t\n') # station (deployment) and cast
                file.write('1\t\t\n')
                file.write('1\t\t\n')
                file.write('1\t\t\n')
                file.write('1\t\t\n')
                file.write('hypro\t\t\n') # user

                # Now lets write the box file data
                for row in data:
                    if row[2] != "":
                        file.write(f'{row[1]}\t{row[2]}\t{row[3]}\n')

            message = hyproMessageBoxTemplate('success', 'Box file successfully created!', 'success')

    def get_deloyments_available(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('SELECT DISTINCT deployment from logsheetData')
        deployments = c.fetchall()
        print(deployments)
        for dep in deployments:
            self.deployments_available.addItem(str(dep[0]))

    def get_logsheet_data(self):
        selected_deployments_raw = self.deployments_available.selectedItems()
        selected_deployments = [item.text() for item in selected_deployments_raw]

        query_placeholder = ', '.join('?' for unused in selected_deployments)

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        if self.rp_descending.checkState():
            rp_sort_direction = 'DESC'
        else:
            rp_sort_direction = 'ASC'

        c.execute(f'SELECT deployment, rosettePosition, oxygen, oxygenTemp '
                  f'FROM logsheetData WHERE deployment in ({query_placeholder}) '
                  f'ORDER BY deployment ASC, rosettePosition {rp_sort_direction}', selected_deployments)

        returned_data = c.fetchall()
        return returned_data

    def make_folder(self):
        if os.path.isdir(f'{self.path}/Oxygen/BoxFiles'):
            pass
        else:
            try:
                os.mkdir(f'{self.path}/Oxygen/BoxFiles')
            except Exception:
                logging.error('ERROR: Cannot make box file directory. Maybe I do not have permissions')
                return False
        return True
