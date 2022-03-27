import json
import logging
import os
import sqlite3
import time
import traceback
from PyQt5.QtCore import pyqtSignal, QObject

import processing.procdata.ProcessGuildlineSalinity as pgs
import processing.readdata.ReadGuildlineSalinity as rgs
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
from dialogs.plotting.SalinityProcessingWindow import salinityDifferencesPlot

'''

Loads in the salinity data from the Salinometer software, this is an excel file
No processing needs to be done just parse, read in and pack into the project database file

'''

class processingSalinityWindow(QObject):

    processing_completed = pyqtSignal()

    def __init__(self, file, database, path, project, interactive, rereading):
        super().__init__()
        try:
            self.file = file
            self.database = database
            self.currpath = path
            self.currproject = project
            self.interactive = interactive
            self.rereading = rereading
            self.filepath = self.currpath + '/' + 'Salinity' + '/' + self.file

            with open(self.currpath + '/' + self.currproject + 'Params.json', 'r') as file:
                self.params = json.loads(file.read())

        except Exception:
            logging.error(traceback.print_exc())

    def process_routine(self):
        # Parse the excel file
        self.salinity_data = rgs.parse_guildline_excel(self.filepath)

        # If the correct data is found, proceed and pull out the relevant data
        if self.salinity_data:
            self.salinity_data.run = pgs.determine_run(self.file, self.params)
            self.salinity_data.file = self.file

            self.salinity_data.deployment, self.salinity_data.rosette_position, self.salinity_data.survey = \
                pgs.populate_salinity_survey(self.salinity_data.sample_id, self.salinity_data.bottle_id,
                                             self.database, self.params)

            # Plot the data for the user to see
            self.call_plot(self.salinity_data.sample_id, self.salinity_data.deployment,
                           self.salinity_data.rosette_position, self.salinity_data.salinity)

    def call_plot(self, sample_ids, deployments, rosette_positions, salinity):

        # Pull out relevant CTD data based on the samples that were analysed
        deps_set = tuple(set(sample_ids))
        queryq = '?'
        queryplace = ', '.join(queryq for unused in deps_set)

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        q = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % queryplace
        c.execute(q, deps_set)
        conn.commit()
        ctd_data = list(c.fetchall())
        conn.close()
        if not ctd_data:
            logging.info(
                f'WARNING: The salinity file {self.file} contains CTD samples - however there is no CTD sensor data in HyPro. The file'
                ' is processed but no error plot appears because of this error. Once CTD data is imported, '
                'reprocess this file to see the error plot.')
            time.sleep(0.3)
            message_box = hyproMessageBoxTemplate('HyPro - Salinity Processing Warning',
                                                  f'CTD data matching results in the file {self.file} is not in HyPro.',
                                                  'information',
                                                  long_text=f'The salinity file {self.file} contains CTD samples, '
                                                            f'however there is no matching CTD sensor data in HyPro. '
                                                            f'The file is processed but no difference plot appears because '
                                                            f'of this error. Once CTD data is imported, reprocess '
                                                            f'this file to see the error plot.')
            time.sleep(0.2)
            self.interactive = False
            self.proceed_processing()

        else:
            ctd_salt1 = [x[8] for x in ctd_data]
            ctd_salt2 = [x[9] for x in ctd_data]
            ctd_deployment = [x[0] for x in ctd_data]
            ctd_rp = [x[11] for x in ctd_data]
            ctd_depths = [x[7] for x in ctd_data]

            ctd_data_to_plot = {'primary_sal': [], 'secondary_sal': [], 'dep_rosette_postion': [],
                                'rosette_position_to_plot': [], 'deployment': [], 'depths': [], 'bottle_sal': []}

            reference_indexes = []
            for i, bottle_dep in enumerate(deployments):
                for l, ctd_dep in enumerate(ctd_deployment):
                    if bottle_dep == ctd_dep:
                        if rosette_positions[i] == ctd_rp[l]:
                            reference_indexes.append(i)
                            ctd_data_to_plot['bottle_sal'].append(salinity[i])
                            ctd_data_to_plot['deployment'].append(bottle_dep)
                            ctd_data_to_plot['depths'].append(ctd_depths[l])
                            ctd_data_to_plot['rosette_position_to_plot'].append(rosette_positions[i])
                            ctd_data_to_plot['primary_sal'].append(ctd_salt1[l])
                            ctd_data_to_plot['secondary_sal'].append(ctd_salt2[l])

            if max(ctd_data_to_plot['rosette_position_to_plot']) > 24:
                max_rp = 36
            else:
                max_rp = 24

            # Create the X data for the plot - x data is calculated as RP times Deployment, meaning x data will
            # go up continually from 1. i.e. deployment 2 RP 5 will equal x data of 41
            ctd_data_to_plot['dep_rosette_position'] = [(((x - 1) * max_rp) + ctd_data_to_plot['rosette_position_to_plot'][i])
                                                        for i, x in enumerate(ctd_data_to_plot['deployment'])]

            time.sleep(0.2)
            self.salinity_error_plot = salinityDifferencesPlot(ctd_data_to_plot['deployment'],
                                                               ctd_data_to_plot['dep_rosette_position'],
                                                               ctd_data_to_plot['bottle_sal'],
                                                               ctd_data_to_plot['primary_sal'],
                                                               ctd_data_to_plot['secondary_sal'],
                                                               ctd_data_to_plot['depths'],
                                                               max_rp,
                                                               reference_indexes,
                                                               self.salinity_data)

            self.salinity_error_plot.proceed.clicked.connect(self.proceed_processing)

    def proceed_processing(self):
        modified_time = float(os.path.getmtime(self.filepath))

        # Pull through the edited flags from the interactive plot
        if self.interactive:
            edited_flags = self.salinity_error_plot.working_quality_flags
            self.salinity_data.quality_flag = edited_flags

        pgs.store_data(self.database, self.salinity_data, self.file, modified_time)

        logging.info('Salinity file - ' + self.file + ' successfully processed')

        if not self.rereading:
            self.processing_completed.emit()
