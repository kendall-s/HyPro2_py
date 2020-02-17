# https://stackoverflow.com/questions/8979409/get-text-from-qpushbutton-in-pyqt

from dialogs.templates.DialogTemplate import hyproDialogTemplate
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QGridLayout, QMessageBox, QFrame,
                             QCheckBox, QTabWidget, QGroupBox)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import traceback
import json
import hyproicons, style

# The GUI for adding or editing surveys to the required settings needed
class surveyDialog(hyproDialogTemplate):
    def __init__(self, project, survey, path):
        super().__init__(420, 650, 'HyPro - Add Survey')

        self.currproject = project
        self.survey = survey
        self.currpath = path
        
        if survey != 'new':
            self.setWindowTitle('HyPro - Survey Settings')
            self.surveyName = QLineEdit(self.survey)
            self.surveyName.setReadOnly(True)
        else: 
            self.surveyName = QLineEdit(self)
        self.surveyName.setStyleSheet("QLineEdit {font: 14px Segoe UI; font-weight: bold; }")
        self.init_ui()


    def init_ui(self):
        try:
            self.setFont(QFont('Segoe UI'))
            
            headerLabel = QLabel('Survey name: ', self)

            analyses = ['Guildline Salinity', 'Scripps Oxygen', 'Seal Nutrients', 'Seasave CTD']
            analyseskey = ['guildline', 'scripps', 'seal', 'seasave']

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())

            self.tabs = QTabWidget()
            self.saltactive = False
            self.oxyactive = False
            self.nuts_active = False
            self.ctdactive = False

            tabnotadded = True
            for i, analysis in enumerate(params['analysisparams'].keys()):
                print(analysis)
                if params['analysisparams'][analysis]['activated'] == True:
                    if analysis == 'seal':
                        self.nutrient_tab = QWidget()
                        self.tabs.addTab(self.nutrient_tab, 'Nutrients')
                        self.nuts_active = True
                    if analysis == 'guildline':
                        self.salttab = QWidget()
                        self.tabs.addTab(self.salttab, 'Salinity')
                        self.saltactive = True
                    if analysis == 'scripps':
                        self.oxygentab = QWidget()
                        self.tabs.addTab(self.oxygentab, 'Oxygen')
                        self.oxyactive = True
                    if analysis == 'seasave':
                        self.ctdtab = QWidget()
                        self.tabs.addTab(self.ctdtab, 'CTD')
                        self.ctdactive = True
                    tabnotadded = False

            if tabnotadded:
                self.add_analysis = QWidget()
                self.tabs.addTab(self.add_analysis, 'Tab')
                self.add_analysis_label = QLabel('Add an analysis first to set survey settings')
                self.add_analysis.layout = QGridLayout()
                self.add_analysis.layout.addWidget(self.add_analysis_label, 0, 0)
                self.add_analysis.setLayout(self.add_analysis.layout)

            save = QPushButton('Save', self)
            save.clicked.connect(self.savefunction)

            cancel = QPushButton('Cancel', self)
            cancel.clicked.connect(self.cancelfunction)

            self.grid_layout.addWidget(headerLabel, 0, 0)
            self.grid_layout.addWidget(self.surveyName, 0, 1)

            self.grid_layout.addWidget(self.tabs, 1, 0, 5, 3)

            self.grid_layout.addWidget(save, 10, 0)
            self.grid_layout.addWidget(cancel, 10, 2)

            self.setLayout(self.grid_layout)

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
                oxy_grid.setSpacing(5)
                self.activate_oxygen = QCheckBox('Activate for use with this survey', self)
                self.activate_oxygen.setStyleSheet('QCheckBox { font-weight: bold; }')

                self.ctd_survey_oxygen = QCheckBox('This is the survey for CTD samples ')
                self.ctd_survey_oxygen_label = QLabel('<i>This is used for samples collected from a CTD and recorded '
                                                          'with a logsheet. Tick if this is the CTD survey.</i>')
                self.ctd_survey_oxygen_label.setWordWrap(True)

                self.decode_oxygen = QCheckBox('Decode Oxygen file Station value to a survey')
                self.decode_oxygen_label = QLabel('<i>Use this to represent a custom survey, do not use a station '
                                                   'number less than 900. Less than 900 and HyPro will not recognise. Increase RP for each sample. </i>')
                self.decode_oxygen_label.setWordWrap(True)
                #self.decodeOxygen.clicked.connect(self.enabledisable)

                self.survey_number_station_label = QLabel('Enter a number to represent the survey: ')

                self.survey_number_station = QLineEdit(self)

                self.decode_oxygen_deployment = QCheckBox('Decode deployment and RP from oxygen file')
                self.decode_oxygen_deployment_label = QLabel('<i>Use the Cast and Rosette Position data columns to decode '
                                                              'a deployment and rp. Do not use for typical CTD '
                                                              'deployments, use for TMR or Coastal projects without a '
                                                              'CTD file or logsheet.</i>')
                self.decode_oxygen_deployment_label.setWordWrap(True)

                self.sample_oxygen_id = QCheckBox('Just use Bottle ID', self)
                self.sample_oxygen_id_label = QLabel('<i>Directly use bottle ID instead of dep/ros label decoding system,'
                                                ' beware this overrides all other decoding of IDs')
                self.sample_oxygen_id_label.setWordWrap(True)

                oxylinesep1 = QFrame(self)
                oxylinesep1.setFrameShape(QFrame.HLine)
                oxylinesep1.setFrameShadow(QFrame.Sunken)

                #oxylinesep2 = QFrame(self)
                #oxylinesep2.setFrameShape(QFrame.HLine)
                #oxylinesep2.setFrameShadow(QFrame.Sunken)

                oxy_group_box = QGroupBox(self)
                oxy_group_box.setTitle(' Settings for grouping custom surveys ')
                oxy_group_box.setStyleSheet("font-weight: bold;")
                oxy_group_box.setAlignment(Qt.AlignRight)

                oxylinesep3 = QFrame(self)
                oxylinesep3.setFrameShape(QFrame.HLine)
                oxylinesep3.setFrameShadow(QFrame.Sunken)

                oxy_grid.addWidget(self.activate_oxygen, 0, 1, 1, 4)
                oxy_grid.addWidget(oxylinesep1, 1, 1, 1, 6)

                oxy_grid.addWidget(self.ctd_survey_oxygen, 2, 1, 1, 1)
                oxy_grid.addWidget(self.ctd_survey_oxygen_label, 3, 1, 1, 6)

                oxy_grid.addWidget(oxy_group_box, 4, 0, 9, 6)
                oxy_grid.addWidget(self.decode_oxygen, 6, 1)
                oxy_grid.addWidget(self.decode_oxygen_label, 7, 1, 1, 4)
                oxy_grid.addWidget(self.survey_number_station_label, 8, 1, 1, 4)
                oxy_grid.addWidget(self.survey_number_station, 8, 3)

                oxy_grid.addWidget(oxylinesep3, 9, 1, 1, 4)

                oxy_grid.addWidget(self.decode_oxygen_deployment, 10, 1)
                oxy_grid.addWidget(self.decode_oxygen_deployment_label, 11, 1, 1, 4)

                oxy_grid.addWidget(self.sample_oxygen_id, 13, 1)
                oxy_grid.addWidget(self.sample_oxygen_id_label, 14, 1, 1, 6)

                
                self.oxygentab.setLayout(oxy_grid)

            # Nutrient tab
            if self.nuts_active:
                self.nutrient_tab.layout = QGridLayout()
                self.nutrient_tab.layout.setSpacing(5)

                self.activate_nutrient = QCheckBox('Activate for use with this survey', self)
                self.activate_nutrient.setStyleSheet('QCheckBox { font-weight: bold; }')
                #self.activateNutrient.clicked.connect(self.enabledisable)

                nut_linesep1 = QFrame()
                nut_linesep1.setFrameShape(QFrame.HLine)
                nut_linesep1.setFrameShadow(QFrame.Sunken)


                self.ctd_survey_nutrient = QCheckBox('This is the survey for CTD samples', self)
                ctd_survey_nutrient_label = QLabel( '<i>This is used for samples collected from a CTD and recorded '
                                                    'with a logsheet. Tick if this is the CTD survey. Assumes sample'
                                                    ' ID has Dep/RP format of DDBB.</i>')
                ctd_survey_nutrient_label.setWordWrap(True)

                nut_group_box = QGroupBox(self)
                nut_group_box.setTitle(' Settings for grouping custom surveys ')
                nut_group_box.setStyleSheet("font-weight: bold;")
                nut_group_box.setAlignment(Qt.AlignRight)

                self.decode_nutrient = QCheckBox('Decode Sample ID value to a survey')
                decode_nutrient_label = QLabel('<i>Use this to represent a custom survey, such as underway or TSG. Keep'
                                               '  the prefix short for ease of use.')
                decode_nutrient_label.setWordWrap(True)

                survey_prefix_nutrient_label = QLabel('Survey prefix on sample ID:')

                self.survey_prefix_nutrient = QLineEdit(self)
                self.survey_prefix_nutrient.setDisabled(True)

                nut_linesep2 = QFrame()
                nut_linesep2.setFrameShape(QFrame.HLine)
                nut_linesep2.setFrameShadow(QFrame.Sunken)

                self.decode_deployment_nutrient = QCheckBox('Decode deployment and RP from ID', self)

                decode_deprp_nutrient_label = QLabel('<i>Decode the sample ID for deployment and RP. Do not use for '
                                                     'typical CTD deployments, use for TMR or Coastal projects without'
                                                     'a CTD file or HyPro logsheet.</i>')
                decode_deprp_nutrient_label.setWordWrap(True)

                dep_rp_format_nutrient_label = QLabel('Dep/Bottle format after prefix:')

                self.dep_rp_format_nutrient = QLineEdit()
                self.dep_rp_format_nutrient.setPlaceholderText('e.g. DDDBB')

                self.sample_id_nutrient = QCheckBox('Just use sample ID', self)

                sample_id_nutrient_label = QLabel('<i>Directly use sample ID value instead of dep/rp label decoding'
                                                  'system, beware this overrides all other decoding of IDs')
                sample_id_nutrient_label.setWordWrap(True)

                self.nutrient_tab.layout.addWidget(self.activate_nutrient, 0, 1)
                self.nutrient_tab.layout.addWidget(nut_linesep1, 1, 0, 1, 6)
                self.nutrient_tab.layout.addWidget(self.ctd_survey_nutrient, 2, 1)
                self.nutrient_tab.layout.addWidget(ctd_survey_nutrient_label, 3, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(nut_group_box, 4, 0, 9, 6)
                self.nutrient_tab.layout.addWidget(self.decode_nutrient, 5, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(decode_nutrient_label, 6, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(survey_prefix_nutrient_label, 7, 1, 1, 2)
                self.nutrient_tab.layout.addWidget(self.survey_prefix_nutrient, 7, 3)
                self.nutrient_tab.layout.addWidget(nut_linesep2, 8, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(self.decode_deployment_nutrient, 9, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(decode_deprp_nutrient_label, 10, 1, 1, 4)
                self.nutrient_tab.layout.addWidget(dep_rp_format_nutrient_label, 11, 1, 1, 2)
                self.nutrient_tab.layout.addWidget(self.dep_rp_format_nutrient, 11, 3, 1, 1)
                self.nutrient_tab.layout.addWidget(self.sample_id_nutrient, 13, 1)
                self.nutrient_tab.layout.addWidget(sample_id_nutrient_label, 14, 1, 1, 6)

                self.nutrient_tab.setLayout(self.nutrient_tab.layout)

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
                if self.oxyactive:
                    self.activate_oxygen.setChecked(params['surveyparams'][k]['scripps']['activated'])
                    self.ctd_survey_oxygen.setChecked(params['surveyparams'][k]['scripps']['ctdsurvey'])
                    self.decode_oxygen.setChecked(params['surveyparams'][k]['scripps']['decodesampleid'])
                    self.survey_number_station.setText(params['surveyparams'][k]['scripps']['surveyprefix'])
                    self.decode_oxygen_deployment.setChecked(params['surveyparams'][k]['scripps']['decodedepfromid'])
                    self.sample_oxygen_id.setChecked(params['surveyparams'][k]['scripps']['usesampleid'])

                if self.nuts_active:
                    self.activate_nutrient.setChecked(params['surveyparams'][k]['seal']['activated'])
                    self.ctd_survey_nutrient.setChecked(params['surveyparams'][k]['seal']['ctdsurvey'])
                    self.decode_nutrient.setChecked(params['surveyparams'][k]['seal']['decodesampleid'])
                    self.survey_prefix_nutrient.setText(params['surveyparams'][k]['seal']['surveyprefix'])
                    self.decode_deployment_nutrient.setChecked(params['surveyparams'][k]['seal']['decodedepfromid'])
                    self.dep_rp_format_nutrient.setText(params['surveyparams'][k]['seal']['depformat'])
                    self.sample_id_nutrient.setChecked(params['surveyparams'][k]['seal']['usesampleid'])

    def savefunction(self):
        try:
            surveyname = str(self.surveyName.text())
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())
            # TODO Fix this so it changes the save query based on tabs open

            newsurvey = {'%s' % surveyname: {}}
            if self.nuts_active:
                newsurvey[surveyname]['seal'] = {'activated': self.activate_nutrient.isChecked(),
                                                      'ctdsurvey': self.ctd_survey_nutrient.isChecked(),
                                                      'usesampleid': self.sample_id_nutrient.isChecked(),
                                                      'surveyprefix': self.survey_prefix_nutrient.text(),
                                                      'decodedepfromid': self.decode_deployment_nutrient.isChecked(),
                                                      'depformat': self.dep_rp_format_nutrient.text()}
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
                                                         'ctdsurvey': self.ctd_survey_oxygen.isChecked(),
                                                         'decodesampleid': self.decode_oxygen.isChecked(),
                                                         'surveyprefix': self.survey_number_station.text(),
                                                         'decodedepfromid': self.decode_oxygen_deployment.isChecked(),
                                                         'usesampleid': self.sample_oxygen_id.isChecked()}

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
