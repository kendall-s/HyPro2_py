import sys, os, pprint, statistics, json, xlrd, sqlite3, traceback, logging
from PyQt5.QtCore import pyqtSignal, QObject

# Reads in the sample log sheet for the bottle numbers, currently using a prototype excel sheet, was meant to be easy
# to edit and modify as needed for hydrochem members

class initSampleSheet(QObject):

    processing_completed = pyqtSignal()

    def __init__(self, file, project, database, path, interactive, rereading):
        super().__init__()

        self.currproject = project

        self.file = file

        self.database = database

        self.currpath = path

        self.interactive = interactive

        self.rereading = rereading

        self.filepath = self.currpath + '/' + 'Sampling' + '/' + self.file

        self.loadfilein()

    def loadfilein(self):
        try:
            # Open file
            fileopen = xlrd.open_workbook(self.filepath)

            datasheet = fileopen.sheet_by_index(0)

            rosetteposition = datasheet.col_values(0)
            rosetteposition.__delitem__(0)

            oxygenlabels = datasheet.col_values(1)
            oxygenlabels.__delitem__(0)

            oxygentemp = datasheet.col_values(2)
            oxygentemp.__delitem__(0)

            salinitylabels = datasheet.col_values(3)
            salinitylabels.__delitem__(0)

            nutrientlabels = datasheet.col_values(4)
            nutrientlabels.__delitem__(0)

            # Work out deployment number
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())

            prefixlength = len(params['analysis_params']['logsheet']['file_prefix'])
            runformatlength = len(params['analysis_params']['logsheet']['run_format'])
            depnum = self.file[prefixlength: (prefixlength + runformatlength)]
            depnumber = []
            for i in range(len(rosetteposition)):
                depnumber.append(depnum)

            # Pack it up and put it in db
            logdata = tuple(zip(depnumber, rosetteposition, oxygenlabels, oxygentemp, salinitylabels, nutrientlabels))

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.executemany('INSERT OR REPLACE INTO logsheetData VALUES(?,?,?,?,?,?)', logdata)
            conn.commit()
            conn.close()

            modtime = float(os.path.getmtime(self.filepath))
            holder = ((self.file, modtime),)

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.executemany('INSERT OR REPLACE INTO logsheetFilesProcessed VALUES(?,?)', holder)
            conn.commit()

            logging.info('Sample sheet ' + str(self.file) + ' successfully processed')
            if not self.rereading:
                self.processing_completed.emit()

        except Exception:
            logging.error(traceback.print_exc())
