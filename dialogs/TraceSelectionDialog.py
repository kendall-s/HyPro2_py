from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox)
from PyQt5.QtCore import *
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# Small GUI dialog that provides information and functionality when a peak is clicked on the trace of
# nutrient processing
class traceSelection(hyproDialogTemplate):
    setStart = pyqtSignal()
    setEnd = pyqtSignal()
    saveSig = pyqtSignal()
    peakShiftRight = pyqtSignal()
    peakShiftLeft = pyqtSignal()

    def __init__(self, sampleid, cuptype, peaknumber, admedian, conc, flag, dil, type):
        super().__init__(550, 245, 'HyPro - Peak:')

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

        if self.flag == 1:
            self.flagbox.setCurrentText('Good')
        if self.flag == 2:
            self.flagbox.setCurrentText('Suspect')
        if self.flag == 3:
            self.flagbox.setCurrentText('Bad')

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

            self.shiftpeakleft.hide()
            self.shiftpeakright.hide()

            self.grid_layout.addWidget(self.okbut, 3, 1)
            self.gridl_ayout.addWidget(self.cancelbut, 3, 2)

        self.show()

    def save(self):
        self.saveSig.emit()
        self.close()

    def cancel(self):
        self.close()

    def peakshiftright(self):
        self.peakShiftRight.emit()
        self.close()

    def peakshiftleft(self):
        self.peakShiftLeft.emit()
        self.close()

    def pickstart(self):
        self.setStart.emit()
        self.close()

    def pickend(self):
        self.setEnd.emit()
        self.close()

