from PyQt5.QtWidgets import (QPushButton, QLineEdit, QLabel, QComboBox, QTableWidgetItem, QFrame, QCheckBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
from dialogs.templates.DataTable import Datatable
from dialogs.templates.DialogTemplate import hyproDialogTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
import sqlite3
from processing.algo.HyproComplexities import load_proc_settings, save_proc_settings

# Small GUI dialog that provides information and functionality when a peak is clicked on the trace of
# nutrient processing
"""
Flagging system: 1 = Good, 2 = Suspect, 3 = Bad, 4 = Peak shape suspect, 5 = Peak shape bad, 
                91 = Calibrant error suspect, 92 = Calibrant error bad, 8 = Duplicate different
"""


class samplingLogsheet(hyproDialogTemplate):

    def __init__(self, database, path, project):
        super().__init__(560, 900, 'HyPro - Voyage Sampling Logsheet')

        self.database = database
        self.path = path
        self.project = project

        self.processing_params = load_proc_settings(path, project)

        self.init_ui()

        self.show()

    def init_ui(self):
        deployment_label = QLabel('Deployment:')
        self.deployment = QLineEdit()
        self.onlyInt = QIntValidator()
        self.deployment.setValidator(self.onlyInt)
        self.deployment.textChanged.connect(self.update_table)

        salinity_letter_label = QLabel('Salinity Letter:')
        self.salinity_letter = QLineEdit()
        self.salinity_letter.textChanged.connect(self.update_table)

        rosette_size_label = QLabel('CTD Rosette Size:')
        self.rosette_size = QComboBox()
        self.rosette_size.addItems(['24', '36'])
        rosette_default = self.processing_params['rosettedefault']

        self.rosette_size.setCurrentText(str(rosette_default))
        self.rosette_size.setEditable(True)
        self.rosette_size.setEditable(False)
        self.rosette_size.currentIndexChanged.connect(self.update_table)

        self.lock_checkbox = QCheckBox('Lock Updates')

        data = []
        for x in range(int(rosette_default)):
            data.append([x+1, '', '', '', ''])

        self.datatable = Datatable(data)
        self.datatable.setHorizontalHeaderLabels(['RP', 'Oxygen', 'Oxygen Temp', 'Salinity', 'Nutrient'])

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save)

        self.grid_layout.addWidget(deployment_label, 0, 0)
        self.grid_layout.addWidget(self.deployment, 0, 1)

        self.grid_layout.addWidget(salinity_letter_label, 0, 2)
        self.grid_layout.addWidget(self.salinity_letter, 0, 3)

        self.grid_layout.addWidget(rosette_size_label, 0, 4)
        self.grid_layout.addWidget(self.rosette_size, 0, 5)

        self.grid_layout.addWidget(self.lock_checkbox, 1, 4, 1, 2)

        self.grid_layout.addWidget(self.datatable, 2, 0, 10, 6)

        self.grid_layout.addWidget(self.save_button, 12, 0, 1, 6)

        self.show()


    def get_table_data(self):
        """
        Retrieve the current data in the table and return it
        """
        rows = self.datatable.rowCount()
        cols = self.datatable.columnCount()

        data = []
        for x in range(rows):
            temp = []
            for y in range(cols):
                temp.append(self.datatable.item(x, y).text())
            data.append(temp)

        return data


    def update_table(self):
        """
        Update the table to reflect changes made to the inputs. It is important to first grab the data out of the
        table, so that we can put the oxygen data back in - because I have just been a bit haphazard with the
        implementation
        """
        if not self.lock_checkbox.isChecked():
            current_data = self.get_table_data()

            deployment = self.deployment.text()
            ros_size = int(self.rosette_size.currentText())
            salinity_letter = self.salinity_letter.text()

            data = []

            for rp in range(ros_size):
                rp = rp + 1
                if rp < 10:
                    fmt_rp = f'0{rp}'
                else:
                    fmt_rp = rp
                try:
                    data.append([rp, current_data[rp][1], current_data[rp][2],
                                f'{salinity_letter}{fmt_rp}', f'{deployment}{fmt_rp}'])
                except IndexError:
                    data.append([rp, '', '',
                                 f'{salinity_letter}{fmt_rp}', f'{deployment}{fmt_rp}'])

            self.datatable.update_data(data)

    def save(self):
        deployment = self.deployment.text()
        data = self.get_table_data()

        if deployment != '':
            db_data = []
            for row in data:
                row.insert(0, deployment)
                db_data.append(row)

            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.executemany('INSERT OR REPLACE INTO logsheetData VALUES (?,?,?,?,?,?)', db_data)
            conn.commit()

            c.execute('INSERT OR REPLACE INTO logsheetFilesProcessed VALUES (?,?)', (f'hypro_created_{deployment}', 999))
            conn.commit()

            conn.close()

            self.processing_params['rosettedefault'] = int(self.rosette_size.currentText())
            save_proc_settings(self.path, self.project, self.processing_params)

            message = hyproMessageBoxTemplate('Success', 'The logsheet was successfully saved!', 'success')

    def keyPressEvent(self, event):
        k_id = event.key()
        # On enter - move down one row
        if k_id == Qt.Key_Enter or k_id == 16777220:
            selected_cell_row = self.datatable.currentIndex().row()
            selected_cell_col = self.datatable.currentIndex().column()
            self.datatable.setCurrentCell(selected_cell_row+1, selected_cell_col)

        # On delete - delete the selected cell contents
        elif k_id == Qt.Key_Delete:
            selection = self.datatable.selectedIndexes()
            if len(selection) < 2:
                selected_cell_row = self.datatable.currentIndex().row()
                selected_cell_col = self.datatable.currentIndex().column()
                self.datatable.setItem(selected_cell_row, selected_cell_col, QTableWidgetItem(str('')))
            else:
                rows = sorted(index.row() for index in selection)
                columns = sorted(index.column() for index in selection)
                for i, x in enumerate(rows):
                    self.datatable.setItem(x, columns[i], QTableWidgetItem(str('')))