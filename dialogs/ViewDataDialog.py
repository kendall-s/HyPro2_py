from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QListWidget, QAbstractItemView)
import sqlite3
from dialogs.ViewData import viewData
import traceback
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from PyQt5.QtCore import Qt

DATABASE_NAME_CONVERTER = {'Salinity': 'salinity', 'Dissolved Oxygen': 'oxygen', 'Nitrate': 'nitrate',
                           'Silicate': 'silicate', 'Phosphate': 'phosphate', 'Nitrite': 'nitrite', 'Ammonia': 'ammonia'}

class viewDataDialog(hyproDialogTemplate):
    def __init__(self, database, parameters):
        super().__init__(220, 550, 'HyPro - Select Data to View')

        self.db = database
        self.params = parameters
        self.nutrients = ['nitrate', 'phosphate', 'silicate', 'ammonia', 'nitrite']

        self.analyses = ['As CTD Results', 'All Available Nutrients', 'Nitrate', 'Phosphate', 'Silicate', 'Nitrite',
                    'Ammonia', 'Salinity', 'Dissolved Oxygen', 'CTD',
                    'Logsheet']

        self.init_ui()

        self.populate_list()

        self.show()


    def init_ui(self):

        # Remove modality for this dialog, not really necessary
        self.setWindowModality(Qt.NonModal)

        survey_label = QLabel('Survey:')

        self.survey_combo = QComboBox()
        self.survey_combo.clear()
        self.survey_combo.addItems(self.params['survey_params'].keys())
        self.survey_combo.addItems(['Any', 'StandardQC', 'RMNS', 'Null', 'MDL', 'BQC', 'Test'])
        self.survey_combo.setEditable(True)
        self.survey_combo.setEditable(False)
        self.survey_combo.activated.connect(self.populate_list)

        analysistypelabel = QLabel('Analysis Type: ', self)

        self.analysis_type = QComboBox()
        self.analysis_type.clear()
        self.analysis_type.addItems(self.analyses)
        self.analysis_type.setEditable(True)
        self.analysis_type.setEditable(False)
        self.analysis_type.activated.connect(self.populate_list)

        view_by_label = QLabel('View Data by: ', self)

        views = ['Deployment', 'File']

        self.view_by = QComboBox()
        self.view_by.clear()
        self.view_by.addItems(views)
        self.view_by.setEditable(True)
        self.view_by.setEditable(False)
        self.view_by.activated.connect(self.populate_list)

        datafileslabel = QLabel('Select data to view: ', self)

        self.datafiles = QListWidget()
        self.datafiles.setSelectionMode(QAbstractItemView.ExtendedSelection)

        okbut = QPushButton('View Data', self)
        okbut.clicked.connect(self.view_data)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(survey_label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.survey_combo, 1, 0, 1, 2)

        self.grid_layout.addWidget(analysistypelabel, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.analysis_type, 3, 0, 1, 2)

        self.grid_layout.addWidget(view_by_label, 4, 0, 1, 2)
        self.grid_layout.addWidget(self.view_by, 5, 0, 1, 2)

        self.grid_layout.addWidget(datafileslabel, 6, 0, 1, 2)
        self.grid_layout.addWidget(self.datafiles, 7, 0, 5, 2)
        self.grid_layout.setRowStretch(7, 1)

        self.grid_layout.addWidget(okbut, 13, 0)
        self.grid_layout.addWidget(cancelbut, 13, 1)

    def view_data(self):
        try:
            selected = self.datafiles.selectedItems()
            selected_text = [item.text() for item in selected]
            if len(selected_text) > 0:
                sel = 0
                if self.view_by.currentText() == 'Deployment':
                    sel = [x[11:] for x in selected_text]

                if self.view_by.currentText() == 'File':
                    sel = [x[5:] for x in selected_text]

                survey = self.survey_combo.currentText()
                analysis = self.analysis_type.currentText()
                view = self.view_by.currentText()

                self.tableview = viewData(survey, analysis, view, sel, self.db)
                self.tableview.show()

        except Exception as e:
            print(e)
            print(traceback.print_exc())

    def cancel(self):
        self.close()

    def populate_list(self):

        all_nuts = False
        self.view_by.setDisabled(False)

        self.datafiles.clear()

        # If the survey is anything other than the base (i.e. one for voyage deployments
        # remove the deployments option. The base survey will always be index 0
        in_combobox = self.analysis_type.findText('As CTD Results')
        if self.survey_combo.currentIndex() != 0:
            self.view_by.setCurrentText('File')
            self.view_by.setDisabled(True)
            # Remove the CTD results option as there won't be any in this survey, best to check
            # that it is still in the combobox too - we might have already removed it
            if in_combobox > -1: # The find text method returns the index if text is in combobox or -1 if not
                self.analysis_type.removeItem(0)
        else:
            if in_combobox < 0:
                self.view_by.setDisabled(False)
                self.analysis_type.clear()
                self.analysis_type.addItems(self.analyses)

        survey = self.survey_combo.currentText()
        analysis = self.analysis_type.currentText()
        view = self.view_by.currentText()

        conn = sqlite3.connect(self.db)
        c = conn.cursor()


        if analysis in ['Salinity', 'Dissolved Oxygen', 'Nitrate', 'Silicate', 'Phosphate', 'Nitrite', 'Ammonia']:
            analysis = DATABASE_NAME_CONVERTER[analysis]

            # If the survey is set to any, remove the WHERE survey filter and just get all runNumbers for an analysis
            if survey == 'Any':
                c.execute('SELECT DISTINCT runNumber from %sData' % analysis)

            else:
                if view == 'Deployment':
                    c.execute('SELECT DISTINCT deployment from %sData WHERE survey=?' % analysis, (survey,))
                elif view == 'File':
                    c.execute('SELECT DISTINCT runNumber from %sData WHERE survey=?' % analysis, (survey,))


        elif analysis == 'CTD':
            if view == 'Deployment':
                c.execute('SELECT DISTINCT deployment from ctdData')
            elif view == 'File':
                c.execute('SELECT DISTINCT deployment from ctdData')


        elif analysis == 'Logsheet':
            if view == 'Deployment':
                c.execute('SELECT DISTINCT deployment from logsheetData')
            elif view == 'File':
                c.execute('SELECT DISTINCT deployment from logsheetData')


        elif analysis == 'As CTD Results':
            self.view_by.setCurrentText('Deployment')
            self.view_by.setDisabled(True)
            c.execute('SELECT DISTINCT deployment from logsheetData')


        elif analysis == 'All Available Nutrients':
                if view == 'Deployment':
                    c.execute('SELECT DISTINCT deployment from nutrientMeasurements')
                elif view == 'File':
                    c.execute('SELECT DISTINCT runNumber from nutrientMeasurements')


        data = list(c.fetchall())
        c.close()
        
        data_to_display = []
        if view == 'Deployment':
            for i in data:
                data_to_display.append('Deployment ' + str(i[0]))
        if view == 'File':
            for i in data:
                data_to_display.append('File ' + str(i[0]))

        self.datafiles.addItems(data_to_display)
