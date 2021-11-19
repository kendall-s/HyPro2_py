# old color fcfcfc
import sys, os, sqlite3, json, traceback
# Need these imports for pyinstaller
import sqlalchemy
import sqlalchemy.ext.baked
import sqlalchemy.sql.default_comparator
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, QLabel, QGridLayout,
                             QInputDialog, QComboBox, QAction, QDesktopWidget, QFrame)
from time import sleep
import time
import logging
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dialogs.CreateNewProject import createNewProject
from dialogs.OpenProject import openProject
from dialogs.ImportProject import importProject
from processing.ProcessingMenu import Processingmenu
from dialogs.RMNSDialog import rmnsDialog
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate
# from MapPlotting import mapPlotting these are currently disabled ..
# from TriaxusPlotting import triaxusPlotting
import hyproicons, style


# TODO: please clean me up - style sheet needs transfer to style file
# TODO: Refactor code to suit current code style
# TODO: re-write of QMainWindow to template for Main and processing menu. Total lines in half that way.
# TODO: clean up Tools menu - revmoved ununsed. Change to Utility menu, include DO calc, QC stats

# The class that starts it all, the main menu for HyPro, main event loop runs from this
class Mainmenu(hyproMainWindowTemplate):

    def __init__(self):
        super().__init__(870, 420, 'HyPro - Main Menu')

        self.grid_layout.setContentsMargins(0, 0, 5, 0)

        self.hypro_settings = self.start_up()
        self.init_ui()

        self.create_base_dbs()

    def init_ui(self):

        # Set the current project, if there is already one set of course, if not = no active project
        if self.hypro_settings['activeproject'] != "":
            self.currproject = self.hypro_settings['activeproject']
            project = True
        else:
            self.currproject = 'No active project'
            project = False

        self.setFont(QFont('Segoe UI'))

        # Initialise menu buttons and options
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolMenu = mainMenu.addMenu('Utilities')
        helpMenu = mainMenu.addMenu('Help')

        createNewProjectMenu = QAction(QIcon(':/assets/newfile.svg'), 'New Project', self)
        createNewProjectMenu.triggered.connect(self.create_new_project)
        fileMenu.addAction(createNewProjectMenu)

        openProjectMenu = QAction(QIcon(':/assets/open.svg'), 'Open Project', self)
        openProjectMenu.triggered.connect(self.load_project)
        fileMenu.addAction(openProjectMenu)

        importProjectMenu = QAction(QIcon(':/assets/import.svg'), 'Import Project', self)
        importProjectMenu.triggered.connect(self.import_project)
        fileMenu.addAction(importProjectMenu)

        fileMenu.addSeparator()

        exitMenu = QAction(QIcon(':/assets/exit.svg'), 'Exit', self)
        exitMenu.triggered.connect(self.close)
        fileMenu.addAction(exitMenu)

        editRMNSMenu = QAction(QIcon(':/assets/food.svg'), 'Edit RMNS', self)
        editRMNSMenu.triggered.connect(self.rmns_standards)
        editMenu.addAction(editRMNSMenu)

        editOSILMenu = QAction(QIcon(':/assets/saltshaker.svg'), 'Edit OSIL', self)
        editOSILMenu.triggered.connect(self.osil_standards)
        editMenu.addAction(editOSILMenu)

        enableDarkMode = QAction('Dark Mode', self, checkable=True)
        if self.hypro_settings['theme'] == 'dark':
            enableDarkMode.setChecked(True)
        enableDarkMode.triggered.connect(self.enable_dark_mode)
        editMenu.addAction(enableDarkMode)

        viewDataMenu = QAction(QIcon(':/assets/search.svg'), 'View Data', self)
        viewDataMenu.triggered.connect(self.view_data)
        viewMenu.addAction(viewDataMenu)

        mapPlotMenu = QAction(QIcon(':/assets/mapmarker.svg'), 'Map Plotting', self)
        mapPlotMenu.triggered.connect(self.mapplot)
        viewMenu.addAction(mapPlotMenu)

        triaxusPlotMenu = QAction(QIcon(), 'Triaxus Plotting', self)
        triaxusPlotMenu.triggered.connect(self.triaxusplot)
        viewMenu.addAction(triaxusPlotMenu)

        aboutMenu = QAction(QIcon(':/assets/roundquestionmark.svg'), 'About', self)
        aboutMenu.triggered.connect(self.about_information)
        helpMenu.addAction(aboutMenu)

        manualMenu = QAction(QIcon(':/assets/roundinfo.svg'), 'Manual', self)
        manualMenu.triggered.connect(self.show_manual)
        helpMenu.addAction(manualMenu)

        header_logo = QLabel(self)
        header_logo.setPixmap(QPixmap(':/assets/2dropsshadow.ico').scaled(32, 32, Qt.KeepAspectRatio))
        header_logo.setProperty('headerLogo', True)

        # Labels
        header_frame = QFrame(self)
        header_frame.setProperty('sideHeaderFrame', True)
        header_label = QLabel('<b>       HyPro②</b>')
        header_label.setProperty('headerText', True)

        curr_project_frame = QFrame(self)
        curr_project_frame.setProperty('topBarFrame', True)

        sidebar_frame = QFrame(self)
        sidebar_frame.setProperty('sideBarFrame', True)

        self.curr_project_label = QLabel('Active Project: ', self)
        self.curr_project_label.setProperty('dashboardText', True)
        self.curr_project_label.setStyleSheet('font: 15px; padding: 20px; font-weight: bold;')

        self.curr_project_disp = QLabel(str(self.currproject))
        self.curr_project_disp.setProperty('dashboardText', True)
        self.curr_project_disp.setStyleSheet('font: 15px; font-weight: bold;')


        sel_project_label = QLabel('<b>Select Active Project</b>')
        sel_project_label.setAlignment(Qt.AlignCenter)
        sel_project_label.setProperty('sideBarText', True)

        processor_label = QLabel('<b>Processor</b>')
        processor_label.setProperty('sideBarText', True)

        option_label = QLabel('<b>Options</b>')
        option_label.setProperty('sideBarText', True)

        # Dropdowns
        self.processor = QComboBox()
        self.processor.setFixedWidth(100)
        self.processor.setFixedHeight(20)
        self.processor.setEditable(True)
        self.processor.lineEdit().setAlignment(QtCore.Qt.AlignHCenter)
        self.processor.lineEdit().setReadOnly(True)

        for procr in self.hypro_settings['processors']:
            self.processor.addItem(procr)

        self.processor.setProperty('sidebarbox', True)
        self.processor.activated.connect(self.active_processor_function)

        self.processor.setCurrentText(self.hypro_settings['activeprocessor'])

        # ------------------------- Sidebar Buttons -------------------------------------------------------------------
        create_new_proj = QPushButton('Create New Project')
        create_new_proj.setProperty('sideBarButton', True)
        create_new_proj.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        create_new_proj.clicked.connect(self.create_new_project)

        load_proj = QPushButton('Load Existing Project')
        load_proj.setProperty('sideBarButton', True)
        load_proj.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        load_proj.clicked.connect(self.load_project)

        import_proj = QPushButton('Import Project')
        import_proj.setProperty('sideBarButton', True)
        import_proj.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        import_proj.clicked.connect(self.import_project)

        edit_rmns_stds = QPushButton('Edit RMNS Standards')
        edit_rmns_stds.setProperty('sideBarButton', True)
        edit_rmns_stds.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        edit_rmns_stds.clicked.connect(self.rmns_standards)

        add_proc = QPushButton('Add Processor')
        add_proc.setProperty('sideBarButton', True)
        add_proc.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        add_proc.clicked.connect(self.add_processor)

        view_data = QPushButton('View Data')
        view_data.setProperty('sideBarButton', True)
        view_data.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        view_data.clicked.connect(self.view_data)

        open_processing = QPushButton('Open Processing')
        open_processing.setProperty('procButton', True)
        open_processing.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        open_processing.clicked.connect(self.open_processing)

        # Set up grid layout
        self.grid_layout.addWidget(header_frame, 0, 0, 3, 1)
        self.grid_layout.addWidget(header_logo, 0, 0, 2, 1, QtCore.Qt.AlignLeft)
        self.grid_layout.addWidget(header_label, 0, 0, 2, 1, QtCore.Qt.AlignCenter)

        self.grid_layout.addWidget(curr_project_frame, 0, 1, 2, 3)
        self.grid_layout.addWidget(self.curr_project_label, 0, 1, 2, 1, QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(self.curr_project_disp, 0, 2, 2, 1, QtCore.Qt.AlignLeft)

        self.grid_layout.addWidget(open_processing, 0, 3, 2, 1, QtCore.Qt.AlignLeft)

        self.grid_layout.addWidget(sidebar_frame, 2, 0, 16, 1)
        self.grid_layout.addWidget(sel_project_label, 3, 0)
        self.grid_layout.addWidget(create_new_proj, 4, 0)
        self.grid_layout.addWidget(load_proj, 5, 0)
        self.grid_layout.addWidget(import_proj, 6, 0)

        self.grid_layout.addWidget(option_label, 8, 0, QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(edit_rmns_stds, 9, 0)
        self.grid_layout.addWidget(view_data, 10, 0)

        self.grid_layout.addWidget(processor_label, 12, 0, 1, 1, QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(self.processor, 13, 0, QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(add_proc, 14, 0)

        # ------------------------- Dashboard elements ---------------------------------------------------------------
        # Project information
        path_frame = QFrame(self)
        path_frame.setProperty('dashboardFrame', True)

        project_info = QLabel('<b>Project Information</b>')
        project_info.setProperty('dashboardText', True)

        path_label = QLabel('<b>Path:</b>', self)
        path_label.setProperty('dashboardText', True)

        # self.project_path = QPushButton(str(self.hypro_settings['projects'][self.hypro_settings['activeproject']]['path']), self)
        self.project_path = QPushButton('Project path', self)
        self.project_path.setFont(QFont('Segoe UI'))
        self.project_path.setProperty('stealth', True)
        self.project_path.setMaximumWidth(400)
        self.project_path.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.project_path.clicked.connect(self.open_explorer)

        # self.project_type = QLabel(
        #    '<b>Project Type:</b> ' + self.hypro_settings['projects'][self.hypro_settings['activeproject']]['type'], self)
        self.project_type = QLabel('Project Type', self)
        self.project_type.setFont(QFont('Segoe UI'))
        self.project_type.setProperty('dashboardText', True)

        self.grid_layout.addWidget(path_frame, 2, 1, 5, 2)
        self.grid_layout.addWidget(project_info, 2, 1, 2, 2, QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(path_label, 3, 1, 2, 1)
        self.grid_layout.addWidget(self.project_path, 4, 1, 2, 2)
        self.grid_layout.addWidget(self.project_type, 5, 1, 2, 2)

        # Date created and last accessed
        date_frame = QFrame(self)
        date_frame.setProperty('dashboardFrame', True)

        project_created_label = QLabel('<b>Date Created:</b>', self)
        project_created_label.setProperty('dashboardText', True)

        self.project_created = QLabel('Project created', self)
        self.project_created.setProperty('dashboardText', True)

        project_modified_label = QLabel('<b>Date Last Accessed:</b>', self)
        project_modified_label.setProperty('dashboardText', True)

        self.project_modified = QLabel('Project modified', self)
        self.project_modified.setProperty('dashboardText', True)

        self.grid_layout.addWidget(date_frame, 2, 3, 5, 1)
        self.grid_layout.addWidget(project_created_label, 2, 3, 2, 1)
        self.grid_layout.addWidget(self.project_created, 3, 3, 2, 1)
        self.grid_layout.addWidget(project_modified_label, 4, 3, 2, 1)
        self.grid_layout.addWidget(self.project_modified, 5, 3, 2, 1)

        # analysis display
        analysis_frame = QFrame(self)
        analysis_frame.setProperty('dashboardFrame', True)

        analyses_activated_label = QLabel('<b>Analysis</b>')
        analyses_activated_label.setProperty('dashboardText', True)

        activated_label = QLabel('<b>Active</b>')
        activated_label.setProperty('dashboardText', True)

        number_files_processed_label = QLabel('<b>Files processed:</b>')
        number_files_processed_label.setProperty('dashboardText', True)

        number_samples_processed_label = QLabel('<b>Samples processed:</b>')
        number_samples_processed_label.setProperty('dashboardText', True)

        nutrients_activated_label = QLabel('Seal Nutrients')
        nutrients_activated_label.setProperty('dashboardText', True)
        self.nutrients_activated_state = QLabel('No')
        self.nutrients_activated_state.setProperty('dashboardText', True)
        self.nutrients_files_processed = QLabel('0')
        self.nutrients_files_processed.setProperty('dashboardText', True)
        self.nutrients_samples_processed = QLabel('0')
        self.nutrients_samples_processed.setProperty('dashboardText', True)

        salinity_activated_label = QLabel('Guildline Salinity')
        salinity_activated_label.setProperty('dashboardText', True)
        self.salinity_activated_state = QLabel('No')
        self.salinity_activated_state.setProperty('dashboardText', True)
        self.salinity_files_processed = QLabel('0')
        self.salinity_files_processed.setProperty('dashboardText', True)
        self.salinity_samples_processed = QLabel('0')
        self.salinity_samples_processed.setProperty('dashboardText', True)

        oxygen_activated_label = QLabel('Scripps Oxygen')
        oxygen_activated_label.setProperty('dashboardText', True)
        self.oxygen_activated_state = QLabel('No')
        self.oxygen_activated_state.setProperty('dashboardText', True)
        self.oxygen_files_processed = QLabel('0')
        self.oxygen_files_processed.setProperty('dashboardText', True)
        self.oxygen_samples_processed = QLabel('0')
        self.oxygen_samples_processed.setProperty('dashboardText', True)

        sub_grid_layout = QGridLayout()
        
        self.grid_layout.addWidget(analysis_frame, 7, 1, 10, 3)

        sub_grid_layout.addWidget(analyses_activated_label, 0, 1)
        sub_grid_layout.addWidget(activated_label, 0, 2)
        sub_grid_layout.addWidget(number_files_processed_label, 0, 3)
        sub_grid_layout.addWidget(number_samples_processed_label, 0, 4)

        sub_grid_layout.addWidget(nutrients_activated_label, 1, 1)
        sub_grid_layout.addWidget(self.nutrients_activated_state, 1, 2)
        sub_grid_layout.addWidget(self.nutrients_files_processed, 1, 3)
        sub_grid_layout.addWidget(self.nutrients_samples_processed, 1, 4)
        
        sub_grid_layout.addWidget(salinity_activated_label, 2, 1)
        sub_grid_layout.addWidget(self.salinity_activated_state, 2, 2)
        sub_grid_layout.addWidget(self.salinity_files_processed, 2, 3)
        sub_grid_layout.addWidget(self.salinity_samples_processed, 2, 4)
        
        sub_grid_layout.addWidget(oxygen_activated_label, 3, 1)
        sub_grid_layout.addWidget(self.oxygen_activated_state, 3, 2)
        sub_grid_layout.addWidget(self.oxygen_files_processed, 3, 3)
        sub_grid_layout.addWidget(self.oxygen_samples_processed, 3, 4)
        
        self.grid_layout.addLayout(sub_grid_layout, 7, 1, 10, 3)

        # Set grid layout to overarching main window central layout

        if project:
            self.populate_dashboards()

        self.show()


        # End of initialising Main Menu.

    def start_up(self):
        # Check if the base directory for settings exists
        base_path = 'C:/HyPro'
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        # Check if the parameters file exists
        parameters_file = 'C:/HyPro/hyprosettings.json'
        if not os.path.isfile(parameters_file):
            params = {
                'processors': [],
                'projects': {},
                'activeprocessor': '',
                'activeproject': '',
                'theme': 'normal'
            }
            with open(parameters_file, 'w+') as writing_file:
                json.dump(params, writing_file)
            hypro_settings = params

        else:
            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                hypro_settings = json.load(f)

        return hypro_settings

    def create_base_dbs(self):
        # Make Hypro settings database file
        if not os.path.isdir('C:/HyPro/Settings'):
            os.makedirs('C:/HyPro/Settings')
        # Put hypro settings database in the settings subfolder
        conn = sqlite3.connect('C:/HyPro/Settings/hypro.db')
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS rmnsData
                                    (lot TEXT,
                                    phosphate FLOAT,
                                    phosphateU FLOAT,
                                    silicate FLOAT,
                                    silicateU FLOAT,
                                    nitrate FLOAT,
                                    nitrateU FLOAT,
                                    nitrite FLOAT,
                                    nitriteU FLOAT,
                                    ammonia FLOAT,
                                    ammoniaU FLOAT, UNIQUE(lot))''')
        c.execute('''CREATE TABLE IF NOT EXISTS osilData
                                    (lot TEXT,
                                    salinity FLOAT, UNIQUE(lot))''')
        c.close()

    # Populates the various text for the 'dashboard' layout thingo
    def populate_dashboards(self):
        try:
            print(self.hypro_settings['activeproject'])
            self.project_path.setText(str(self.hypro_settings['projects'][self.hypro_settings['activeproject']]['path']))

            self.project_type.setText(
                '<b>Project Type:</b> ' + self.hypro_settings['projects'][self.hypro_settings['activeproject']]['type'])

            # Setting the creation time and modified times - a little bit unwieldly trying to format the times
            active_project = self.hypro_settings['activeproject']
            project_path = self.hypro_settings['projects'][active_project]['path']
            hypro_file = project_path + '/' + active_project + '.hypro'
            proj_db_file = project_path + '/' + active_project + 'Data.db'

            self.project_created.setText(str(time.strftime("%d/%m/%y %I:%M:%S %p", (time.localtime((os.path.getctime(hypro_file)))))))

            try:
                self.project_modified.setText(str(time.strftime("%d/%m/%y %I:%M:%S %p", (time.localtime((os.path.getmtime(proj_db_file)))))))

                params_file = project_path + '/' + active_project + 'Params.json'

                with open(params_file, 'r') as file:
                    params = json.loads(file.read())

                if params['analysis_params']['seal']['activated']:
                    self.nutrients_activated_state.setText('Yes')
                if params['analysis_params']['guildline']['activated']:
                    self.salinity_activated_state.setText('Yes')
                if params['analysis_params']['scripps']['activated']:
                    self.oxygen_activated_state.setText('Yes')

                conn = sqlite3.connect(proj_db_file)
                c = conn.cursor()

                c.execute('''SELECT COUNT(*) FROM oxygenData''')
                oxy_count = c.fetchone()
                self.oxygen_samples_processed.setText(str(oxy_count[0]))
                c.execute('''SELECT COUNT(*) FROM oxygenFilesProcessed''')
                oxy_count = c.fetchone()
                self.oxygen_files_processed.setText(str(oxy_count[0]))

                c.execute('''SELECT COUNT(*) FROM salinityData''')
                sal_count = c.fetchone()
                self.salinity_samples_processed.setText(str(sal_count[0]))
                c.execute('''SELECT COUNT(*) FROM salinityFilesProcessed''')
                sal_count = c.fetchone()
                self.salinity_files_processed.setText(str(sal_count[0]))

                c.execute('''SELECT COUNT(*) FROM nutrientFilesProcessed''')
                nut_count = c.fetchone()
                self.nutrients_files_processed.setText(str(nut_count[0]))

                nuts = ['nitrate', 'phosphate', 'silicate', 'nitrite', 'ammonia']
                counts = []
                for nut in nuts:
                    c.execute(f'''SELECT COUNT(*) from {nut}Data WHERE survey NOT IN ('StandardQC', 'Null', 'RMNS', 'BQC', 'MDL', 'Test', 'Unknown')  ''')
                    nut_count = c.fetchone()
                    counts.append(nut_count[0])
                self.nutrients_samples_processed.setText(str(max(counts)))

                c.close()

            except Exception:
                self.project_modified.setText('Not yet accessed...')

        except Exception:
            print(traceback.print_exc())
            self.project_modified.setText('Not yet accessed...')
            print('No data for this project just yet...')

    # Opens the create a new project dialog
    def create_new_project(self):
        self.create_new_project_window = createNewProject()
        self.create_new_project_window.new_project_created.connect(lambda: self.set_project_name_from_open('new'))

    # Opens the load a project dialog
    def load_project(self):
        self.open_existing_project = openProject()
        self.open_existing_project.selectbutton.clicked.connect(lambda: self.set_project_name_from_open('load'))
        self.open_existing_project.selectprojbox.doubleClicked.connect(lambda: self.set_project_name_from_open('load'))

    # Once a project is selected this updates the main menu
    def set_project_name_from_open(self, method):
        self.hypro_settings = self.start_up()

        if method == 'new':
            self.curr_project_disp.setText(self.create_new_project_window.project_prefix_str)
            self.currproject = self.create_new_project_window.project_prefix_str

        if method == 'load':
            self.curr_project_disp.setText(self.open_existing_project.selectedproject)

        try:
            self.populate_dashboards()
        except Exception:
            print(Exception)
            print('No data for the project just yet...')

    # Opens the import a project dialog
    def import_project(self):
        self.importProj = importProject()
        self.importProj.show()

    # Opens the RMNS standard dialog
    def rmns_standards(self):
        self.rmns = rmnsDialog()
        self.rmns.show()

    # Opens the osil standard dialog
    # TODO: finish this feature
    def osil_standards(self):
        print('osils')


    def enable_dark_mode(self):
        with open('C:/HyPro/hyprosettings.json', 'r') as file:
            params = json.loads(file.read())
        if params['theme'] == 'normal':
            params['theme'] = 'dark'
        else:
            params['theme'] = 'normal'
        with open('C:/HyPro/hyprosettings.json', 'w') as file:
            json.dump(params, file)

        self.hypro_settings = params
        self.setStyleSheet(style.stylesheet[params['theme']])

    # Opens a dialog to add a new processor
    def add_processor(self):
        try:
            inp = QInputDialog(self)
            inp.setFont(QFont('Segoe UI'))
            inp.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            text, ok = inp.getText(self, 'Add Processor', 'Enter Processor:')
            if ok:
                if text != "":
                    with open('C:/HyPro/hyprosettings.json', 'r') as file:
                        params = json.loads(file.read())
                    params['processors'].append(text)

                    self.processor.clear()

                    for x in params['processors']:
                        self.processor.addItem(x)

                    with open('C:/HyPro/hyprosettings.json', 'w') as file:
                        json.dump(params, file)

                    self.hypro_settings = params
                    self.processor.setCurrentText(text)

        except Exception as e:
            print(e)

    # Nothing yet need to link up TODO: add view data feature
    def view_data(self):
        print('i am nothing')

    # Opens the processing menu
    def open_processing(self):
        try:
            if self.currproject == 'No active project':
                message_box = hyproMessageBoxTemplate('Error',
                                                      'There is no active project currently selected, please create or import one.',
                                                      'information')
            else:
                self.project = self.curr_project_disp.text()
                with open('C:/HyPro/hyprosettings.json', 'r') as file:
                    params = json.loads(file.read())

                path = params['projects'][self.project]['path']

                self.proccing = Processingmenu(self.project, path)
                self.proccing.show()
                sleep(0.3)
                self.hide()

                self.proccing.backToMain.connect(self.show)
                #self.proccing.backToMain.connect(self.proccing.output_box.close)
                self.proccing.backToMain.connect(lambda: self.proccing.output_box.widget.close())
                self.proccing.backToMain.connect(lambda: logging.shutdown())
                self.proccing.backToMain.connect(lambda: self.proccing.hide())

        except Exception as e:
            print(e)

    # Assigns the current active processor upon opening main menu
    def active_processor_function(self):
        try:
            with open('C:/HyPro/hyprosettings.json', 'r') as file:
                params = json.loads(file.read())
            params['activeprocessor'] = self.processor.currentText()

            with open('C:/HyPro/hyprosettings.json', 'w') as file:
                json.dump(params, file)

        except Exception as e:
            print(e)

    # Opens windows explorer to look a the project path
    def open_explorer(self):
        path = self.project_path.text()
        if os.path.isdir(path):
            time.sleep(0.2)
            os.startfile(path)

    # Message box including about info
    def about_information(self):
        message_box = hyproMessageBoxTemplate('About Hypro',
                                              'This is an experimental version of HyPro built using Python',
                                              'about')

    # Show the manual TODO: add a standalone directory for packaged versions
    # TODO: write manual lol
    def show_manual(self):
        file = 'C:/Users/she384/Documents/Tests/Manual.pdf'
        os.system('start ' + file)
        print('showmanul')

    # Not working currently
    def mapplot(self):
        # self.mapplot = mapPlotting(self.currproject)
        # self.mapplot.show()
        print('Disabled')

    # Works but not great
    def triaxusplot(self):
        # self.triaxusplot = triaxusPlotting(self.currproject)
        # self.triaxusplot.show()
        print('Disabled')

    # Close everything on close event
    def closeEvent(self, event):
        app.closeAllWindows()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Mainmenu()
    sys.exit(app.exec_())
