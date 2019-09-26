# https://stackoverflow.com/questions/8979409/get-text-from-qpushbutton-in-pyqt

from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QMessageBox, QFrame,
                             QCheckBox, QTabWidget)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import traceback
import json
import hyproicons, style

# The GUI for adding or editing surveys to the required settings needed
class surveyDialog(QWidget):
    def __init__(self, project, survey, path):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))

        self.currproject = project
        self.survey = survey
        self.currpath = path

        self.init_ui()

        self.setStyleSheet(style.stylesheet['normal'])


    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))

            self.gridlayout = QGridLayout()
            self.gridlayout.setSpacing(20)

            # Center window on active screen
            self.setGeometry(0, 0, 515, 725)
            qtRectangle = self.frameGeometry()
            screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
            centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
            self.setWindowModality(QtCore.Qt.ApplicationModal)


            headerLabel = QLabel('Survey name: ', self)

            if self.survey == 'new':
                self.setWindowTitle('HyPro - Add Survey')
                self.surveyName = QLineEdit(self)
            else:
                self.setWindowTitle('HyPro - Survey Settings')
                self.surveyName = QLineEdit(self.survey)
                self.surveyName.setReadOnly(True)

            analyses = ['Guildline Salinity', 'Scripps Oxygen', 'Seal Nutrients', 'Seasave CTD']
            analyseskey = ['guildline', 'scripps', 'seal', 'seasave']

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())

            self.tabs = QTabWidget()
            self.saltactive = False
            self.oxyactive = False
            self.nutsactive = False
            self.ctdactive = False

            tabnotadded = True
            for c, i in enumerate(params['analysisparams'].keys()):
                if params['analysisparams'][i]['activated'] == True:
                    if i == 'guildline':
                        self.salttab = QWidget()
                        self.tabs.addTab(self.salttab, 'Salinity')
                        self.saltactive = True
                    if i == 'scripps':
                        self.oxygentab = QWidget()
                        self.tabs.addTab(self.oxygentab, 'Oxygen')
                        self.oxyactive = True
                    if i == 'seal':
                        self.nutrienttab = QWidget()
                        self.tabs.addTab(self.nutrienttab, 'Nutrients')
                        self.nutsactive = True
                    if i == 'seasave':
                        self.ctdtab = QWidget()
                        self.tabs.addTab(self.ctdtab, 'CTD')
                        self.ctdactive = True
                    tabnotadded = False

            if tabnotadded:
                self.addanalysis = QWidget()
                self.tabs.addTab(self.addanalysis, 'Tab')
                self.addanal = QLabel('Add an analysis first to set survey settings')
                self.addanalysis.layout = QGridLayout()
                self.addanalysis.layout.addWidget(self.addanal, 0, 0)
                self.addanalysis.setLayout(self.addanalysis.layout)

            self.tabs.resize(400, 300)

            save = QPushButton('Save', self)
            save.clicked.connect(self.savefunction)

            cancel = QPushButton('Cancel', self)
            cancel.clicked.connect(self.cancelfunction)

            self.gridlayout.addWidget(headerLabel, 0, 0)
            self.gridlayout.addWidget(self.surveyName, 0, 1)

            self.gridlayout.addWidget(self.tabs, 1, 0, 5, 3)

            self.gridlayout.addWidget(save, 10, 0)
            self.gridlayout.addWidget(cancel, 10, 2)

            self.setLayout(self.gridlayout)

            # Salinity Tab
            if self.saltactive:
                self.salttab.layout = QGridLayout()

                self.activateSalinity = QCheckBox('Activate for use with this survey', self)
                #self.activateSalinity.clicked.connect(self.enabledisable)

                self.matchSalinityLabel = QLabel('Use sampling logsheet to match RP and bottle label:', self)

                self.matchSalinityCheck = QCheckBox(self)
                #self.matchSalinityCheck.setProperty('survey_checkbox', True)

                self.decodeSalinityLabel = QLabel('Decode sample ID:')

                self.decodeSalinity = QCheckBox(self)
                #self.decodeSalinity.clicked.connect(self.enabledisable)

                self.surveyPrefixSalinity = QLabel('Sample survey prefix')

                self.surveyPrefixSalinityEdit = QLineEdit(self)
                self.surveyPrefixSalinityEdit.setDisabled(True)

                self.decodeSalinityDeployment = QCheckBox('Decode Deployment from sample ID', self)
                #self.decodeSalinityDeployment.clicked.connect(self.enabledisable)
                self.decodeSalinityDeployment.setDisabled(True)

                self.deploymentSalinityFormat = QLabel(
                    'Deployment/Bottle format after prefix (if there is one) e.g. DDDBB', self)

                self.deploymentSalinityFormatEdit = QLineEdit(self)
                self.deploymentSalinityFormatEdit.setDisabled(True)

                self.decodeSalinityDate = QCheckBox('Decode Sample ID date format', self)
                #self.decodeSalinityDate.clicked.connect(self.enabledisable)
                self.decodeSalinityDate.setDisabled(True)

                self.dateSalinityFormat = QLabel('Date/Time format e.g. YYYYMMDD hh:mm:ss', self)

                self.decodeSalinityDateEdit = QLineEdit(self)
                self.decodeSalinityDateEdit.setDisabled(True)

                self.sampleSalinityID = QCheckBox('Use sample ID instead of dep/ros label', self)

                self.createSalinityMetadata = QCheckBox('Automatically create meta-data', self)

                sallinesep1 = QFrame(self)
                sallinesep1.setFrameShape(QFrame.HLine)
                sallinesep1.setFrameShadow(QFrame.Sunken)

                sallinesep2 = QFrame(self)
                sallinesep2.setFrameShape(QFrame.HLine)
                sallinesep2.setFrameShadow(QFrame.Sunken)

                sallinesep3 = QFrame(self)
                sallinesep3.setFrameShape(QFrame.HLine)
                sallinesep3.setFrameShadow(QFrame.Sunken)

                self.salttab.layout.addWidget(self.activateSalinity, 0, 0)
                self.salttab.layout.addWidget(sallinesep1, 1, 0, 1, 2)

                self.salttab.layout.addWidget(self.matchSalinityLabel, 2, 0)
                self.salttab.layout.addWidget(self.matchSalinityCheck, 2, 1)

                self.salttab.layout.addWidget(sallinesep2, 3, 0, 1, 2)

                self.salttab.layout.addWidget(self.decodeSalinityLabel, 4, 0)
                self.salttab.layout.addWidget(self.decodeSalinity, 4, 1)

                self.salttab.layout.addWidget(self.surveyPrefixSalinity, 5, 0)
                self.salttab.layout.addWidget(self.surveyPrefixSalinityEdit, 5, 1)

                self.salttab.layout.addWidget(self.decodeSalinityDeployment, 6, 0)

                self.salttab.layout.addWidget(self.deploymentSalinityFormat, 7, 0)
                self.salttab.layout.addWidget(self.deploymentSalinityFormatEdit, 7, 1)

                self.salttab.layout.addWidget(self.decodeSalinityDate, 8, 0)

                self.salttab.layout.addWidget(self.dateSalinityFormat, 9, 0)
                self.salttab.layout.addWidget(self.decodeSalinityDateEdit, 9, 1)

                self.salttab.layout.addWidget(sallinesep3, 10, 0, 1, 2)

                self.salttab.layout.addWidget(self.sampleSalinityID, 11, 0)

                self.salttab.layout.addWidget(self.createSalinityMetadata, 12, 0)

                self.salttab.setLayout(self.salttab.layout)

            # Oxygen Tab
            if self.oxyactive:
                
                oxy_grid = QGridLayout()
                self.activate_oxygen = QCheckBox('Activate for use with this survey', self)

                self.match_logsheet_oxygen = QCheckBox()
                self.match_logsheet_oxygen_label = QLabel('Attempt to match to sampling logsheet: ')
                self.match_logsheet_oxygen_label2= QLabel('<i>This is used for samples collected from a CTD and recorded '
                                                          'with a logsheet. Tick this is this the CTD survey.</i>')
                self.match_logsheet_oxygen_label2.setWordWrap(True)

                self.custom_survey_label = QLabel('<b>Settings for grouping custom surveys</b>')


                self.decode_oxygen_label = QLabel('Decode Oxygen file Station number to a survey: ')
                self.decode_oxygen_label2 = QLabel('<i>Use this to represent a custom survey, do not use a station '
                                                   'number less than 900. Less than 900 and HyPro will not recognise. Increase RP for each sample. </i>')
                self.decode_oxygen_label2.setWordWrap(True)
                self.decode_oxygen = QCheckBox(self)
                #self.decodeOxygen.clicked.connect(self.enabledisable)

                self.survey_number_station_label = QLabel('Enter a number to represent the survey: ')

                self.survey_number_station = QLineEdit(self)

                self.decode_oxygen_deployment = QCheckBox()
                self.decode_oxygen_deployment_label = QLabel('Decode deployment and RP: ')
                self.decode_oxygen_deployment_label2 = QLabel('<i>Use the Cast and Rosette Position data columns to decode '
                                                              'a deployment and rp. Do not use for typical CTD '
                                                              'deployments, use for TMR or Coastal projects without a '
                                                              'CTD file or logsheet.</i>')
                self.decode_oxygen_deployment_label2.setWordWrap(True)
                self.sample_oxygen_id = QCheckBox('Just use Bottle ID', self)

                self.create_oxygen_metadata = QCheckBox('Automatically create meta-data', self)

                oxylinesep1 = QFrame(self)
                oxylinesep1.setFrameShape(QFrame.HLine)
                oxylinesep1.setFrameShadow(QFrame.Sunken)

                oxylinesep2 = QFrame(self)
                oxylinesep2.setFrameShape(QFrame.HLine)
                oxylinesep2.setFrameShadow(QFrame.Sunken)

                oxylinesep3 = QFrame(self)
                oxylinesep3.setFrameShape(QFrame.HLine)
                oxylinesep3.setFrameShadow(QFrame.Sunken)

                oxylinesep4 = QFrame(self)
                oxylinesep4.setFrameShape(QFrame.HLine)
                oxylinesep4.setFrameShadow(QFrame.Sunken)

                oxy_grid.addWidget(self.activate_oxygen, 0, 0, 2, 4)
                oxy_grid.addWidget(oxylinesep1, 1, 0, 1, 4)

                oxy_grid.addWidget(self.match_logsheet_oxygen, 2, 3, 1, 1)
                oxy_grid.addWidget(self.match_logsheet_oxygen_label, 2, 0, 1, 4)
                oxy_grid.addWidget(self.match_logsheet_oxygen_label2, 3, 0, 1, 4)

                oxy_grid.addWidget(oxylinesep2, 4, 0, 1, 4)

                oxy_grid.addWidget(self.custom_survey_label, 5, 0, 1, 4, Qt.AlignHCenter)

                oxy_grid.addWidget(self.decode_oxygen, 6, 3)
                oxy_grid.addWidget(self.decode_oxygen_label, 6, 0, 1, 3)
                oxy_grid.addWidget(self.decode_oxygen_label2, 7, 0, 1, 4)

                oxy_grid.addWidget(self.survey_number_station_label, 8, 0, 1, 2)
                oxy_grid.addWidget(self.survey_number_station, 8, 3, 1, 1)

                oxy_grid.addWidget(oxylinesep4, 9, 0, 1, 4)

                oxy_grid.addWidget(self.decode_oxygen_deployment, 10, 3)
                oxy_grid.addWidget(self.decode_oxygen_deployment_label, 10, 0, 1, 4)
                oxy_grid.addWidget(self.decode_oxygen_deployment_label2, 11, 0, 1, 4)

                oxy_grid.addWidget(oxylinesep3, 12, 0, 1, 4)
                oxy_grid.addWidget(self.sample_oxygen_id, 13, 0)

                oxy_grid.addWidget(self.create_oxygen_metadata, 14, 0)
                
                
                self.oxygentab.setLayout(oxy_grid)

            # Nutrient tab
            if self.nutsactive:
                self.nutrienttab.layout = QGridLayout()

                self.activateNutrient = QCheckBox('Activate for use with this survey', self)
                #self.activateNutrient.clicked.connect(self.enabledisable)

                self.matchNutrientLabel = QLabel('Use sampling logsheet to match RP and bottle label:', self)

                self.matchNutrientCheck = QCheckBox(self)

                self.decodeNutrientLabel = QLabel('Decode sample ID:')

                self.decodeNutrient = QCheckBox(self)
                #self.decodeNutrient.clicked.connect(self.enabledisable)

                self.surveyPrefixNutrient = QLabel('Sample survey prefix')

                self.surveyPrefixNutrientEdit = QLineEdit(self)
                self.surveyPrefixNutrientEdit.setDisabled(True)

                self.decodeNutrientDeployment = QCheckBox('Decode Deployment from sample ID', self)
                #self.decodeNutrientDeployment.clicked.connect(self.enabledisable)
                self.decodeNutrientDeployment.setDisabled(True)

                self.deploymentNutrientFormat = QLabel(
                    'Deployment/Bottle format after prefix (if there is one) e.g. DDDBB', self)

                self.deploymentNutrientFormatEdit = QLineEdit(self)
                self.deploymentNutrientFormatEdit.setDisabled(True)

                self.decodeNutrientDate = QCheckBox('Decode Sample ID date format', self)
                #self.decodeNutrientDate.clicked.connect(self.enabledisable)
                self.decodeNutrientDate.setDisabled(True)

                self.dateNutrientFormat = QLabel('Date/Time format e.g. YYYYMMDD hh:mm:ss', self)

                self.decodeNutrientDateEdit = QLineEdit(self)
                self.decodeNutrientDateEdit.setDisabled(True)

                self.sampleNutrientID = QCheckBox('Use sample ID instead of dep/ros label', self)

                self.createNutrientMetadata = QCheckBox('Automatically create meta-data', self)

                nutlinesep1 = QFrame(self)
                nutlinesep1.setFrameShape(QFrame.HLine)
                nutlinesep1.setFrameShadow(QFrame.Sunken)

                nutlinesep2 = QFrame(self)
                nutlinesep2.setFrameShape(QFrame.HLine)
                nutlinesep2.setFrameShadow(QFrame.Sunken)

                nutlinesep3 = QFrame(self)
                nutlinesep3.setFrameShape(QFrame.HLine)
                nutlinesep3.setFrameShadow(QFrame.Sunken)

                self.nutrienttab.layout.addWidget(self.activateNutrient, 0, 0)
                self.nutrienttab.layout.addWidget(nutlinesep1, 1, 0, 1, 2)

                self.nutrienttab.layout.addWidget(self.matchNutrientLabel, 2, 0)
                self.nutrienttab.layout.addWidget(self.matchNutrientCheck, 2, 1)

                self.nutrienttab.layout.addWidget(nutlinesep2, 3, 0, 1, 2)

                self.nutrienttab.layout.addWidget(self.decodeNutrientLabel, 4, 0)
                self.nutrienttab.layout.addWidget(self.decodeNutrient, 4, 1)

                self.nutrienttab.layout.addWidget(self.surveyPrefixNutrient, 5, 0)
                self.nutrienttab.layout.addWidget(self.surveyPrefixNutrientEdit, 5, 1)

                self.nutrienttab.layout.addWidget(self.decodeNutrientDeployment, 6, 0)

                self.nutrienttab.layout.addWidget(self.deploymentNutrientFormat, 7, 0)
                self.nutrienttab.layout.addWidget(self.deploymentNutrientFormatEdit, 7, 1)

                self.nutrienttab.layout.addWidget(self.decodeNutrientDate, 8, 0)

                self.nutrienttab.layout.addWidget(self.dateNutrientFormat, 9, 0)
                self.nutrienttab.layout.addWidget(self.decodeNutrientDateEdit, 9, 1)

                self.nutrienttab.layout.addWidget(nutlinesep3, 10, 0, 1, 2)

                self.nutrienttab.layout.addWidget(self.sampleNutrientID, 11, 0)
                self.nutrienttab.layout.addWidget(self.createNutrientMetadata, 12, 0)

                self.nutrienttab.setLayout(self.nutrienttab.layout)

            self.populatefields()

        except Exception:
            traceback.print_exc()

    def populatefields(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())
        surveys = list(params['surveyparams'].keys())
        for k in surveys:
            if k == self.survey:
                if self.saltactive:
                    self.activateSalinity.setChecked(params['surveyparams'][k]['guildline']['activated'])
                    self.matchSalinityCheck.setChecked(params['surveyparams'][k]['guildline']['matchlogsheet'])
                    self.decodeSalinity.setChecked(params['surveyparams'][k]['guildline']['decodesampleid'])
                    self.surveyPrefixSalinityEdit.setText(params['surveyparams'][k]['guildline']['surveyprefix'])
                    self.decodeSalinityDeployment.setChecked(params['surveyparams'][k]['guildline']['decodedepfromid'])
                    self.deploymentSalinityFormatEdit.setText(params['surveyparams'][k]['guildline']['depformat'])
                    self.decodeSalinityDate.setChecked(params['surveyparams'][k]['guildline']['decodetimefromid'])
                    self.decodeSalinityDateEdit.setText(params['surveyparams'][k]['guildline']['dateformat'])
                    self.sampleSalinityID.setChecked(params['surveyparams'][k]['guildline']['usesampleid'])
                    self.createSalinityMetadata.setChecked(params['surveyparams'][k]['guildline']['autometadata'])
                # if self.oxyactive:
                #     self.activateOxygen.setChecked(params['surveyparams'][k]['scripps']['activated'])
                #     self.matchOxygenCheck.setChecked(params['surveyparams'][k]['scripps']['matchlogsheet'])
                #     self.decodeOxygen.setChecked(params['surveyparams'][k]['scripps']['decodesampleid'])
                #     self.surveyPrefixOxygenEdit.setText(params['surveyparams'][k]['scripps']['surveyprefix'])
                #     self.decodeOxygenDeployment.setChecked(params['surveyparams'][k]['scripps']['decodedepfromid'])
                #     self.deploymentOxygenFormatEdit.setText(params['surveyparams'][k]['scripps']['depformat'])
                #     self.decodeOxygenDate.setChecked(params['surveyparams'][k]['scripps']['decodetimefromid'])
                #     self.decodeOxygenDateEdit.setText(params['surveyparams'][k]['scripps']['dateformat'])
                #     self.sampleOxygenID.setChecked(params['surveyparams'][k]['scripps']['usesampleid'])
                #     self.createOxygenMetadata.setChecked(params['surveyparams'][k]['scripps']['autometadata'])
                if self.nutsactive:
                    self.activateNutrient.setChecked(params['surveyparams'][k]['seal']['activated'])
                    self.matchNutrientCheck.setChecked(params['surveyparams'][k]['seal']['matchlogsheet'])
                    self.decodeNutrient.setChecked(params['surveyparams'][k]['seal']['decodesampleid'])
                    self.surveyPrefixNutrientEdit.setText(params['surveyparams'][k]['seal']['surveyprefix'])
                    self.decodeNutrientDeployment.setChecked(params['surveyparams'][k]['seal']['decodedepfromid'])
                    self.deploymentNutrientFormatEdit.setText(params['surveyparams'][k]['seal']['depformat'])
                    self.decodeNutrientDate.setChecked(params['surveyparams'][k]['seal']['decodetimefromid'])
                    self.decodeNutrientDateEdit.setText(params['surveyparams'][k]['seal']['dateformat'])
                    self.sampleNutrientID.setChecked(params['surveyparams'][k]['seal']['usesampleid'])
                    self.createNutrientMetadata.setChecked(params['surveyparams'][k]['seal']['autometadata'])

    def savefunction(self):
        try:
            surveyname = str(self.surveyName.text())
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())
            # TODO Fix this so it changes the save query based on tabs open

            newsurvey = {'%s' % surveyname: {}}
            if self.nutsactive:
                newsurvey[surveyname]['seal'] = {'activated': self.activateNutrient.isChecked(),
                                                      'matchlogsheet': self.matchNutrientCheck.isChecked(),
                                                      'decodesampleid': self.decodeNutrient.isChecked(),
                                                      'surveyprefix': self.surveyPrefixNutrientEdit.text(),
                                                      'decodedepfromid': self.decodeNutrientDeployment.isChecked(),
                                                      'depformat': self.deploymentNutrientFormatEdit.text(),
                                                      'decodetimefromid': self.decodeNutrientDate.isChecked(),
                                                      'dateformat': self.decodeNutrientDateEdit.text(),
                                                      'usesampleid': self.sampleNutrientID.isChecked(),
                                                      'autometadata': self.createNutrientMetadata.isChecked()}
            if self.saltactive:
                newsurvey[surveyname]['guildline'] = {'activated': self.activateSalinity.isChecked(),
                                                           'matchlogsheet': self.matchSalinityCheck.isChecked(),
                                                           'decodesampleid': self.decodeSalinity.isChecked(),
                                                           'surveyprefix': self.surveyPrefixSalinityEdit.text(),
                                                           'decodedepfromid': self.decodeSalinityDeployment.isChecked(),
                                                           'depformat': self.deploymentSalinityFormatEdit.text(),
                                                           'decodetimefromid': self.decodeSalinityDate.isChecked(),
                                                           'dateformat': self.decodeSalinityDateEdit.text(),
                                                           'usesampleid': self.sampleSalinityID.isChecked(),
                                                           'autometadata': self.createSalinityMetadata.isChecked()}
            if self.oxyactive:
                newsurvey[surveyname]['scripps'] = {'activated': self.activate_oxygen.isChecked(),
                                                         'matchlogsheet': self.match_logsheet_oxygen.isChecked(),
                                                         'decodesampleid': self.decode_oxygen.isChecked(),
                                                         'surveyprefix': self.survey_number_station.text(),
                                                         'decodedepfromid': self.decode_oxygen_deployment.isChecked(),
                                                         'usesampleid': self.sample_oxygen_id.isChecked(),
                                                         'autometadata': self.create_oxygen_metadata.isChecked()}
            params['surveyparams'].update(newsurvey)

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
                json.dump(params, file)

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                     "Survey settings saved",
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()

        except Exception as e:
            print('Error: ' + e)

    def cancelfunction(self):
        self.close()
