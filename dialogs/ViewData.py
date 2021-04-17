# https://stackoverflow.com/questions/283645/python-list-in-sql-query-as-parameter

from PyQt5.QtWidgets import (QTableWidget, QApplication)
import sqlite3
import csv, io
from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QEvent
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from processing.algo.ComplexSQL import export_ctd_data, export_all_nuts

class viewData(hyproDialogTemplate):
    def __init__(self, survey, analysis, view, selected, database):
        super().__init__(1450, 600, 'HyPro - View Data')

        self.survey = survey
        self.analysis = analysis
        self.view = view
        self.selected = selected
        self.db = database

        self.init_ui()

        self.show()

    def init_ui(self):

        self.datatable = QTableWidget(self)
        self.datatable.installEventFilter(self)

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        query_length_deployments = ', '.join('?' for unused in self.selected)

        if self.analysis == 'Salinity':
            headers = ['Run Number', 'Deployment', 'Bottle Label', 'Date/Time', 'Uncorrected Ratio',
                       'Unorrected Ratio StDev', 'Salinity', 'Salinity StDev', 'Comment', 'Flag', 'Deployment',
                       'RP', 'Survey']
            if self.view == 'Deployment':
                q = 'SELECT * FROM salinityData WHERE deployment IN (%s) AND survey=?' % query_length_deployments
                self.selected.append(self.survey)
            elif self.view == 'File':
                q = 'SELECT * FROM salinityData WHERE runNumber IN (%s) AND survey=?' % query_length_deployments

        elif self.analysis == 'Dissolved Oxygen':
            headers = ['Run Number', 'Station #', 'Cast', 'RP', 'Bottle ID', 'Bottle Vol', 'Raw Titer', 'Titer',
                       'Oxygen', 'Oxygen uM', 'Thio Temp', 'Draw Temp', 'Final Volt', 'Time', 'Flag', 'Deployment',
                       'RP', 'Survey']
            if self.view == 'Deployment':
                q = 'SELECT * FROM oxygenData WHERE stationNumber IN (%s) AND survey=?' % query_length_deployments
            elif self.view == 'File':

                q = 'SELECT * FROM oxygenData WHERE runNumber IN (%s) and survey =?' % query_length_deployments

        elif self.analysis == 'CTD':
            headers = ['Deployment', 'Temp #1', 'Temp #2', 'Conductivity #1', 'Conductivity #2', 'Oxygen #1',
                       'Oxygen #2', 'Pressure', 'Salinity #1', 'Salinity #2', 'Bottle Fired', 'RP', 'Time', 'Longitude',
                       'Latitiude', 'Fluorescence']
            if self.view == 'Deployment':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s) AND survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM ctdData WHERE deployment IN (%s) AND survey=?' % query_length_deployments

        elif self.analysis == 'Logsheet':
            headers = ['Deployment', 'RP', 'Oxygen', 'Oxygen Draw Temp', 'Salinity', 'Nutrient']
            if self.view == 'Deployment':
                q = 'SELECT * FROM logsheetData WHERE deployment IN (%s)' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM logsheetData WHERE deployment IN (%s)' % query_length_deployments

        elif self.analysis == 'Silicate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Flag', 'Dilution', 'EpochTime']
            if self.view == 'Deployment':
                q = 'SELECT * FROM silicateData WHERE deployment IN (%s) and survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM silicateData WHERE runNumber IN (%s) and survey=?' % query_length_deployments

        elif self.analysis == 'Nitrate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag', 'Dilution', 'EpochTime']
            if self.view == 'Deployment':
                q = 'SELECT * FROM  nitrateData WHERE deployment IN (%s) and survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM nitrateData WHERE runNumber IN (%s) and survey=?' % query_length_deployments

        elif self.analysis == 'Phosphate':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag', 'Dilution', 'EpochTime']
            if self.view == 'Deployment':
                q = 'SELECT * FROM phosphateData WHERE deployment IN (%s) and survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM phosphateData WHERE runNumber IN (%s) and survey=?' % query_length_deployments

        elif self.analysis == 'Nitrite':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag', 'Dilution', 'EpochTime']
            if self.view == 'Deployment':
                q = 'SELECT * FROM nitriteData WHERE deployment IN (%s) and survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM nitriteData WHERE runNumber IN (%s) and survey=?' % query_length_deployments

        elif self.analysis == 'Ammonia':
            headers = ['Run Number', 'Cup Type', 'Sample ID', 'Peak Number', 'Raw AD', 'Corrected AD',
                       'Concentration', 'Survey', 'Deployment', 'Rosette Pos', 'Flag', 'Dilution', 'EpochTime']
            if self.view == 'Deployment':
                q = 'SELECT * FROM ammoniaData WHERE deployment IN (%s) and survey=?' % query_length_deployments
            elif self.view == 'File':
                q = 'SELECT * FROM ammoniaData WHERE runNumber IN (%s) and survey=?' % query_length_deployments

        elif self.analysis == 'All Available Nutrients':

            headers = ['Run Number', 'Sample ID', 'Cup Type', 'Peak Number', 'Survey', 'Deployment', 'RP',
                       'Ammonium Conc', 'Ammonium Flag', 'Nitrate Conc', 'Nitrate Flag', 'Nitrite Conc', 'Nitrite Flag',
                       'Phosphate Conc', 'Phosphate Flag', 'Silicate Conc', 'Silicate Flag']

            if self.view == 'Deployment':
                # Looks odd but export_ctd_data is a super long SQL query. query_length_deployments is just filling in the ?
                q = export_all_nuts % ('deployment', query_length_deployments)

            elif self.view == 'File':
                q = export_all_nuts % ('runNumber', query_length_deployments)


        elif self.analysis == 'As CTD Results':
            headers = ['Deployment', 'RP', 'Pressure(db)', 'CTD Temp 1', 'CTD Temp 2', 'CTD Salinity 1',
                       'CTD Salinity 2', 'CTD Oxygen 1', 'CTD Oxygen 2', 'CTD Fluoro', 'Time', 'Lon', 'Lat',
                       'Nut Label', 'Ammonium Conc', 'Ammonium Flag', 'Nitrate Conc', 'Nitrate Flag', 'Nitrite Conc',
                       'Nitrite Flag', 'Phosphate Conc', 'Phosphate Flag', 'Silicate Conc', 'Silicate Flag', 'Salinity',
                       'Salinity Flag', 'Oxygen (ml/l)', 'Oxygen (uM)', 'Oxygen Flag']
            q = export_ctd_data % query_length_deployments

        # Add the survey to the query input if anything other than logsheet data
        if not self.analysis == 'Logsheet':
            if not self.analysis == 'As CTD Results':
                self.selected.append(self.survey)

        c.execute(q, self.selected)
        data = list(c.fetchall())

        c.close()

        self.datatable.setRowCount(len(data))
        self.datatable.setColumnCount(len(data[0]))

        for row, x in enumerate(data):
            for col, item in enumerate(x):
                self.datatable.setItem(row, col, QtWidgets.QTableWidgetItem(str(item)))

        self.datatable.setHorizontalHeaderLabels(headers)
        self.datatable.resizeColumnsToContents()
        self.grid_layout.addWidget(self.datatable, 0, 0)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
                event.matches(QKeySequence.Copy)):
            self.copySelection()
            return True
        return super(hyproDialogTemplate, self).eventFilter(source, event)

    def copySelection(self):
        selection = self.datatable.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream, delimiter='\t').writerows(table)
            QApplication.clipboard().setText(stream.getvalue())
