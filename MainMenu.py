# old color fcfcfc
import sys, os, sqlite3, json, traceback
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
# from MapPlotting import mapPlotting these are currently disabled ..
# from TriaxusPlotting import triaxusPlotting
import hyproicons


# TODO: please clean me up - style sheet needs transfer to style file
# TODO: Refactor code to suit current code style
# TODO: re-write of QMainWindow to template for Main and processing menu. Total lines in half that way.
# TODO: clean up Tools menu - revmoved ununsed. Change to Utility menu, include DO calc, QC stats

# The class that starts it all, is the main menu for HyPro, main event loop runs from this
class Mainmenu(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(':/assets/icon.svg'))
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

        self.setStyleSheet("""
        
            QMainWindow {
                background-color: #ebeff2;
                border: 0px solid #bababa;
                font-family: Segoe UI;   
            }
            QMenuBar {
                background-color: #ffffff;
                color: #000000;
                font: 13px Segoe UI;  
            }
            QMenuBar:hover {
                color: #000000;
            }
            QMenu {
                font: 13px Segoe UI;
            }
            QMdiArea{
                background-color: #ebeff2;
            }
            QMdiSubWindow {
                background-color: #000000;
            }
            
            QLabel[headertext=true] {   
                min-width: 60px;
                min-height:20px;
                font: 24px;
                color: #ffffff; 
                font-weight: bold;
            }
            QFrame[headerframe=true]{
                background-color: #555c78;
                border-radius: 1px;
            }
            QLabel[headerlogo=true] {
                padding-left: 33px
            }
            QLabel[sidebartext=true] {           
                font: 14px;
                color: #ffffff;
                font-weight: bold;
            }
            QFrame[sidebarframe=true]{
                background-color: #4e546c;
                border-radius: 1px;
            }
            QLabel[projecttext=true]{
                color: #222222;
                font: 15px;
                font-weight: bold;  
            }
            QFrame[projectframe=true]{
                background-color: #ddeaff;
            }
            QLabel[activeprojtext=true] {        
                font: 15px;
                font-weight: bold;
                padding: 20px;
                color: #222222;
            }   
            QFrame[dashboardframe=true] {
                background-color: #f7faff;
            }
            QLabel[dashboardtext=true] {
                font: 15px;
                font-family: Segoe UI;
                color: #222222;
                padding: 10px;
            }
            QPushButton[stealth=true] {
                text-align: left;
                font: 15px;
                color: #222222;
                padding: 10px;
                background-color: #f4f8ff;
                border: 0px;   
            }
            QPushButton[stealth=true]:hover {
                font: 15px;
                color: #6bb7ff;
                padding: 10px;
                background-color: #f4f8ff;
                border: 0px;
            }
            QPushButton[stealth=true]:pressed {
                font: 15px;
                color: #086ece;
                padding: 10px;
                background-color: #f4f8ff;
                border: 0px;
            }
            QComboBox[sidebarbox=true]{
                font: 13px;
                color: #222222;
                padding: 1px;
                background-color: #ffffff;
                border: 1px solid #e8e8e8;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #fefefe;
                selection-background-color: #cbe8f6;
                border: 0px;
                font: 13px;
                selection-color: #222222;
                padding: 2px;
                border: 1px solid #bababa;
            }
            QComboBox[sidebarbox=true]:down-arrow {
                border-image: url(':/assets/downarrowicon.svg');
            }
            
            QComboBox[sidebarbox=true]:drop-down {
                border: 0px;
            }
            QPushButton[procbutton=true] {
                color: #222222;
                border: 1px solid #ededed;
                border-radius: 5px;
                background: #ededed;
                font: 14px;
                padding-left: 30px;
                padding-right: 30px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            QPushButton[procbutton=true]:hover {
                color: #222222;
                border: 1px solid #f7f7f7;
                background: #f7f7f7;
                font: 14px;
            }
            QPushButton[procbutton=true]:pressed{
                border: 1px solid #8f98a8;
                color: #222222;
                background-color: #f7f7f7;
                font: 14px;
                border-style: inset;
            }
            QPushButton[sidebar=true] {
                border: 1px solid #4e546c;
                color: #ffffff;
                font: 14px;
                height: 25px;
            }
            QPushButton[sidebar=true]:hover {
                border: 1px solid #4e546c;
                color: #ccd5e0;
            }
            QPushButton[sidebar=true]:pressed {
                border: 1px solid #4e546c;
                color: #6bb7ff;
                border-radius: 1px;
            }
            QInputDialog {
                background: #ebeff2;
            }
            QInputDialog QLabel {
                font: 14px;
            }
            QInputDialog QLineEdit {
                height: 20px;
                font: 16px;
                background: #fefefe
            }
            QInputDialog QPushButton {
                border: 2px solid #e8e8e8;
                background-color: #e8e8e8;
                border-radius: 5px;
                color: #222222;
                font: 14px;
                min-width: 80px;
                height: 20px;                
            }
            QInputDialog QPushButton:hover {
                border: 2px solid #f7f7f7;
                color: #222222;
                background-color: #f7f7f7;
                min-width: 80px;
            }
            QInputDialog QPushButton:pressed {
                border: 2px solid #e8e8e8;
                color: #222222;
                background-color: #f7f7f7;
                min-width: 80px;
                border-radius: 5px;
                border-style: inset;
            }
                           """)

    def init_ui(self):

        # TODO: make first time start up own function
        # Complete setup if this is the first time running on the system
        newpath = 'C:/HyPro'
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        # Make settings json file
        paramfile = 'C:/HyPro/hyprosettings.json'
        if not os.path.isfile(paramfile):
            params = {
                'processors': [],
                'projects': {},
                'activeprocessor': '',
                'activeproject': '',
                'theme': 'normal'
            }
            with open('C:/HyPro/hyprosettings.json', 'w+') as file:
                json.dump(params, file)

        with open('C:/HyPro/hyprosettings.json', 'r') as f:
            hyprosettings = json.load(f)

        # Set the current project, if there is already one set of course, if not = no active project
        if hyprosettings['activeproject'] != "":
            self.currproject = hyprosettings['activeproject']
            project = True
        else:
            self.currproject = 'No active project'
            project = False

        deffont = QFont('Segoe UI')
        self.setFont(deffont)

        gridlayout = QGridLayout()
        gridlayout.setSpacing(6)
        gridlayout.setContentsMargins(0, 0, 5, 0)

        self.setGeometry(400, 400, 900, 440)
        qtRectangle = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        # self.setFixedSize(self.size())
        self.setWindowTitle('HyPro - Main Menu')
        # self.statusBar().showMessage('Load a project')

        # Initialise menu buttons and options
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        viewMenu = mainMenu.addMenu('View')
        toolMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        createNewProjectMenu = QAction(QIcon(':/assets/newfile.svg'), 'New Project', self)
        createNewProjectMenu.triggered.connect(self.createnewproject)
        fileMenu.addAction(createNewProjectMenu)

        openProjectMenu = QAction(QIcon(':/assets/open.svg'), 'Open Project', self)
        openProjectMenu.triggered.connect(self.loadproject)
        fileMenu.addAction(openProjectMenu)

        importProjectMenu = QAction(QIcon(':/assets/import.svg'), 'Import Project', self)
        importProjectMenu.triggered.connect(self.importproject)
        fileMenu.addAction(importProjectMenu)

        fileMenu.addSeparator()

        exitMenu = QAction(QIcon(':/assets/exit.svg'), 'Exit', self)
        exitMenu.triggered.connect(self.close)
        fileMenu.addAction(exitMenu)

        editRMNSMenu = QAction(QIcon(':/assets/food.svg'), 'Edit RMNS', self)
        editRMNSMenu.triggered.connect(self.rmnsstandards)
        editMenu.addAction(editRMNSMenu)

        editOSILMenu = QAction(QIcon(':/assets/saltshaker.svg'), 'Edit OSIL', self)
        editOSILMenu.triggered.connect(self.osilstandards)
        editMenu.addAction(editOSILMenu)

        enableDarkMode = QAction('Dark Mode', self, checkable = True)
        if hyprosettings['theme'] == 'dark':
            enableDarkMode.setChecked(True)
        enableDarkMode.triggered.connect(self.enable_dark_mode)
        editMenu.addAction(enableDarkMode)

        viewDataMenu = QAction(QIcon(':/assets/search.svg'), 'View Data', self)
        viewDataMenu.triggered.connect(self.viewdata)
        viewMenu.addAction(viewDataMenu)

        mapPlotMenu = QAction(QIcon(':/assets/mapmarker.svg'), 'Map Plotting', self)
        mapPlotMenu.triggered.connect(self.mapplot)
        viewMenu.addAction(mapPlotMenu)

        triaxusPlotMenu = QAction(QIcon(), 'Triaxus Plotting', self)
        triaxusPlotMenu.triggered.connect(self.triaxusplot)
        viewMenu.addAction(triaxusPlotMenu)

        aboutMenu = QAction(QIcon(':/assets/roundquestionmark.svg'), 'About', self)
        aboutMenu.triggered.connect(self.aboutinformation)
        helpMenu.addAction(aboutMenu)

        manualMenu = QAction(QIcon(':/assets/roundinfo.svg'), 'Manual', self)
        manualMenu.triggered.connect(self.showmanual)
        helpMenu.addAction(manualMenu)

        headerlogo = QLabel(self)
        headerlogo.setPixmap(QPixmap(':/assets/2dropsshadow.ico').scaled(32, 32, Qt.KeepAspectRatio))
        headerlogo.setProperty('headerlogo', True)

        # Labels
        headerframe = QFrame()
        headerframe.setProperty('headerframe', True)
        headerlabel = QLabel('    HyPro②')
        headerlabel.setProperty('headertext', True)

        currprojectframe = QFrame(self)
        currprojectframe.setProperty('projectframe', True)
        currprojectframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        currprojectframeshadow.setBlurRadius(6)
        currprojectframeshadow.setColor(QtGui.QColor('#e1e6ea'))
        currprojectframeshadow.setYOffset(2)
        currprojectframeshadow.setXOffset(3)
        currprojectframe.setGraphicsEffect(currprojectframeshadow)

        sidebarframe = QFrame(self)
        sidebarframe.setProperty('sidebarframe', True)

        self.currprojectlabel = QLabel('Active Project: ')
        self.currprojectlabel.setProperty('projecttext', True)

        self.currprojectdisp = QLabel(str(self.currproject))
        self.currprojectdisp.setProperty('activeprojtext', True)

        selprojectlabel = QLabel('Select Active Project')
        selprojectlabel.setAlignment(Qt.AlignCenter)
        selprojectlabel.setProperty('sidebartext', True)

        processorlabel = QLabel('Processor')
        processorlabel.setProperty('sidebartext', True)

        optionlabel = QLabel('Options')
        optionlabel.setProperty('sidebartext', True)

        # Dropdowns
        self.processor = QComboBox()
        self.processor.setFixedWidth(100)
        self.processor.setFixedHeight(20)
        self.processor.setEditable(True)
        self.processor.lineEdit().setAlignment(QtCore.Qt.AlignHCenter)
        self.processor.lineEdit().setReadOnly(True)

        with open('C:/HyPro/hyprosettings.json', 'r') as f:
            hyprosettings = json.load(f)

        for x in hyprosettings['processors']:
            self.processor.addItem(x)

        self.processor.setProperty('sidebarbox', True)
        self.processor.activated.connect(self.activeprocessorfunction)

        self.processor.setCurrentText(hyprosettings['activeprocessor'])

        # Buttons
        button1 = QPushButton('Create New Project')
        button1.setProperty('sidebar', True)
        button1.setObjectName('StyledButton')
        button1.clicked.connect(self.createnewproject)

        button2 = QPushButton('Load Existing Project')
        button2.setProperty('sidebar', True)
        button2.clicked.connect(self.loadproject)

        button3 = QPushButton('Import Project')
        button3.setProperty('sidebar', True)
        button3.clicked.connect(self.importproject)

        button4 = QPushButton('Edit RMNS Standards')
        button4.setProperty('sidebar', True)
        button4.clicked.connect(self.rmnsstandards)

        button5 = QPushButton('Add Processor')
        button5.setProperty('sidebar', True)
        button5.clicked.connect(self.add_processor)

        button6 = QPushButton('View Data')
        button6.setProperty('sidebar', True)
        button6.clicked.connect(self.viewdata)

        button7 = QPushButton('Open Processing')
        button7.setProperty('procbutton', True)
        button7.clicked.connect(self.openprocessing)

        # Set up grid layout
        gridlayout.addWidget(headerframe, 0, 0, 3, 1)
        gridlayout.addWidget(headerlogo, 0, 0, 2, 1, QtCore.Qt.AlignLeft)
        gridlayout.addWidget(headerlabel, 0, 0, 2, 1, QtCore.Qt.AlignCenter)

        gridlayout.addWidget(currprojectframe, 0, 1, 2, 3)
        gridlayout.addWidget(self.currprojectlabel, 0, 1, 2, 1, QtCore.Qt.AlignRight)
        gridlayout.addWidget(self.currprojectdisp, 0, 2, 2, 1, QtCore.Qt.AlignLeft)

        gridlayout.addWidget(button7, 0, 3, 2, 1, QtCore.Qt.AlignLeft)

        gridlayout.addWidget(sidebarframe, 2, 0, 16, 1)
        gridlayout.addWidget(selprojectlabel, 3, 0)
        gridlayout.addWidget(button1, 4, 0)
        gridlayout.addWidget(button2, 5, 0)
        gridlayout.addWidget(button3, 6, 0)

        gridlayout.addWidget(optionlabel, 8, 0, QtCore.Qt.AlignCenter)
        gridlayout.addWidget(button4, 9, 0)
        gridlayout.addWidget(button6, 10, 0)

        gridlayout.addWidget(processorlabel, 12, 0, 1, 1, QtCore.Qt.AlignCenter)
        gridlayout.addWidget(self.processor, 13, 0, QtCore.Qt.AlignCenter)
        gridlayout.addWidget(button5, 14, 0)

        # Dashboard elements

        # Project information

        pathframe = QFrame(self)
        pathframe.setProperty('dashboardframe', True)
        pathframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        pathframeshadow.setBlurRadius(6)
        pathframeshadow.setColor(QtGui.QColor('#e1e6ea'))
        pathframeshadow.setYOffset(2)
        pathframeshadow.setXOffset(3)
        pathframe.setGraphicsEffect(pathframeshadow)

        projectinfo = QLabel('<b>Project Information</b>')
        projectinfo.setFont(deffont)
        projectinfo.setProperty('dashboardtext', True)

        pathlabel = QLabel('<b>Path:</b>', self)
        pathlabel.setFont(deffont)
        pathlabel.setProperty('dashboardtext', True)

        # self.projectpath = QPushButton(str(hyprosettings['projects'][hyprosettings['activeproject']]['path']), self)
        self.projectpath = QPushButton('Project path', self)
        self.projectpath.setFont(deffont)
        self.projectpath.setProperty('stealth', True)
        self.projectpath.setMaximumWidth(400)
        self.projectpath.clicked.connect(self.open_explorer)

        # self.projecttype = QLabel(
        #    '<b>Project Type:</b> ' + hyprosettings['projects'][hyprosettings['activeproject']]['type'], self)
        self.projecttype = QLabel('Project Type', self)
        self.projecttype.setFont(deffont)
        self.projecttype.setProperty('dashboardtext', True)

        gridlayout.addWidget(pathframe, 2, 1, 5, 2)
        gridlayout.addWidget(projectinfo, 2, 1, 2, 2, QtCore.Qt.AlignCenter)
        gridlayout.addWidget(pathlabel, 3, 1, 2, 2)
        gridlayout.addWidget(self.projectpath, 4, 1, 2, 2)
        gridlayout.addWidget(self.projecttype, 5, 1, 2, 2)

        # Date created and last accessed
        dateframe = QFrame(self)
        dateframe.setProperty('dashboardframe', True)
        dateframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        dateframeshadow.setBlurRadius(6)
        dateframeshadow.setColor(QtGui.QColor('#e1e6ea'))
        dateframeshadow.setYOffset(2)
        dateframeshadow.setXOffset(3)
        dateframe.setGraphicsEffect(dateframeshadow)

        projectcreatedlabel = QLabel('<b>Date Created:</b>', self)
        projectcreatedlabel.setFont(deffont)
        projectcreatedlabel.setProperty('dashboardtext', True)

        self.projectcreated = QLabel('Project created', self)
        self.projectcreated.setFont(deffont)
        self.projectcreated.setProperty('dashboardtext', True)

        projectmodifedlabel = QLabel('<b>Date Last Accessed:</b>', self)
        projectmodifedlabel.setFont(deffont)
        projectmodifedlabel.setProperty('dashboardtext', True)

        self.projectmodified = QLabel('Project modified', self)
        self.projectmodified.setFont(deffont)
        self.projectmodified.setProperty('dashboardtext', True)

        gridlayout.addWidget(dateframe, 2, 3, 5, 1)
        gridlayout.addWidget(projectcreatedlabel, 2, 3, 2, 1)
        gridlayout.addWidget(self.projectcreated, 3, 3, 2, 1)
        gridlayout.addWidget(projectmodifedlabel, 4, 3, 2, 1)
        gridlayout.addWidget(self.projectmodified, 5, 3, 2, 1)

        # analysis display
        analysisframe = QFrame(self)
        analysisframe.setProperty('dashboardframe', True)
        analysisframeshadow = QtWidgets.QGraphicsDropShadowEffect()
        analysisframeshadow.setBlurRadius(6)
        analysisframeshadow.setColor(QtGui.QColor('#e1e6ea'))
        analysisframeshadow.setYOffset(2)
        analysisframeshadow.setXOffset(3)
        analysisframe.setGraphicsEffect(analysisframeshadow)

        analyses_activated_label = QLabel('<b>Analysis</b>')
        analyses_activated_label.setProperty('dashboardtext', True)

        activated_label = QLabel('<b>Active</b>')
        activated_label.setProperty('dashboardtext', True)

        number_files_processed_label = QLabel('<b>Files processed:</b>')
        number_files_processed_label.setProperty('dashboardtext', True)

        number_samples_processed_label = QLabel('<b>Samples processed:</b>')
        number_samples_processed_label.setProperty('dashboardtext', True)

        nutrients_activated_label = QLabel('Seal Nutrients')
        nutrients_activated_label.setProperty('dashboardtext', True)
        self.nutrients_activated_state = QLabel('No')
        self.nutrients_activated_state.setProperty('dashboardtext', True)
        self.nutrients_files_processed = QLabel('0')
        self.nutrients_files_processed.setProperty('dashboardtext', True)
        self.nutrients_samples_processed = QLabel('0')
        self.nutrients_samples_processed.setProperty('dashboardtext', True)

        salinity_activated_label = QLabel('Guildline Salinity')
        salinity_activated_label.setProperty('dashboardtext', True)
        self.salinity_activated_state = QLabel('No')
        self.salinity_activated_state.setProperty('dashboardtext', True)
        self.salinity_files_processed = QLabel('0')
        self.salinity_files_processed.setProperty('dashboardtext', True)
        self.salinity_samples_processed = QLabel('0')
        self.salinity_samples_processed.setProperty('dashboardtext', True)

        oxygen_activated_label = QLabel('Scripps Oxygen')
        oxygen_activated_label.setProperty('dashboardtext', True)
        self.oxygen_activated_state = QLabel('No')
        self.oxygen_activated_state.setProperty('dashboardtext', True)
        self.oxygen_files_processed = QLabel('0')
        self.oxygen_files_processed.setProperty('dashboardtext', True)
        self.oxygen_samples_processed = QLabel('0')
        self.oxygen_samples_processed.setProperty('dashboardtext', True)

        sub_grid_layout = QGridLayout()
        
        gridlayout.addWidget(analysisframe, 7, 1, 10, 3)

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
        
        gridlayout.addLayout(sub_grid_layout, 7, 1, 10, 3)

        # Set grid layout to overarching main window central layout
        self.centralWidget().setLayout(gridlayout)

        if project:
            self.populatedashboards()

        self.show()

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

        # End of initialising Main Menu.

    # Populates the various text for the 'dashboard' layout thingo
    def populatedashboards(self):
        with open('C:/HyPro/hyprosettings.json', 'r') as f:
            hyprosettings = json.load(f)
        try:
            self.projectpath.setText(str(hyprosettings['projects'][hyprosettings['activeproject']]['path']))

            self.projecttype.setText(
                '<b>Project Type:</b> ' + hyprosettings['projects'][hyprosettings['activeproject']]['type'])

            self.projectcreated.setText(
                str(time.strftime("%d/%m/%y %I:%M:%S %p",
                                  (time.localtime((os.path.getctime
                                                   (hyprosettings['projects'][hyprosettings['activeproject']][
                                                        'path'] + '/' +
                                                   hyprosettings['activeproject'] + '.hypro')))))))
            try:
                self.projectmodified.setText(
                    str(time.strftime("%d/%m/%y %I:%M:%S %p",
                                      (time.localtime((os.path.getmtime
                                                       (hyprosettings['projects'][hyprosettings['activeproject']][
                                                            'path'] + '/' +
                                                        hyprosettings['activeproject'] + 'Data.db')))))))

                with open(hyprosettings['projects'][hyprosettings['activeproject']]['path'] + '/' + hyprosettings['activeproject'] + 'Params.json', 'r') as file:
                    params = json.loads(file.read())

                if params['analysisparams']['seal']['activated']:
                    self.nutrients_activated_state.setText('Yes')
                if params['analysisparams']['guildline']['activated']:
                    self.salinity_activated_state.setText('Yes')
                if params['analysisparams']['scripps']['activated']:
                    self.oxygen_activated_state.setText('Yes')

                db_path = hyprosettings['projects'][hyprosettings['activeproject']]['path'] + '/' + hyprosettings['activeproject'] + 'Data.db'
                conn = sqlite3.connect(db_path)
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
                    c.execute(f'''SELECT COUNT(*) from {nut}Data''')
                    nut_count = c.fetchone()
                    counts.append(nut_count[0])
                self.nutrients_samples_processed.setText(str(max(counts)))

                c.close()

            except Exception:
                self.projectmodified.setText('Not yet accessed...')
        except Exception:
            print('No data for this project just yet...')

    # Opens the create a new project dialog
    def createnewproject(self):
        self.create_new_project_window = createNewProject()
        self.create_new_project_window.new_project_created.connect(lambda: self.setprojectnamefromopen('new'))

    # Opens the load a project dialog
    def loadproject(self):
        self.open_existing_project = openProject()
        self.open_existing_project.selectbutton.clicked.connect(lambda: self.setprojectnamefromopen('load'))
        self.open_existing_project.selectprojbox.doubleClicked.connect(lambda: self.setprojectnamefromopen('load'))

    # Once a project is selected this updates the main menu
    def setprojectnamefromopen(self, method):
        if method == 'new':
            self.currprojectdisp.setText(self.create_new_project_window.project_prefix_str)
            self.currproject = self.create_new_project_window.project_prefix_str

        elif method == 'load':
            self.currprojectdisp.setText(self.open_existing_project.selectedproject)
        try:
            self.populatedashboards()
        except Exception:
            print('No data for the project just yet...')

    # Opens the import a project dialog
    def importproject(self):
        self.importProj = importProject()
        self.importProj.show()

    # Opens the RMNS standard dialog
    def rmnsstandards(self):
        self.rmns = rmnsDialog()
        self.rmns.show()

    # Opens the osil standard dialog TODO: finish this feature
    def osilstandards(self):
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

        self.update()

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

                    self.processor.setCurrentText(text)

        except Exception as e:
            print(e)

    # Nothing yet need to link up TODO: add view data feature
    def viewdata(self):
        print('i am nothing')

    # Opens the processing menu
    def openprocessing(self):
        try:
            if self.currproject == 'No active project':
                message_box = hyproMessageBoxTemplate('Error',
                                                      'There is no active project currently selected, please create or import one.',
                                                      'information')
            else:
                self.project = self.currprojectdisp.text()
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
                self.proccing.backToMain.connect(self.proccing.hide)

        except Exception as e:
            print(e)

    # Assigns the current active processor upon opening main menu
    def activeprocessorfunction(self):

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
        path = self.projectpath.text()
        if os.path.isdir(path):
            time.sleep(0.2)
            os.startfile(path)

    # Message box including about info
    def aboutinformation(self):
        message_box = hyproMessageBoxTemplate('About Hypro',
                                              'This is an experimental version of HyPro built using Python',
                                              'about')

    # Show the manual TODO: add a standalone directory for packaged versions
    # TODO: write manual lol
    def showmanual(self):
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
