from PyQt5.QtWidgets import (QPushButton, QLabel, QTableWidget, QTableWidgetItem)
import sqlite3
from time import sleep
from dialogs.AddRMNSDialog import addrmnsDialog
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# Shows a table of the current RMNS in the database, need to finish to incorporate a import function
class rmnsDialog(hyproDialogTemplate):
    def __init__(self):
        super().__init__(780, 320, 'HyPro - View RMNS')

        self.db = 'C:/HyPro/Settings/hypro.db'

        self.adding = addrmnsDialog(self.db)

        try:
            self.adding.rmnsaddedtodb.connect(self.populatetable)
        except Exception as e:
            print(e)

        self.init_ui()

        self.populatetable()

        self.show()

    def init_ui(self):
        rmnsHeader = QLabel('Current RMNS in HyPro:', self)

        self.rmnsTable = QTableWidget()

        rmnsImport = QPushButton('Import RMNS', self)
        rmnsImport.clicked.connect(self.importrmns)

        rmnsAdd = QPushButton('Add RMNS', self)
        rmnsAdd.clicked.connect(self.addrmns)

        saveEdit = QPushButton('Save', self)
        saveEdit.clicked.connect(self.saveedit)

        close = QPushButton('Close', self)
        close.clicked.connect(self.close)

        self.grid_layout.addWidget(rmnsHeader, 0, 0)
        self.grid_layout.addWidget(self.rmnsTable, 1, 0, 1, 4)
        self.grid_layout.addWidget(rmnsImport, 2, 0)
        self.grid_layout.addWidget(rmnsAdd, 2, 1)
        self.grid_layout.addWidget(saveEdit, 2, 2)
        self.grid_layout.addWidget(close, 2, 3)


    def populatetable(self):
        print('refresh')
        try:
            conn = sqlite3.connect('C:/HyPro/Settings/hypro.db')
            c = conn.cursor()
            c.execute('SELECT * from rmnsData')
            rmnsdata = list(c.fetchall())
            conn.close()
            if rmnsdata:
                self.rmnsTable.setRowCount(len(rmnsdata))
                self.rmnsTable.setColumnCount(len(rmnsdata[0]))

                for row, x in enumerate(rmnsdata):
                    for col, item in enumerate(x):
                        self.rmnsTable.setItem(row, col, QTableWidgetItem(str(item)))

                headers = ['Lot', 'Phosphate', 'Phosphate U', 'Silicate', 'Silicate U', 'Nitrate', 'Nitrate U',
                           'Nitrite', 'Nitrite U', 'Ammonia', 'Ammonia U']
                self.rmnsTable.setHorizontalHeaderLabels(headers)
                self.rmnsTable.resizeColumnsToContents()

        except Exception as e:
            print(e)

    def closewindow(self):
        sleep(0.2)
        self.close()

    def importrmns(self):
        print('TODO: Import RMNS')
        # TODO: Import RMNS function

    def addrmns(self):
        self.adding.show()

    def saveedit(self):
        print('TODO: Saving')
