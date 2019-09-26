import sqlite3
import time
import os
import logging
import traceback


def determine_run(file, processing_parameters):
    file_prefix_length = len(processing_parameters['analysisparams']['guildline']['filePrefix'])
    run_fomat_length = len(processing_parameters['analysisparams']['guildline']['runFormat'])
    run_number = file[file_prefix_length : (file_prefix_length + run_fomat_length)]

    return run_number


def populate_salinity_survey(sample_id, bottle_id, database_path, processing_parameters):
    deployments = []
    rosette_positions = []
    survey = []
    
    for i, s_id in enumerate(sample_id):
        b_id = bottle_id[i]
        print(s_id)
        print(b_id)
        dep, rp, surv = determine_salinity_survey(s_id, b_id, database_path, processing_parameters)
        deployments.append(dep)
        rosette_positions.append(rp)
        survey.append(surv)

    return deployments, rosette_positions, survey


def determine_salinity_survey(sample_id, bottle_id, database_path, processing_parameters):
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    surveys = list(processing_parameters['surveyparams'].keys())

    if sample_id == 'OSIL' or sample_id == '':
        deployment = 'standard'
        rosette_position = 'standard'
        survey = 'standard'
        return deployment, rosette_position, survey

    for surv in surveys:
        if processing_parameters['surveyparams'][surv]['guildline']['activated']:
            if processing_parameters['surveyparams'][surv]['guildline']['usesampleid']:

                deployment = 'usingID'
                rosette_position = 'usingID'
                survey = 'usingID'
                return deployment, rosette_position, survey
            else:
                if str(int(float(sample_id))).isdigit():
                    if processing_parameters['surveyparams'][surv]['guildline']['matchlogsheet']:

                        deployment = int(float(sample_id))
                        survey = surv + ' - Match CTD'
                        c.execute('SELECT * from logsheetData WHERE deployment=?', [deployment, ])
                        logsheet_data = list(c.fetchall())
                        if logsheet_data:
                            ros_p = [x[1] for x in logsheet_data]
                            salt_label = [x[4] for x in logsheet_data]
                            for m, label in enumerate(salt_label):
                                if bottle_id == label:
                                    rosette_position = ros_p[m]
                                    return deployment, rosette_position, survey
                        else:
                            logging.error('Logsheet data is not in the database for ' + str(sample_id))
                            break

                else:
                    if processing_parameters['surveyparams'][surv]['guildline']['decodesampleid']:
                        if processing_parameters['surveyparams'][surv]['guildline']['surveyprefix'] == sample_id[0:len(
                        processing_parameters['surveyparams'][surv]['guildline']['surveyprefix'])]:
                            survey = surv
                            if processing_parameters['surveyparams'][surv]['guildline']['decodedepfromid']:
                                dep_format = processing_parameters['surveyparams'][surv]['guildline']['depformat']
                                dep_format_length = dep_format.count('D')
                                rp_format_length = dep_format.count('B')
                                if dep_format_length > 0 and rp_format_length > 0:
                                    deployment = sample_id[len(survey): dep_format_length]
                                    rosette_position = sample_id[len(survey) + dep_format_length:]

                                    return deployment, rosette_position, survey

                            else:
                                c.execute('SELECT MAX(rosettePosition) from salinityData WHERE survey=? and sampleid!= ? ', [surv, sample_id])
                                max_rosette_position = list(c.fetchone())
                                if max_rosette_position[0]:
                                    rosette_position = max_rosette_position[0] + 1
                                else:
                                    rosette_position = 1
                                deployment = 0
                                return deployment, rosette_position, survey

def store_data(database, salinity_data, file, last_modified_time):
    try:
        run_list = [salinity_data.run for x in salinity_data.sample_id]
        flag_list = [1 for x in salinity_data.sample_id]

        packed_data = list(zip(run_list, salinity_data.sample_id, salinity_data.bottle_id, salinity_data.date_time,
                               salinity_data.uncorrected_ratio, salinity_data.uncorrected_ratio_stdev,
                               salinity_data.salinity, salinity_data.salinity_stdev, salinity_data.comments, flag_list,
                               salinity_data.deployment, salinity_data.rosette_position, salinity_data.survey))

        # Put packed up data into database file
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.executemany('INSERT OR REPLACE INTO salinityData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', packed_data)
        conn.commit()
        conn.close()

        # Put file modfied time into db as salinity file processed
        holder = ((file, last_modified_time),)
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.executemany('INSERT OR REPLACE INTO salinityFilesProcessed VALUES(?,?)', holder)
        conn.commit()
        conn.close()

        conn = sqlite3.connect(database)
        c = conn.cursor()
        processing_time = time.time()

        for i, x in enumerate(salinity_data.survey):
            if x[-9:] == 'Match CTD':
                c.execute \
                ('INSERT or REPLACE INTO ctdSalinityCalibrationData VALUES (?,?,?,?,?)',
                      (salinity_data.deployment[i], salinity_data.rosette_position[i],
                       salinity_data.salinity[i], salinity_data.quality_flag[i], processing_time))

        conn.commit()
        c.close()

        return True

    except Exception:
        logging.error(traceback.print_exc())
        return False

