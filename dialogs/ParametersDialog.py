import json
import logging
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QFrame,
                             QCheckBox, QTabWidget, QGridLayout, QComboBox)

from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate

"""
This dialog provides the ability for a user to change all of the settings and parameters related to processing data. 
"""


class parametersDialog(hyproDialogTemplate):
    def __init__(self, project, path):
        super().__init__(475, 800, 'HyPro Project Parameters')

        self.current_project = project
        self.currpath = path

        self.init_ui()

    def init_ui(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.current_project, 'r') as file:
                params = json.loads(file.read())

            self.tabs = QTabWidget()

            self.nutrient_tab = QTabWidget()
            self.tabs.addTab(self.nutrient_tab, 'Nutrients')

            self.general_tab = QWidget()
            self.nutrient_tab.addTab(self.general_tab, 'General')

            self.nitrate_tab = QWidget()
            self.nutrient_tab.addTab(self.nitrate_tab, 'Nitrate')

            self.phosphate_tab = QWidget()
            self.nutrient_tab.addTab(self.phosphate_tab, 'Phosphate')

            self.silicate_tab = QWidget()
            self.nutrient_tab.addTab(self.silicate_tab, 'Silicate')

            self.nitrite_tab = QWidget()
            self.nutrient_tab.addTab(self.nitrite_tab, 'Nitrite')

            self.ammonia_tab = QWidget()
            self.nutrient_tab.addTab(self.ammonia_tab, 'Ammonia')

            self.salinity_tab = QWidget()
            self.tabs.addTab(self.salinity_tab, 'Salinity')

            self.oxygen_tab = QWidget()
            self.tabs.addTab(self.oxygen_tab, 'Oxygen')

            save = QPushButton('Save', self)
            save.clicked.connect(self.save_function)

            cancel = QPushButton('Cancel', self)
            cancel.clicked.connect(self.cancel_function)

            self.grid_layout.addWidget(self.tabs, 1, 0, 5, 4)

            self.grid_layout.addWidget(save, 10, 1)
            self.grid_layout.addWidget(cancel, 10, 2)

            self.setLayout(self.grid_layout)

            self.general_tab.layout = QGridLayout()

            slk_column_label = QLabel('<b>SLK Column Headers</b>', self)
            sample_id_label = QLabel('Sample ID Header:', self)
            self.sample_id = QLineEdit(self)
            cup_number_label = QLabel('Cup Number Header:', self)
            self.cup_number = QLineEdit(self)
            cup_type_label = QLabel('Cup Type Header:', self)
            self.cup_type = QLineEdit(self)
            date_time_label = QLabel('Time Stamp Header:', self)
            self.date_time = QLineEdit(self)

            gen_line_sep1 = QFrame(self)
            gen_line_sep1.setFrameShape(QFrame.HLine)
            gen_line_sep1.setFrameShadow(QFrame.Sunken)

            cup_names_label = QLabel('<b>Cup Names</b>', self)
            primer_label = QLabel('Primer:', self)
            self.primer = QLineEdit(self)
            recovery_label = QLabel('NO3 Recovery:', self)
            self.recovery = QLineEdit(self)
            drift_label = QLabel('Drift:', self)
            self.drift = QLineEdit(self)
            baseline_label = QLabel('Baseline:', self)
            self.baseline = QLineEdit(self)
            calibrant_label = QLabel('Calibrants:', self)
            self.calibrant = QLineEdit(self)
            high_label = QLabel('High Carryover:', self)
            self.high = QLineEdit(self)
            low_label = QLabel('Low Carryover:', self)
            self.low = QLineEdit(self)
            null_label = QLabel('Null:', self)
            self.null = QLineEdit(self)
            sample_label = QLabel('Sample:', self)
            self.sample = QLineEdit(self)
            end_label = QLabel('End:', self)
            self.end = QLineEdit(self)

            gen_line_sep2 = QFrame(self)
            gen_line_sep2.setFrameShape(QFrame.HLine)
            gen_line_sep2.setFrameShadow(QFrame.Sunken)

            qc_sample_label = QLabel('<b>QC Sample Names</b>', self)
            drift_check_label = QLabel('Drift Check:', self)
            self.drift_check = QLineEdit(self)
            rmns_label = QLabel('RMNS:', self)
            self.rmns = QLineEdit(self)
            mdl_label = QLabel('MDL:', self)
            self.mdl = QLineEdit(self)
            bqc_label = QLabel('Bulk QC:', self)
            self.bqc = QLineEdit(self)
            int_qc_label = QLabel('Internal QC:', self)
            self.int_qc = QLineEdit(self)
            uwy_label = QLabel('Underway Sample:', self)
            self.uwy = QLineEdit(self)

            self.general_tab.layout.addWidget(slk_column_label, 0, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.general_tab.layout.addWidget(sample_id_label, 1, 0)
            self.general_tab.layout.addWidget(self.sample_id, 1, 1)
            self.general_tab.layout.addWidget(cup_number_label, 2, 0)
            self.general_tab.layout.addWidget(self.cup_number, 2, 1)
            self.general_tab.layout.addWidget(cup_type_label, 3, 0)
            self.general_tab.layout.addWidget(self.cup_type, 3, 1)
            self.general_tab.layout.addWidget(date_time_label, 4, 0)
            self.general_tab.layout.addWidget(self.date_time, 4, 1)

            self.general_tab.layout.addWidget(gen_line_sep1, 5, 0, 1, 2)

            self.general_tab.layout.addWidget(cup_names_label, 6, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.general_tab.layout.addWidget(primer_label, 7, 0)
            self.general_tab.layout.addWidget(self.primer, 7, 1)
            self.general_tab.layout.addWidget(recovery_label, 8, 0)
            self.general_tab.layout.addWidget(self.recovery, 8, 1)
            self.general_tab.layout.addWidget(drift_label, 9, 0)
            self.general_tab.layout.addWidget(self.drift, 9, 1)
            self.general_tab.layout.addWidget(baseline_label, 10, 0)
            self.general_tab.layout.addWidget(self.baseline, 10, 1)
            self.general_tab.layout.addWidget(calibrant_label, 11, 0)
            self.general_tab.layout.addWidget(self.calibrant, 11, 1)
            self.general_tab.layout.addWidget(high_label, 12, 0)
            self.general_tab.layout.addWidget(self.high, 12, 1)
            self.general_tab.layout.addWidget(low_label, 13, 0)
            self.general_tab.layout.addWidget(self.low, 13, 1)
            self.general_tab.layout.addWidget(null_label, 14, 0)
            self.general_tab.layout.addWidget(self.null, 14, 1)
            self.general_tab.layout.addWidget(sample_label, 15, 0)
            self.general_tab.layout.addWidget(self.sample, 15, 1)
            self.general_tab.layout.addWidget(end_label, 16, 0)
            self.general_tab.layout.addWidget(self.end, 16, 1)

            self.general_tab.layout.addWidget(gen_line_sep2, 17, 0, 1, 2)

            self.general_tab.layout.addWidget(qc_sample_label, 18, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.general_tab.layout.addWidget(drift_check_label, 19, 0)
            self.general_tab.layout.addWidget(self.drift_check, 19, 1)
            self.general_tab.layout.addWidget(rmns_label, 20, 0)
            self.general_tab.layout.addWidget(self.rmns, 20, 1)
            self.general_tab.layout.addWidget(mdl_label, 21, 0)
            self.general_tab.layout.addWidget(self.mdl, 21, 1)
            self.general_tab.layout.addWidget(bqc_label, 22, 0)
            self.general_tab.layout.addWidget(self.bqc, 22, 1)
            self.general_tab.layout.addWidget(int_qc_label, 23, 0)
            self.general_tab.layout.addWidget(self.int_qc, 23, 1)
            self.general_tab.layout.addWidget(uwy_label, 24, 0)
            self.general_tab.layout.addWidget(self.uwy, 24, 1)

            self.general_tab.setLayout(self.general_tab.layout)

            """
            ************************* Nitrate Tab *************************
            """

            self.nitrate_tab.layout = QGridLayout()

            nitratenamelabel = QLabel('Name:', self)
            self.nitratename = QLineEdit(self)
            nitratewindowsizelabel = QLabel('Window Size: ', self)
            self.nitratewindowsize = QLineEdit(self)
            nitratewindowstartlabel = QLabel('Window Start: ', self)
            self.nitratewindowstart = QLineEdit(self)
            nitratedrifttypelabel = QLabel('Drift Correction Type: ', self)
            self.nitratedrifttype = QComboBox(self)
            self.nitratedrifttype.addItems(('Piecewise', 'Linear'))
            nitratebasetypelabel = QLabel('Baseline Correction Type: ', self)
            self.nitratebasetype = QComboBox(self)
            self.nitratebasetype.addItems(('Piecewise', 'Linear'))
            self.nitratecarryover = QCheckBox('Carryover Correction Enabled ', self)
            nitratecaltypelabel = QLabel('Calibration Type: ')
            self.nitratecaltype = QComboBox(self)
            self.nitratecaltype.addItems(('Linear', 'Quadratic'))
            nitratecalerrorlabel = QLabel('Calibration Error: ')
            self.nitratecalerror = QLineEdit(self)
            nitrate_duplicate_label = QLabel('Duplicate Error: ')
            self.nitrate_duplicate_error = QLineEdit(self)

            self.nitrate_tab.layout.addWidget(nitratenamelabel, 0, 0)
            self.nitrate_tab.layout.addWidget(self.nitratename, 0, 1)
            self.nitrate_tab.layout.addWidget(nitratewindowsizelabel, 1, 0)
            self.nitrate_tab.layout.addWidget(self.nitratewindowsize, 1, 1)
            self.nitrate_tab.layout.addWidget(nitratewindowstartlabel, 2, 0)
            self.nitrate_tab.layout.addWidget(self.nitratewindowstart, 2, 1)
            self.nitrate_tab.layout.addWidget(nitratedrifttypelabel, 3, 0)
            self.nitrate_tab.layout.addWidget(self.nitratedrifttype, 3, 1)
            self.nitrate_tab.layout.addWidget(nitratebasetypelabel, 4, 0)
            self.nitrate_tab.layout.addWidget(self.nitratebasetype, 4, 1)
            self.nitrate_tab.layout.addWidget(self.nitratecarryover, 5, 0)
            self.nitrate_tab.layout.addWidget(nitratecaltypelabel, 6, 0)
            self.nitrate_tab.layout.addWidget(self.nitratecaltype, 6, 1)
            self.nitrate_tab.layout.addWidget(nitratecalerrorlabel, 7, 0)
            self.nitrate_tab.layout.addWidget(self.nitratecalerror, 7, 1)
            self.nitrate_tab.layout.addWidget(nitrate_duplicate_label, 8, 0)
            self.nitrate_tab.layout.addWidget(self.nitrate_duplicate_error, 8, 1)

            self.nitrate_tab.setLayout(self.nitrate_tab.layout)

            """
             ************************ Phosphate Tab ***********************
            """

            self.phosphate_tab.layout = QGridLayout()

            phosphatenamelabel = QLabel('Name:', self)
            self.phosphatename = QLineEdit(self)
            phosphatewindowsizelabel = QLabel('Window Size: ', self)
            self.phosphatewindowsize = QLineEdit(self)
            phosphatewindowstartlabel = QLabel('Window Start: ', self)
            self.phosphatewindowstart = QLineEdit(self)
            phosphatedrifttypelabel = QLabel('Drift Correction Type: ', self)
            self.phosphatedrifttype = QComboBox(self)
            self.phosphatedrifttype.addItems(('Piecewise', 'Linear'))
            phosphatebasetypelabel = QLabel('Baseline Correction Type: ', self)
            self.phosphatebasetype = QComboBox(self)
            self.phosphatebasetype.addItems(('Piecewise', 'Linear'))
            self.phosphatecarryover = QCheckBox('Carryover Correction Enabled ', self)
            phosphatecaltypelabel = QLabel('Calibration Type: ')
            self.phosphatecaltype = QComboBox(self)
            self.phosphatecaltype.addItems(('Linear', 'Quadratic'))
            phosphatecalerrorlabel = QLabel('Calibration Error: ')
            self.phosphatecalerror = QLineEdit(self)

            phosphate_duplicate_label = QLabel('Duplicate Error: ')
            self.phosphate_duplicate_error = QLineEdit(self)

            self.phosphate_tab.layout.addWidget(phosphatenamelabel, 0, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatename, 0, 1)
            self.phosphate_tab.layout.addWidget(phosphatewindowsizelabel, 1, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatewindowsize, 1, 1)
            self.phosphate_tab.layout.addWidget(phosphatewindowstartlabel, 2, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatewindowstart, 2, 1)
            self.phosphate_tab.layout.addWidget(phosphatedrifttypelabel, 3, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatedrifttype, 3, 1)
            self.phosphate_tab.layout.addWidget(phosphatebasetypelabel, 4, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatebasetype, 4, 1)
            self.phosphate_tab.layout.addWidget(self.phosphatecarryover, 5, 0)
            self.phosphate_tab.layout.addWidget(phosphatecaltypelabel, 6, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatecaltype, 6, 1)
            self.phosphate_tab.layout.addWidget(phosphatecalerrorlabel, 7, 0)
            self.phosphate_tab.layout.addWidget(self.phosphatecalerror, 7, 1)
            self.phosphate_tab.layout.addWidget(phosphate_duplicate_label, 8, 0)
            self.phosphate_tab.layout.addWidget(self.phosphate_duplicate_error, 8, 1)

            self.phosphate_tab.setLayout(self.phosphate_tab.layout)

            """
            *************************** Silicate Tab ***************************
            """

            self.silicate_tab.layout = QGridLayout()

            silicatenamelabel = QLabel('Name:', self)
            self.silicatename = QLineEdit(self)
            silicatewindowsizelabel = QLabel('Window Size: ', self)
            self.silicatewindowsize = QLineEdit(self)
            silicatewindowstartlabel = QLabel('Window Start: ', self)
            self.silicatewindowstart = QLineEdit(self)
            silicatedrifttypelabel = QLabel('Drift Correction Type: ', self)
            self.silicatedrifttype = QComboBox(self)
            self.silicatedrifttype.addItems(('Piecewise', 'Linear'))
            silicatebasetypelabel = QLabel('Baseline Correction Type: ', self)
            self.silicatebasetype = QComboBox(self)
            self.silicatebasetype.addItems(('Piecewise', 'Linear'))
            self.silicatecarryover = QCheckBox('Carryover Correction Enabled ', self)
            silicatecaltypelabel = QLabel('Calibration Type: ')
            self.silicatecaltype = QComboBox(self)
            self.silicatecaltype.addItems(('Linear', 'Quadratic'))
            silicatecalerrorlabel = QLabel('Calibration Error: ')
            self.silicatecalerror = QLineEdit(self)
            silicate_duplicate_label = QLabel('Duplicate Error: ')
            self.silicate_duplicate_error = QLineEdit(self)

            self.silicate_tab.layout.addWidget(silicatenamelabel, 0, 0)
            self.silicate_tab.layout.addWidget(self.silicatename, 0, 1)
            self.silicate_tab.layout.addWidget(silicatewindowsizelabel, 1, 0)
            self.silicate_tab.layout.addWidget(self.silicatewindowsize, 1, 1)
            self.silicate_tab.layout.addWidget(silicatewindowstartlabel, 2, 0)
            self.silicate_tab.layout.addWidget(self.silicatewindowstart, 2, 1)
            self.silicate_tab.layout.addWidget(silicatedrifttypelabel, 3, 0)
            self.silicate_tab.layout.addWidget(self.silicatedrifttype, 3, 1)
            self.silicate_tab.layout.addWidget(silicatebasetypelabel, 4, 0)
            self.silicate_tab.layout.addWidget(self.silicatebasetype, 4, 1)
            self.silicate_tab.layout.addWidget(self.silicatecarryover, 5, 0)
            self.silicate_tab.layout.addWidget(silicatecaltypelabel, 6, 0)
            self.silicate_tab.layout.addWidget(self.silicatecaltype, 6, 1)
            self.silicate_tab.layout.addWidget(silicatecalerrorlabel, 7, 0)
            self.silicate_tab.layout.addWidget(self.silicatecalerror, 7, 1)
            self.silicate_tab.layout.addWidget(silicate_duplicate_label, 8, 0)
            self.silicate_tab.layout.addWidget(self.silicate_duplicate_error, 8, 1)

            self.silicate_tab.setLayout(self.silicate_tab.layout)

            """
            ************************ Ammonia Tab ******************************
            """

            self.ammonia_tab.layout = QGridLayout()

            ammonianamelabel = QLabel('Name:', self)
            self.ammonianame = QLineEdit(self)
            ammoniawindowsizelabel = QLabel('Window Size: ', self)
            self.ammoniawindowsize = QLineEdit(self)
            ammoniawindowstartlabel = QLabel('Window Start: ', self)
            self.ammoniawindowstart = QLineEdit(self)
            ammoniadrifttypelabel = QLabel('Drift Correction Type: ', self)
            self.ammoniadrifttype = QComboBox(self)
            self.ammoniadrifttype.addItems(('Piecewise', 'Linear'))
            ammoniabasetypelabel = QLabel('Baseline Correction Type: ', self)
            self.ammoniabasetype = QComboBox(self)
            self.ammoniabasetype.addItems(('Piecewise', 'Linear'))
            self.ammoniacarryover = QCheckBox('Carryover Correction Enabled ', self)
            ammoniacaltypelabel = QLabel('Calibration Type: ')
            self.ammoniacaltype = QComboBox(self)
            self.ammoniacaltype.addItems(('Linear', 'Quadratic'))
            ammoniacalerrorlabel = QLabel('Calibration Error: ')
            self.ammoniacalerror = QLineEdit(self)
            ammonia_duplicate_label = QLabel('Duplicate Error: ')
            self.ammonia_duplicate_error = QLineEdit(self)

            self.ammonia_tab.layout.addWidget(ammonianamelabel, 0, 0)
            self.ammonia_tab.layout.addWidget(self.ammonianame, 0, 1)
            self.ammonia_tab.layout.addWidget(ammoniawindowsizelabel, 1, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniawindowsize, 1, 1)
            self.ammonia_tab.layout.addWidget(ammoniawindowstartlabel, 2, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniawindowstart, 2, 1)
            self.ammonia_tab.layout.addWidget(ammoniadrifttypelabel, 3, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniadrifttype, 3, 1)
            self.ammonia_tab.layout.addWidget(ammoniabasetypelabel, 4, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniabasetype, 4, 1)
            self.ammonia_tab.layout.addWidget(self.ammoniacarryover, 5, 0)
            self.ammonia_tab.layout.addWidget(ammoniacaltypelabel, 6, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniacaltype, 6, 1)
            self.ammonia_tab.layout.addWidget(ammoniacalerrorlabel, 7, 0)
            self.ammonia_tab.layout.addWidget(self.ammoniacalerror, 7, 1)
            self.ammonia_tab.layout.addWidget(ammonia_duplicate_label, 8, 0)
            self.ammonia_tab.layout.addWidget(self.ammonia_duplicate_error, 8, 1)

            self.ammonia_tab.setLayout(self.ammonia_tab.layout)

            """
            ******************* Nitrite Tab ******************************
            """

            self.nitrite_tab.layout = QGridLayout()

            nitritenamelabel = QLabel('Name:', self)
            self.nitritename = QLineEdit(self)
            nitritewindowsizelabel = QLabel('Window Size: ', self)
            self.nitritewindowsize = QLineEdit(self)
            nitritewindowstartlabel = QLabel('Window Start: ', self)
            self.nitritewindowstart = QLineEdit(self)
            nitritedrifttypelabel = QLabel('Drift Correction Type: ', self)
            self.nitritedrifttype = QComboBox(self)
            self.nitritedrifttype.addItems(('Piecewise', 'Linear'))
            nitritebasetypelabel = QLabel('Baseline Correction Type: ', self)
            self.nitritebasetype = QComboBox(self)
            self.nitritebasetype.addItems(('Piecewise', 'Linear'))
            self.nitritecarryover = QCheckBox('Carryover Correction Enabled ', self)
            nitritecaltypelabel = QLabel('Calibration Type: ')
            self.nitritecaltype = QComboBox(self)
            self.nitritecaltype.addItems(('Linear', 'Quadratic'))
            nitritecalerrorlabel = QLabel('Calibration Error: ')
            self.nitritecalerror = QLineEdit(self)
            nitrite_duplicate_label = QLabel('Duplicate Error: ')
            self.nitrite_duplicate_error = QLineEdit(self)

            self.nitrite_tab.layout.addWidget(nitritenamelabel, 0, 0)
            self.nitrite_tab.layout.addWidget(self.nitritename, 0, 1)
            self.nitrite_tab.layout.addWidget(nitritewindowsizelabel, 1, 0)
            self.nitrite_tab.layout.addWidget(self.nitritewindowsize, 1, 1)
            self.nitrite_tab.layout.addWidget(nitritewindowstartlabel, 2, 0)
            self.nitrite_tab.layout.addWidget(self.nitritewindowstart, 2, 1)
            self.nitrite_tab.layout.addWidget(nitritedrifttypelabel, 3, 0)
            self.nitrite_tab.layout.addWidget(self.nitritedrifttype, 3, 1)
            self.nitrite_tab.layout.addWidget(nitritebasetypelabel, 4, 0)
            self.nitrite_tab.layout.addWidget(self.nitritebasetype, 4, 1)
            self.nitrite_tab.layout.addWidget(self.nitritecarryover, 5, 0)
            self.nitrite_tab.layout.addWidget(nitritecaltypelabel, 6, 0)
            self.nitrite_tab.layout.addWidget(self.nitritecaltype, 6, 1)
            self.nitrite_tab.layout.addWidget(nitritecalerrorlabel, 7, 0)
            self.nitrite_tab.layout.addWidget(self.nitritecalerror, 7, 1)
            self.nitrite_tab.layout.addWidget(nitrite_duplicate_label, 8, 0)
            self.nitrite_tab.layout.addWidget(self.nitrite_duplicate_error, 8, 1)

            self.nitrite_tab.setLayout(self.nitrite_tab.layout)

            self.populatefields()

        except Exception as e:
            print(e)

    def populatefields(self):
        with open(self.currpath + '/' + '%sParams.json' % self.current_project, 'r') as file:
            params = json.loads(file.read())

        self.sample_id.setText(params['nutrient_processing']['slk_col_names']['sample_id'])
        self.cup_number.setText(params['nutrient_processing']['slk_col_names']['cup_numbers'])
        self.cup_type.setText(params['nutrient_processing']['slk_col_names']['cup_types'])
        self.date_time.setText(params['nutrient_processing']['slk_col_names']['date_time'])

        self.primer.setText(params['nutrient_processing']['cup_names']['primer'])
        self.recovery.setText(params['nutrient_processing']['cup_names']['recovery'])
        self.drift.setText(params['nutrient_processing']['cup_names']['drift'])
        self.baseline.setText(params['nutrient_processing']['cup_names']['baseline'])
        self.calibrant.setText(params['nutrient_processing']['cup_names']['calibrant'])
        self.high.setText(params['nutrient_processing']['cup_names']['high'])
        self.low.setText(params['nutrient_processing']['cup_names']['low'])
        self.null.setText(params['nutrient_processing']['cup_names']['null'])
        self.end.setText(params['nutrient_processing']['cup_names']['end'])
        self.sample.setText(params['nutrient_processing']['cup_names']['sample'])

        self.drift_check.setText(params['nutrient_processing']['qc_sample_names']['driftcheck'])
        self.rmns.setText(params['nutrient_processing']['qc_sample_names']['rmns'])
        self.mdl.setText(params['nutrient_processing']['qc_sample_names']['mdl'])
        self.bqc.setText(params['nutrient_processing']['qc_sample_names']['bqc'])
        self.int_qc.setText(params['nutrient_processing']['qc_sample_names']['internalqc'])
        self.uwy.setText(params['nutrient_processing']['qc_sample_names']['underway'])

        self.nitratename.setText(params['nutrient_processing']['element_names']['nitrate_name'])

        nitrate_params = params['nutrient_processing']['processing_pars']['nitrate']

        self.nitratewindowsize.setText(str(nitrate_params['window_size']))
        self.nitratewindowstart.setText(str(nitrate_params['window_start']))
        self.nitratedrifttype.setCurrentText(nitrate_params['drift_corr_type'])
        self.nitratebasetype.setCurrentText(nitrate_params['base_corr_type'])
        self.nitratecarryover.setChecked(nitrate_params['carryover_corr'])
        self.nitratecaltype.setCurrentText(nitrate_params['calibration'])
        self.nitratecalerror.setText(str(nitrate_params['cal_error']))
        self.nitrate_duplicate_error.setText(str(nitrate_params['duplicate_error']))

        phosphate_params = params['nutrient_processing']['processing_pars']['phosphate']

        self.phosphatename.setText(params['nutrient_processing']['element_names']['phosphate_name'])
        self.phosphatewindowsize.setText(str(phosphate_params['window_size']))
        self.phosphatewindowstart.setText(str(phosphate_params['window_start']))
        self.phosphatedrifttype.setCurrentText(phosphate_params['drift_corr_type'])
        self.phosphatebasetype.setCurrentText(phosphate_params['base_corr_type'])
        self.phosphatecarryover.setChecked(phosphate_params['carryover_corr'])
        self.phosphatecaltype.setCurrentText(phosphate_params['calibration'])
        self.phosphatecalerror.setText(str(phosphate_params['cal_error']))
        self.phosphate_duplicate_error.setText(str(phosphate_params['duplicate_error']))

        silicate_params = params['nutrient_processing']['processing_pars']['silicate']

        self.silicatename.setText(params['nutrient_processing']['element_names']['silicate_name'])
        self.silicatewindowsize.setText(str(silicate_params['window_size']))
        self.silicatewindowstart.setText(str(silicate_params['window_start']))
        self.silicatedrifttype.setCurrentText(silicate_params['drift_corr_type'])
        self.silicatebasetype.setCurrentText(silicate_params['base_corr_type'])
        self.silicatecarryover.setChecked(silicate_params['carryover_corr'])
        self.silicatecaltype.setCurrentText(silicate_params['calibration'])
        self.silicatecalerror.setText(str(silicate_params['cal_error']))
        self.silicate_duplicate_error.setText(str(silicate_params['duplicate_error']))

        nitrite_params = params['nutrient_processing']['processing_pars']['nitrite']

        self.nitritename.setText(params['nutrient_processing']['element_names']['nitrite_name'])
        self.nitritewindowsize.setText(str(nitrite_params['window_size']))
        self.nitritewindowstart.setText(str(nitrite_params['window_start']))
        self.nitritedrifttype.setCurrentText(nitrite_params['drift_corr_type'])
        self.nitritebasetype.setCurrentText(nitrite_params['base_corr_type'])
        self.nitritecarryover.setChecked(nitrite_params['carryover_corr'])
        self.nitritecaltype.setCurrentText(nitrite_params['calibration'])
        self.nitritecalerror.setText(str(nitrite_params['cal_error']))
        self.nitrite_duplicate_error.setText(str(nitrite_params['duplicate_error']))

        ammonia_params = params['nutrient_processing']['processing_pars']['ammonia']

        self.ammonianame.setText(params['nutrient_processing']['element_names']['ammonia_name'])
        self.ammoniawindowsize.setText(str(ammonia_params['window_size']))
        self.ammoniawindowstart.setText(str(ammonia_params['window_start']))
        self.ammoniadrifttype.setCurrentText(ammonia_params['drift_corr_type'])
        self.ammoniabasetype.setCurrentText(ammonia_params['base_corr_type'])
        self.ammoniacarryover.setChecked(ammonia_params['carryover_corr'])
        self.ammoniacaltype.setCurrentText(ammonia_params['calibration'])
        self.ammoniacalerror.setText(str(ammonia_params['cal_error']))
        self.ammonia_duplicate_error.setText(str(ammonia_params['duplicate_error']))

    def resizewindow(self):
        self.setGeometry(0, 0, 475, 600)

    def save_function(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.current_project, 'r') as file:
                params = json.loads(file.read())
            # TODO Fix this so it changes the save query based on tabs open

            params['nutrient_processing']['slk_col_names']['sample_id'] = self.sample_id.text()
            params['nutrient_processing']['slk_col_names']['cup_numbers'] = self.cup_number.text()
            params['nutrient_processing']['slk_col_names']['cup_types'] = self.cup_type.text()
            params['nutrient_processing']['slk_col_names']['date_time'] = self.date_time.text()

            params['nutrient_processing']['cup_names']['primer'] = self.primer.text()
            params['nutrient_processing']['cup_names']['recovery'] = self.recovery.text()
            params['nutrient_processing']['cup_names']['drift'] = self.drift.text()
            params['nutrient_processing']['cup_names']['baseline'] = self.baseline.text()
            params['nutrient_processing']['cup_names']['calibrant'] = self.calibrant.text()
            params['nutrient_processing']['cup_names']['high'] = self.high.text()
            params['nutrient_processing']['cup_names']['low'] = self.low.text()
            params['nutrient_processing']['cup_names']['null'] = self.null.text()
            params['nutrient_processing']['cup_names']['end'] = self.end.text()
            params['nutrient_processing']['cup_names']['sample'] = self.sample.text()

            params['nutrient_processing']['qc_sample_names']['rmns'] = self.rmns.text()
            params['nutrient_processing']['qc_sample_names']['mdl'] = self.mdl.text()
            params['nutrient_processing']['qc_sample_names']['bqc'] = self.bqc.text()
            params['nutrient_processing']['qc_sample_names']['internalqc'] = self.int_qc.text()
            params['nutrient_processing']['qc_sample_names']['underway'] = self.uwy.text()

            params['nutrient_processing']['element_names']['nitrate_name'] = self.nitratename.text()
            params['nutrient_processing']['processing_pars']['nitrate']['window_size'] = self.nitratewindowsize.text()
            params['nutrient_processing']['processing_pars']['nitrate']['window_start'] = self.nitratewindowstart.text()
            params['nutrient_processing']['processing_pars']['nitrate']['drift_corr_type'] = self.nitratedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['base_corr_type'] = self.nitratebasetype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['carryover_corr'] = self.nitratecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['nitrate']['calibration'] = self.nitratecaltype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['cal_error'] = self.nitratecalerror.text()
            params['nutrient_processing']['processing_pars']['nitrate']['duplicate_error'] = self.nitrate_duplicate_error.text()

            params['nutrient_processing']['element_names']['phosphate_name'] = self.phosphatename.text()
            params['nutrient_processing']['processing_pars']['phosphate']['window_size'] = self.phosphatewindowsize.text()
            params['nutrient_processing']['processing_pars']['phosphate']['window_start'] = self.phosphatewindowstart.text()
            params['nutrient_processing']['processing_pars']['phosphate']['drift_corr_type'] = self.phosphatedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['base_corr_type'] = self.phosphatebasetype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['carryover_corr'] = self.phosphatecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['phosphate']['calibration'] = self.phosphatecaltype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['cal_error'] = self.phosphatecalerror.text()
            params['nutrient_processing']['processing_pars']['phosphate']['duplicate_error'] = self.phosphate_duplicate_error.text()

            params['nutrient_processing']['element_names']['silicate_name'] = self.silicatename.text()
            params['nutrient_processing']['processing_pars']['silicate']['window_size'] = self.silicatewindowsize.text()
            params['nutrient_processing']['processing_pars']['silicate']['window_start'] = self.silicatewindowstart.text()
            params['nutrient_processing']['processing_pars']['silicate']['drift_corr_type'] = self.silicatedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['base_corr_type'] = self.silicatebasetype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['carryover_corr'] = self.silicatecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['silicate']['calibration'] = self.silicatecaltype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['cal_error'] = self.silicatecalerror.text()
            params['nutrient_processing']['processing_pars']['silicate']['duplicate_error'] = self.silicate_duplicate_error.text()

            params['nutrient_processing']['element_names']['nitrite_name'] = self.nitritename.text()
            params['nutrient_processing']['processing_pars']['nitrite']['window_size'] = self.nitritewindowsize.text()
            params['nutrient_processing']['processing_pars']['nitrite']['window_start'] = self.nitritewindowstart.text()
            params['nutrient_processing']['processing_pars']['nitrite']['drift_corr_type'] = self.nitritedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['base_corr_type'] = self.nitritebasetype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['carryover_corr'] = self.nitritecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['nitrite']['calibration'] = self.nitritecaltype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['cal_error'] = self.nitritecalerror.text()
            params['nutrient_processing']['processing_pars']['nitrite']['duplicate_error'] = self.nitrite_duplicate_error.text()

            params['nutrient_processing']['element_names']['ammonia_name'] = self.ammonianame.text()
            params['nutrient_processing']['processing_pars']['ammonia']['window_size'] = self.ammoniawindowsize.text()
            params['nutrient_processing']['processing_pars']['ammonia']['window_start'] = self.ammoniawindowstart.text()
            params['nutrient_processing']['processing_pars']['ammonia']['drift_corr_type'] = self.ammoniadrifttype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['base_corr_type'] = self.ammoniabasetype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['carryover_corr'] = self.ammoniacarryover.isChecked()
            params['nutrient_processing']['processing_pars']['ammonia']['calibration'] = self.ammoniacaltype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['cal_error'] = self.ammoniacalerror.text()
            params['nutrient_processing']['processing_pars']['ammonia']['duplicate_error'] = self.nitrite_duplicate_error.text()

            with open(self.currpath + '/' + '%sParams.json' % self.current_project, 'w') as file:
                json.dump(params, file)

            message = hyproMessageBoxTemplate(
                'Success',
                'Project parameters saved',
                'success'
            )

            time.sleep(0.3)
            self.close()

        except Exception as e:
            logging.error(e)

    def cancel_function(self):
        self.close()
