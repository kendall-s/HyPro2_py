import os, logging, traceback, json, sqlite3, time
from processing.plotting.QCPlots import saltErrorPlot
import processing.RefreshFunction
import processing.procdata.ProcessGuildlineSalinity as pgs
import processing.readdata.ReadGuildlineSalinity as rgs
from dialogs.templates.MessageBoxTemplate import  hyproMessageBoxTemplate
# Loads in the salinity data from the Salinometer software, this is an excel file
# No processing needs to be done just read in and pack into the project database file


class processingSalinityWindow():
    def __init__(self, file, database, path, project, interactive, rereading):
        try:
            self.file = file
            self.database = database
            self.currpath = path
            self.currproject = project
            self.interactive = interactive
            self.rereading = rereading
            self.filepath = self.currpath + '/' + 'Salinity' + '/' + self.file

            with open(self.currpath + '/' + self.currproject + 'Params.json', 'r') as file:
                params = json.loads(file.read())

            self.salinity_data = rgs.parse_guildline_excel(self.filepath)
            print(self.salinity_data)

            if self.salinity_data:
                self.salinity_data.run = pgs.determine_run(self.file, params)
                
                self.salinity_data.deployment, self.salinity_data.rosette_position, self.salinity_data.survey = \
                    pgs.populate_salinity_survey(self.salinity_data.sample_id, self.salinity_data.bottle_id,
                                                 self.database, params)

                self.call_plot(self.salinity_data.sample_id, self.salinity_data.deployment,
                               self.salinity_data.rosette_position, self.salinity_data.salinity)

        except Exception:
            logging.error(traceback.print_exc())

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
                f'<b>The salinity file {self.file} contains CTD samples - however there is no CTD sensor data in HyPro. The file'
                ' is processed but no error plot appears because of this error. Once CTD data is imported, '
                'reprocess this file to see the error plot. </b>')
            time.sleep(0.3)
            message_box = hyproMessageBoxTemplate('HyPro - Oxygen Processing Anomaly',
                                                  f'CTD data matching results in the file {self.file} are not in HyPro.',
                                                  'information',
                                                  long_text=f'The salinity file {self.file} contains CTD samples, '
                                                            f'however there is no matching CTD sensor data in HyPro. '
                                                            f'The file is processed but no error plot appears because '
                                                            f'of this error. Once CTD data is imported, reprocess '
                                                            f'this file to see the error plot.')
            time.sleep(0.2)
            self.proceed_processing()

        else:
            ctd_salt1 = [x[8] for x in ctd_data]
            ctd_salt2 = [x[9] for x in ctd_data]
            ctd_dep = [x[0] for x in ctd_data]
            ctd_rp = [x[11] for x in ctd_data]
            print(ctd_data)
            ctd_data_to_plot = {'primary_difference': [], 'secondary_difference': [], 'dep_rosette_postion': [],
                                'rosette_positon_to_plot': []}

            for i, x in enumerate(deployments):
                for l, m in enumerate(ctd_dep):
                    if x == m:
                        if rosette_positions[i] == ctd_rp[l]:
                            ctd_data_to_plot['rosette_positon_to_plot'].append(rosette_positions[i])
                            ctd_data_to_plot['primary_difference'].append(ctd_salt1[l] - salinity[i])
                            ctd_data_to_plot['secondary_difference'].append(ctd_salt2[l] - salinity[i])
                            ctd_data_to_plot['dep_rosette_postion'].append(x + (rosette_positions[i] / 24))
            time.sleep(0.2)
            self.salinity_error_plot = saltErrorPlot(ctd_data_to_plot['dep_rosette_postion'],
                                                     ctd_data_to_plot['primary_difference'],
                                                     ctd_data_to_plot['secondary_difference'],
                                                     max(ctd_data_to_plot['dep_rosette_postion']),
                                                     self.interactive)

            self.salinity_error_plot.proceed.clicked.connect(self.proceed_processing)

    def proceed_processing(self):
        modified_time = float(os.path.getmtime(self.filepath))
        pgs.store_data(self.database, self.salinity_data, self.file, modified_time)

        logging.info('Salinity file - ' + self.file + ' successfully processed')

        if not self.rereading:
            refreshing = processing.RefreshFunction.refreshFunction(self.currpath, self.currproject, self.interactive)
