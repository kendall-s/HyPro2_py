# http://www.ceda.ac.uk/static/media/uploads/ncas-reading-2015/11_create_netcdf_python.pdf
from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QMessageBox,
                             QListWidget)
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
import sqlite3
import csv, logging, time, traceback
from dialogs.templates.DialogTemplate import hyproDialogTemplate


# Class that provides GUI and functionality for exporting data from a project, will rename to exportdata down the track
# # TODO: implement proper data exporting functionality after everything is setup that way it will be

class exportDeployments(hyproDialogTemplate):
    def __init__(self, database):
        super().__init__(224, 500, 'HyPro - Export')

        self.db = database

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

                self.c.execute('SELECT time from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.time = [x[0] for x in rows]

                self.c.execute('SELECT deployment from ctdData where deployment in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.deployment = [x[0] for x in rows]

                self.c.execute('SELECT bottleposition from ctdData where deployment in (%s)' % queryplace, deployments)
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

                self.c.execute('SELECT oxygenMoles from oxygenData where stationNumber in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygen = [x[0] for x in rows]
                self.c.execute('SELECT flag from oxygenData where stationNumber in (%s)' % queryplace, deployments)
                rows = list(self.c.fetchall())
                self.oxygenflags = [x[0] for x in rows]
                self.c.execute('SELECT stationNumber from oxygenData where stationNumber in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygendeps = [x[0] for x in rows]
                self.c.execute('SELECT rosettePosition from oxygenData where stationNumber in (%s)' % queryplace,
                               deployments)
                rows = list(self.c.fetchall())
                self.oxygenrp = [x[0] for x in rows]

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
            writer.writerow(['Deployment', 'RP', 'Time (UTC)', 'Latitiude', 'Longitude', 'Pressure', 'Temperature',
                             'Salinity (PSU)', 'Salinity Flag', 'Oxygen (uM)', 'Oxygen Flag'])

            for i, dep in enumerate(self.deployment):
                oxy = ''
                oxyflag = ''
                salt = ''
                saltflag = ''
                for x, rospos in enumerate(self.oxygenrp):
                    if rospos == self.rp[i] and self.oxygendeps[x] == dep:
                        oxy = self.oxygen[x]
                        oxyflag = self.oxygenflags[x]
                for y, rospos in enumerate(self.saltrp):
                    if rospos == self.rp[i] and self.saltdeps[y] == dep:
                        salt = self.salts[y]
                        saltflag = self.saltflags[y]

                writer.writerow(
                    [dep, self.rp[i], self.time[i], self.lat[i], self.lon[i], self.pressure[i], self.temp[i], salt,
                     saltflag, oxy, oxyflag])

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
