import os, sqlite3, logging, json, traceback
from processing.readdata import InitialiseCTDData, InitialiseSampleSheet
from processing.procdata.InteractiveOxygenProcessing import processingOxygenWindow
from processing.procdata.InteractiveSalinityProcessing import processingSalinityWindow
from processing.procdata.InteractiveNutrientsProcessing import processingNutrientsWindow

# TODO: there is potentially a small bug that occurs when refresh of multiple files and then they dont process

# Provides the functionality for finding new or updated files that need to be processed when hypro is 'refreshed'
class refreshFunction():
    def __init__(self, path, project, interactive):

        self.currpath = path
        self.currproject = project
        self.interactive = interactive

        self.db = (self.currpath + '/' + self.currproject + 'Data.db')

        self.refresh()

    def refresh(self):
        with open(self.currpath + '/' + '%sParams.json' % self.currproject, 'r') as file:
            self.params = json.loads(file.read())

        # The order is important as it finds CTD first, then sampling sheet then processes files
        differentfoldertypes = ['CTD', 'Sampling', 'Salinity', 'Oxygen', 'Nutrients']
        procfile = False
        try:
            for folder in differentfoldertypes:
                filesindirec = []

                # Little special method for nutrients so it only selects the .SLK files in the folder
                if folder == 'Nutrients':
                    for file in os.listdir(self.currpath + '/' + folder):
                        if file.endswith('.SLK') or file.endswith('.slk'):
                            filesindirec.append(file)
                else:
                    filesindirec = os.listdir(self.currpath + '/' + folder)

                # print(filesindirec)

                # Load up database where files already processed are stored
                conn = sqlite3.connect(self.db)
                c = conn.cursor()

                if folder == 'CTD':
                    c.execute('SELECT * from ctdFilesProcessed')
                if folder == 'Nutrients':
                    c.execute('SELECT * from nutrientFilesProcessed')
                if folder == 'Salinity':
                    c.execute('SELECT * from salinityFilesProcessed')
                if folder == 'Oxygen':
                    c.execute('SELECT * from oxygenFilesProcessed')
                if folder == 'Sampling':
                    c.execute('SELECT * from logsheetFilesProcessed')
                data = list(c.fetchall())
                c.close()

                # Get the filenames and modified times that were stored in the database
                filenames = [x[0] for x in data]
                timemodified = [x[1] for x in data]

                # Go through each file and determine if it is in the database and if it has changed
                # Not sure why I used o as the file name
                for file in filesindirec:
                    if file != 'Hidden' or file != 'hidden':
                        if file not in filenames:
                            # Most likely first time processing this file
                            if folder == 'CTD' and self.params['analysisparams']['seasave']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['seasave']['runFormat']) + 4)
                                if file[: neglen] == self.params['analysisparams']['seasave']['filePrefix']:
                                    logging.info('CTD File - ' + file + ' not in database')
                                    self.initctddata = InitialiseCTDData.initCTDdata(file,
                                                                                     self.db,
                                                                                     self.currpath, self.currproject,
                                                                                     self.interactive, False)
                                    procfile = True

                                else:
                                    logging.info('%s does not match analysis settings' % file)

                            if folder == 'Nutrients' and self.params['analysisparams']['seal']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['seal']['runFormat']) + 4)
                                if file[: neglen] == self.params['analysisparams']['seal']['filePrefix']:
                                    logging.info('Nutrient file - ' + file + ' found. Not yet in database.')
                                    self.initnutrientdata = processingNutrientsWindow(file,self.db,
                                                                                      self.currpath, self.currproject,
                                                                                      self.interactive, False)
                                    procfile = True
                                    break
                                else:
                                    logging.info('%s does not match analysis settings' % file)

                            if folder == 'Salinity' and self.params['analysisparams']['guildline']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['guildline']['runFormat']) + 5)
                                if file[: neglen] == self.params['analysisparams']['guildline']['filePrefix']:
                                    logging.info('Salinity file - ' + file + ' found. Not yet in database.')
                                    self.initsaltdata = processingSalinityWindow(file,
                                                                                 self.db,
                                                                                 self.currpath,
                                                                                 self.currproject,
                                                                                 self.interactive,
                                                                                 False)
                                    procfile = True
                                    break
                                else:
                                    logging.info('%s does not match analysis settings' % file)

                            if folder == 'Oxygen' and self.params['analysisparams']['scripps']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['scripps']['runFormat']) + 4)
                                if file[: neglen] == self.params['analysisparams']['scripps']['filePrefix']:
                                    logging.info('Oxygen file - ' + file + ' found. Not yet in database.')
                                    self.initoxydata = processingOxygenWindow(file, self.db, self.currpath,
                                                                              self.currproject,
                                                                              self.interactive, False)

                                    procfile = True
                                    break
                                else:
                                    logging.info('%s does not match analysis settings' % file)

                            if folder == 'Sampling' and self.params['analysisparams']['logsheet']['activated'] == True:
                                neglen = -(len(self.params['analysisparams']['logsheet']['runFormat']) + 5)
                                if file[: neglen] == self.params['analysisparams']['logsheet']['filePrefix']:
                                    logging.info('Logsheet file - ' + file + ' found. Not yet in database.')
                                    self.initsampledata = InitialiseSampleSheet.initSampleSheet(file,
                                                                                                self.currproject,
                                                                                                self.db,
                                                                                                self.currpath,
                                                                                                self.interactive,
                                                                                                False)
                                    procfile = True
                                    break
                                else:
                                    logging.info('%s does not match analysis settings' % file)

                        else:
                            # Check if file has been updated
                            for count, p in enumerate(filenames):
                                if file == p:
                                    # Has been processed but check if date modified has changed
                                    time = os.path.getmtime(self.currpath + '/' + folder + '/' + file)
                                    if time == timemodified[count]:
                                        # print('File has not changed') # I don't think this will ever be reached...
                                        print('')
                                    else:
                                        if folder == 'CTD':
                                            logging.info(
                                                'CTD file - ' + file + ' has been updated. It will be reprocessed.')
                                            self.initctddata = InitialiseCTDData.initCTDdata(file,
                                                                                             self.db,
                                                                                             self.currpath,
                                                                                             self.currproject,
                                                                                             self.interactive, False)
                                            procfile = True
                                            break
                                        if folder == 'Nutrients':
                                            logging.info(
                                                'Nutrient file - ' + file + ' has been updated. It will be reprocessed.')
                                            self.initnutrientdata = processingNutrientsWindow(file, self.db,
                                                                                              self.currpath,
                                                                                              self.currproject,
                                                                                              self.interactive, False)
                                            procfile = True
                                            break
                                        if folder == 'Salinity':
                                            logging.info(
                                                'Salinity file - ' + file + ' has been updated. It will be reprocessed.')
                                            self.initsaltdata = processingSalinityWindow(file, self.db,
                                                                                         self.currpath,
                                                                                         self.currproject,
                                                                                         self.interactive,
                                                                                         False)
                                            procfile = True
                                            break

                                        if folder == 'Oxygen':
                                            logging.info(
                                                'Oxygen file - ' + file + ' has been updated. It will be reprocessed.')
                                            self.initoxydata = processingOxygenWindow(file, self.db, self.currpath,
                                                                                      self.currproject,
                                                                                      self.interactive, False)
                                            procfile = True
                                            break
                                        if folder == 'Sampling':
                                            logging.info(
                                                'Logsheet file - ' + file + ' has been updated. It will be reprocessed.')
                                            self.initsampledata = InitialiseSampleSheet.initSampleSheet(file,
                                                                                                        self.currproject,
                                                                                                        self.db,
                                                                                                        self.currpath,
                                                                                                        self.interactive,
                                                                                                        False)
                                            procfile = True
                if procfile:
                    break
            if not procfile:
                logging.info('No new files to process')

        except Exception:
            logging.error(traceback.print_exc())
            print(traceback.print_exc())
