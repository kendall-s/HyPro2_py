import sqlite3
import os
import logging
import time
# TODO: Redo processing to split more down into smaller TESTABLE functions


def store_data(database, oxygen_data, file, last_modified_time):

    conn = sqlite3.connect(database)
    c = conn.cursor()
    run_list = [oxygen_data.run for x in oxygen_data.station]

    submit = zip(run_list, oxygen_data.station, oxygen_data.cast, oxygen_data.rosette,
                 oxygen_data.bottle_id, oxygen_data.flask_vol, oxygen_data.raw_titer, oxygen_data.titer,
                 oxygen_data.oxygen, oxygen_data.oxygen_mols, oxygen_data.thio_temp, oxygen_data.draw_temp,
                 oxygen_data.final_volts, oxygen_data.time, oxygen_data.quality_flag, oxygen_data.deployment,
                 oxygen_data.rosette_position, oxygen_data.survey)

    c.executemany('INSERT OR REPLACE INTO oxygenData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', submit)
    conn.commit()
    conn.close()

    holder = ((file, last_modified_time),)

    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.executemany('INSERT OR REPLACE INTO oxygenFilesProcessed VALUES(?,?)', holder)
    conn.commit()
    conn.close()

    process_time = time.time()
    conn = sqlite3.connect(database)
    c = conn.cursor()
    for i, x in enumerate(oxygen_data.survey):
        if x[-9:] == 'Match CTD':
            submit = (oxygen_data.deployment[i], oxygen_data.rosette_position[i],
                      oxygen_data.oxygen_mols[i], oxygen_data.quality_flag[i], process_time)
            c.execute('INSERT OR REPLACE INTO ctdOxygenCalibrationData VALUES (?,?,?,?,?)', submit)

    conn.commit()
    conn.close()

def populate_oxygen_survey(station, cast, rosp, bottle_id, database_path, processing_parameters):
    deployments = []
    rosette_positions = []
    survey = []

    for i, b_id in enumerate(bottle_id):

        dep, rp, surv = determine_oxygen_survey(station[i], cast[i], rosp[i], b_id, database_path, processing_parameters)

        deployments.append(dep)
        rosette_positions.append(rp)
        survey.append(surv)

    return deployments, rosette_positions, survey


def determine_oxygen_survey(station, cast, rp, bottle_id, database_path, processing_parameters):

    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    surveys = list(processing_parameters['surveyparams'].keys())

    for surv in surveys:
        if station < 900:
            if processing_parameters['surveyparams'][surv]['scripps']['ctdsurvey']:
                deployment = station
                rosette_position = rp
                c.execute('SELECT oxygen from logsheetData WHERE deployment=? AND rosettePosition=?', [deployment, rosette_position])
                logsheet_bottle = c.fetchone()

                if logsheet_bottle[0] == bottle_id:
                    survey = surv + ' - Match CTD'

                    return deployment, rosette_position, survey
                else:
                    logging.error('Oxygen bottle '+str(bottle_id)+' does not match position entered on sampling logsheet for deployment ' + str(deployment))
                    return None

        else:
            if processing_parameters['surveyparams'][surv]['scripps']['decodesampleid']:
                survey_prefix = processing_parameters['surveyparams'][surv]['scripps']['surveyprefix']
                if station == int(survey_prefix):
                    survey = surv
                    if processing_parameters['surveyparams'][surv]['scripps']['decodedepfromid']:
                        deployment = cast
                        rosette_position = rp
                        return deployment, rosette_position, survey
                    else:
                        deployment = surv
                        rosette_position = rp * cast
                        return deployment, rosette_position, survey

    logging.error(f'Oxygen sample {bottle_id} does not match any surveys - please add a matching survey to process.')
    return None
