# https://stackoverflow.com/questions/283645/python-list-in-sql-query-as-parameter

from PyQt5.QtWidgets import (QTableWidget)
import sqlite3
from PyQt5 import QtWidgets
from dialogs.templates.DialogTemplate import hyproDialogTemplate

class viewData(hyproDialogTemplate):
    def __init__(self, analysis, view, selected, database):
        super().__init__(1450, 600, 'HyPro - View Data')

        self.analysis = analysis
        self.view = view
        self.selected = selected
        self.db = database

        self.init_ui()

        self.show()

    def init_ui(self):
        self.datatable = QTableWidget(self)

        conn = sqlite3.connect(self.db)
        self.c = conn.cursor()

        queryq = '?'
        queryplace = ', '.join(queryq for unused in self.selected)

        if self.analysis == 'Salinity':
            headers = ['Run Number', 'Deployment', 'Bottle Label', 'Date/Time', 'Uncorrected Ratio',
                       'Unorrected Ratio StDev', 'Salinity', 'Salinity StDev', 'Comment', 'Flag', 'RP', 'Survey']
            if self.view == 'Deployment':
                q = 'SELECT * FROM salinityData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM salinityData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Dissolved Oxygen':
            headers = ['Run Number', 'Deployment', 'Cast', 'RP', 'Bottle ID', 'Bottle Vol', 'Raw Titer', 'Titer',
                       'Oxygen', 'Oxygen uM', 'Thio Temp', 'Draw Temp', 'Final Volt', 'Time', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM oxygenData WHERE stationNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM oxygenData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'CTD':
            headers = ['Deployment', 'Temp #1', 'Temp #2', 'Conductivity #1', 'Conductivity #2', 'Oxygen #1',
                       'Oxygen #2', 'Pressure', 'Salinity #1', 'Salinity #2', 'Bottle Fired', 'RP', 'Time', 'Longitude',
                       'Latitiude', 'Fluorescence']
            if self.view == 'Deployment':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Logsheet':
            headers = ['Deployment', 'RP', 'Oxygen', 'Oxygen Draw Temp', 'Salinity', 'Nutrient']
            if self.view == 'Deployment':
                q = 'SELECT * FROM logsheetData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM logsheetData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Silicate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM silicateData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM silicateData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Nitrate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM  nitrateData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM nitrateData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Phosphate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM phosphateData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM phosphateData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Nitrite':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM nitriteeData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM nitriteData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        elif self.analysis == 'Ammonia':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag']
            if self.view == 'Deployment':
                q = 'SELECT * FROM ammoniaData WHERE deployment IN (%s)' % queryplace
                self.c.execute(q, self.selected)
            elif self.view == 'File':
                q = 'SELECT * FROM ammoniaData WHERE runNumber IN (%s)' % queryplace
                self.c.execute(q, self.selected)

        data = list(self.c.fetchall())

        self.c.close()

        self.datatable.setRowCount(len(data))
        self.datatable.setColumnCount(len(data[0]))

        for row, x in enumerate(data):
            for col, item in enumerate(x):
                self.datatable.setItem(row, col, QtWidgets.QTableWidgetItem(str(item)))

        self.datatable.setHorizontalHeaderLabels(headers)
        self.datatable.resizeColumnsToContents()
        self.grid_layout.addWidget(self.datatable, 0, 0)
