import logging
import sqlite3
import traceback
from time import sleep

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QMessageBox, QFrame)

from dialogs.templates.DialogTemplate import hyproDialogTemplate

"""
Produces the dialog allowing the entry of RMNS data into the computer wide db living under C:/HyPro

"""


class addrmnsDialog(hyproDialogTemplate):
    rmnsaddedtodb = pyqtSignal()

    def __init__(self, database):
        super().__init__(250, 580, 'HyPro - Add RMNS')

        self.db = database

        self.init_ui()

    def init_ui(self):
        # Add labels and edit fields to window
        rmnsheader = QLabel('Add a RMNS lot to HyPro:', self)

        rmnslot = QLabel('Lot:', self)
        self.rmnslotedit = QLineEdit()
        self.rmnslotedit.setFixedWidth(85)

        self.validator = QDoubleValidator()

        genlinesep1 = QFrame(self)
        genlinesep1.setFrameShape(QFrame.HLine)
        genlinesep1.setFrameShadow(QFrame.Sunken)

        noxlabel = QLabel('[NOx]:')
        self.noxconc = QLineEdit()
        self.noxconc.setFixedWidth(85)
        self.noxconc.setValidator(self.validator)

        noxulabel = QLabel('NOx U:')
        self.noxuconc = QLineEdit()
        self.noxuconc.setFixedWidth(85)
        self.noxuconc.setValidator(self.validator)

        phosphatelabel = QLabel('[Phosphate]:')
        self.phosphateconc = QLineEdit()
        self.phosphateconc.setFixedWidth(85)
        self.phosphateconc.setValidator(self.validator)

        phosphateulabel = QLabel('Phosphate U:')
        self.phosphateuconc = QLineEdit()
        self.phosphateuconc.setFixedWidth(85)
        self.phosphateuconc.setValidator(self.validator)

        silicatelabel = QLabel('[Silicate]:')
        self.silicateconc = QLineEdit()
        self.silicateconc.setFixedWidth(85)
        self.silicateconc.setValidator(self.validator)

        silicateulabel = QLabel('Silicate U:')
        self.silicateuconc = QLineEdit()
        self.silicateuconc.setFixedWidth(85)
        self.silicateuconc.setValidator(self.validator)

        nitritelabel = QLabel('[Nitrite]:')
        self.nitriteconc = QLineEdit()
        self.nitriteconc.setFixedWidth(85)
        self.nitriteconc.setValidator(self.validator)

        nitriteulabel = QLabel('Nitrite U:')
        self.nitriteuconc = QLineEdit()
        self.nitriteuconc.setFixedWidth(85)
        self.nitriteuconc.setValidator(self.validator)

        ammonialabel = QLabel('[Ammonia]:')
        self.ammoniaconc = QLineEdit()
        self.ammoniaconc.setFixedWidth(85)
        self.ammoniaconc.setValidator(self.validator)

        ammoniaulabel = QLabel('Ammonia U:')
        self.ammoniauconc = QLineEdit()
        self.ammoniauconc.setFixedWidth(85)
        self.ammoniauconc.setValidator(self.validator)

        genlinesep2 = QFrame(self)
        genlinesep2.setFrameShape(QFrame.HLine)
        genlinesep2.setFrameShadow(QFrame.Sunken)

        self.rmnsAdd = QPushButton('Add RMNS', self)
        self.rmnsAdd.clicked.connect(self.addrmns)

        close = QPushButton('Close', self)
        close.clicked.connect(self.close)

        self.grid_layout.addWidget(rmnsheader, 0, 0, 1, 2)

        self.grid_layout.addWidget(rmnslot, 1, 0, 1, 2)
        self.grid_layout.addWidget(self.rmnslotedit, 1, 1)

        self.grid_layout.addWidget(genlinesep1, 2, 0, 1, 2, Qt.AlignVCenter)

        self.grid_layout.addWidget(noxlabel, 3, 0)
        self.grid_layout.addWidget(noxulabel, 3, 1)
        self.grid_layout.addWidget(self.noxconc, 4, 0)
        self.grid_layout.addWidget(self.noxuconc, 4, 1)

        self.grid_layout.addWidget(nitritelabel, 5, 0)
        self.grid_layout.addWidget(nitriteulabel, 5, 1)
        self.grid_layout.addWidget(self.nitriteconc, 6, 0)
        self.grid_layout.addWidget(self.nitriteuconc, 6, 1)

        self.grid_layout.addWidget(phosphatelabel, 7, 0)
        self.grid_layout.addWidget(phosphateulabel, 7, 1)
        self.grid_layout.addWidget(self.phosphateconc, 8, 0)
        self.grid_layout.addWidget(self.phosphateuconc, 8, 1)

        self.grid_layout.addWidget(silicatelabel, 9, 0)
        self.grid_layout.addWidget(silicateulabel, 9, 1)
        self.grid_layout.addWidget(self.silicateconc, 10, 0)
        self.grid_layout.addWidget(self.silicateuconc, 10, 1)

        self.grid_layout.addWidget(ammonialabel, 11, 0)
        self.grid_layout.addWidget(ammoniaulabel, 11, 1)
        self.grid_layout.addWidget(self.ammoniaconc, 12, 0)
        self.grid_layout.addWidget(self.ammoniauconc, 12, 1)

        self.grid_layout.addWidget(genlinesep2, 13, 0, 1, 2, Qt.AlignVCenter)

        self.grid_layout.addWidget(self.rmnsAdd, 14, 0)
        self.grid_layout.addWidget(close, 14, 1)

    def addrmns(self):
        # Add rmns to database, got to confirm that it makes sense though
        if self.rmnslotedit.text() == '' or self.rmnslotedit.text().isspace():

            messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Error...',
                                     ('Please add a RMNS Lot, otherwise how will I know what these numbers are...'),
                                     buttons=QtWidgets.QMessageBox.Ok, parent=self)
            messagebox.setIconPixmap(QPixmap(':/assets/exclamation.svg'))
            messagebox.setFont(QFont('Segoe UI'))
            messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 20px; }')
            messagebox.exec_()
        else:
            if self.validator.Acceptable:
                try:
                    lot = self.rmnslotedit.text()
                    nox = self.noxconc.text()
                    noxu = self.noxuconc.text()
                    nit = self.nitriteconc.text()
                    nitu = self.nitriteuconc.text()
                    phos = self.phosphateconc.text()
                    phosu = self.phosphateuconc.text()
                    sil = self.silicateconc.text()
                    silu = self.silicateuconc.text()
                    amm = self.ammoniaconc.text()
                    ammu = self.ammoniauconc.text()

                    # Pack up the data for putting into the db
                    rmnsdata = tuple((lot, phos, phosu, sil, silu, nox, noxu, nit, nitu, amm, ammu))

                    conn = sqlite3.connect(self.db)
                    c = conn.cursor()
                    c.execute('INSERT OR REPLACE INTO rmnsData VALUES(?,?,?,?,?,?,?,?,?,?,?)', rmnsdata)
                    conn.commit()
                    conn.close()

                    messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Success',
                                             ('RMNS Lot: ' + self.rmnslotedit.text() + ' successfully added to HyPro'),
                                             buttons=QtWidgets.QMessageBox.Ok, parent=self)
                    messagebox.setIconPixmap(QPixmap(':/assets/success.svg'))
                    messagebox.setFont(QFont('Segoe UI'))
                    messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 20px; }')
                    messagebox.exec_()

                    sleep(0.3)
                    self.close()

                    self.rmnsaddedtodb.emit()

                except Exception as e:
                    logging.error(traceback.print_exc())


            else:
                messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Error...',
                                         ('Please put in a concentration for each nutrient... '),
                                         buttons=QtWidgets.QMessageBox.Ok, parent=self)
                messagebox.setIconPixmap(QPixmap(':/assets/exclamation.svg'))
                messagebox.setFont(QFont('Segoe UI'))
                messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
                messagebox.exec_()

    def closewindow(self):
        sleep(0.3)
        self.close()
