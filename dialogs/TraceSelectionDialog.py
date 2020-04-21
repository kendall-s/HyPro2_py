from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox)
from PyQt5.QtCore import *
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# Small GUI dialog that provides information and functionality when a peak is clicked on the trace of
# nutrient processing
"""
Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad, 
                91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different
"""


class traceSelection(hyproDialogTemplate):
    setStart = pyqtSignal()
    setEnd = pyqtSignal()
    saveSig = pyqtSignal()
    peakShiftRight = pyqtSignal()
    peakShiftLeft = pyqtSignal()

    def __init__(self, sampleid, cuptype, peaknumber, admedian, conc, flag, dil, type):
        super().__init__(550, 245, 'HyPro - Peak:')

        self.flag_converter = {1 : 'Good', 2 : 'Suspect', 3 : 'Bad', 4 : 'Shape Sus', 5 : 'Shape Bad', 6: 'Cal Bad',
                               91 : 'CalError Sus', 92 : 'CalError Bad', 8 : 'Dup Diff'}


        self.sampleid = sampleid
        self.cuptype = cuptype
        self.peaknum = peaknumber
        self.admedian = admedian
        self.conc = conc
        self.flag = flag
        self.dil = dil
        self.dialogtype = type

        self.init_ui()

        self.show()

    def init_ui(self):
        self.setWindowTitle('HyPro - Peak: ' + str(self.peaknum))

        peakselectedlabel = QLabel('Peak Selected: ')

        self.peakselected = QLineEdit(self)
        self.peakselected.setText(self.sampleid)
        self.peakselected.setReadOnly(True)

        peakcuptype = QLabel('Cup Type: ')

        self.peakcupline = QLineEdit(self)
        self.peakcupline.setText(self.cuptype)

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

        self.flagbox.setCurrentText(self.flag_converter[self.flag])

        dilutionlabel = QLabel('Dilution Factor: ')

        self.dilutionline = QLineEdit(self)
        self.dilutionline.setText(str(self.dil))

        self.shiftpeakright = QPushButton('Shift Right', self)
        self.shiftpeakright.clicked.connect(self.peakshiftright)

        self.shiftpeakleft = QPushButton('Shift Left', self)
        self.shiftpeakleft.clicked.connect(self.peakshiftleft)

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


        if self.dialogtype == 'Trace':
            self.setstart = QPushButton('Set Start', self)
            self.setstart.clicked.connect(self.setStart)

            self.setend = QPushButton('Set End', self)
            self.setend.clicked.connect(self.setEnd)

            self.grid_layout.addWidget(self.setstart, 3, 0)
            self.grid_layout.addWidget(self.setend, 3, 1)

            self.grid_layout.addWidget(self.shiftpeakleft, 3, 2)
            self.grid_layout.addWidget(self.shiftpeakright, 3, 3)

            self.grid_layout.addWidget(self.okbut, 4, 1)
            self.grid_layout.addWidget(self.cancelbut, 4, 2)

        else:

            self.peakcupline.setReadOnly(True)
            self.dilutionline.setReadOnly(True)

            self.shiftpeakleft.hide()
            self.shiftpeakright.hide()

            self.grid_layout.addWidget(self.okbut, 3, 1)
            self.grid_layout.addWidget(self.cancelbut, 3, 2)

        self.show()

    def save(self):
        if self.any_change:
            self.saveSig.emit()

        self.close()

    def any_change(self):
        cup = self.peakcupline.text()
        dilution = self.dilutionline.text()
        q_flag = self.flagbox.currentText()

        if cup != self.cuptype or dilution != self.dil or q_flag != self.flag_converter[self.flag]:
            return True

    def cancel(self):
        self.close()

    def peakshiftright(self):
        self.peakShiftRight.emit()

    def peakshiftleft(self):
        self.peakShiftLeft.emit()

    def pickstart(self):
        self.setStart.emit()
        self.close()

    def pickend(self):
        self.setEnd.emit()
        self.close()

