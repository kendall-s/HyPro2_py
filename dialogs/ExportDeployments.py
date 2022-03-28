# http://www.ceda.ac.uk/static/media/uploads/ncas-reading-2015/11_create_netcdf_python.pdf
import csv
import logging
import sqlite3
import time
import traceback

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QMessageBox,
                             QListWidget)

from dialogs.templates.DialogTemplate import hyproDialogTemplate

"""
Provides the user with the ability to select specific deployments for export, with ideally export functionality for 
both csv and netcdf and whatever else is necessary
"""
# TODO: implement proper data exporting functionality after everything is setup that way it will be

class exportDeployments(hyproDialogTemplate):
    def __init__(self, database, curr_project):
        super().__init__(224, 500, 'HyPro - Export')

        self.db = database
        self.current_project = curr_project

        self.init_ui()

        self.show()

    def init_ui(self):
        export_type_label = QLabel('Select data format to export', self)

        self.data_formats = QComboBox()
        self.data_formats.addItem('CSV')
        self.data_formats.addItem('NetCDF')

        export_label = QLabel('Select Deployments to export...', self)

        self.deployments = QListWidget()
        self.depsel = False
        self.deployments.itemSelectionChanged.connect(self.itemselected)
        self.deployments.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        okbut = QPushButton('Export', self)
        okbut.clicked.connect(self.get_data)
        okbut.setFixedWidth(90)

        cancelbut = QPushButton('Cancel', self)
        cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(export_type_label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.data_formats, 1, 0, 1, 2)
        self.grid_layout.addWidget(export_label, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.deployments, 3, 0, 1, 2)
        self.grid_layout.addWidget(okbut, 4, 0)
        self.grid_layout.addWidget(cancelbut, 4, 1)

        # Populate the deployments list
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute('SELECT DISTINCT deployment from ctdData')
            deployments = list(c.fetchall())
            c.close()
            depstodisplay = []
            for i in deployments:
                depstodisplay.append(str(i[0]))
            self.deployments.addItems(depstodisplay)
        except Exception as e:
            print(traceback.print_exc())

    def get_data(self):
        try:
            logging.info('Attempting to package and export data')
            if self.depsel:
                datatype = str(self.data_formats.currentText())
                deploymentsobjects = self.deployments.selectedItems()
                deployments = [item.text() for item in deploymentsobjects]

                conn = sqlite3.connect(self.db)
                self.c = conn.cursor()

                queryq = '?'
                queryplace = ', '.join(queryq for unused in deployments)

                """
                CTD data selects
                """
                self.c.execute('SELECT time from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.time = [x[0] for x in rows]

                self.c.execute('SELECT deployment from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.deployment = [x[0] for x in rows]

                self.c.execute('SELECT rosettePosition from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.rp = [x[0] for x in rows]

                self.c.execute('SELECT longitude from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.lon = [x[0] for x in rows]

                self.c.execute('SELECT latitude from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.lat = [x[0] for x in rows]

                self.c.execute('SELECT pressure from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.pressure = [x[0] for x in rows]

                self.c.execute('SELECT temp1 from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.temp = [x[0] for x in rows]

                """
                Salinity data selects
                """
                self.c.execute('SELECT salinity from salinityData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.salts = [x[0] for x in rows]
                self.c.execute('SELECT flag from salinityData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.saltflags = [x[0] for x in rows]
                self.c.execute('SELECT deployment from salinityData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.saltdeps = [x[0] for x in rows]
                self.c.execute('SELECT rosettePosition from salinityData where deployment in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.saltrp = [x[0] for x in rows]

                """
                Oxygen data selects
                """
                self.c.execute('SELECT oxygenMoles from oxygenData where deployment in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygen = [x[0] for x in rows]
                self.c.execute('SELECT flag from oxygenData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.oxygenflags = [x[0] for x in rows]
                self.c.execute('SELECT stationNumber from oxygenData where deployment in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygendeps = [x[0] for x in rows]
                self.c.execute('SELECT rosettePosition from oxygenData where deployment in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygenrp = [x[0] for x in rows]

                """
                Nutrient data selects
                """
                self.c.execute(
                    'SELECT concentration, flag, deployment, rosettePosition from nitrateData where deployment in (%s)' % queryplace,
                    deployments)
                rows = list(self.c.fetchall())
                self.nitrate_concs = [x[0] for x in rows]
                self.nitrate_flags = [x[1] for x in rows]
                self.nitrate_deps = [x[2] for x in rows]
                self.nitrate_rps = [x[3] for x in rows]

                self.c.execute(
                    'SELECT concentration, flag, deployment, rosettePosition from phosphateData where deployment in (%s)' % queryplace,
                    deployments)
                rows = list(self.c.fetchall())
                self.phosphate_concs = [x[0] for x in rows]
                self.phosphate_flags = [x[1] for x in rows]
                self.phosphate_deps = [x[2] for x in rows]
                self.phosphate_rps = [x[3] for x in rows]

                self.c.execute(
                    'SELECT concentration, flag, deployment, rosettePosition from nitriteData where deployment in (%s)' % queryplace,
                    deployments)
                rows = list(self.c.fetchall())
                self.nitrite_concs = [x[0] for x in rows]
                self.nitrite_flags = [x[1] for x in rows]
                self.nitrite_deps = [x[2] for x in rows]
                self.nitrite_rps = [x[3] for x in rows]

                self.c.execute(
                    'SELECT concentration, flag, deployment, rosettePosition from silicateData where deployment in (%s)' % queryplace,
                    deployments)
                rows = list(self.c.fetchall())
                self.silicate_concs = [x[0] for x in rows]
                self.silicate_flags = [x[1] for x in rows]
                self.silicate_deps = [x[2] for x in rows]
                self.silicate_rps = [x[3] for x in rows]

                self.c.execute(
                    'SELECT concentration, flag, deployment, rosettePosition from ammoniaData where deployment in (%s)' % queryplace,
                    deployments)
                rows = list(self.c.fetchall())
                self.ammonia_concs = [x[0] for x in rows]
                self.ammonia_flags = [x[1] for x in rows]
                self.ammonia_deps = [x[2] for x in rows]
                self.ammonia_rps = [x[3] for x in rows]

                self.c.close()

                if datatype == 'CSV':
                    self.exportcsv()

                if datatype == 'NetCDF':
                    self.exportnetcdf()
            else:
                logging.info('Please select some deployments...')
                self.exportnetcdf()

        except Exception as e:
            logging.error('Error: ' + e)

    def itemselected(self):
        self.depsel = True

    def exportcsv(self):

        filedialog = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '', '.csv')
        if filedialog[0]:
            filepath = filedialog[0] + filedialog[1]
            filebuffer = open(filepath, 'w', newline='')
            writer = csv.writer(filebuffer, delimiter=',')
            writer.writerow(
                ['Voyage', 'Deployment', 'RP', 'Time (UTC)', 'Latitiude', 'Longitude', 'Pressure', 'Temperature',
                 'Salinity (PSU)', 'Salinity Flag', 'Oxygen (uM)', 'Oxygen Flag', 'Nitrate (uM)',
                 'Nitrate Flag', 'Phosphate (uM)', 'Phosphate Flag', 'Silicate (uM)', 'Silicate Flag',
                 'Nitrite (uM)', 'Nitrite Flag', 'Ammonia (uM)', 'Ammonia Flag'
                 ])

            for i, dep in enumerate(self.deployment):
                oxy = ''
                oxyflag = ''
                salt = ''
                saltflag = ''
                nitrate = ''
                nitrate_flag = ''
                phosphate = ''
                phosphate_flag = ''
                silicate = ''
                silicate_flag = ''
                nitrite = ''
                nitrite_flag = ''
                ammonia = ''
                ammonia_flag = ''

                for x, rospos in enumerate(self.oxygenrp):
                    if rospos == self.rp[i] and self.oxygendeps[x] == dep:
                        oxy = self.oxygen[x]
                        oxyflag = self.oxygenflags[x]
                for y, rospos in enumerate(self.saltrp):
                    if rospos == self.rp[i] and self.saltdeps[y] == dep:
                        salt = self.salts[y]
                        saltflag = self.saltflags[y]

                for nitrate_ind, rp in enumerate(self.nitrate_rps):
                    if rp == self.rp[i] and self.nitrate_deps[nitrate_ind] == dep:
                        nitrate = self.nitrate_concs[nitrate_ind]
                        nitrate_flag = self.nitrate_flags[nitrate_ind]

                for phosphate_ind, rp in enumerate(self.phosphate_rps):
                    if rp == self.rp[i] and self.phosphate_deps[phosphate_ind] == dep:
                        phosphate = self.phosphate_concs[phosphate_ind]
                        phosphate_flag = self.phosphate_flags[phosphate_ind]

                for silicate_ind, rp in enumerate(self.silicate_rps):
                    if rp == self.rp[i] and self.silicate_deps[silicate_ind] == dep:
                        silicate = self.silicate_concs[silicate_ind]
                        silicate_flag = self.silicate_flags[silicate_ind]

                for nitrite_ind, rp in enumerate(self.nitrite_rps):
                    if rp == self.rp[i] and self.nitrite_deps[nitrite_ind] == dep:
                        nitrite = self.nitrite_concs[nitrite_ind]
                        nitrite_flag = self.nitrite_flags[nitrite_ind]

                for ammonia_ind, rp in enumerate(self.ammonia_rps):
                    if rp == self.rp[i] and self.ammonia_deps[ammonia_ind] == dep:
                        ammonia = self.ammonia_concs[ammonia_ind]
                        ammonia_flag = self.ammonia_flags[ammonia_ind]

                writer.writerow(
                    [self.current_project, dep, self.rp[i], self.time[i], self.lat[i], self.lon[i],
                     self.pressure[i], self.temp[i], salt, saltflag, oxy, oxyflag, nitrate, nitrate_flag,
                     phosphate, phosphate_flag, silicate, silicate_flag, nitrite, nitrite_flag, ammonia,
                     ammonia_flag
                     ])

            filebuffer.close()

            logging.info('Successfully exported data as .CSV')

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                     "The data was successfully exported in a .csv format!",
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()

    def exportnetcdf(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('SELECT * from underwayNutrients')
        data = list(c.fetchall())

        lat = [x[0] for x in data]
        lon = [x[1] for x in data]
        times = [x[2] for x in data]
        nitrate = [x[3] for x in data]
        phosphate = [x[4] for x in data]
        file = [x[8] for x in data]

        format = '%d/%m/%Y %H:%M:%S'

        stringtime = [time.strftime(format, time.gmtime(x)) for x in times]

        c.close()

        filedialog = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '', '.csv')
        if filedialog[0]:
            filepath = filedialog[0] + filedialog[1]
            filebuffer = open(filepath, 'w', newline='')
            writer = csv.writer(filebuffer, delimiter=',')
            writer.writerow(['Latitude', 'Longitude', 'Time (UTC)', 'Nitrate (uM)', 'Phosphate (uM)', 'File'])

            for i, x in enumerate(lat):
                writer.writerow([x, lon[i], times[i], nitrate[i], phosphate[i], file[i]])

            logging.info('Successfully exported data as NetCDF')
            filebuffer.close()

    def cancel(self):
        self.close()
