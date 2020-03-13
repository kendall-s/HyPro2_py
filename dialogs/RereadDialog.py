from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QMessageBox, QListWidget)
import sqlite3, re
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
    def __init__(self, path, project, database, interactive):
        super().__init__(220, 480, 'HyPro - Reread Data')

        self.currpath = path
        self.currproject = project
        self.db = database
        self.interactive = interactive

        self.init_ui()

        self.show()

    def init_ui(self):
        analysistypeslist = ['Nutrients', 'Salinity', 'Oxygen', 'CTD', 'Sampling']

        analysistypelabel = QLabel('Analysis Type: ', self)

        self.analysistype = QComboBox()
        self.analysistype.addItems(analysistypeslist)
        self.analysistype.setFixedHeight(25)
        self.analysistype.activated.connect(self.populatefileslist)
        self.analysistype.setCurrentText('Nutrients')
        self.analysistype.setEditable(True)
        self.analysistype.setEditable(False)
        datafileslabel = QLabel('Select data to reread: ', self)

        self.itemselectedboolean = 0

        self.datafiles = QListWidget()
        self.datafiles.itemSelectionChanged.connect(self.itemselected)
        self.datafiles.itemDoubleClicked.connect(self.rereaddata)

        okbut = QPushButton('Reread Data', self)
        okbut.clicked.connect(self.rereaddata)
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
            filenames = [x[0] for x in data]

            self.datafiles.addItems(filenames)
        except Exception as e:
            print(e)

    def populatefileslist(self):
        # Fill the list with the files that have already been processed
        filetype = self.analysistype.currentText()

        self.datafiles.clear()

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        if filetype == 'CTD':
            c.execute('SELECT * from ctdFilesProcessed ORDER BY filename')
        if filetype == 'Nutrients':
            c.execute('SELECT * from nutrientFilesProcessed ORDER BY filename')
        if filetype == 'Salinity':
            c.execute('SELECT * from salinityFilesProcessed ORDER BY filename')
        if filetype == 'Oxygen':
            c.execute('SELECT * from oxygenFilesProcessed ORDER BY filename')
        if filetype == 'Sampling':
            c.execute('SELECT * from logsheetFilesProcessed ORDER BY filename')

        data = list(c.fetchall())
        c.close()
        filenames = [x[0] for x in data]

        self.datafiles.addItems(filenames)

    def itemselected(self):
        self.itemselectedboolean = 1

    def rereaddata(self):

        filetype = self.analysistype.currentText()

        if self.itemselectedboolean == 1:
            selectedfile = str(self.datafiles.currentItem().text())

            if filetype == 'CTD':
                self.initctd = InitialiseCTDData.initCTDdata(selectedfile, self.db, self.currpath, self.currproject,
                                                             self.interactive, True)

            if filetype == 'Nutrients':
                self.initnutrientdata = processingNutrientsWindow(selectedfile, self.db, self.currpath,
                                                                  self.currproject, self.interactive, True)

            if filetype == 'Salinity':
                self.initsaltdata = processingSalinityWindow(selectedfile, self.db, self.currpath, self.currproject,
                                                             self.interactive, True)

            if filetype == 'Oxygen':
                self.initoxydata = processingOxygenWindow(selectedfile, self.db, self.currpath, self.currproject,
                                                          self.interactive, True)

            if filetype == 'Sampling':
                self.initsampledata = InitialiseSampleSheet.initSampleSheet(selectedfile, self.currproject, self.db,
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
