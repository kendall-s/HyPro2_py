import json
import logging
import os
import sqlite3
import time
import traceback
from PyQt5.QtCore import pyqtSignal, QObject

import processing.RefreshFunction
import processing.procdata.ProcessScrippsOxygen as pso
import processing.readdata.ReadScrippsOxygen as rso
from processing.algo.HyproComplexities import get_max_rp
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
from processing.plotting.OxygenProcessingWindow import oxygenDifferencesPlot


class processingOxygenWindow(QObject):

    processing_completed = pyqtSignal()

    def __init__(self, file, database, path, project, interactive, rereading):
        super().__init__()
        try:
            self.processing = True

            self.file = file
            self.database = database
            self.current_path = path
            self.current_project = project
            self.interactive = interactive
            self.rereading = rereading
            self.file_path = self.current_path + '/' + 'Oxygen' + '/' + self.file

            with open(self.current_path + '/' + self.current_project + 'Params.json', 'r') as file:
                self.params = json.loads(file.read())

            self.process_routine()

        except Exception:
            traceback.print_exc()

    def process_routine(self):

        # Parse in the oxygen LST file
        self.oxygen_data = rso.parse_lst(self.file_path, self.current_path, self.current_project, self.file)

        if self.oxygen_data:
            self.oxygen_data.deployment, self.oxygen_data.rosette_position, self.oxygen_data.survey = \
                pso.populate_oxygen_survey(self.oxygen_data.station, self.oxygen_data.cast,
                                           self.oxygen_data.niskin, self.oxygen_data.bottle_id,
                                           self.database, self.params)
            if self.interactive:
                self.call_plot(self.oxygen_data)
            else:
                self.proceed_processing()

    def call_plot(self, oxygen_data):

        deployments = tuple(set(oxygen_data.station))

        built_query = ', '.join('?' for dep in deployments)

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        query = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % built_query
        c.execute(query, deployments)
        ctd_data = list(c.fetchall())
        conn.close()

        deps_comparison = [x for x in deployments if x < 900]

        # If there is not the correct CTD burst data in HyPro raise this warning - plot will not be created.
        if not ctd_data or sum(deps_comparison) != sum(set([x[0] for x in ctd_data])):
            logging.info(f'<b>The oxygen file {self.file} contains CTD samples - however there is no CTD sensor data in HyPro. The file'
                         ' is processed but no error plot appears because of this error. Once CTD data is imported, '
                         'reprocess this file to see the error plot. </b>')
            time.sleep(0.3)
            message_box = hyproMessageBoxTemplate('HyPro - Oxygen Processing Anomaly',
                                                  f'CTD data matching results in the file {self.file} are not in HyPro.',
                                                  'information',
                                                  long_text=f'The oxygen file {self.file} contains CTD samples, '
                                                            f'however there is no matching CTD sensor data in HyPro. '
                                                            f'The file is processed but no plot appears because of this '
                                                            f'error. Once CTD deployment {deps_comparison} data is '
                                                            f'imported, reprocess this file to see the error plot.')
            time.sleep(0.2)
            self.proceed_processing()

        else:
            oxygen_sensor_1 = [x[5] for x in ctd_data]
            oxygen_sensor_2 = [x[6] for x in ctd_data]
            ctd_deployment = [x[0] for x in ctd_data]
            ctd_rosette_positions = [x[11] for x in ctd_data]
            ctd_depths = [x[7] for x in ctd_data]

            ctd_data_to_plot = {'primary_oxygen': [], 'secondary_oxygen': [], 'dep_rosette_postion': [],
                                'rosette_position_to_plot': [], 'deployment': [], 'depths': [], 'bottle_oxy': []}

            # Need to keep a reference to the original indexes so that flags can be pulled back and updated
            reference_indexes = []

            # Got to match the bottle data up to the CTD burst data, keep a reference index back to the original file
            # data so that flags can be replaced back into the data after processing.
            for i, x in enumerate(oxygen_data.station):
                for l, m in enumerate(ctd_deployment):
                    if x == m:
                        if oxygen_data.niskin[i] == ctd_rosette_positions[l]:
                            reference_indexes.append(i)
                            ctd_data_to_plot['bottle_oxy'].append(oxygen_data.oxygen_mols[i])
                            ctd_data_to_plot['deployment'].append(x)
                            ctd_data_to_plot['rosette_position_to_plot'].append(oxygen_data.rosette_position[i])
                            ctd_data_to_plot['depths'].append(ctd_depths[l])
                            ctd_data_to_plot['primary_oxygen'].append(oxygen_sensor_1[l])
                            ctd_data_to_plot['secondary_oxygen'].append(oxygen_sensor_2[l])

            max_rp = get_max_rp(ctd_data_to_plot['rosette_position_to_plot'])

            # Create the X data for the plot - x data is calculated as RP times Deployment + max RP, meaning x data will
            # go up continually from 1. i.e. deployment 2 RP 5 will equal x data of 41
            ctd_data_to_plot['dep_rosette_postion'] = [(((x-1) * max_rp) + ctd_data_to_plot['rosette_position_to_plot'][i])
                                                       for i, x in enumerate(ctd_data_to_plot['deployment'])]

            time.sleep(0.2)
            self.oxygen_error_plot = oxygenDifferencesPlot(ctd_data_to_plot['deployment'],
                                                           ctd_data_to_plot['dep_rosette_postion'],
                                                           ctd_data_to_plot['bottle_oxy'],
                                                           ctd_data_to_plot['primary_oxygen'],
                                                           ctd_data_to_plot['secondary_oxygen'],
                                                           ctd_data_to_plot['depths'],
                                                           max_rp,
                                                           reference_indexes,
                                                           oxygen_data)

            self.oxygen_error_plot.proceed.clicked.connect(self.proceed_processing)

    def proceed_processing(self):
        last_modified_time = float(os.path.getmtime(self.file_path))

        # Pull through the edited flags from the interactive plot
        if self.interactive:
            edited_flags = self.oxygen_error_plot.working_quality_flags
            self.oxygen_data.quality_flag = edited_flags

        pso.store_data(self.database, self.oxygen_data, self.file, last_modified_time)

        logging.info('Oyxgen file - ' + self.file + ' successfully processed')

        if not self.rereading:
            self.processing_completed.emit()
