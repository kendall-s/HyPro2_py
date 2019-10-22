import os, logging, json, sys
from PyQt5.QtWidgets import (QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QFileDialog,
                             QMessageBox, QDesktopWidget, QFrame, QAction, QCheckBox)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dialogs.ViewDataDialog import viewDataDialog
from processing.RefreshFunction import refreshFunction
from dialogs.RereadDialog import rereadDialog
from dialogs.ProducePlotsDialog import producePlotsDialog
from dialogs.DeleteDialog import deleteDialog
from dialogs.ExportDeployments import exportDeployments
from processing.LoggerOutput import QTextEditLogger
from dialogs.AnalysisDialog import analysisSettings
from dialogs.SurveyDialog import surveyDialog
from dialogs.RMNSDialog import rmnsDialog
from dialogs.ParametersDialog import parametersDialog
from processing.QCStats import statsDialog
import processing.readdata.InitialiseTables as inittabs
import processing.plotting.QCPlots as qcp
import sqlite3
from netCDF4 import Dataset
import numpy as np
import traceback
import time
import calendar
import hyproicons, style
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate


# TODO: Make output for ODV
# TODO: make logsheet go to Dissolved Oxygen box file
# TODO: convert QMainWindow to template, cut total code in half.
# TODO: transfer style sheet to style file - make dark mode please

# This file contains the GUI functionality of the processing menu which is secondary to the main menu
# Processing of all files within a project takes place from within this menu


class Processingmenu(hyproMainWindowTemplate, QtWidgets.QPlainTextEdit):
    backToMain = pyqtSignal()

    def __init__(self, project, path):
        super().__init__(820, 440, 'HyPro - Processing')

        self.setProperty('ProcessingMenu', True)

        self.grid_layout.setContentsMargins(0, 0, 5, 0)

        self.currproject = project
        self.currpath = path
        self.db = self.currpath + '/' + self.currproject + 'Data.db'

        inittabs.main(self.currproject, self.currpath)

        self.init_ui()

        self.userprompter()


    def init_ui(self):
        self.makeparamsfile()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        exportMenu = fileMenu.addMenu(QIcon(':/assets/archivebox.svg'), 'Export')
        outputMenu = fileMenu.addMenu(QIcon(':/assets/text.svg'), 'Output Log')

        editMenu = mainMenu.addMenu('Edit')
        rmnsMenu = QAction(QIcon(':/assets/food.svg'), 'Edit RMNS', self)
        rmnsMenu.triggered.connect(self.rmnsstandards)
        editMenu.addAction(rmnsMenu)

        osilMenu = QAction(QIcon(':/assets/saltshaker.svg'), 'Edit OSIL', self)
        editMenu.addAction(osilMenu)

        editMenu.addSeparator()

        paramsMenu = QAction(QIcon(':/assets/settings2.svg'), 'Edit Parameters', self)
        editMenu.addAction(paramsMenu)
        paramsMenu.triggered.connect(self.parametersettings)

        analysisMenu = mainMenu.addMenu('Analyses')
        self.surveyMenu = mainMenu.addMenu('Surveys')
        viewMenu = mainMenu.addMenu('View')
        nutrientqcMenu = viewMenu.addMenu('Nutrient QC Plots')
        salinityqcMenu = viewMenu.addMenu('Salinity QC Plots')
        oxygenqcMenu = viewMenu.addMenu('Oxygen QC Plots')
        helpMenu = mainMenu.addMenu('Help')

        addAnalysisMenu = analysisMenu.addMenu(QIcon(':/assets/flask.svg'), 'Add Analysis')

        exportData = QAction(QIcon(':/assets/ship.svg'), 'Export Deployments', self)
        exportData.triggered.connect(self.exportdata)
        exportMenu.addAction(exportData)

        exportUnderwayNutrients = QAction('Export Underway Nutrients', self)
        exportUnderwayNutrients.triggered.connect(self.exportuwynuts)
        exportMenu.addAction(exportUnderwayNutrients)

        deleteFiles = QAction(QIcon(':/assets/trash2.svg'), 'Delete Files', self)
        deleteFiles.triggered.connect(self.deletefiles)
        fileMenu.addAction(deleteFiles)

        saveOutput = QAction(QIcon(':/assets/save.svg'), 'Save Output', self)
        saveOutput.triggered.connect(self.saveoutput)
        outputMenu.addAction(saveOutput)

        clearOutput = QAction(QIcon(':/assets/clear.svg'), 'Clear Output', self)
        clearOutput.triggered.connect(self.clearoutput)
        outputMenu.addAction(clearOutput)

        mainmenuAction = QAction(QIcon(':/assets/home.svg'), 'Main Menu', self)
        mainmenuAction.setShortcut('Ctrl+Alt+H')
        mainmenuAction.setStatusTip('Back to the main menu')
        mainmenuAction.triggered.connect(self.backtomenufunction)
        fileMenu.addAction(mainmenuAction)

        fileMenu.addSeparator()

        exitMenu = QAction(QIcon(':/assets/exit.svg'), 'Exit', self)
        exitMenu.triggered.connect(self.close)
        fileMenu.addAction(exitMenu)

        self.addGuildlineSalinity = QAction('Guildline Salinity', self)
        self.addGuildlineSalinity.triggered.connect(self.addguildline)
        addAnalysisMenu.addAction(self.addGuildlineSalinity)

        self.addScrippsOxygen = QAction('Scripps Oxygen', self)
        self.addScrippsOxygen.triggered.connect(self.addscripps)
        addAnalysisMenu.addAction(self.addScrippsOxygen)

        self.addSealNutrients = QAction('Seal Nutrients', self)
        self.addSealNutrients.triggered.connect(self.addseal)
        addAnalysisMenu.addAction(self.addSealNutrients)

        self.addSeasaveCTD = QAction('Seasave CTD', self)
        self.addSeasaveCTD.triggered.connect(self.addseasave)
        addAnalysisMenu.addAction(self.addSeasaveCTD)

        self.addLogsheet = QAction('Sampling Logsheet', self)
        self.addLogsheet.triggered.connect(self.addlogsheet)
        addAnalysisMenu.addAction(self.addLogsheet)

        self.setcheckboxes()

        self.populatesurveys()

        self.surveyMenu.addSeparator()
        self.addNewSurvey = QAction(QIcon(':/assets/roundplus.svg'), 'New', self)
        self.addNewSurvey.triggered.connect(lambda: self.surveysettings('new'))
        self.surveyMenu.addAction(self.addNewSurvey)

        rmnsPlots = QAction('RMNS', self)
        rmnsPlots.triggered.connect(self.rmnsplots)
        nutrientqcMenu.addAction(rmnsPlots)

        mdlPlots = QAction('MDL', self)
        mdlPlots.triggered.connect(self.mdlplots)
        nutrientqcMenu.addAction(mdlPlots)

        redfieldPlot = QAction('Redfield Ratio', self)
        redfieldPlot.triggered.connect(self.redfield)
        nutrientqcMenu.addAction(redfieldPlot)

        salinityErrorPlot = QAction('Salinity - CTD Error', self)
        salinityErrorPlot.triggered.connect(self.salinityerror)
        salinityqcMenu.addAction(salinityErrorPlot)

        salinityStandardPlot = QAction('Salinity Standards', self)
        salinityStandardPlot.triggered.connect(self.salinitystandards)
        salinityqcMenu.addAction(salinityStandardPlot)

        oxygenErrorPlot = QAction('Oxygen - CTD Error', self)
        oxygenErrorPlot.triggered.connect(self.oxygenerror)
        oxygenqcMenu.addAction(oxygenErrorPlot)

        oxygenStandardPlot = QAction('Oxygen Standards', self)
        oxygenStandardPlot.triggered.connect(self.oxygenstandards)
        oxygenqcMenu.addAction(oxygenStandardPlot)

        plotsAction = QAction('Create Plots', self)
        plotsAction.triggered.connect(self.produceplots)
        viewMenu.addAction(plotsAction)

        statsAction = QAction('View QC Stats', self)
        statsAction.triggered.connect(self.producestats)
        viewMenu.addAction(statsAction)

        aboutMenu = QAction(QIcon(':/assets/roundquestionmark.svg'), 'About', self)
        aboutMenu.triggered.connect(self.aboutinformation)
        helpMenu.addAction(aboutMenu)

        manualMenu = QAction(QIcon(':/assets/roundinfo.svg'), 'Manual', self)
        manualMenu.triggered.connect(self.showmanual)
        helpMenu.addAction(manualMenu)

        currprojectframe = QFrame(self)
        currprojectframe.setProperty('sideHeaderFrame', True)
        # Shadow graphics parameters
        currprojectframeshadow = QtWidgets.QGraphicsDropShadowEffect()

        currprojectframeshadow.setBlurRadius(5)
        currprojectframeshadow.setYOffset(1)
        currprojectframeshadow.setXOffset(2)

        currprojectlabel = QLabel('Current Project:')
        currprojectlabel.setProperty('sideBarText', True)

        currproject = QLabel('<b>' + self.currproject + '</b>')
        currproject.setAlignment(Qt.AlignCenter)
        currproject.setProperty('sideHeaderHeading', True)

        topperframe = QFrame(self)
        topperframe.setProperty('topBarFrame', True)
        topperframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        topperframeshadow.setBlurRadius(5)
        topperframeshadow.setYOffset(2)
        topperframeshadow.setXOffset(3)
        topperframe.setGraphicsEffect(topperframeshadow)

        outputboxframe = QFrame(self)
        outputboxframe.setProperty('dashboardFrame', True)
        outputboxframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        outputboxframeshadow.setBlurRadius(5)
        outputboxframeshadow.setYOffset(2)
        outputboxframeshadow.setXOffset(3)
        outputboxframe.setGraphicsEffect(outputboxframeshadow)

        outputboxlabel = QLabel(' Output: ')
        outputboxlabel.setProperty('dashboardText', True)

        # TODO: finish the logger, logging to file and reloading each time hypro opened
        logged_path = self.currpath + '/' +self.currproject + '.txt'
        self.outputbox = QTextEditLogger(self, logged_path)
        logging.getLogger().addHandler(self.outputbox)
        logging.getLogger().setLevel(logging.INFO)

        sidebarframe = QFrame(self)
        sidebarframe.setProperty('sideBarFrame', True)
        sidebarframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        sidebarframeshadow.setBlurRadius(5)
        sidebarframeshadow.setColor(QtGui.QColor('#183666'))
        sidebarframeshadow.setYOffset(1)
        sidebarframeshadow.setXOffset(2)
        # sidebarframe.setGraphicsEffect(sidebarframeshadow)

        self.interactiveprocessing = QCheckBox('Interactive Processing')
        self.interactiveprocessing.setChecked(True)
        self.interactiveprocessing.setProperty('sideBarCheckbox', True)

        procdatalabel = QLabel('<b>Process Data</b>')
        procdatalabel.setProperty('sideBarText', True)

        rereadbut = QPushButton('Reread File')
        rereadbut.setProperty('sideBarButton', True)

        refreshfilesbut = QPushButton('Refresh Files')
        refreshfilesbut.setProperty('sideBarButton', True)
        # refreshfilesbut.setIcon(QIcon('roundrefresh'))

        optionslabel = QLabel('<b>Options</b>')
        optionslabel.setProperty('sideBarText', True)

        viewdatabut = QPushButton('View Data')
        viewdatabut.setProperty('sideBarButton', True)

        deletedatabut = QPushButton('Delete Data')
        deletedatabut.setProperty('sideBarButton', True)

        self.grid_layout.addWidget(currprojectframe, 0, 0, 5, 1)
        self.grid_layout.addWidget(sidebarframe, 4, 0, 15, 1)

        self.grid_layout.addWidget(currprojectlabel, 0, 0, 2, 1, Qt.AlignCenter)
        self.grid_layout.addWidget(currproject, 1, 0, 3, 1, Qt.AlignCenter)

        self.grid_layout.addWidget(procdatalabel, 5, 0, Qt.AlignCenter)
        self.grid_layout.addWidget(refreshfilesbut, 6, 0)
        self.grid_layout.addWidget(rereadbut, 7, 0)

        self.grid_layout.addWidget(optionslabel, 9, 0, Qt.AlignCenter)
        self.grid_layout.addWidget(viewdatabut, 10, 0)
        self.grid_layout.addWidget(deletedatabut, 11, 0)

        self.grid_layout.addWidget(self.interactiveprocessing, 17, 0, Qt.AlignHCenter)

        self.grid_layout.addWidget(topperframe, 0, 1, 3, 3)

        self.grid_layout.addWidget(outputboxframe, 3, 1, 15, 3)
        self.grid_layout.addWidget(outputboxlabel, 3, 1, 1, 2)
        self.grid_layout.addWidget(self.outputbox.widget, 4, 1, 14, 3)

        #self.grid_layout.setColumnMinimumWidth(5, 3)

        rereadbut.clicked.connect(self.reread)
        viewdatabut.clicked.connect(self.viewdata)
        refreshfilesbut.clicked.connect(self.refresh)
        deletedatabut.clicked.connect(self.deletefiles)

    def userprompter(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())
        analyses = params['analysisparams'].keys()
        anyactivated = False
        for x in analyses:
            if params['analysisparams'][x]['activated']:
                anyactivated = True

        if not anyactivated:
            logging.info("There is not any analyses currently activated, HyPro can not recognise files that need "
                         "processing if you don't activate and assign a naming nomenclature. If this is also the first "
                         "time setting up the project it would be a good idea to check Parameters, under Edit. "
                         "Don't forget to also set up the surveys required, so data can be automatically grouped for "
                         "your ease.")

    def reread(self):
        self.rereadDialog = rereadDialog(self.currpath, self.currproject, self.db,
                                         self.interactiveprocessing.checkState())
        self.rereadDialog.show()

    def viewdata(self):

        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        self.viewDataDialog = viewDataDialog(self.db, params)
        self.viewDataDialog.show()

    def refresh(self):
        self.refreshing = refreshFunction(self.currpath, self.currproject, self.interactiveprocessing.checkState())

    def backtomenufunction(self):
        self.backToMain.emit()

    def rmnsplots(self):
        self.rmnsWindow = qcp.rmnsPlotWindow(self.currproject, self.currpath, self.db)
        self.rmnsWindow.show()

    def mdlplots(self):
        self.mdlWindow = qcp.mdlPlotWindow(self.currproject, self.currpath, self.db)
        self.mdlWindow.show()

    def redfield(self):
        self.redfieldWindow = qcp.redfieldPlot(self.db)

    def salinityerror(self):
        pass

    def salinitystandards(self):
        pass

    def oxygenerror(self):
        pass

    def oxygenstandards(self):
        pass

    def produceplots(self):
        self.prodplots = producePlotsDialog()
        self.prodplots.show()

    def deletefiles(self):
        self.deletefilesdialog = deleteDialog(self.currpath, self.currproject, self.db)
        self.deletefilesdialog.show()

    def saveoutput(self):
        filedialog = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', '.txt')
        if filedialog[0]:
            outputfile = open(filedialog[0] + filedialog[1], 'w')
            outputtext = self.outputbox.gettext()
            outputfile.write(outputtext)
            outputfile.close()

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                     "Output log was successfully saved",
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()

    def clearoutput(self):
        self.outputbox.clear()

    def exportdata(self):
        self.exporter = exportDeployments(self.db)
        self.exporter.show()

    def exportuwynuts(self):
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute(
                'SELECT latitude, longitude, time, nitrate, phosphate, file '
                'FROM underwayNutrients')
            data = list(c.fetchall())
            c.close()

            format = '%d/%m/%Y %H:%M:%S'
            starttime = '01/01/2018 00:00:00'
            starttimeinseconds = calendar.timegm(time.strptime(starttime, format))

            lat = [x[0] for x in data]
            lon = [x[1] for x in data]
            timer = [(x[2] - starttimeinseconds) for x in data]
            timevals = [x[2] for x in data]
            nitrate = [x[3] for x in data]
            phos = [x[4] for x in data]
            file = [int(x[5][14:16]) for x in data]

            propath = QFileDialog.Options()
            files = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

            if files:
                preppedfile = Dataset(files + '/' + self.currproject + '.nc', 'w')

                preppedfile.description = 'in2018_v04 Underway Nutrients, Nitrate (NOx) and Phosphate ' \
                                          'analysed on Seal AA100. Time stamps are seconds since 01/01/2018 00:00 UTC.'

                vals = preppedfile.createDimension('value', len(lat))
                lats = preppedfile.createVariable('latitude', np.float64, ('value',))
                lats.units = 'decimal_deg_north'
                lons = preppedfile.createVariable('longitude', np.float64, ('value',))
                lons.units = 'decimal_deg_east'
                times = preppedfile.createVariable('time', np.int_, ('value',))
                times.units = 'utc'
                nitrates = preppedfile.createVariable('nitrate', np.float64, ('value',))
                nitrates.units = 'µM'
                phosphates = preppedfile.createVariable('phosphate', np.float64, ('value',))
                phosphates.units = 'µM'
                filesnc = preppedfile.createVariable('file', np.int32, ('value',))

                lats[:] = lat
                lons[:] = lon
                times[:] = timevals
                nitrates[:] = nitrate
                phosphates[:] = phos
                filesnc[:] = file

                preppedfile.close()

        except Exception:
            print(traceback.print_exc())

    def addguildline(self):
        self.guildline = analysisSettings(self.currproject, 'guildline', self.currpath)
        self.guildline.show()
        self.guildline.analysisSettingsUpdated.connect(self.setcheckboxes)

    def addseal(self):
        self.seal = analysisSettings(self.currproject, 'seal', self.currpath)
        self.seal.show()
        self.seal.analysisSettingsUpdated.connect(self.setcheckboxes)

    def addscripps(self):
        self.scripps = analysisSettings(self.currproject, 'scripps', self.currpath)
        self.scripps.show()
        self.scripps.analysisSettingsUpdated.connect(self.setcheckboxes)

    def addseasave(self):
        self.seasave = analysisSettings(self.currproject, 'seasave', self.currpath)
        self.seasave.show()
        self.seasave.analysisSettingsUpdated.connect(self.setcheckboxes)

    def addlogsheet(self):
        self.logsheet = analysisSettings(self.currproject, 'logsheet', self.currpath)
        self.logsheet.show()
        self.logsheet.analysisSettingsUpdated.connect(self.setcheckboxes)

    def setcheckboxes(self):
        analyses = ['guildline', 'scripps', 'seal', 'seasave', 'logsheet']

        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        for i in analyses:
            if params['analysisparams'][i]['activated'] == True:
                if i == 'guildline':
                    self.addGuildlineSalinity.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'scripps':
                    self.addScrippsOxygen.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'seal':
                    self.addSealNutrients.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'seasave':
                    self.addSeasaveCTD.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'logsheet':
                    self.addLogsheet.setIcon(QIcon(':/assets/roundchecked.svg'))
            else:
                if i == 'guildline':
                    self.addGuildlineSalinity.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'scripps':
                    self.addScrippsOxygen.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'seal':
                    self.addSealNutrients.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'seasave':
                    self.addSeasaveCTD.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'logsheet':
                    self.addLogsheet.setIcon(QIcon(':/assets/roundcross.svg'))

    def surveysettings(self, name):
        nameinput = name
        self.addsurvey = surveyDialog(self.currproject, nameinput, self.currpath)
        self.addsurvey.show()

    def parametersettings(self):
        self.paramsettings = parametersDialog(self.currproject, self.currpath)
        self.paramsettings.show()

    def populatesurveys(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        surveys = list(params['surveyparams'].keys())

        for k in surveys:
            survey = QAction(k, self)
            survey.triggered.connect(lambda checked, k=k: self.surveysettings(k))
            self.surveyMenu.addAction(survey)

    def aboutinformation(self):
        messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'About',
                                 "This is an experimental version of HyPro built using Python",
                                 buttons=QtWidgets.QMessageBox.Ok, parent=self)
        messagebox.setIconPixmap(QPixmap(':/assets/questionmark.svg'))
        messagebox.setFont(QFont('Segoe UI'))
        messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
        messagebox.exec_()

    def showmanual(self):
        file = 'C:/Users/she384/Documents/Tests/Manual.pdf'
        os.system('start ' + file)

    # Make parameters file if it doesn't currently exist - fill with defaults
    def makeparamsfile(self):
        if os.path.isfile(self.currpath + '/' + '%sParams.json' % self.currproject):
            print('Parameter file checked')
        else:
            # TODO: make this a file to include into distribution
            params = {
                "nutrientprocessing": {
                    "elementNames": {
                        "silicateName": "SILICATE",
                        "phosphateName": "PHOSPHATE",
                        "nitrateName": "NOx",
                        "nitriteName": "NITRITE",
                        "ammoniaName": "AMMONIA"
                    },
                    "processingpars": {
                        "silicate": {
                            "peakPeriod": 80,
                            "washPeriod": 40,
                            "windowSize": 37,
                            "windowStart": 36,
                            "driftCorrType": "Piecewise",
                            "baseCorrType": "Piecewise",
                            "carryoverCorr": True,
                            "calibration": "Linear",
                            "calerror": 0.2
                        },
                        "phosphate": {
                            "peakPeriod": 80,
                            "washPeriod": 40,
                            "windowSize": 29,
                            "windowStart": 39,
                            "driftCorrType": "Piecewise",
                            "baseCorrType": "Piecewise",
                            "carryoverCorr": True,
                            "calibration": "Linear",
                            "calerror": 0.02
                        },
                        "nitrate": {
                            "peakPeriod": 80,
                            "washPeriod": 40,
                            "windowSize": 22,
                            "windowStart": 40,
                            "driftCorrType": "Piecewise",
                            "baseCorrType": "Piecewise",
                            "carryoverCorr": True,
                            "calibration": "Linear",
                            "calerror": 0.02
                        },
                        "nitrite": {
                            "peakPeriod": 80,
                            "washPeriod": 40,
                            "windowSize": 29,
                            "windowStart": 40,
                            "driftCorrType": "Piecewise",
                            "baseCorrType": "Piecewise",
                            "carryoverCorr": True,
                            "calibration": "Linear",
                            "calerror": 0.02
                        },
                        "ammonia": {
                            "peakPeriod": 80,
                            "washPeriod": 40,
                            "windowSize": 28,
                            "windowStart": 45,
                            "driftCorrType": "Piecewise",
                            "baseCorrType": "Piecewise",
                            "carryoverCorr": True,
                            "calibration": "Linear",
                            "calerror": 0.02
                        }
                    },
                    "calibrants": {
                        "maxnumber": "7",
                        "cal0": "Cal 0",
                        "cal1": "Cal 1",
                        "cal2": "Cal 2",
                        "cal3": "Cal 3",
                        "cal4": "Cal 4",
                        "cal5": "Cal 5",
                        "cal6": "Cal 6"
                    },
                    "slkcolumnnames": {
                        "sampleID": "Sample ID",
                        "cupNumbers": "Cup Number",
                        "cupTypes": "Cup Type",
                        "dateTime": "Date Time Stamp"
                    },
                    "cupnames": {
                        "primer": "PRIM",
                        "recovery": "UNKNOWN",
                        "drift": "DRIF",
                        "baseline": "BASL",
                        "calibrant": "CALB",
                        "high": "HIGH",
                        "low": "LOW ",
                        "null": "NULL",
                        "end": "END",
                        "sample": "SAMP"
                    },
                    "qcsamplenames": {
                        "rmns": "RMNS",
                        "mdl": "MDL",
                        "bqc": "BQC",
                        "internalqc": "IntQC",
                        "driftcheck": "Drift Sample Check"
                    }
                },
                "analysisparams": {
                    "guildline": {
                        "filePrefix": "",
                        "runFormat": "RRR",
                        "activated": False
                    },
                    "scripps": {
                        "filePrefix": "",
                        "runFormat": "RRR",
                        "activated": False
                    },
                    "seal": {
                        "filePrefix": "",
                        "runFormat": "RRR",
                        "activated": False
                    },
                    "seasave": {
                        "filePrefix": "",
                        "runFormat": "RRR",
                        "activated": False
                    },
                    "logsheet": {
                        "filePrefix": "",
                        "runFormat": "RRR",
                        "activated": False
                    }
                },
                "surveyparams": {
                    "%s" % self.currproject: {
                        "guildline": {
                            "activated": False,
                            "matchlogsheet": True,
                            "decodesampleid": False,
                            "surveyprefix": "",
                            "decodedepfromid": True,
                            "depformat": "DDBB",
                            "decodetimefromid": False,
                            "dateformat": "",
                            "usesampleid": False,
                            "autometadata": True
                        },
                        "scripps": {
                            "activated": False,
                            "matchlogsheet": False,
                            "decodesampleid": False,
                            "surveyprefix": "",
                            "decodedepfromid": False,
                            "depformat": "DDD",
                            "decodetimefromid": False,
                            "dateformat": "",
                            "usesampleid": False,
                            "autometadata": False
                        },
                        "seal": {
                            "activated": False,
                            "matchlogsheet": True,
                            "decodesampleid": True,
                            "surveyprefix": "",
                            "decodedepfromid": True,
                            "depformat": "DDBB",
                            "decodetimefromid": False,
                            "dateformat": "",
                            "usesampleid": False,
                            "autometadata": False
                        }
                    }
                }
            }

            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                hyproprojs = json.load(f)
            if hyproprojs['projects'][self.currproject]['type'] == 'Shore':
                params['surveyparams'][self.currproject]['guildline']['matchlogsheet'] = False
                params['surveyparams'][self.currproject]['guildline']['decodedepfromid'] = False
                params['surveyparams'][self.currproject]['guildline']['usesampleid'] = True
                params['surveyparams'][self.currproject]['scripps']['matchlogsheet'] = False
                params['surveyparams'][self.currproject]['scripps']['decodedepfromid'] = False
                params['surveyparams'][self.currproject]['scripps']['usesampleid'] = True
                params['surveyparams'][self.currproject]['seal']['matchlogsheet'] = False
                params['surveyparams'][self.currproject]['seal']['decodedepfromid'] = False
                params['surveyparams'][self.currproject]['seal']['usesampleid'] = True

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
                json.dump(params, file)
            print('Parameter file created')

    def rmnsstandards(self):
        self.rmns = rmnsDialog()
        self.rmns.show()

    def producestats(self):
        self.stats = statsDialog(self.currproject, self.db)
        self.stats.show()

    def closeEvent(self, event):
        # Closes everything if main processing window is closed
        app = QtWidgets.QApplication.instance()
        app.closeAllWindows()
