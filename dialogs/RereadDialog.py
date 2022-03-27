from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QMessageBox, QListWidget)
import sqlite3, re
import logging
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from processing.readdata import InitialiseCTDData, InitialiseSampleSheet
from processing.procdata.InteractiveOxygenProcessing import processingOxygenWindow
from processing.procdata.InteractiveSalinityProcessing import processingSalinityWindow
from processing.procdata.InteractiveNutrientsProcessing import processingNutrientsWindow
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate


# GUI interface for reprocessing any files, the files need to already be processed and ingested through the refresh
# function
class rereadDialog(hyproDialogTemplate):
    def __init__(self, path, project, database, interactive, perf_mode, ultra_perf_mode):
        super().__init__(220, 480, 'HyPro - Reread Data')

        self.currpath = path
        self.currproject = project
        self.db = database
        self.interactive = interactive

        self.performance_mode = perf_mode
        self.ultra_performance_mode = ultra_perf_mode

        self.init_ui()

        self.show()

    def init_ui(self):
        analysistypeslist = ['Nutrients', 'Salinity', 'Oxygen', 'CTD', 'Sampling']

        analysistypelabel = QLabel('Analysis Type: ', self)

        self.analysistype = QComboBox()
        self.analysistype.addItems(analysistypeslist)
        self.analysistype.setFixedHeight(25)
        self.analysistype.activated.connect(self.populate_files_list)
        self.analysistype.setCurrentText('Nutrients')
        self.analysistype.setEditable(True)
        self.analysistype.setEditable(False)
        datafileslabel = QLabel('Select data to reread: ', self)

        self.item_selected_check = 0

        self.datafiles = QListWidget()
        self.datafiles.itemSelectionChanged.connect(self.item_selected)
        self.datafiles.itemDoubleClicked.connect(self.reread_data)

        okbut = QPushButton('Reread Data', self)
        okbut.clicked.connect(self.reread_data)
        okbut.setFixedWidth(100)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)
        cancelbut.setFixedWidth(100)

        self.grid_layout.addWidget(analysistypelabel, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.analysistype, 1, 0, 1, 2)

        self.grid_layout.addWidget(datafileslabel, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.datafiles, 3, 0, 6, 2)

        self.grid_layout.addWidget(okbut, 10, 0)
        self.grid_layout.addWidget(cancelbut, 10, 1)

        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute('SELECT * from nutrientFilesProcessed')
            data = list(c.fetchall())
            c.close()
            file_names = [x[0] for x in data]

            self.datafiles.addItems(file_names)
        except Exception as e:
            print(e)

    def populate_files_list(self):
        # Fill the list with the files that have already been processed
        file_type = self.analysistype.currentText()

        db_name_folder_converter = {'CTD': 'ctd', 'Sampling': 'logsheet', 'Salinity': 'salinity', 'Oxygen': 'oxygen',
                                    'Nutrients': 'nutrient'}

        self.datafiles.clear()

        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute(f'SELECT * from {db_name_folder_converter[file_type]}FilesProcessed')

        data = list(c.fetchall())
        c.close()
        file_names = [x[0] for x in data]

        self.datafiles.addItems(file_names)

    def item_selected(self):
        self.item_selected_check = 1

    def reread_data(self):

        file_type = self.analysistype.currentText()

        if self.item_selected_check == 1:
            selected_file = str(self.datafiles.currentItem().text())
            logging.info(f'Rereading file {selected_file}')

            if file_type == 'CTD':
                self.init_ctd = InitialiseCTDData.initCTDdata(selected_file, self.db, self.currpath, self.currproject,
                                                             self.interactive, True)

            if file_type == 'Nutrients':
                self.init_nutrient_data = processingNutrientsWindow(selected_file, self.db, self.currpath,
                                                                  self.currproject, self.interactive, rereading=True,
                                                                  perf_mode=self.performance_mode,
                                                                  ultra_perf_mode=self.ultra_performance_mode)
            if file_type == 'Salinity':
                self.init_salt_data = processingSalinityWindow(selected_file, self.db, self.currpath, self.currproject,
                                                             self.interactive, True)
                self.init_salt_data.process_routine()

            if file_type == 'Oxygen':
                self.init_oxy_data = processingOxygenWindow(selected_file, self.db, self.currpath, self.currproject,
                                                          self.interactive, True)

            if file_type == 'Sampling':
                self.init_sample_data = InitialiseSampleSheet.initSampleSheet(selected_file, self.currproject, self.db,
                                                                            self.currpath, self.interactive, True)

        else:
            messagebox = hyproMessageBoxTemplate('Error',
                                                 'Please select a file to reread...         ',
                                                 'information')
    def cancel(self):
        self.close()

    def intcheck(self, text):
        return int(text) if text.isdigit() else text

    def naturalsort(self, text):
        return [self.intcheck(x) for x in re.split('(\d+)', text)]
