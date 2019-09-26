from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QListWidget, QAbstractItemView)
import sqlite3
from dialogs.ViewData import viewData
from dialogs.templates.DialogTemplate import hyproDialogTemplate


class viewDataDialog(hyproDialogTemplate):
    def __init__(self, database, parameters):
        super().__init__(380, 420, 'HyPro - Select Data to View')

        self.db = database
        self.params = parameters
        self.nutrients = ['nitrate', 'phosphate', 'silicate', 'ammonia', 'nitrite']
        
        self.init_ui()

        self.populatelist()

        self.show()


    def init_ui(self):
        survey_label = QLabel('Survey')

        self.survey_combo = QComboBox()
        self.survey_combo.clear()
        self.survey_combo.addItems(self.params['surveyparams'].keys())
        self.survey_combo.setEditable(True)
        self.survey_combo.setEditable(False)

        analysistypelabel = QLabel('Analysis Type: ', self)

        analyses = ['As CTD Results', 'All Available Nutrients', 'Nitrate', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia', 'Salinity', 'Dissolved Oxygen', 'CTD',
                    'Logsheet']

        self.analysistype = QComboBox()
        self.analysistype.clear()
        self.analysistype.addItems(analyses)
        self.analysistype.setEditable(True)
        self.analysistype.setEditable(False)
        self.analysistype.activated.connect(self.populatelist)

        viewbylabel = QLabel('View Data by: ', self)

        views = ['Deployment', 'File']

        self.viewby = QComboBox()
        self.viewby.clear()
        self.viewby.addItems(views)
        self.viewby.setEditable(True)
        self.viewby.setEditable(False)
        self.viewby.activated.connect(self.populatelist)

        datafileslabel = QLabel('Select data to view: ', self)

        self.datafiles = QListWidget()
        self.datafiles.setSelectionMode(QAbstractItemView.ExtendedSelection)

        okbut = QPushButton('View Data', self)
        okbut.clicked.connect(self.viewdata)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(survey_label, 0, 0)
        self.grid_layout.addWidget(self.survey_combo, 0, 1, 1, 4)

        self.grid_layout.addWidget(analysistypelabel, 1, 0)
        self.grid_layout.addWidget(self.analysistype, 1, 1, 1, 4)

        self.grid_layout.addWidget(viewbylabel, 2, 0)
        self.grid_layout.addWidget(self.viewby, 2, 1, 1, 4)

        self.grid_layout.addWidget(datafileslabel, 3, 0)
        self.grid_layout.addWidget(self.datafiles, 3, 1, 1, 4)

        self.grid_layout.addWidget(okbut, 4, 1)
        self.grid_layout.addWidget(cancelbut, 4, 2)

    def viewdata(self):
        try:
            print('View Data')
            selected = self.datafiles.selectedItems()
            selectedtext = [item.text() for item in selected]
            sel = 0
            if self.viewby.currentText() == 'Deployment':
                sel = [x[11:] for x in selectedtext]

            if self.viewby.currentText() == 'File':
                sel = [x[5:] for x in selectedtext]

            analysis = self.analysistype.currentText()
            view = self.viewby.currentText()

            self.tableview = viewData(analysis, view, sel, self.db)
            self.tableview.show()

        except Exception as e:
            print(e)

    def cancel(self):
        self.close()

    def populatelist(self):

        all_nuts = False
        self.viewby.setDisabled(False)

        self.datafiles.clear()

        analysis = self.analysistype.currentText()
        view = self.viewby.currentText()

        conn = sqlite3.connect(self.db)
        self.c = conn.cursor()

        if analysis == 'Salinity':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from salinityData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from salinityData')

        elif analysis == 'Dissolved Oxygen':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT stationNumber from oxygenData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from oxygenData')

        elif analysis == 'CTD':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from ctdData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT deployment from ctdData')

        elif analysis == 'Logsheet':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from logsheetData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT deployment from logsheetData')

        elif analysis == 'Nitrate':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from nitrateData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from nitrateData')

        elif analysis == 'Silicate':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from silicateData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from silicateData')

        elif analysis == 'Phosphate':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from phosphateData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from phosphateData')

        elif analysis == 'Nitrite':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from nitriteData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from nitriteData')

        elif analysis == 'Ammonia':
            if view == 'Deployment':
                self.c.execute('SELECT DISTINCT deployment from ammoniaData')
            elif view == 'File':
                self.c.execute('SELECT DISTINCT runNumber from ammoniaData')
        elif analysis == 'As CTD Results':
            self.viewby.setCurrentText('Deployment')
            self.viewby.setDisabled(True)
            self.c.execute('SELECT DISTINCT deployment from ctdData')
        elif analysis == 'All Available Nutrients':
            avail_numbers = []
            for x in self.nutrients:
                if view == 'Deployment':
                    self.c.execute('SELECT DISTINCT deployment from %sData' % x)
                elif view == 'File':
                    self.c.execute('SELECT DISTINCT runNumber from %sData' % x)

                avail_numbers.append(self.c.fetchall())
            # TODO: get rid of duplicates in a clean manner - can't be bothered with it right now
            data = avail_numbers
            all_nuts = True

        if not all_nuts:
            data = list(self.c.fetchall())

        self.c.close()
        datatodisp = []
        if view == 'Deployment':
            for i in data:
                datatodisp.append('Deployment ' + str(i[0]))
        if view == 'File':
            for i in data:
                datatodisp.append('File ' + str(i[0]))
        self.datafiles.addItems(datatodisp)
