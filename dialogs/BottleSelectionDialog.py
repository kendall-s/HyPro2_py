from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox)

from dialogs.templates.DialogTemplate import hyproDialogTemplate

"""
Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad, 
                91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different
"""
# TODO: consolidate the flagging elsewhere
flag_converter = {1: 'Good', 2: 'Suspect', 3: 'Bad', 4: 'Shape Sus', 5: 'Shape Bad', 6: 'Cal Bad',
                  91: 'CalError Sus', 92: 'CalError Bad', 8: 'Dup Diff'}

"""
A bottle refers to either salinity or oxygen sample, this window is used to provide info and allow a user to flag a 
bad measurement when interactively processing salinity and oxygen data 
"""


class bottleSelection(hyproDialogTemplate):
    saveSig = pyqtSignal(tuple)

    def __init__(self, file, deployment, rosette, bottle_id, concentration, flag, analyte):
        super().__init__(470, 215, 'HyPro - Bottle:')

        self.file = file
        self.deployment = deployment
        self.rosette = rosette
        self.bottle_id = bottle_id
        self.concentration = concentration
        self.flag = flag

        self.analyte = analyte

        self.init_ui()

        self.show()

    def init_ui(self):
        self.setWindowTitle('HyPro - Bottle: ' + str(self.bottle_id))

        bottle_selected_label = QLabel('Bottle ID Selected:')
        self.bottle_id_line = QLineEdit(str(self.bottle_id))
        self.bottle_id_line.setReadOnly(True)

        concentration_label = QLabel('Concentration:')
        self.concentration_line = QLineEdit(str(self.concentration))
        self.concentration_line.setReadOnly(True)

        deployment_label = QLabel('Deployment:')
        self.deployment_line = QLineEdit(str(self.deployment))
        self.deployment_line.setReadOnly(True)

        rosette_label = QLabel('Rosette:')
        self.rosette_line = QLineEdit(str(self.rosette))
        self.rosette_line.setReadOnly(True)

        file_label = QLabel('From File:')
        self.file_line = QLineEdit(str(self.file))
        self.file_line.setReadOnly(True)

        flag_label = QLabel('Quality Flag:')
        self.flag_box = QComboBox()
        self.flag_box.addItems(('Good', 'Suspect', 'Bad'))
        self.flag_box.setEditable(True)
        self.flag_box.setEditable(False)
        self.flag_box.setCurrentText(flag_converter[self.flag])

        self.ok_but = QPushButton('Ok', self)
        self.ok_but.clicked.connect(self.save)

        self.cancel_but = QPushButton('Cancel', self)
        self.cancel_but.clicked.connect(self.cancel)

        self.grid_layout.addWidget(bottle_selected_label, 0, 0)
        self.grid_layout.addWidget(self.bottle_id_line, 0, 1)
        self.grid_layout.addWidget(concentration_label, 0, 2)
        self.grid_layout.addWidget(self.concentration_line, 0, 3)

        self.grid_layout.addWidget(deployment_label, 1, 0)
        self.grid_layout.addWidget(self.deployment_line, 1, 1)
        self.grid_layout.addWidget(rosette_label, 1, 2)
        self.grid_layout.addWidget(self.rosette_line, 1, 3)

        self.grid_layout.addWidget(file_label, 2, 0)
        self.grid_layout.addWidget(self.file_line, 2, 1)
        self.grid_layout.addWidget(flag_label, 2, 2)
        self.grid_layout.addWidget(self.flag_box, 2, 3)

        self.grid_layout.addWidget(self.ok_but, 3, 1)
        self.grid_layout.addWidget(self.cancel_but, 3, 2)

        self.show()

    def save(self):
        if self.any_change:
            self.saveSig.emit((self.flag_box.currentText(), self.file, self.deployment, self.rosette,
                               self.bottle_id, self.analyte))
        self.close()

    def any_change(self):
        q_flag = self.flag_box.currentText()
        if q_flag != flag_converter[self.flag]:
            return True

    def cancel(self):
        self.close()
