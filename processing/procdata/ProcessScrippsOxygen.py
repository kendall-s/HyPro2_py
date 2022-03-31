import sqlite3
import os
import logging
import time
# TODO: Redo processing to split more down into smaller TESTABLE functions


def store_data(database, oxygen_data, file, last_modified_time):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    run_list = [oxygen_data.run for x in oxygen_data.station]

    submit = zip(run_list, oxygen_data.station, oxygen_data.cast, oxygen_data.niskin,
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
        if oxygen_data.deployment[i] != 'Unknown' and oxygen_data.rosette_position[i] != 'Unknown':
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
    surveys = list(processing_parameters['survey_params'].keys())

    # Iterate through the different surveys
    for surv in surveys:
        # Anything above station 900 is likely a custom survey not a CTD
        if station < 900:
            # If this current survey is activated as a CTD survey
            if processing_parameters['survey_params'][surv]['scripps']['ctd_survey']:
                deployment = station
                rosette_position = rp
                # Try to match the oxygen samples to the logsheet data if it is a CTD
                c.execute('SELECT oxygen from logsheetData WHERE deployment=? AND rosettePosition=?', [deployment, rosette_position])
                logsheet_bottle = c.fetchone()

                if logsheet_bottle[0] == bottle_id:
                    survey = surv

                    return deployment, rosette_position, survey
                else:
                    logging.error('Oxygen bottle '+str(bottle_id)+' does not match position entered on sampling logsheet for deployment ' + str(deployment))
                    return None

        else:
            # Above 900 on the station will have to match to a custom survey
            if processing_parameters['survey_params'][surv]['scripps']['decode_sample_id']:
                # Get the survey prefix and check if it matches the entered station
                survey_prefix = processing_parameters['survey_params'][surv]['scripps']['survey_prefix']
                if station == int(survey_prefix):
                    survey = surv
                    if processing_parameters['survey_params'][surv]['scripps']['decode_dep_from_id']:
                        deployment = cast
                        rosette_position = rp
                        return deployment, rosette_position, survey
                    else:
                        deployment = surv
                        rosette_position = rp * cast
                        return deployment, rosette_position, survey

    logging.error(f'Oxygen sample {bottle_id} does not match any surveys - please add a matching survey to process.')
    return None
