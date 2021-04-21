# https://stackoverflow.com/questions/283645/python-list-in-sql-query-as-parameter
from PyQt5.QtCore import Qt
import sqlite3
from dialogs.templates.DataTable import Datatable
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from processing.algo.ComplexSQL import export_ctd_data, export_all_nuts, export_all_nuts_in_survey

NUTRIENT_HEADER = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                   'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag', 'Dilution', 'EpochTime']
HEADERS = {
    'Salinity': ['Run Number', 'Deployment', 'Bottle Label', 'Date/Time', 'Uncorrected Ratio',
                       'Unorrected Ratio StDev', 'Salinity', 'Salinity StDev', 'Comment', 'Flag', 'Deployment',
                       'RP', 'Survey'],
           'Dissolved Oxygen': ['Run Number', 'Station #', 'Cast', 'RP', 'Bottle ID', 'Bottle Vol', 'Raw Titer', 'Titer',
                       'Oxygen', 'Oxygen uM', 'Thio Temp', 'Draw Temp', 'Final Volt', 'Time', 'Flag', 'Deployment',
                       'RP', 'Survey'],
           'CTD': ['Deployment', 'Temp #1', 'Temp #2', 'Conductivity #1', 'Conductivity #2', 'Oxygen #1',
                       'Oxygen #2', 'Pressure', 'Salinity #1', 'Salinity #2', 'Bottle Fired', 'RP', 'Time', 'Longitude',
                       'Latitiude', 'Fluorescence'],
           'Logsheet': ['Deployment', 'RP', 'Oxygen', 'Oxygen Draw Temp', 'Salinity', 'Nutrient'],
           'Silicate': NUTRIENT_HEADER,
           'Nitrate': NUTRIENT_HEADER,
           'Nitrite': NUTRIENT_HEADER,
           'Phosphate': NUTRIENT_HEADER,
           'Ammonia': NUTRIENT_HEADER,
           'All Available Nutrients': ['Run Number', 'Sample ID', 'Cup Type', 'Peak Number', 'Survey', 'Deployment',
                                       'RP', 'Ammonium Conc', 'Ammonium Flag', 'Nitrate Conc', 'Nitrate Flag',
                                       'Nitrite Conc', 'Nitrite Flag', 'Phosphate Conc', 'Phosphate Flag',
                                       'Silicate Conc', 'Silicate Flag'],
           'As CTD Results': ['Deployment', 'RP', 'Pressure(db)', 'CTD Temp 1', 'CTD Temp 2', 'CTD Salinity 1',
                       'CTD Salinity 2', 'CTD Oxygen 1', 'CTD Oxygen 2', 'CTD Fluoro', 'Time', 'Lon', 'Lat',
                       'Nut Label', 'Ammonium Conc', 'Ammonium Flag', 'Nitrate Conc', 'Nitrate Flag', 'Nitrite Conc',
                       'Nitrite Flag', 'Phosphate Conc', 'Phosphate Flag', 'Silicate Conc', 'Silicate Flag', 'Salinity',
                       'Salinity Flag', 'Oxygen (ml/l)', 'Oxygen (uM)', 'Oxygen Flag']
}


class viewData(hyproDialogTemplate):
    def __init__(self, survey, analysis, view, selected, database):
        super().__init__(1450, 600, 'HyPro - View Data')

        self.survey = survey
        self.analysis = analysis
        self.view = view
        self.selected = selected
        self.db = database

        self.data = self.get_data()
        self.init_ui()

        self.show()

    def init_ui(self):

        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint);

        self.datatable = Datatable(self.data)
        self.datatable.setHorizontalHeaderLabels(HEADERS[self.analysis])
        self.datatable.resizeColumnsToContents()

        self.grid_layout.addWidget(self.datatable, 0, 0)

    def get_data(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        query_length_deployments = ', '.join('?' for unused in self.selected)

        """
        If statements here follow analysis -> survey -> view structuring 
        """
        if self.analysis == 'All Available Nutrients':
            # If survey is Any, we can remove the survey filter from the query
            if self.survey == 'Any':
                if self.view == 'File':
                    q = export_all_nuts % ('runNumber', query_length_deployments)

            else: # Otherwise standard filtering with the survey
                if self.view == 'Deployment':
                    q = export_all_nuts_in_survey % ('deployment', query_length_deployments)

                elif self.view == 'File':
                    q = export_all_nuts_in_survey % ('runNumber', query_length_deployments)


        elif self.analysis == 'As CTD Results':
            q = export_ctd_data % query_length_deployments

        # CTD and logsheet grouped together because FILE always equals DEPLOYMENT
        elif self.analysis == 'CTD' or self.analysis == 'Logsheet':
            if self.view == 'Deployment':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % query_length_deployments


        # Everything else includes the individual nutrients, salinity and DO
        else:
            # Again, if survey is any we remove the WHERE for survey
            if self.survey == 'Any':
                if self.view == 'Deployment':
                    q = 'SELECT * FROM %sData WHERE deployment IN (%s)' % \
                        (self.analysis, query_length_deployments)
                elif self.view == 'File':
                    q = 'SELECT * FROM %sData WHERE runNumber IN (%s)' % \
                        (self.analysis, query_length_deployments)

            else: # We've picked a specific survey here
                if self.view == 'Deployment':
                    q = 'SELECT * FROM %sData WHERE deployment IN (%s) AND survey=?' % \
                        (self.analysis, query_length_deployments)
                elif self.view == 'File':
                    q = 'SELECT * FROM %sData WHERE runNumber IN (%s) AND survey=?' % \
                        (self.analysis, query_length_deployments)

        # Add the survey to the query input if anything other than logsheet, CTD results and CTD
        # And also no need to append it to the query if the survey selection is any
        if self.survey != 'Any':
            if not self.analysis in ['Logsheet', 'As CTD Results', 'CTD']:
                self.selected.append(self.survey)

        c.execute(q, self.selected)
        data = list(c.fetchall())
        print(data)

        conn.close()

        return data
