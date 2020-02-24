import sqlite3, logging, traceback, json

# This file contains some more of the complicated functions that are required for hypro, namely determining a survey..

# TODO: delete determineSurvey, split this into the processing scripts of each analyte
def determineSurvey(database, params, analyte, sampleid, bottleid = None):
    try:
        #print(sampleid)
        conn = sqlite3.connect(database)
        c = conn.cursor()

        surveys = list(params['surveyparams'].keys())

        # Dealing with the edge cases that crop up, these are mostly accounted for
        if analyte == 'guildline':
            if sampleid == 'OSIL' or sampleid == '':
                deployment = 'standard'
                rosettepos = 'standard'
                survey = 'standard'
                return deployment, rosettepos, survey

        if analyte == 'seal':
            qctypes = list(params['nutrientprocessing']['qcsamplenames'].keys())

            if sampleid[0:4] == 'Test' or sampleid[0:4] == 'test': # TODO: change to regex
                deployment = 'testdata'
                rosettepos = 'testdata'
                survey = 'test'
                return deployment, rosettepos, survey
            for x in qctypes: # The QC types are samples, so pull them out now
                if params['nutrientprocessing']['qcsamplenames'][x] in sampleid:
                    deployment = x
                    rosettepos = x
                    survey = x
                    return deployment, rosettepos, survey

        # Cycle through the survey groupings to match the SAMPLE ID to a corresponding survey
        for x in surveys:
            if analyte == 'guildline' and bottleid:
                if params['surveyparams'][x][analyte]['activated']:
                    if params['surveyparams'][x][analyte]['usesampleid']:
                        return 'usingID', 'usingID', 'usingID'
                    else:
                        if str(sampleid).isdigit(): # check if sample id is just digits aka deployment
                        # if not re.search('[a-zA-Z]', sampleid):  # Check if it is a digit - match to deployment if it is
                            if params['surveyparams'][x][analyte]['matchlogsheet']:
                                survey = x
                                deployment = sampleid
                                c.execute('SELECT * from logsheetData WHERE deployment=?', [deployment,])
                                deps = list(c.fetchall())
                                if deps:
                                    rps = [x[1] for x in deps]
                                    sallabel = [x[4] for x in deps]
                                    for m, l in enumerate(sallabel):
                                        if bottleid == l:
                                            rosettepos = rps[m]
                                            return deployment, rosettepos, survey
                                        #else:
                                        #    logging.error('Cannot match a salinity bottle label %s to the logsheet, '
                                        #                  'check what is entered in the sample sheet and excel' % bottleid)
                                        #    break
                                else:
                                    logging.info(
                                        "Can't find details in sampling logsheet for salt result: " + sampleid + ' / ' +
                                        bottleid + ' please enter this in a sampling logsheet')
                                    return None

                        else:
                            if params['surveyparams'][x][analyte]['decodesampleid']:
                                if params['surveyparams'][x][analyte]['surveyprefix'] == sampleid[0:len(
                                        params['surveyparams'][x][analyte]['surveyprefix'])]:
                                    survey = x
                                    if params['surveyparams'][x][analyte]['decodedepfromid']:
                                        depformat = params['surveyparams'][x][analyte]['depformat']
                                        depformatlength = depformat.count('D')
                                        rpformatlength = depformat.count('B')
                                        if depformatlength > 0:
                                            deployment = sampleid[len(survey):depformatlength]
                                            rosettepos = sampleid[len(survey)+depformatlength:]

                                            return deployment, rosettepos, survey

                                    else:
                                        c.execute('SELECT MAX(rosettePosition) from salinityData WHERE survey=? '
                                                  'and sampleid!= ? ', [x, sampleid])
                                        maxrp = list(c.fetchone())
                                        if maxrp[0]:
                                            rosettepos = maxrp[0] + 1
                                        else:
                                            rosettepos = 1
                                        deployment = 99999
                                        return deployment, rosettepos, survey
            if analyte == 'seal':
                if params['surveyparams'][x][analyte]['activated']:
                    if params['surveyparams'][x][analyte]['usesampleid']:
                        return 'usingID', 'usingID', 'usingID'
                    else:
                        if str(sampleid).isdigit(): # CTD sample is only numbers in name
                            if params['surveyparams'][x][analyte]['matchlogsheet']:
                                survey = x
                                if params['surveyparams'][x][analyte]['decodedepfromid']:
                                    depformat = params['surveyparams'][x][analyte]['depformat']
                                    depformatlength = depformat.count('D')
                                    rpformatlength = depformat.count('B')
                                    if depformatlength > 0:
                                        deployment = sampleid[0:depformatlength]
                                        rosettepos = sampleid[depformatlength:(depformatlength+rpformatlength)]

                                        return deployment, rosettepos, survey
                                else:
                                    print('TODO pull dep/rp from logsheet instead')
                                    # TODO: pull dep/rp from logsheet option
                        else:   # Sample id has more than just numbers in it
                            if params['surveyparams'][x][analyte]['decodesampleid']: # Decode the sample ID, needs a prefix too
                                surveyprefix = params['surveyparams'][x][analyte]['surveyprefix']
                                if len(params['surveyparams'][x][analyte]['surveyprefix']) > 0: # Check theres actually a prefix
                                    sampleprefix = sampleid[0:len(params['surveyparams'][x][analyte]['surveyprefix'])]
                                    if surveyprefix == sampleprefix:
                                        survey = x
                                    else:
                                        logging.error('Sample: ' + str(sampleid) + ' does not match existing surveys.')
                                        break
                                    if params['surveyparams'][x][analyte]['decodedepfromid']: # Decode a dep/rp
                                        depformat = params['surveyparams'][x][analyte]['depformat']
                                        depformatlength = depformat.count('D')
                                        rpformatlength = depformat.count('B')
                                        if depformatlength > 0:
                                            deployment = sampleid[len(survey):depformatlength]
                                            rosettepos = sampleid[len(survey) + depformatlength:]

                                            return deployment, rosettepos, survey
                                    else:
                                        rosettepos = int(sampleid[len(surveyprefix):])
                                        deployment = x
                                        survey = x
                                        return deployment, rosettepos, survey

        conn.close()

    except Exception:
        print(traceback.print_exc())


def match_click_to_peak(x_time, slk_data, current_nutrient):
    '''
    Finds the closest peak to where was clicked on the trace, returns the index of this peak
    :param x_time:
    :param slk_data:
    :param current_nutrient:
    :return:
    '''
    for i, x in enumerate(slk_data.peak_starts[current_nutrient]):
        if i < len(slk_data.peak_starts[current_nutrient]):
            if x[0] == '#':
                peak_start = x[2:-1]
            else:
                peak_start = x

            if slk_data.peak_starts[current_nutrient][i+1][0] == '#':
                next_peak_start = slk_data.peak_starts[current_nutrient][i+1][2:-1]
            else:
                next_peak_start = slk_data.peak_starts[current_nutrient][i+1]

            if x_time > int(peak_start) and x_time < int(next_peak_start):
                clicked_peak_index = i

                return True, clicked_peak_index


def load_proc_settings(path, project):
    """
    Read processing parameters from disk of json format
    :param path:
    :param project:
    :return:
    """
    try:
        with open(path + '/' + '%sParams.json' % project, 'r') as file:
            params = json.loads(file.read())
            return params
    except Exception as e:
        logging.error('ERROR: Could not load project parameters file, this should live within the project folder')


def save_proc_settings(path, project, settings):
    """
    Save processing parameters to disk in json file
    :param path:
    :param project:
    :param settings:
    :return:
    """
    try:
        with open(path + '/' + '%sParams.json' % project, 'w') as file:
            json.dump(settings, file)
    except Exception as e:
        logging.error(
            'ERROR: Could not save to project parameters file, this should live within the project folder')

