# https://stackoverflow.com/questions/283645/python-list-in-sql-query-as-parameter

from PyQt5.QtWidgets import (QTableWidget, QApplication)
import sqlite3
import csv, io
from PyQt5 import QtWidgets
from dialogs.templates.DataTable import Datatable
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QEvent
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from processing.algo.ComplexSQL import export_ctd_data, export_all_nuts

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
        self.datatable = Datatable(self.data)
        self.datatable.setHorizontalHeaderLabels(HEADERS[self.analysis])
        self.datatable.resizeColumnsToContents()

        self.grid_layout.addWidget(self.datatable, 0, 0)

    def get_data(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        query_length_deployments = ', '.join('?' for unused in self.selected)

        if self.analysis == 'All Available Nutrients':
            if self.view == 'Deployment':
                # Looks odd but export_ctd_data is a super long SQL query. query_length_deployments is just filling in the ?
                q = export_all_nuts % ('deployment', query_length_deployments)

            elif self.view == 'File':
                q = export_all_nuts % ('runNumber', query_length_deployments)


        elif self.analysis == 'As CTD Results':
            q = export_ctd_data

        # CTD and logsheet grouped together because FILE always equals DEPLOYMENT
        elif self.analysis == 'CTD' or self.analysis == 'Logsheet':
            if self.view == 'Deployment':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % query_length_deployments


        # Everything else includes the individual nutrients, salinity and DO
        else:
            if self.view == 'Deployment':
                q = 'SELECT * FROM %sData WHERE deployment IN (%s) AND survey=?' % \
                    (self.analysis, query_length_deployments)
            elif self.view == 'File':
                q = 'SELECT * FROM %sData WHERE runNumber IN (%s) AND survey=?' % \
                    (self.analysis, query_length_deployments)

        # Add the survey to the query input if anything other than logsheet, CTD results and CTD
        if not self.analysis in ['Logsheet', 'As CTD Results', 'CTD']:
            self.selected.append(self.survey)

        c.execute(q, self.selected)
        data = list(c.fetchall())

        conn.close()

        return data
