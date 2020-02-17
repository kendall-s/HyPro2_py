from PyQt5.QtWidgets import (QPushButton, QLabel, QComboBox, QMessageBox,
                             QCheckBox, QListWidget)
import os, sqlite3, logging, traceback
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from dialogs.templates.DialogTemplate import hyproDialogTemplate

# Functionality and GUI to delete data from a projects database, also can delete original files as well
class deleteDialog(hyproDialogTemplate):
    def __init__(self, path, project, database):
        super().__init__(235, 470, 'HyPro - Select Data to Delete')

        self.currpath = path
        self.currproject = project
        self.db = database

        self.init_ui()

        self.populatefileslist()

        self.show()

    def init_ui(self):
        analysis_types_list = ['Nutrients', 'Salinity', 'Oxygen', 'CTD', 'Sampling']

        analysis_type_label = QLabel('Analysis Type: ', self)

        self.analysis_type = QComboBox()
        self.analysis_type.addItems(analysis_types_list)
        self.analysis_type.activated.connect(self.populatefileslist)
        self.analysis_type.setEditable(True)
        self.analysis_type.setEditable(False)

        data_files_label = QLabel('Select data to delete: ', self)

        self.items_elected_boolean = 0

        self.data_files = QListWidget()
        self.data_files.itemSelectionChanged.connect(self.itemselected)

        self.delete_files_checkbox = QCheckBox('Delete data files as well?', self)

        ok_but = QPushButton('Delete Data', self)
        ok_but.clicked.connect(self.deletedata)

        cancel_but = QPushButton('Cancel', self)
        cancel_but.clicked.connect(self.cancel)

        self.grid_layout.addWidget(analysis_type_label, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.analysis_type, 1, 0, 1, 2)

        self.grid_layout.addWidget(data_files_label, 2, 0, 1, 2)
        self.grid_layout.addWidget(self.data_files, 3, 0, 1, 2)

        self.grid_layout.addWidget(self.delete_files_checkbox, 4, 0, 1, 2)

        self.grid_layout.addWidget(ok_but, 5, 0)
        self.grid_layout.addWidget(cancel_but, 5, 1)

    def populatefileslist(self):
        # Fill the list with the files that have already been processed
        filetype = self.analysis_type.currentText()

        # Need to clear each time it is populated otherwise will pile up
        self.data_files.clear()

        conn = sqlite3.connect(self.db)
        c = conn.cursor()

        if filetype == 'CTD':
            c.execute('SELECT * from ctdFilesProcessed')
        if filetype == 'Nutrients':
            c.execute('SELECT * from nutrientFilesProcessed')
        if filetype == 'Salinity':
            c.execute('SELECT * from salinityFilesProcessed')
        if filetype == 'Oxygen':
            c.execute('SELECT * from oxygenFilesProcessed')
        if filetype == 'Sampling':
            c.execute('SELECT * from logsheetFilesProcessed')

        data = list(c.fetchall())
        c.close()
        filenames = [x[0] for x in data]

        self.data_files.addItems(filenames)

    def itemselected(self):
        # Not sure why I did this
        self.itemselectedboolean = 1

    def deletedata(self):
        try:
            filetype = self.analysis_type.currentText()

            if self.itemselectedboolean == 1:
                selectedfile = str(self.data_files.currentItem().text())

                conn = sqlite3.connect(self.db)
                c = conn.cursor()

                filename = [selectedfile]
                # Different statement for each analysis as the database structure for each is different
                if filetype == 'CTD':
                    deploymentnumber = [selectedfile[-7:-4]]
                    print(deploymentnumber)
                    c.execute('DELETE from ctdData where deployment=?', deploymentnumber)
                    conn.commit()
                    c.execute('DELETE from ctdFilesProcessed where filename=?', filename)
                    conn.commit()
                    conn.close()
                    if self.deletefilescheckbox.isChecked():
                        print('Deleting data files as well')
                        file = self.currpath + '/' + 'CTD' + '/' + selectedfile
                        os.remove(file)
                        logging.info('CTD data - ' + str(selectedfile) + ' deleted, the file was also deleted')

                    else:
                        logging.info('CTD data - ' + str(selectedfile) + ' deleted')

                if filetype == 'Nutrients':
                    message = QMessageBox.about(self, "Success", "File was successfully processed")
                    # TODO: complete the section for nutrients

                if filetype == 'Salinity':
                    runnumber = [selectedfile[-8:-5]]
                    c.execute('DELETE from salinityData where runNumber=?', runnumber)
                    conn.commit()
                    c.execute('DELETE from salinityFilesProcessed where filename=?', filename)
                    conn.commit()
                    conn.close()
                    if self.delete_files_checkbox.isChecked():
                        print('Deleting data files as well')
                        file = self.currpath + '/' + 'Salinity' + '/' + selectedfile
                        os.remove(file)
                        logging.info('Salinity data - ' + str(selectedfile) + ' deleted, the file was also deleted')
                    else:
                        logging.info('Salinity data - ' + str(selectedfile) + ' deleted')

                if filetype == 'Oxygen':
                    runnumber = [selectedfile[-7:-4]]
                    c.execute('DELETE from oxygenData where runNumber=?', runnumber)
                    conn.commit()
                    c.execute('DELETE from oxygenFilesProcessed where filename=?', filename)
                    conn.commit()
                    conn.close()
                    if self.delete_files_checkbox.isChecked():
                        print('Deleting data files as well')
                        file = self.currpath + '/' + 'Oxygen' + '/' + selectedfile
                        os.remove(file)
                        logging.info('Oxygen data - ' + str(selectedfile) + ' deleted, the file was also deleted')
                    else:
                        logging.info('Oxygen data - ' + str(selectedfile) + ' deleted')

                if filetype == 'Sampling':
                    runnumber = [selectedfile[-11:-8]]
                    print(runnumber)
                    c.execute('DELETE from logsheetData where deployment=?', runnumber)
                    conn.commit()
                    c.execute('DELETE from logsheetFilesProcessed where filename=?', filename)
                    conn.commit()
                    conn.close()
                    if self.delete_files_checkbox.isChecked():
                        print('Deleting data files as well')
                        file = self.currpath + '/' + 'Sampling' + '/' + selectedfile
                        os.remove(file)
                        logging.info('Sample logsheet data - ' + str(selectedfile) + ' deleted, the file was also deleted')
                    else:
                        logging.info('Sample logsheet data - ' + str(selectedfile) + ' deleted')

                messagebox = QMessageBox(QtWidgets.QMessageBox.Information, 'Deleted successfully',
                                         'Data was deleted from the database',
                                         buttons=QtWidgets.QMessageBox.Ok, parent=self)
                messagebox.setIconPixmap(QPixmap(':/assets/trash.svg'))
                messagebox.setFont(QFont('Segoe UI'))
                messagebox.setStyleSheet('QLabel { font: 15px; } QPushButton { font: 15px; }')
                messagebox.exec_()

            else:
                message = QMessageBox.about(self, "Error", "Please select a file...")

        except Exception:
            logging.error(traceback.print_exc())

    def cancel(self):
        self.close()
