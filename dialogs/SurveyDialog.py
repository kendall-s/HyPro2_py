# https://stackoverflow.com/questions/8979409/get-text-from-qpushbutton-in-pyqt

from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
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
        super().__init__(420, 665, 'HyPro - Add Survey')

        self.currproject = project
        self.survey = survey
        self.currpath = path

        if self.survey != 'new':
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
            self.salt_active = False
            self.oxy_active = False
            self.nuts_active = False
            self.ctdactive = False

            tabnotadded = True
            for i, analysis in enumerate(params['analysis_params'].keys()):
                print(analysis)
                if params['analysis_params'][analysis]['activated'] == True or self.survey == 'new':
                    if analysis == 'seal':
                        self.nutrient_tab = QWidget()
                        self.tabs.addTab(self.nutrient_tab, 'Nutrients')
                        self.nuts_active = True
                    if analysis == 'guildline':
                        self.salttab = QWidget()
                        self.tabs.addTab(self.salttab, 'Salinity')
                        self.salt_active = True
                    if analysis == 'scripps':
                        self.oxygentab = QWidget()
                        self.tabs.addTab(self.oxygentab, 'Oxygen')
                        self.oxy_active = True
                    if analysis == 'seasave' and self.survey != 'new':
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
            save.setMinimumWidth(100)
            save.clicked.connect(self.savefunction)

            cancel = QPushButton('Cancel', self)
            cancel.setMinimumWidth(100)
            cancel.clicked.connect(self.cancelfunction)

            self.grid_layout.addWidget(headerLabel, 0, 0)
            self.grid_layout.addWidget(self.surveyName, 0, 1)

            self.grid_layout.addWidget(self.tabs, 1, 0, 5, 3)

            self.grid_layout.addWidget(save, 10, 0)
            self.grid_layout.addWidget(cancel, 10, 2)

            self.setLayout(self.grid_layout)

            # Salinity Tab
            if self.salt_active:

                salt_grid = QGridLayout()
                salt_grid.setSpacing(5)
                self.activate_salt = QCheckBox('Activate for use with this survey', self)
                self.activate_salt.setStyleSheet('QCheckBox { font-weight: bold; }')

                self.ctd_survey_salt = QCheckBox('This is the survey for CTD samples ')
                self.ctd_survey_salt_label = QLabel('<i>This is used for samples collected from a CTD and recorded '
                                                      'with a logsheet. Tick if this is the CTD survey. \n</i>')
                self.ctd_survey_salt_label.setWordWrap(True)

                self.decode_salt = QCheckBox('Decode Salinity file Sample ID value to a survey')
                self.decode_salt_label = QLabel('<i>Use this to represent a custom survey, such as underway or TSG. '
                                                  'Keep the prefix short for ease of use. </i>')
                self.decode_salt_label.setWordWrap(True)
                # self.decodeOxygen.clicked.connect(self.enabledisable)

                self.survey_number_station_label = QLabel('Survey prefix on sample ID: ')

                self.survey_prefix_salt = QLineEdit(self)

                self.decode_salt_deployment = QCheckBox('Decode deployment and RP from oxygen file')
                self.decode_salt_deployment_label = QLabel(
                    '<i>Use the Cast and Rosette Position data columns to decode '
                    'a deployment and rp. Do not use for typical CTD '
                    'deployments, use for TMR or Coastal projects without a '
                    'CTD file or logsheet.</i>')
                self.decode_salt_deployment_label.setWordWrap(True)

                dep_rp_format_salt_label = QLabel('Dep/Bottle format after prefix:')
                self.dep_rp_format_salt = QLineEdit()
                self.dep_rp_format_salt.setPlaceholderText('e.g. DDDBB')

                self.sample_salt_id = QCheckBox('Just use Sample ID', self)
                self.sample_salt_id_label = QLabel(
                    '<i>Directly use sample ID instead of dep/ros label decoding system,'
                    ' beware this overrides all other decoding of IDs')
                self.sample_salt_id_label.setWordWrap(True)

                saltlinesep1 = QFrame(self)
                saltlinesep1.setFrameShape(QFrame.HLine)
                saltlinesep1.setFrameShadow(QFrame.Sunken)

                salt_group_box = QGroupBox(self)
                salt_group_box.setTitle(' Settings for grouping custom surveys ')
                salt_group_box.setStyleSheet("font-weight: bold;")
                salt_group_box.setAlignment(Qt.AlignRight)

                saltlinesep3 = QFrame(self)
                saltlinesep3.setFrameShape(QFrame.HLine)
                saltlinesep3.setFrameShadow(QFrame.Sunken)

                salt_grid.addWidget(self.activate_salt, 0, 1, 1, 4)
                salt_grid.addWidget(saltlinesep1, 1, 0, 1, 6)

                salt_grid.addWidget(self.ctd_survey_salt, 2, 1)
                salt_grid.addWidget(self.ctd_survey_salt_label, 3, 1, 1, 4)

                salt_grid.addWidget(salt_group_box, 4, 0, 10, 6)
                salt_grid.addWidget(self.decode_salt, 6, 1, 1, 4)
                salt_grid.addWidget(self.decode_salt_label, 7, 1, 1, 2)
                salt_grid.addWidget(self.survey_number_station_label, 8, 1, 1, 4)
                salt_grid.addWidget(self.survey_prefix_salt, 8, 3)

                salt_grid.addWidget(saltlinesep3, 9, 1, 1, 4)

                salt_grid.addWidget(self.decode_salt_deployment, 10, 1, 1, 4)
                salt_grid.addWidget(self.decode_salt_deployment_label, 11, 1, 1, 4)

                salt_grid.addWidget(dep_rp_format_salt_label, 12, 1, 1, 2)
                salt_grid.addWidget(self.dep_rp_format_salt, 12, 3, 1, 1)

                salt_grid.addWidget(self.sample_salt_id, 14, 1)
                salt_grid.addWidget(self.sample_salt_id_label, 15, 1, 1, 6)


                self.salttab.setLayout(salt_grid)

            # Oxygen Tab
            if self.oxy_active:
                
                oxy_grid = QGridLayout()
                oxy_grid.setSpacing(5)
                self.activate_oxygen = QCheckBox('Activate for use with this survey', self)
                self.activate_oxygen.setStyleSheet('QCheckBox { font-weight: bold; }')

                self.ctd_survey_oxygen = QCheckBox('This is the survey for CTD samples ')
                self.ctd_survey_oxygen_label = QLabel('<i>This is used for samples collected from a CTD and recorded '
                                                          'with a logsheet. Tick if this is the CTD survey. \n</i>')
                self.ctd_survey_oxygen_label.setWordWrap(True)

                self.decode_oxygen = QCheckBox('Decode Oxygen file Station value to a survey')
                self.decode_oxygen_label = QLabel('<i>Use this to represent a custom survey, do not use a station '
                                                   'number less than 900. Less than 900 and HyPro will not recognise. Increase RP for each sample. </i>')
                self.decode_oxygen_label.setWordWrap(True)
                #self.decodeOxygen.clicked.connect(self.enabledisable)

                self.survey_number_station_label = QLabel('Enter a number to represent the survey: ')

                self.survey_number_station = QLineEdit(self)
                self.survey_number_station.setPlaceholderText('e.g. 901')

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
                oxy_grid.addWidget(self.ctd_survey_oxygen_label, 3, 1, 1, 4)

                oxy_grid.addWidget(oxy_group_box, 4, 0, 9, 6)
                oxy_grid.addWidget(self.decode_oxygen, 6, 1)
                oxy_grid.addWidget(self.decode_oxygen_label, 7, 1, 1, 4)
                oxy_grid.addWidget(self.survey_number_station_label, 8, 1, 1, 2)
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
                self.sample_id_nutrient.setToolTip('Please be aware this will supersede any other sample id matching.')

                sample_id_nutrient_label = QLabel('<i>Use sample ID value instead of dep/rp label decoding'
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
        surveys = list(params['survey_params'].keys())
        for k in surveys:
            if k == self.survey:
                try:
                    if self.salt_active:
                        self.activate_salt.setChecked(params['survey_params'][k]['guildline']['activated'])
                        self.ctd_survey_salt.setChecked(params['survey_params'][k]['guildline']['ctd_survey'])
                        self.decode_salt.setChecked(params['survey_params'][k]['guildline']['decode_sample_id'])
                        self.survey_prefix_salt.setText(params['survey_params'][k]['guildline']['survey_prefix'])
                        self.decode_salt_deployment.setChecked(params['survey_params'][k]['guildline']['decode_dep_from_id'])
                        self.sample_salt_id.setChecked(params['survey_params'][k]['guildline']['use_sample_id'])
                        self.dep_rp_format_salt.setText(params['survey_params'][k]['guildline']['depformat'])
                        
                    if self.oxy_active:
                        self.activate_oxygen.setChecked(params['survey_params'][k]['scripps']['activated'])
                        self.ctd_survey_oxygen.setChecked(params['survey_params'][k]['scripps']['ctd_survey'])
                        self.decode_oxygen.setChecked(params['survey_params'][k]['scripps']['decode_sample_id'])
                        self.survey_number_station.setText(params['survey_params'][k]['scripps']['survey_prefix'])
                        self.decode_oxygen_deployment.setChecked(params['survey_params'][k]['scripps']['decode_dep_from_id'])
                        self.sample_oxygen_id.setChecked(params['survey_params'][k]['scripps']['use_sample_id'])
    
                    if self.nuts_active:
                        self.activate_nutrient.setChecked(params['survey_params'][k]['seal']['activated'])
                        self.ctd_survey_nutrient.setChecked(params['survey_params'][k]['seal']['ctd_survey'])
                        self.decode_nutrient.setChecked(params['survey_params'][k]['seal']['decode_sample_id'])
                        self.survey_prefix_nutrient.setText(params['survey_params'][k]['seal']['survey_prefix'])
                        self.decode_deployment_nutrient.setChecked(params['survey_params'][k]['seal']['decode_dep_from_id'])
                        self.dep_rp_format_nutrient.setText(params['survey_params'][k]['seal']['depformat'])
                        self.sample_id_nutrient.setChecked(params['survey_params'][k]['seal']['use_sample_id'])
                except KeyError:
                    print('Missing key from parameters file')
                    pass
                    
    def savefunction(self):
        try:
            surveyname = str(self.surveyName.text())
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())

            newsurvey = {'%s' % surveyname: {}}
            if self.nuts_active:
                newsurvey[surveyname]['seal'] = {'activated': self.activate_nutrient.isChecked(),
                                                      'ctd_survey': self.ctd_survey_nutrient.isChecked(),
                                                      'use_sample_id': self.sample_id_nutrient.isChecked(),
                                                      'survey_prefix': self.survey_prefix_nutrient.text(),
                                                      'decode_dep_from_id': self.decode_deployment_nutrient.isChecked(),
                                                      'depformat': self.dep_rp_format_nutrient.text(),
                                                      'decode_sample_id': self.decode_nutrient.isChecked()}
            if self.salt_active:
                newsurvey[surveyname]['guildline'] = {'activated': self.activate_salt.isChecked(),
                                                         'ctd_survey': self.ctd_survey_salt.isChecked(),
                                                         'decode_sample_id': self.decode_salt.isChecked(),
                                                         'survey_prefix': self.survey_prefix_salt.text(),
                                                         'decode_dep_from_id': self.decode_salt_deployment.isChecked(),
                                                         'use_sample_id': self.sample_salt_id.isChecked(),
                                                          'depformat': self.dep_rp_format_salt.text()}
            if self.oxy_active:
                newsurvey[surveyname]['scripps'] = {'activated': self.activate_oxygen.isChecked(),
                                                         'ctd_survey': self.ctd_survey_oxygen.isChecked(),
                                                         'decode_sample_id': self.decode_oxygen.isChecked(),
                                                         'survey_prefix': self.survey_number_station.text(),
                                                         'decode_dep_from_id': self.decode_oxygen_deployment.isChecked(),
                                                         'use_sample_id': self.sample_oxygen_id.isChecked()}

            params['survey_params'].update(newsurvey)

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
                json.dump(params, file)

            message_box = hyproMessageBoxTemplate('Settings Saved',
                                                  'Survey settings were successfully saved',
                                                  'success')

        except Exception as e:
            print('Error: ' + e)

    def cancelfunction(self):
        self.close()
