from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox)
from PyQt5.QtCore import *
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# Provides functionality for clicking in QC plots after the nutrient processing stage, ie after the fact manually
# produced plots


class plotSelection(hyproDialogTemplate):
    setStart = pyqtSignal()
    setEnd = pyqtSignal()
    saveSig = pyqtSignal()

    def __init__(self, sampleid, cuptype, admedian, conc, flag, dil):
        super().__init__(450, 240, 'Hypro - Peak')

        self.sampleid = sampleid
        self.cuptype = cuptype
        self.admedian = admedian
        self.conc = conc
        self.flag = flag
        self.dil = dil

        self.init_ui()

        self.show()


    def init_ui(self):
        peakselectedlabel = QLabel('Peak Selected: ')

        self.peakselected = QLineEdit(self)
        self.peakselected.setText(self.sampleid)
        self.peakselected.setReadOnly(True)

        peakcuptype = QLabel('Cup Type: ')

        self.peakcupline = QLineEdit(self)
        self.peakcupline.setText(self.cuptype)
        self.peakcupline.setReadOnly(True)

        admedianlabel = QLabel('A/D Median: ')

        self.admedianline = QLineEdit(self)
        self.admedianline.setText(str(round(self.admedian, 2)))
        self.admedianline.setReadOnly(True)

        concentrationlabel = QLabel('Concentration (uM): ')

        self.concentration = QLineEdit(self)
        self.concentration.setText(str(round(self.conc, 4)))
        self.concentration.setReadOnly(True)

        flaglabel = QLabel('Quality Flag: ')

        self.flagbox = QComboBox(self)
        self.flagbox.addItems(('Good', 'Suspect', 'Bad'))

        if self.flag == 1:
            self.flagbox.setCurrentText('Good')
        if self.flag == 2:
            self.flagbox.setCurrentText('Suspect')
        if self.flag == 3:
            self.flagbox.setCurrentText('Bad')

        dilutionlabel = QLabel('Dilution Factor: ')

        self.dilutionline = QLineEdit(self)
        self.dilutionline.setText(str(self.dil))
        self.dilutionline.setDisabled(True)

        self.okbut = QPushButton('Ok', self)
        self.okbut.clicked.connect(self.save)

        self.cancelbut = QPushButton('Cancel', self)
        self.cancelbut.clicked.connect(self.cancel)

        self.grid_layout.addWidget(peakselectedlabel, 0, 0)
        self.grid_layout.addWidget(self.peakselected, 0, 1)
        self.grid_layout.addWidget(peakcuptype, 0, 2)
        self.grid_layout.addWidget(self.peakcupline, 0, 3)

        self.grid_layout.addWidget(admedianlabel, 1, 0)
        self.grid_layout.addWidget(self.admedianline, 1, 1)
        self.grid_layout.addWidget(concentrationlabel, 1, 2)
        self.grid_layout.addWidget(self.concentration, 1, 3)

        self.grid_layout.addWidget(dilutionlabel, 2, 0)
        self.grid_layout.addWidget(self.dilutionline, 2, 1)
        self.grid_layout.addWidget(flaglabel, 2, 2)
        self.grid_layout.addWidget(self.flagbox, 2, 3)

        self.grid_layout.addWidget(self.okbut, 3, 1)
        self.grid_layout.addWidget(self.cancelbut, 3, 2)

    def save(self):
        self.saveSig.emit()
        self.close()

    def cancel(self):
        self.close()

