import os, sqlite3, logging, json, traceback
from time import sleep
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from processing.readdata import InitialiseCTDData, InitialiseSampleSheet
from processing.procdata.InteractiveOxygenProcessing import processingOxygenWindow
from processing.procdata.InteractiveSalinityProcessing import processingSalinityWindow
from processing.procdata.InteractiveNutrientsProcessing import processingNutrientsWindow

# TODO: there is potentially a small bug that occurs when refresh of multiple files and then they dont process

# Provides the functionality for finding new or updated files that need to be processed when hypro is 'refreshed'
class refreshFunction(QObject):

    files_found_signal = pyqtSignal(dict)

    def __init__(self, path, project):
        super().__init__()
        self.currpath = path
        self.currproject = project


        self.db = (self.currpath + '/' + self.currproject + 'Data.db')

        self.files_found = {'CTD': [], 'Sampling': [], 'Salinity': [], 'Oxygen': [], 'Nutrients': []}

    def refresh(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            self.params = json.loads(file.read())

        # The order is important as it finds CTD first, then sampling sheet then processes files
        different_folder_types = ['CTD', 'Sampling', 'Salinity', 'Oxygen', 'Nutrients']
        db_name_folder_converter = {'CTD': 'ctd', 'Sampling': 'logsheet', 'Salinity': 'salinity', 'Oxygen': 'oxygen',
                                    'Nutrients': 'nutrient'}
        procfile = False
        try:
            for folder in different_folder_types:
                files_in_directory = []

                # Little special method for nutrients so it only selects the .SLK files in the folder
                if folder == 'Nutrients':
                    for file in os.listdir(self.currpath + '/' + folder):
                        if file.endswith('.SLK') or file.endswith('.slk'):
                            files_in_directory.append(file)
                else:
                    files_in_directory = os.listdir(self.currpath + '/' + folder)

                # Load up database where files already processed are stored
                conn = sqlite3.connect(self.db)
                c = conn.cursor()
                # Pull the processed files from each table
                c.execute(f'SELECT * from {db_name_folder_converter[folder]}FilesProcessed')

                data = list(c.fetchall())
                c.close()

                # Get the processed_file_names and modified times that were stored in the database
                processed_file_names = [x[0] for x in data]
                time_modified = [x[1] for x in data]

                # Go through each file and determine if it is in the database and if it has changed
                for file in files_in_directory:
                    if (file != 'Hidden' or file != 'hidden') & (not procfile):
                        file_last_modified_time = os.path.getmtime(self.currpath + '/' + folder + '/' + file)
                        file_changed = False
                        # Lets just check if the file has already been processed, if it has, just double check it
                        # if it has or not been updated
                        if (file in processed_file_names):
                            for ind, procd_file in enumerate(processed_file_names):
                                if file == procd_file:
                                    if file_last_modified_time != time_modified[ind]:
                                        file_changed = True

                        if (file not in processed_file_names) or file_changed:

                            if folder == 'CTD' and self.params['analysisparams']['seasave']['activated'] == True:
                                run_format_length = -(len(self.params['analysisparams']['seasave']['runFormat']) + 4)
                                if file[: run_format_length] == self.params['analysisparams']['seasave']['filePrefix']:
                                    logging.info(f'Nutrient file {file} found. Not yet in database.')
                                    self.files_found['CTD'].append(file)
                                else:
                                    logging.info(f'{file} does not match analysis settings')

                            if folder == 'Nutrients' and self.params['analysisparams']['seal']['activated'] == True:
                                run_format_length = -(len(self.params['analysisparams']['seal']['runFormat']) + 4)
                                if file[: run_format_length] == self.params['analysisparams']['seal']['filePrefix']:
                                    logging.info(f'Nutrient file {file} found. Not yet in database.')
                                    self.files_found['Nutrients'].append(file)
                                else:
                                    logging.info(f'{file} does not match analysis settings')

                            if folder == 'Salinity' and self.params['analysisparams']['guildline']['activated'] == True:
                                run_format_length = -(len(self.params['analysisparams']['guildline']['runFormat']) + 5)
                                if file[: run_format_length] == self.params['analysisparams']['guildline']['filePrefix']:
                                    logging.info(f'Salinity file {file} found. Not yet in database.')
                                    self.files_found['Salinity'].append(file)
                                else:
                                    logging.info(f'{file} does not match analysis settings')

                            if folder == 'Oxygen' and self.params['analysisparams']['scripps']['activated'] == True:
                                run_format_length = -(len(self.params['analysisparams']['scripps']['runFormat']) + 4)
                                if file[: run_format_length] == self.params['analysisparams']['scripps']['filePrefix']:
                                    logging.info(f'Oxygen file {file} found. Not yet in database.')
                                    self.files_found['Oxygen'].append(file)
                                else:
                                    logging.info(f'{file} does not match analysis settings')

                            if folder == 'Sampling' and self.params['analysisparams']['logsheet']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['logsheet']['runFormat']) + 5)
                                if file[: neglen] == self.params['analysisparams']['logsheet']['filePrefix']:
                                    logging.info('Logsheet file - ' + file + ' found. Not yet in database.')
                                    self.files_found['Sampling'].append(file)
                                else:
                                    logging.info('%s does not match analysis settings' % file)
                if procfile:
                    break
            # if not procfile:
            #     logging.info('No new files to process')
            self.files_found_signal.emit(self.files_found)

        except Exception:
            pass
            #logging.error(traceback.print_exc())
            print(traceback.print_exc())
