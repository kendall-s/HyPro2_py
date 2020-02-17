import json
import logging
import os
import sqlite3
import time
import traceback

import processing.RefreshFunction
import processing.procdata.ProcessScrippsOxygen as pso
import processing.readdata.ReadScrippsOxygen as rso
from dialogs.templates.MessageBoxTemplate import hyproMessageBoxTemplate
from processing.plotting.QCPlots import oxygenErrorPlot


class processingOxygenWindow():
    def __init__(self, file, database, path, project, interactive, rereading):
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
                params = json.loads(file.read())

            self.oxygen_data = rso.parse_lst(self.file_path, self.current_path, self.current_project, self.file)

            if self.oxygen_data:

                self.oxygen_data.deployment, self.oxygen_data.rosette_position, self.oxygen_data.survey = \
                pso.populate_oxygen_survey(self.oxygen_data.station, self.oxygen_data.cast,
                                           self.oxygen_data.rosette, self.oxygen_data.bottle_id,
                                           self.database, params)

                self.call_plot(self.oxygen_data)

        except Exception:
            traceback.print_exc()

    def call_plot(self, oxygen_data):

        deployments = tuple(set(oxygen_data.station))

        built_query = ', '.join('?' for dep in deployments)

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        query = 'SELECT * FROM ctdData WHERE deployment IN (%s)' % built_query
        c.execute(query, deployments)

        ctd_data = list(c.fetchall())

        if not ctd_data:
            logging.info(f'<b>The oxygen file {self.file} contains CTD samples - however there is no CTD sensor data in HyPro. The file'
                         ' is processed but no error plot appears because of this error. Once CTD data is imported, '
                         'reprocess this file to see the error plot. </b>')
            time.sleep(0.3)
            message_box = hyproMessageBoxTemplate('HyPro - Oxygen Processing Anomaly',
                                                  f'CTD data matching results in the file {self.file} are not in HyPro.',
                                                  'information',
                                                  long_text=f'The oxygen file {self.file} contains CTD samples, '
                                                            f'however there is no matching CTD sensor data in HyPro. '
                                                            f'The file is processed but no error plot appears because '
                                                            f'of this error. Once CTD data is imported, reprocess '
                                                            f'this file to see the error plot.')

            self.proceed_processing()

        else:
            oxygen_sensor_1 = [x[5] for x in ctd_data]
            oxygen_sensor_2 = [x[6] for x in ctd_data]
            ctd_deployment = [x[0] for x in ctd_data]
            ctd_rosette_positions = [x[11] for x in ctd_data]

            ctd_data_to_plot = {'primary_difference': [], 'secondary_difference': [], 'dep_rosette_postion': [],
                                'rosette_position_to_plot': []}

            for i, x in enumerate(oxygen_data.station):
                for l, m in enumerate(ctd_deployment):
                    if x == m:
                        if oxygen_data.rosette[i] == ctd_rosette_positions[l]:
                            ctd_data_to_plot['rosette_position_to_plot'].append(oxygen_data.rosette[i])
                            ctd_data_to_plot['primary_difference'].append(oxygen_sensor_1[l] - oxygen_data.oxygen_mols[i])
                            ctd_data_to_plot['secondary_difference'].append(oxygen_sensor_2[l] - oxygen_data.oxygen_mols[i])
                            ctd_data_to_plot['dep_rosette_postion'].append(x + (oxygen_data.rosette[i] / 24))

            self.oxygen_error_plot = oxygenErrorPlot(ctd_data_to_plot['dep_rosette_postion'],
                                                     ctd_data_to_plot['primary_difference'],
                                                     ctd_data_to_plot['secondary_difference'],
                                                     max(ctd_data_to_plot['rosette_position_to_plot']),
                                                     self.interactive)

            self.oxygen_error_plot.proceed.clicked.connect(self.proceed_processing)

    def proceed_processing(self):

        last_modified_time = float(os.path.getmtime(self.file_path))

        pso.store_data(self.database, self.oxygen_data, self.file, last_modified_time)

        logging.info('Oyxgen file - ' + self.file + ' successfully processed')

        if not self.rereading:
            refreshing = processing.RefreshFunction.refreshFunction(self.current_path, self.current_project, self.interactive)
