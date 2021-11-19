from PyQt5.QtWidgets import (QWidget, QPushButton, QLineEdit, QLabel, QMessageBox, QFrame,
                             QCheckBox, QTabWidget, QGridLayout, QComboBox)
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtGui import *
import json, time, logging
import hyproicons, style
from dialogs.templates.DialogTemplate import hyproDialogTemplate


# File that provides the GUI for editing all of the parameters used in processing, these parameters
# live in the project paramters json file

class parametersDialog(hyproDialogTemplate):
    def __init__(self, project, path):
        super().__init__(475, 800, 'HyPro Project Parameters')

        self.currproject = project
        self.currpath = path

        self.init_ui()


    def init_ui(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())

            self.tabs = QTabWidget()

            self.nutrienttab = QTabWidget()
            self.tabs.addTab(self.nutrienttab, 'Nutrients')

            self.generaltab = QWidget()
            self.nutrienttab.addTab(self.generaltab, 'General')

            self.nitratetab = QWidget()
            self.nutrienttab.addTab(self.nitratetab, 'Nitrate')

            self.phosphatetab = QWidget()
            self.nutrienttab.addTab(self.phosphatetab, 'Phosphate')

            self.silicatetab = QWidget()
            self.nutrienttab.addTab(self.silicatetab, 'Silicate')

            self.nitritetab = QWidget()
            self.nutrienttab.addTab(self.nitritetab, 'Nitrite')

            self.ammoniatab = QWidget()
            self.nutrienttab.addTab(self.ammoniatab, 'Ammonia')

            self.salinitytab = QWidget()
            self.tabs.addTab(self.salinitytab, 'Salinity')

            self.oxygentab = QWidget()
            self.tabs.addTab(self.oxygentab, 'Oxygen')

            save = QPushButton('Save', self)
            save.clicked.connect(self.savefunction)

            cancel = QPushButton('Cancel', self)
            cancel.clicked.connect(self.cancelfunction)

            self.grid_layout.addWidget(self.tabs, 1, 0, 5, 4)

            self.grid_layout.addWidget(save, 10, 1)
            self.grid_layout.addWidget(cancel, 10, 2)

            self.setLayout(self.grid_layout)


            self.generaltab.layout = QGridLayout()

            slkcolumnlabel = QLabel('<b>SLK Column Headers</b>', self)
            sampleidlabel = QLabel('Sample ID Header:', self)
            self.sampleid = QLineEdit(self)
            cupnumberlabel = QLabel('Cup Number Header:', self)
            self.cupnumber = QLineEdit(self)
            cuptypelabel = QLabel('Cup Type Header:', self)
            self.cuptype = QLineEdit(self)
            datetimelabel = QLabel('Time Stamp Header:', self)
            self.datetime = QLineEdit(self)

            genlinesep1 = QFrame(self)
            genlinesep1.setFrameShape(QFrame.HLine)
            genlinesep1.setFrameShadow(QFrame.Sunken)

            cupnameslabel = QLabel('<b>Cup Names</b>', self)
            primerlabel = QLabel('Primer:', self)
            self.primer = QLineEdit(self)
            recoverylabel = QLabel('NO3 Recovery:', self)
            self.recovery = QLineEdit(self)
            driftlabel = QLabel('Drift:', self)
            self.drift = QLineEdit(self)
            baselinelabel = QLabel('Baseline:', self)
            self.baseline = QLineEdit(self)
            calibrantlabel = QLabel('Calibrants:', self)
            self.calibrant = QLineEdit(self)
            highlabel = QLabel('High Carryover:', self)
            self.high = QLineEdit(self)
            lowlabel = QLabel('Low Carryover:', self)
            self.low = QLineEdit(self)
            nulllabel = QLabel('Null:', self)
            self.null = QLineEdit(self)
            samplelabel = QLabel('Sample:', self)
            self.sample = QLineEdit(self)
            endlabel = QLabel('End:', self)
            self.end = QLineEdit(self)

            genlinesep2 = QFrame(self)
            genlinesep2.setFrameShape(QFrame.HLine)
            genlinesep2.setFrameShadow(QFrame.Sunken)

            qcsamplelabel = QLabel('<b>QC Sample Names</b>', self)
            driftchecklabel = QLabel('Drift Check:', self)
            self.driftcheck = QLineEdit(self)
            rmnslabel = QLabel('RMNS:', self)
            self.rmns = QLineEdit(self)
            mdllabel = QLabel('MDL:', self)
            self.mdl = QLineEdit(self)
            bqclabel = QLabel('Bulk QC:', self)
            self.bqc = QLineEdit(self)
            intqclabel = QLabel('Internal QC:', self)
            self.intqc = QLineEdit(self)
            uwylabel = QLabel('Underway Sample:', self)
            self.uwy = QLineEdit(self)

            self.generaltab.layout.addWidget(slkcolumnlabel, 0, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.generaltab.layout.addWidget(sampleidlabel, 1, 0)
            self.generaltab.layout.addWidget(self.sampleid, 1, 1)
            self.generaltab.layout.addWidget(cupnumberlabel, 2, 0)
            self.generaltab.layout.addWidget(self.cupnumber, 2, 1)
            self.generaltab.layout.addWidget(cuptypelabel, 3, 0)
            self.generaltab.layout.addWidget(self.cuptype, 3, 1)
            self.generaltab.layout.addWidget(datetimelabel, 4, 0)
            self.generaltab.layout.addWidget(self.datetime, 4, 1)

            self.generaltab.layout.addWidget(genlinesep1, 5, 0, 1, 2)

            self.generaltab.layout.addWidget(cupnameslabel, 6, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.generaltab.layout.addWidget(primerlabel, 7, 0)
            self.generaltab.layout.addWidget(self.primer, 7, 1)
            self.generaltab.layout.addWidget(recoverylabel, 8, 0)
            self.generaltab.layout.addWidget(self.recovery, 8, 1)
            self.generaltab.layout.addWidget(driftlabel, 9, 0)
            self.generaltab.layout.addWidget(self.drift, 9, 1)
            self.generaltab.layout.addWidget(baselinelabel, 10, 0)
            self.generaltab.layout.addWidget(self.baseline, 10, 1)
            self.generaltab.layout.addWidget(calibrantlabel, 11, 0)
            self.generaltab.layout.addWidget(self.calibrant, 11, 1)
            self.generaltab.layout.addWidget(highlabel, 12, 0)
            self.generaltab.layout.addWidget(self.high, 12, 1)
            self.generaltab.layout.addWidget(lowlabel, 13, 0)
            self.generaltab.layout.addWidget(self.low, 13, 1)
            self.generaltab.layout.addWidget(nulllabel, 14, 0)
            self.generaltab.layout.addWidget(self.null, 14, 1)
            self.generaltab.layout.addWidget(samplelabel, 15, 0)
            self.generaltab.layout.addWidget(self.sample, 15, 1)
            self.generaltab.layout.addWidget(endlabel, 16, 0)
            self.generaltab.layout.addWidget(self.end, 16, 1)

            self.generaltab.layout.addWidget(genlinesep2, 17, 0, 1, 2)

            self.generaltab.layout.addWidget(qcsamplelabel, 18, 0, 1, 2, QtCore.Qt.AlignCenter)
            self.generaltab.layout.addWidget(driftchecklabel, 19, 0)
            self.generaltab.layout.addWidget(self.driftcheck, 19, 1)
            self.generaltab.layout.addWidget(rmnslabel, 20, 0)
            self.generaltab.layout.addWidget(self.rmns, 20, 1)
            self.generaltab.layout.addWidget(mdllabel, 21, 0)
            self.generaltab.layout.addWidget(self.mdl, 21 ,1)
            self.generaltab.layout.addWidget(bqclabel, 22, 0)
            self.generaltab.layout.addWidget(self.bqc, 22, 1)
            self.generaltab.layout.addWidget(intqclabel, 23, 0)
            self.generaltab.layout.addWidget(self.intqc, 23, 1)
            self.generaltab.layout.addWidget(uwylabel, 24, 0)
            self.generaltab.layout.addWidget(self.uwy, 24, 1)

            self.generaltab.setLayout(self.generaltab.layout)

            # ************************* Nitrate Tab *************************

            self.nitratetab.layout = QGridLayout()

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

            self.nitratetab.layout.addWidget(nitratenamelabel, 0, 0)
            self.nitratetab.layout.addWidget(self.nitratename, 0, 1)
            self.nitratetab.layout.addWidget(nitratewindowsizelabel, 1, 0)
            self.nitratetab.layout.addWidget(self.nitratewindowsize, 1, 1)
            self.nitratetab.layout.addWidget(nitratewindowstartlabel, 2, 0)
            self.nitratetab.layout.addWidget(self.nitratewindowstart, 2, 1)
            self.nitratetab.layout.addWidget(nitratedrifttypelabel, 3, 0)
            self.nitratetab.layout.addWidget(self.nitratedrifttype, 3, 1)
            self.nitratetab.layout.addWidget(nitratebasetypelabel, 4, 0)
            self.nitratetab.layout.addWidget(self.nitratebasetype, 4, 1)
            self.nitratetab.layout.addWidget(self.nitratecarryover, 5, 0)
            self.nitratetab.layout.addWidget(nitratecaltypelabel, 6, 0)
            self.nitratetab.layout.addWidget(self.nitratecaltype, 6, 1)
            self.nitratetab.layout.addWidget(nitratecalerrorlabel, 7, 0)
            self.nitratetab.layout.addWidget(self.nitratecalerror, 7, 1)

            self.nitratetab.setLayout(self.nitratetab.layout)

            # ************************ Phosphate Tab ***********************

            self.phosphatetab.layout = QGridLayout()

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

            self.phosphatetab.layout.addWidget(phosphatenamelabel, 0, 0)
            self.phosphatetab.layout.addWidget(self.phosphatename, 0, 1)
            self.phosphatetab.layout.addWidget(phosphatewindowsizelabel, 1, 0)
            self.phosphatetab.layout.addWidget(self.phosphatewindowsize, 1, 1)
            self.phosphatetab.layout.addWidget(phosphatewindowstartlabel, 2, 0)
            self.phosphatetab.layout.addWidget(self.phosphatewindowstart, 2, 1)
            self.phosphatetab.layout.addWidget(phosphatedrifttypelabel, 3, 0)
            self.phosphatetab.layout.addWidget(self.phosphatedrifttype, 3, 1)
            self.phosphatetab.layout.addWidget(phosphatebasetypelabel, 4, 0)
            self.phosphatetab.layout.addWidget(self.phosphatebasetype, 4, 1)
            self.phosphatetab.layout.addWidget(self.phosphatecarryover, 5, 0)
            self.phosphatetab.layout.addWidget(phosphatecaltypelabel, 6, 0)
            self.phosphatetab.layout.addWidget(self.phosphatecaltype, 6, 1)
            self.phosphatetab.layout.addWidget(phosphatecalerrorlabel, 7, 0)
            self.phosphatetab.layout.addWidget(self.phosphatecalerror, 7, 1)
            self.phosphatetab.setLayout(self.phosphatetab.layout)

            # *************************** Silicate Tab ***************************

            self.silicatetab.layout = QGridLayout()

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

            self.silicatetab.layout.addWidget(silicatenamelabel, 0, 0)
            self.silicatetab.layout.addWidget(self.silicatename, 0, 1)
            self.silicatetab.layout.addWidget(silicatewindowsizelabel, 1, 0)
            self.silicatetab.layout.addWidget(self.silicatewindowsize, 1, 1)
            self.silicatetab.layout.addWidget(silicatewindowstartlabel, 2, 0)
            self.silicatetab.layout.addWidget(self.silicatewindowstart, 2, 1)
            self.silicatetab.layout.addWidget(silicatedrifttypelabel, 3, 0)
            self.silicatetab.layout.addWidget(self.silicatedrifttype, 3, 1)
            self.silicatetab.layout.addWidget(silicatebasetypelabel, 4, 0)
            self.silicatetab.layout.addWidget(self.silicatebasetype, 4, 1)
            self.silicatetab.layout.addWidget(self.silicatecarryover, 5, 0)
            self.silicatetab.layout.addWidget(silicatecaltypelabel, 6, 0)
            self.silicatetab.layout.addWidget(self.silicatecaltype, 6, 1)
            self.silicatetab.layout.addWidget(silicatecalerrorlabel, 7, 0)
            self.silicatetab.layout.addWidget(self.silicatecalerror, 7, 1)
            self.silicatetab.setLayout(self.silicatetab.layout)

            # ************************ Ammonia Tab ******************************

            self.ammoniatab.layout = QGridLayout()


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

            self.ammoniatab.layout.addWidget(ammonianamelabel, 0, 0)
            self.ammoniatab.layout.addWidget(self.ammonianame, 0, 1)
            self.ammoniatab.layout.addWidget(ammoniawindowsizelabel, 1, 0)
            self.ammoniatab.layout.addWidget(self.ammoniawindowsize, 1, 1)
            self.ammoniatab.layout.addWidget(ammoniawindowstartlabel, 2, 0)
            self.ammoniatab.layout.addWidget(self.ammoniawindowstart, 2, 1)
            self.ammoniatab.layout.addWidget(ammoniadrifttypelabel, 3, 0)
            self.ammoniatab.layout.addWidget(self.ammoniadrifttype, 3, 1)
            self.ammoniatab.layout.addWidget(ammoniabasetypelabel, 4, 0)
            self.ammoniatab.layout.addWidget(self.ammoniabasetype, 4, 1)
            self.ammoniatab.layout.addWidget(self.ammoniacarryover, 5, 0)
            self.ammoniatab.layout.addWidget(ammoniacaltypelabel, 6, 0)
            self.ammoniatab.layout.addWidget(self.ammoniacaltype, 6, 1)
            self.ammoniatab.layout.addWidget(ammoniacalerrorlabel, 7, 0)
            self.ammoniatab.layout.addWidget(self.ammoniacalerror, 7, 1)
            self.ammoniatab.setLayout(self.ammoniatab.layout)

            # ******************* Nitrite Tab ******************************

            self.nitritetab.layout = QGridLayout()

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

            self.nitritetab.layout.addWidget(nitritenamelabel, 0, 0)
            self.nitritetab.layout.addWidget(self.nitritename, 0, 1)
            self.nitritetab.layout.addWidget(nitritewindowsizelabel, 1, 0)
            self.nitritetab.layout.addWidget(self.nitritewindowsize, 1, 1)
            self.nitritetab.layout.addWidget(nitritewindowstartlabel, 2, 0)
            self.nitritetab.layout.addWidget(self.nitritewindowstart, 2, 1)
            self.nitritetab.layout.addWidget(nitritedrifttypelabel, 3, 0)
            self.nitritetab.layout.addWidget(self.nitritedrifttype, 3, 1)
            self.nitritetab.layout.addWidget(nitritebasetypelabel, 4, 0)
            self.nitritetab.layout.addWidget(self.nitritebasetype, 4, 1)
            self.nitritetab.layout.addWidget(self.nitritecarryover, 5, 0)
            self.nitritetab.layout.addWidget(nitritecaltypelabel, 6, 0)
            self.nitritetab.layout.addWidget(self.nitritecaltype, 6, 1)
            self.nitritetab.layout.addWidget(nitritecalerrorlabel, 7, 0)
            self.nitritetab.layout.addWidget(self.nitritecalerror, 7, 1)
            self.nitritetab.setLayout(self.nitritetab.layout)

            self.populatefields()

        except Exception as e:
            print(e)

    def populatefields(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            params = json.loads(file.read())

        self.sampleid.setText(params['nutrient_processing']['slk_col_names']['sample_id'])
        self.cupnumber.setText(params['nutrient_processing']['slk_col_names']['cup_numbers'])
        self.cuptype.setText(params['nutrient_processing']['slk_col_names']['cup_types'])
        self.datetime.setText(params['nutrient_processing']['slk_col_names']['date_time'])

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

        self.driftcheck.setText(params['nutrient_processing']['qc_sample_names']['driftcheck'])
        self.rmns.setText(params['nutrient_processing']['qc_sample_names']['rmns'])
        self.mdl.setText(params['nutrient_processing']['qc_sample_names']['mdl'])
        self.bqc.setText(params['nutrient_processing']['qc_sample_names']['bqc'])
        self.intqc.setText(params['nutrient_processing']['qc_sample_names']['internalqc'])
        self.uwy.setText(params['nutrient_processing']['qc_sample_names']['underway'])

        self.nitratename.setText(params['nutrient_processing']['element_names']['nitrate_name'])
        self.nitratewindowsize.setText(str(params['nutrient_processing']['processing_pars']['nitrate']['window_size']))
        self.nitratewindowstart.setText(str(params['nutrient_processing']['processing_pars']['nitrate']['window_start']))
        self.nitratedrifttype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrate']['drift_corr_type'])
        self.nitratebasetype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrate']['base_corr_type'])
        self.nitratecarryover.setChecked(params['nutrient_processing']['processing_pars']['nitrate']['carryover_corr'])
        self.nitratecaltype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrate']['calibration'])
        self.nitratecalerror.setText(str(params['nutrient_processing']['processing_pars']['nitrate']['cal_error']))

        self.phosphatename.setText(params['nutrient_processing']['element_names']['phosphate_name'])
        self.phosphatewindowsize.setText(str(params['nutrient_processing']['processing_pars']['phosphate']['window_size']))
        self.phosphatewindowstart.setText(str(params['nutrient_processing']['processing_pars']['phosphate']['window_start']))
        self.phosphatedrifttype.setCurrentText(params['nutrient_processing']['processing_pars']['phosphate']['drift_corr_type'])
        self.phosphatebasetype.setCurrentText(params['nutrient_processing']['processing_pars']['phosphate']['base_corr_type'])
        self.phosphatecarryover.setChecked(params['nutrient_processing']['processing_pars']['phosphate']['carryover_corr'])
        self.phosphatecaltype.setCurrentText(params['nutrient_processing']['processing_pars']['phosphate']['calibration'])
        self.phosphatecalerror.setText(str(params['nutrient_processing']['processing_pars']['phosphate']['cal_error']))

        self.silicatename.setText(params['nutrient_processing']['element_names']['silicate_name'])
        self.silicatewindowsize.setText(str(params['nutrient_processing']['processing_pars']['silicate']['window_size']))
        self.silicatewindowstart.setText(str(params['nutrient_processing']['processing_pars']['silicate']['window_start']))
        self.silicatedrifttype.setCurrentText(params['nutrient_processing']['processing_pars']['silicate']['drift_corr_type'])
        self.silicatebasetype.setCurrentText(params['nutrient_processing']['processing_pars']['silicate']['base_corr_type'])
        self.silicatecarryover.setChecked(params['nutrient_processing']['processing_pars']['silicate']['carryover_corr'])
        self.silicatecaltype.setCurrentText(params['nutrient_processing']['processing_pars']['silicate']['calibration'])
        self.silicatecalerror.setText(str(params['nutrient_processing']['processing_pars']['silicate']['cal_error']))

        self.nitritename.setText(params['nutrient_processing']['element_names']['nitrite_name'])
        self.nitritewindowsize.setText(str(params['nutrient_processing']['processing_pars']['nitrite']['window_size']))
        self.nitritewindowstart.setText(str(params['nutrient_processing']['processing_pars']['nitrite']['window_start']))
        self.nitritedrifttype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrite']['drift_corr_type'])
        self.nitritebasetype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrite']['base_corr_type'])
        self.nitritecarryover.setChecked(params['nutrient_processing']['processing_pars']['nitrite']['carryover_corr'])
        self.nitritecaltype.setCurrentText(params['nutrient_processing']['processing_pars']['nitrite']['calibration'])
        self.nitritecalerror.setText(str(params['nutrient_processing']['processing_pars']['nitrite']['cal_error']))

        self.ammonianame.setText(params['nutrient_processing']['element_names']['ammonia_name'])
        self.ammoniawindowsize.setText(str(params['nutrient_processing']['processing_pars']['ammonia']['window_size']))
        self.ammoniawindowstart.setText(str(params['nutrient_processing']['processing_pars']['ammonia']['window_start']))
        self.ammoniadrifttype.setCurrentText(params['nutrient_processing']['processing_pars']['ammonia']['drift_corr_type'])
        self.ammoniabasetype.setCurrentText(params['nutrient_processing']['processing_pars']['ammonia']['base_corr_type'])
        self.ammoniacarryover.setChecked(params['nutrient_processing']['processing_pars']['ammonia']['carryover_corr'])
        self.ammoniacaltype.setCurrentText(params['nutrient_processing']['processing_pars']['ammonia']['calibration'])
        self.ammoniacalerror.setText(str(params['nutrient_processing']['processing_pars']['ammonia']['cal_error']))

    def resizewindow(self):
        self.setGeometry(0, 0, 475, 600)

    def savefunction(self):
        try:
            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
                params = json.loads(file.read())
            # TODO Fix this so it changes the save query based on tabs open

            params['nutrient_processing']['slk_col_names']['sample_id'] = self.sampleid.text()
            params['nutrient_processing']['slk_col_names']['cup_numbers'] = self.cupnumber.text()
            params['nutrient_processing']['slk_col_names']['cup_types'] = self.cuptype.text()
            params['nutrient_processing']['slk_col_names']['date_time'] = self.datetime.text()

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
            params['nutrient_processing']['qc_sample_names']['internalqc'] = self.intqc.text()
            params['nutrient_processing']['qc_sample_names']['underway'] = self.uwy.text()

            params['nutrient_processing']['element_names']['nitrate_name'] = self.nitratename.text()
            params['nutrient_processing']['processing_pars']['nitrate']['window_size'] = self.nitratewindowsize.text()
            params['nutrient_processing']['processing_pars']['nitrate']['window_start'] = self.nitratewindowstart.text()
            params['nutrient_processing']['processing_pars']['nitrate']['drift_corr_type'] = self.nitratedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['base_corr_type'] = self.nitratebasetype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['carryover_corr'] = self.nitratecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['nitrate']['calibration'] = self.nitratecaltype.currentText()
            params['nutrient_processing']['processing_pars']['nitrate']['cal_error'] = self.nitratecalerror.text()

            params['nutrient_processing']['element_names']['phosphate_name'] = self.phosphatename.text()
            params['nutrient_processing']['processing_pars']['phosphate']['window_size'] = self.phosphatewindowsize.text()
            params['nutrient_processing']['processing_pars']['phosphate']['window_start'] = self.phosphatewindowstart.text()
            params['nutrient_processing']['processing_pars']['phosphate']['drift_corr_type'] = self.phosphatedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['base_corr_type'] = self.phosphatebasetype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['carryover_corr'] = self.phosphatecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['phosphate']['calibration'] = self.phosphatecaltype.currentText()
            params['nutrient_processing']['processing_pars']['phosphate']['cal_error'] = self.phosphatecalerror.text()

            params['nutrient_processing']['element_names']['silicate_name'] = self.silicatename.text()
            params['nutrient_processing']['processing_pars']['silicate']['window_size'] = self.silicatewindowsize.text()
            params['nutrient_processing']['processing_pars']['silicate']['window_start'] = self.silicatewindowstart.text()
            params['nutrient_processing']['processing_pars']['silicate']['drift_corr_type'] = self.silicatedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['base_corr_type'] = self.silicatebasetype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['carryover_corr'] = self.silicatecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['silicate']['calibration'] = self.silicatecaltype.currentText()
            params['nutrient_processing']['processing_pars']['silicate']['cal_error'] = self.silicatecalerror.text()
            
            params['nutrient_processing']['element_names']['nitrite_name'] = self.nitritename.text()
            params['nutrient_processing']['processing_pars']['nitrite']['window_size'] = self.nitritewindowsize.text()
            params['nutrient_processing']['processing_pars']['nitrite']['window_start'] = self.nitritewindowstart.text()
            params['nutrient_processing']['processing_pars']['nitrite']['drift_corr_type'] = self.nitritedrifttype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['base_corr_type'] = self.nitritebasetype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['carryover_corr'] = self.nitritecarryover.isChecked()
            params['nutrient_processing']['processing_pars']['nitrite']['calibration'] = self.nitritecaltype.currentText()
            params['nutrient_processing']['processing_pars']['nitrite']['cal_error'] = self.nitritecalerror.text()

            params['nutrient_processing']['element_names']['ammonia_name'] = self.ammonianame.text()
            params['nutrient_processing']['processing_pars']['ammonia']['window_size'] = self.ammoniawindowsize.text()
            params['nutrient_processing']['processing_pars']['ammonia']['window_start'] = self.ammoniawindowstart.text()
            params['nutrient_processing']['processing_pars']['ammonia']['drift_corr_type'] = self.ammoniadrifttype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['base_corr_type'] = self.ammoniabasetype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['carryover_corr'] = self.ammoniacarryover.isChecked()
            params['nutrient_processing']['processing_pars']['ammonia']['calibration'] = self.ammoniacaltype.currentText()
            params['nutrient_processing']['processing_pars']['ammonia']['cal_error'] = self.ammoniacalerror.text()

            with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'w') as file:
                json.dump(params, file)

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                     "Project parameters saved",
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
            messagebox.exec_()
            time.sleep(0.3)
            self.close()

        except Exception as e:
            logging.error(e)

    def cancelfunction(self):
        self.close()
