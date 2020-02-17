import os, logging, json, sys
from PyQt5.QtWidgets import (QPushButton, QLabel, QFileDialog, QFrame, QAction, QCheckBox, QPlainTextEdit,
                             QGraphicsDropShadowEffect, QApplication)
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dialogs.ViewDataDialog import viewDataDialog
from processing.RefreshFunction import refreshFunction
from dialogs.RereadDialog import rereadDialog
from dialogs.ProducePlotsDialog import producePlotsDialog
from dialogs.DeleteDialog import deleteDialog
from dialogs.ExportDeployments import exportDeployments
from processing.LoggerOutput import QTextEditLogger
from dialogs.AnalysisDialog import analysisSettings
from dialogs.SurveyDialog import surveyDialog
from dialogs.RMNSDialog import rmnsDialog
from dialogs.ParametersDialog import parametersDialog
from processing.QCStats import statsDialog
import processing.readdata.InitialiseTables as inittabs
import processing.plotting.QCPlots as qcp
import sqlite3
from netCDF4 import Dataset
import numpy as np
import traceback
import time
import calendar
import hyproicons, style
from dialogs.templates.MainWindowTemplate import hyproMainWindowTemplate
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate

# TODO: Make output for ODV
# TODO: make logsheet go to Dissolved Oxygen box file
# TODO: convert QMainWindow to template, cut total code in half.

# This file contains the GUI functionality of the processing menu which is secondary to the main menu
# Processing of all files within a project takes place from within this menu


class Processingmenu(hyproMainWindowTemplate, QPlainTextEdit):
    backToMain = pyqtSignal()

    def __init__(self, project, path):
        super().__init__(820, 440, 'HyPro - Processing')

        self.setProperty('ProcessingMenu', True)

        self.grid_layout.setContentsMargins(0, 0, 5, 0)

        self.currproject = project
        self.currpath = path
        self.db = self.currpath + '/' + self.currproject + 'Data.db'

        self.params_path = self.currpath + '/' + '%sParams.json' % self.currproject

        inittabs.main(self.currproject, self.currpath)

        self.init_ui()

        self.user_prompter()


    def init_ui(self):
        self.make_default_params_file()

        file_menu = self.main_menu.addMenu('File')
        export_menu = file_menu.addMenu(QIcon(':/assets/archivebox.svg'), 'Export')
        output_menu = file_menu.addMenu(QIcon(':/assets/text.svg'), 'Output Log')

        edit_menu = self.main_menu.addMenu('Edit')
        rmns_menu = QAction(QIcon(':/assets/food.svg'), 'Edit RMNS', self)
        rmns_menu.triggered.connect(self.rmns_standards_window)
        edit_menu.addAction(rmns_menu)

        osil_menu = QAction(QIcon(':/assets/saltshaker.svg'), 'Edit OSIL', self)
        edit_menu.addAction(osil_menu)

        edit_menu.addSeparator()

        params_menu = QAction(QIcon(':/assets/settings2.svg'), 'Edit Parameters', self)
        edit_menu.addAction(params_menu)
        params_menu.triggered.connect(self.parameter_settings_window)

        analysis_menu = self.main_menu.addMenu('Analyses')
        self.survey_menu = self.main_menu.addMenu('Surveys')
        view_menu = self.main_menu.addMenu('View')
        nutrient_qc_menu = view_menu.addMenu('Nutrient QC Plots')
        salinity_qc_menu = view_menu.addMenu('Salinity QC Plots')
        oxygen_qc_menu = view_menu.addMenu('Oxygen QC Plots')
        help_menu = self.main_menu.addMenu('Help')

        add_analysis_menu = analysis_menu.addMenu(QIcon(':/assets/flask.svg'), 'Add Analysis')

        export_data = QAction(QIcon(':/assets/ship.svg'), 'Export Deployments', self)
        export_data.triggered.connect(self.export_data_window)
        export_menu.addAction(export_data)

        exportUnderwayNutrients = QAction('Export Underway Nutrients', self)
        exportUnderwayNutrients.triggered.connect(self.exportuwynuts)
        export_menu.addAction(exportUnderwayNutrients)

        delete_files = QAction(QIcon(':/assets/trash2.svg'), 'Delete Files', self)
        delete_files.triggered.connect(self.delete_files_window)
        file_menu.addAction(delete_files)

        save_output = QAction(QIcon(':/assets/save.svg'), 'Save Output', self)
        save_output.triggered.connect(self.save_output_window)
        output_menu.addAction(save_output)

        clear_output = QAction(QIcon(':/assets/clear.svg'), 'Clear Output', self)
        clear_output.triggered.connect(self.clear_output_function)
        output_menu.addAction(clear_output)

        main_menu_action = QAction(QIcon(':/assets/home.svg'), 'Main Menu', self)
        main_menu_action.setShortcut('Ctrl+Alt+H')
        main_menu_action.setStatusTip('Back to the main menu')
        main_menu_action.triggered.connect(self.backtomenufunction)
        file_menu.addAction(main_menu_action)

        file_menu.addSeparator()

        exit_menu = QAction(QIcon(':/assets/exit.svg'), 'Exit', self)
        exit_menu.triggered.connect(self.close)
        file_menu.addAction(exit_menu)

        self.add_guildline_salinity = QAction('Guildline Salinity', self)
        self.add_guildline_salinity.triggered.connect(self.add_guildline_analysis)
        add_analysis_menu.addAction(self.add_guildline_salinity)

        self.add_scripps_oxygen = QAction('Scripps Oxygen', self)
        self.add_scripps_oxygen.triggered.connect(self.add_scripps_analysis)
        add_analysis_menu.addAction(self.add_scripps_oxygen)

        self.add_seal_nutrients = QAction('Seal Nutrients', self)
        self.add_seal_nutrients.triggered.connect(self.add_seal_analysis)
        add_analysis_menu.addAction(self.add_seal_nutrients)

        self.add_seasave_ctd = QAction('Seasave CTD', self)
        self.add_seasave_ctd.triggered.connect(self.add_seasave_analysis)
        add_analysis_menu.addAction(self.add_seasave_ctd)

        self.add_logsheet = QAction('Sampling Logsheet', self)
        self.add_logsheet.triggered.connect(self.add_logsheet_analysis)
        add_analysis_menu.addAction(self.add_logsheet)

        self.populate_analysis_checkboxes()
        self.populate_surveys()

        self.survey_menu.addSeparator()
        self.add_new_survey = QAction(QIcon(':/assets/roundplus.svg'), 'New', self)
        self.add_new_survey.triggered.connect(lambda: self.survey_settings_window('new'))
        self.survey_menu.addAction(self.add_new_survey)

        rmns_plots = QAction('RMNS', self)
        rmns_plots.triggered.connect(self.rmnsplots)
        nutrient_qc_menu.addAction(rmns_plots)

        mdl_plots = QAction('MDL', self)
        mdl_plots.triggered.connect(self.mdlplots)
        nutrient_qc_menu.addAction(mdl_plots)

        redfield_plots = QAction('Redfield Ratio', self)
        redfield_plots.triggered.connect(self.redfield)
        nutrient_qc_menu.addAction(redfield_plots)

        salinity_error_plot = QAction('Salinity - CTD Error', self)
        salinity_error_plot.triggered.connect(self.salinityerror)
        salinity_qc_menu.addAction(salinity_error_plot)

        salinity_standard_plot = QAction('Salinity Standards', self)
        salinity_standard_plot.triggered.connect(self.salinitystandards)
        salinity_qc_menu.addAction(salinity_standard_plot)

        oxygen_error_plot = QAction('Oxygen - CTD Error', self)
        oxygen_error_plot.triggered.connect(self.oxygenerror)
        oxygen_qc_menu.addAction(oxygen_error_plot)

        oxygen_standard_plot = QAction('Oxygen Standards', self)
        oxygen_standard_plot.triggered.connect(self.oxygenstandards)
        oxygen_qc_menu.addAction(oxygen_standard_plot)

        plots_action = QAction('Create Plots', self)
        plots_action.triggered.connect(self.produce_plots_window)
        view_menu.addAction(plots_action)

        stats_action = QAction('View QC Stats', self)
        stats_action.triggered.connect(self.produce_stats_window)
        view_menu.addAction(stats_action)

        about_menu = QAction(QIcon(':/assets/roundquestionmark.svg'), 'About', self)
        about_menu.triggered.connect(self.about_information)
        help_menu.addAction(about_menu)

        manual_menu = QAction(QIcon(':/assets/roundinfo.svg'), 'Manual', self)
        manual_menu.triggered.connect(self.show_manual)
        help_menu.addAction(manual_menu)

        current_project_frame = QFrame(self)
        current_project_frame.setProperty('sideHeaderFrame', True)
        # Shadow graphics parameters
        current_project_frame_shadow = QGraphicsDropShadowEffect()
        current_project_frame_shadow.setBlurRadius(5)
        current_project_frame_shadow.setYOffset(1)
        current_project_frame_shadow.setXOffset(2)

        current_project_label = QLabel('Current Project:')
        current_project_label.setProperty('sideBarText', True)

        current_project_heading = QLabel('<b>' + self.currproject + '</b>')
        current_project_heading.setAlignment(Qt.AlignCenter)
        current_project_heading.setProperty('sideHeaderHeading', True)

        top_h_frame = QFrame(self)
        top_h_frame.setProperty('topBarFrame', True)
        top_h_frame_shadow = QGraphicsDropShadowEffect()
        top_h_frame_shadow.setBlurRadius(5)
        top_h_frame_shadow.setYOffset(2)
        top_h_frame_shadow.setXOffset(3)
        #topperframe.setGraphicsEffect(topperframeshadow)

        output_frame = QFrame(self)
        output_frame.setProperty('dashboardFrame', True)
        output_frame_shadow = QGraphicsDropShadowEffect()
        output_frame_shadow.setBlurRadius(5)
        output_frame_shadow.setYOffset(2)
        output_frame_shadow.setXOffset(3)
        #outputboxframe.setGraphicsEffect(outputboxframeshadow)

        output_label = QLabel(' Output: ')
        output_label.setProperty('dashboardText', True)

        logged_path = self.currpath + '/' +self.currproject + '.txt'
        self.output_box = QTextEditLogger(self, logged_path)
        logging.getLogger().addHandler(self.output_box)
        logging.getLogger().setLevel(logging.INFO)

        side_bar_frame = QFrame(self)
        side_bar_frame.setProperty('sideBarFrame', True)
        side_bar_frame_shadow = QGraphicsDropShadowEffect()
        side_bar_frame_shadow.setBlurRadius(5)
        #side_bar_frame_shadow.setColor(QtGui.QColor('#183666'))
        side_bar_frame_shadow.setYOffset(1)
        side_bar_frame_shadow.setXOffset(2)
        # side_bar_frame.setGraphicsEffect(side_bar_frame_shadow)

        self.interactive_processing = QCheckBox('Interactive Processing')
        self.interactive_processing.setChecked(True)
        self.interactive_processing.setProperty('sideBarCheckbox', True)

        process_data_label = QLabel('<b>Process Data</b>')
        process_data_label.setProperty('sideBarText', True)

        reread_button = QPushButton('Reread File')
        reread_button.setProperty('sideBarButton', True)

        refresh_button = QPushButton('Refresh Files')
        refresh_button.setProperty('sideBarButton', True)
        # refresh_button.setIcon(QIcon('roundrefresh'))

        options_label = QLabel('<b>Options</b>')
        options_label.setProperty('sideBarText', True)

        view_data_button = QPushButton('View Data')
        view_data_button.setProperty('sideBarButton', True)

        delete_data_button = QPushButton('Delete Data')
        delete_data_button.setProperty('sideBarButton', True)

        self.grid_layout.addWidget(current_project_frame, 0, 0, 5, 1)
        self.grid_layout.addWidget(side_bar_frame, 4, 0, 15, 1)

        self.grid_layout.addWidget(current_project_label, 0, 0, 2, 1, Qt.AlignCenter)
        self.grid_layout.addWidget(current_project_heading, 1, 0, 3, 1, Qt.AlignCenter)

        self.grid_layout.addWidget(process_data_label, 5, 0, Qt.AlignCenter)
        self.grid_layout.addWidget(refresh_button, 6, 0)
        self.grid_layout.addWidget(reread_button, 7, 0)

        self.grid_layout.addWidget(options_label, 9, 0, Qt.AlignCenter)
        self.grid_layout.addWidget(view_data_button, 10, 0)
        self.grid_layout.addWidget(delete_data_button, 11, 0)

        self.grid_layout.addWidget(self.interactive_processing, 17, 0, Qt.AlignHCenter)

        self.grid_layout.addWidget(top_h_frame, 0, 1, 3, 3)

        self.grid_layout.addWidget(output_frame, 3, 1, 15, 3)
        self.grid_layout.addWidget(output_label, 3, 1, 1, 2)
        self.grid_layout.addWidget(self.output_box.widget, 4, 1, 14, 3)

        reread_button.clicked.connect(self.reread)
        view_data_button.clicked.connect(self.view_data_window)
        refresh_button.clicked.connect(self.refresh)
        delete_data_button.clicked.connect(self.delete_files_window)

    def user_prompter(self):
        with open(self.params_path, 'r') as file:
            params = json.loads(file.read())
        analyses = params['analysisparams'].keys()
        anyactivated = False
        for x in analyses:
            if params['analysisparams'][x]['activated']:
                anyactivated = True

        if not anyactivated:
            logging.info("There is not any analyses currently activated, HyPro can not recognise files that need "
                         "processing if you don't activate and assign a naming nomenclature. If this is also the first "
                         "time setting up the project it would be a good idea to check Parameters, under Edit. "
                         "Don't forget to also set up the surveys required, so data can be automatically grouped for "
                         "your ease.")

    def reread(self):
        self.rereadDialog = rereadDialog(self.currpath, self.currproject, self.db,
                                         self.interactive_processing.checkState())
        self.rereadDialog.show()

    def view_data_window(self):

        with open(self.params_path, 'r') as file:
            params = json.loads(file.read())

        self.viewDataDialog = viewDataDialog(self.db, params)
        self.viewDataDialog.show()

    def refresh(self):
        self.refreshing = refreshFunction(self.currpath, self.currproject, self.interactive_processing.checkState())

    def backtomenufunction(self):
        self.backToMain.emit()

    def rmnsplots(self):
        self.rmnsWindow = qcp.rmnsPlotWindowTemplate(self.db, self.params_path)
        self.rmnsWindow.show()

    def mdlplots(self):
        #self.mdlWindow = qcp.mdlPlotWindow(self.currproject, self.currpath, self.db)
        self.mdlWindow = qcp.mdlPlotWindowTemplate(self.db, self.params_path)
        self.mdlWindow.show()

    def redfield(self):
        self.redfieldWindow = qcp.redfieldPlot(self.db)

    def salinityerror(self):
        pass

    def salinitystandards(self):
        pass

    def oxygenerror(self):
        pass

    def oxygenstandards(self):
        pass

    def produce_plots_window(self):
        self.prodplots = producePlotsDialog()
        self.prodplots.show()

    def delete_files_window(self):
        self.deletefilesdialog = deleteDialog(self.currpath, self.currproject, self.db)
        self.deletefilesdialog.show()

    def save_output_window(self):
        filedialog = QFileDialog.getSaveFileName(self, 'Save File', '', '.txt')
        if filedialog[0]:
            outputfile = open(filedialog[0] + filedialog[1], 'w')
            outputtext = self.output_box.gettext()
            outputfile.write(outputtext)
            outputfile.close()
            message_box = hyproMessageBoxTemplate('Saving Success',
                                                  'Output log was successfully saved.',
                                                  'success')

    def clear_output_function(self):
        self.output_box.clear()

    def export_data_window(self):
        self.exporter = exportDeployments(self.db)
        self.exporter.show()

    def exportuwynuts(self):
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            c.execute(
                'SELECT latitude, longitude, time, nitrate, phosphate, file '
                'FROM underwayNutrients')
            data = list(c.fetchall())
            c.close()

            format = '%d/%m/%Y %H:%M:%S'
            starttime = '01/01/2019 00:00:00'
            starttimeinseconds = calendar.timegm(time.strptime(starttime, format))

            lat = [x[0] for x in data]
            lon = [x[1] for x in data]
            timer = [(x[2] - starttimeinseconds) for x in data]
            timevals = [x[2] for x in data]
            nitrate = [x[3] for x in data]
            phos = [x[4] for x in data]
            file = [int(x[5][14:16]) for x in data]

            propath = QFileDialog.Options()
            files = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

            if files:
                preppedfile = Dataset(files + '/' + self.currproject + '.nc', 'w')

                preppedfile.description = 'in2019_v05 Underway Nutrients, Nitrate (NOx) and Phosphate ' \
                                          'analysed on Seal AA100. Time stamps are seconds since 01/01/2019 00:00 UTC.'

                vals = preppedfile.createDimension('value', len(lat))
                lats = preppedfile.createVariable('latitude', np.float64, ('value',))
                lats.units = 'decimal_deg_north'
                lons = preppedfile.createVariable('longitude', np.float64, ('value',))
                lons.units = 'decimal_deg_east'
                times = preppedfile.createVariable('time', np.int_, ('value',))
                times.units = 'utc'
                nitrates = preppedfile.createVariable('nitrate', np.float64, ('value',))
                nitrates.units = 'µM'
                phosphates = preppedfile.createVariable('phosphate', np.float64, ('value',))
                phosphates.units = 'µM'
                filesnc = preppedfile.createVariable('file', np.int32, ('value',))

                lats[:] = lat
                lons[:] = lon
                times[:] = timer
                nitrates[:] = nitrate
                phosphates[:] = phos
                filesnc[:] = file

                preppedfile.close()

        except Exception:
            print(traceback.print_exc())

    def add_guildline_analysis(self):
        self.guildline = analysisSettings(self.currproject, 'guildline', self.currpath)
        self.guildline.show()
        self.guildline.analysisSettingsUpdated.connect(self.populate_analysis_checkboxes)

    def add_seal_analysis(self):
        self.seal = analysisSettings(self.currproject, 'seal', self.currpath)
        self.seal.show()
        self.seal.analysisSettingsUpdated.connect(self.populate_analysis_checkboxes)

    def add_scripps_analysis(self):
        self.scripps = analysisSettings(self.currproject, 'scripps', self.currpath)
        self.scripps.show()
        self.scripps.analysisSettingsUpdated.connect(self.populate_analysis_checkboxes)

    def add_seasave_analysis(self):
        self.seasave = analysisSettings(self.currproject, 'seasave', self.currpath)
        self.seasave.show()
        self.seasave.analysisSettingsUpdated.connect(self.populate_analysis_checkboxes)

    def add_logsheet_analysis(self):
        self.logsheet = analysisSettings(self.currproject, 'logsheet', self.currpath)
        self.logsheet.show()
        self.logsheet.analysisSettingsUpdated.connect(self.populate_analysis_checkboxes)

    def populate_analysis_checkboxes(self):
        analyses = ['guildline', 'scripps', 'seal', 'seasave', 'logsheet']

        with open(self.params_path, 'r') as file:
            params = json.loads(file.read())

        for i in analyses:
            if params['analysisparams'][i]['activated'] == True:
                if i == 'guildline':
                    self.add_guildline_salinity.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'scripps':
                    self.add_scripps_oxygen.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'seal':
                    self.add_seal_nutrients.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'seasave':
                    self.add_seasave_ctd.setIcon(QIcon(':/assets/roundchecked.svg'))
                elif i == 'logsheet':
                    self.add_logsheet.setIcon(QIcon(':/assets/roundchecked.svg'))
            else:
                if i == 'guildline':
                    self.add_guildline_salinity.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'scripps':
                    self.add_scripps_oxygen.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'seal':
                    self.add_seal_nutrients.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'seasave':
                    self.add_seasave_ctd.setIcon(QIcon(':/assets/roundcross.svg'))
                elif i == 'logsheet':
                    self.add_logsheet.setIcon(QIcon(':/assets/roundcross.svg'))

    def survey_settings_window(self, name):
        nameinput = name
        self.addsurvey = surveyDialog(self.currproject, nameinput, self.currpath)
        self.addsurvey.show()

    def parameter_settings_window(self):
        self.paramsettings = parametersDialog(self.currproject, self.currpath)
        self.paramsettings.show()

    def populate_surveys(self):
        with open(self.params_path, 'r') as file:
            params = json.loads(file.read())

        surveys = list(params['surveyparams'].keys())

        for k in surveys:
            survey = QAction(k, self)
            survey.triggered.connect(lambda checked, k=k: self.survey_settings_window(k))
            self.survey_menu.addAction(survey)

    def about_information(self):
        message_box = hyproMessageBoxTemplate('About Hypro',
                                              'This is an experimental version of HyPro built using Python.',
                                              'about')

    def show_manual(self):
        file = 'C:/Users/she384/Documents/Tests/Manual.pdf'
        os.system('start ' + file)

    # Make parameters file if it doesn't currently exist - fill with defaults
    def make_default_params_file(self):

        """
        Create the default parameters file for analysis and processing settings.
        Pulls the default parameters from the style.py file (yes, I know, not very logical.)
        :return:
        """

        if os.path.isfile(self.params_path):
            pass
        else:
            default_params = style.default_params
            default_params['surveyparams'][f'{self.currproject}'] = default_params['surveyparams'].pop('default')

            with open('C:/HyPro/hyprosettings.json', 'r') as f:
                hyproprojs = json.load(f)
            if hyproprojs['projects'][self.currproject]['type'] == 'Shore':
                default_params['surveyparams'][self.currproject]['guildline']['ctdsurvey'] = False
                default_params['surveyparams'][self.currproject]['guildline']['decodedepfromid'] = False
                default_params['surveyparams'][self.currproject]['guildline']['usesampleid'] = True
                default_params['surveyparams'][self.currproject]['scripps']['ctdsurvey'] = False
                default_params['surveyparams'][self.currproject]['scripps']['decodedepfromid'] = False
                default_params['surveyparams'][self.currproject]['scripps']['usesampleid'] = True
                default_params['surveyparams'][self.currproject]['seal']['ctdsurvey'] = False
                default_params['surveyparams'][self.currproject]['seal']['decodedepfromid'] = False
                default_params['surveyparams'][self.currproject]['seal']['usesampleid'] = True

            with open(self.params_path, 'w') as file:
                json.dump(default_params, file)
            logging.info('Parameters file created successfully')

    def rmns_standards_window(self):
        self.rmns = rmnsDialog()
        self.rmns.show()

    def produce_stats_window(self):
        self.stats = statsDialog(self.currproject, self.db)
        self.stats.show()

    def closeEvent(self, event):
        # Closes everything if main processing window is closed
        app = QApplication.instance()
        app.closeAllWindows()
