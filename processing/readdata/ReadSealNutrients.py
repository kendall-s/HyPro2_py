import csv, time, calendar, logging, traceback, os
from processing.algo.Structures import SLKData, CHDData
import processing.procdata.ProcessSealNutrients as psn
NUTRIENTS = ['nitrate', 'phosphate', 'silicate', 'nitrite', 'ammonia']

def get_data_routine(file_path, w_d, processing_parameters, database):
    """
    Feeds the files to the parsing functions to be return objects containing relevant data
    :param file_path:
    :return:
    """
    st = time.time()
    # Extract data from the .SLK file - loads into slk data object
    slk_data = extract_slk_data(file_path, processing_parameters)

    # Extract data from the .CHD file - laods into chd data object
    chd_data = extract_chd_data(file_path[:-3]+'CHD', slk_data)

    # Determine our first active (was present in the file) nutrient and assign
    # Fill out dilutions and flags with 1s as this point
    current_nutrient = slk_data.active_nutrients[0]
    w_d.analyte = current_nutrient
    w_d.quality_flag = [1 for x in range(len(slk_data.sample_ids))]
    w_d.dilution_factor = [1 for x in range(len(slk_data.sample_ids))]

    # Check and determine if we know the surveys
    slk_data.deployment, slk_data.rosette_position, slk_data.survey = psn.populate_nutrient_survey(database,
                                                                                               processing_parameters,
                                                                                               slk_data.sample_ids,
                                                                                               slk_data.cup_types)
    ft = time.time()
    print('Read time: ' + str(ft-st))

    return slk_data, chd_data, w_d, current_nutrient


def parse_slk(slk_path):
    slk_path = slk_path

    # Open the file
    if os.path.isfile(slk_path):
        with open(slk_path) as file:
            readr = csv.reader(file, delimiter=';')
            readr_list = list(readr)
    else:
        raise FileNotFoundError

    # Now the .SLK will be parsed, this is messy because there are different 'versions' of the
    # .slk as there isn't a defined standard..
    # THe .slk is essentially a spreadsheet and it will be broken up into an array

    read_data = []
    for x in readr_list:
        if x[0] == 'C' or x[0] == 'F':
            read_data.append(x)
            # Get size of spreadsheet to make array to hold data
        if x[0] == 'B':
            if x[1][0] == 'X':
                w = int(x[1][1:])
            if x[2][0] == 'X':
                w = int(x[2][1:])
            if x[2][0] == 'Y':
                h = int(x[2][1:])
            if x[1][0] == 'Y':
                h = int(x[1][1:])

    data_hold = [['' for w_i in range(w)] for h_i in range(h)]

    row = 0
    column = 0

    for x in read_data:
        try:
            if x[1][0] == 'Y':
                row = int(x[1][1:]) - 1
            if len(x) > 2:
                if x[2][0] == 'X':
                    column = int(x[2][1:]) - 1
            if x[1][0] == 'X':
                column = int(x[1][1:]) - 1
            if x[0][0] == 'F':
                if len(x) == 4:
                    if x[3][0] == 'M':
                        pass
                    else:
                        column = int(x[3][1:]) - 1
                else:
                    if x[1][0] != 'W':
                        column = int(x[3][1:]) - 1

            data_hold[row][column] = x[-1][1:]
        except Exception as e:
            print('len: ' + str(len(x)))

    return data_hold


def extract_chd_data(chd_path, slk_data):
    chd_data = CHDData('unknown')

    with open(chd_path) as file:
        readr = csv.reader(file, delimiter=';')
        readrlist = list(readr)
    try:
        for x in slk_data.active_nutrients:
            chd_data.ad_data[x] = [int(row[int(slk_data.chd_channel[x])]) for row in readrlist]

    except IndexError:
        with open(chd_path) as file:
            readr = csv.reader(file, delimiter=',')
            readrlist = list(readr)
        for x in slk_data.active_nutrients:
            chd_data.ad_data[x] = [int(row[int(slk_data.chd_channel[x])]) for row in readrlist]


    return chd_data


def extract_slk_data(slk_path, processing_parameters):
    data_hold = parse_slk(slk_path)

    slk_data = SLKData('unknown')
    # By finding where certain headers are the associated data can be found
    findx, findy = getIndex(data_hold, '"TIME"')
    slk_data.time = data_hold[findx][findy + 1][1:-1]

    findx, findy = getIndex(data_hold, '"DATE"')
    slk_data.date = data_hold[findx][findy + 1][1:-1]

    findx, findy = getIndex(data_hold, '"OPER"')
    slk_data.operator = data_hold[findx][findy + 1][1:-1]

    findx, findy = getIndex(data_hold, '"METH"')
    # This was added a little later on, aftr realising that channel number in SLK does not
    # correspond with the A/D data in the CHD, if say only channel 2 is missing, leaving channels 1,3,4,5
    channel_orders = data_hold[findx][:]
    channel_temp = 1
    for x in channel_orders:
        # Check that the method name matches an expected channel
        cleaned_x = x.replace('"', '')
        if cleaned_x in processing_parameters['nutrientprocessing']['elementNames'].values():
            for name, channel_name in processing_parameters['nutrientprocessing']['elementNames'].items():
                if cleaned_x == channel_name:
                    name_cleaned = name.replace('Name', '')

                    slk_data.chd_channel[name_cleaned] = channel_temp
                    channel_temp += 1
                    # Break because there is only going to be ONE match
                    break

    for x in NUTRIENTS:
        findx, findy = getIndex(data_hold, '"' + processing_parameters['nutrientprocessing']['elementNames']['%sName' % x] + '"')
        if findx != 'no':
            slk_data.active_nutrients.append(x)
            slk_data.channel[x] = data_hold[findx - 1][findy]
            slk_data.gains[x] = data_hold[findx + 3][findy]
            slk_data.bases[x] = data_hold[findx + 2][findy]
            slk_data.calibrants[x] = [row[findy - 1] for row in data_hold[findx + 6:]]
            slk_data.peak_starts[x] = [row[findy + 2].replace('"', '') for row in data_hold[findx + 6:]]

            if 'peak' in str(slk_data.peak_starts[x][0]).lower():
                logging.error('Too many rows between analyte header and start of tray protocol.')
                raise TypeError
            if '' in slk_data.peak_starts[x]:
                logging.error(f'There is a blank peak start value in the SLK file for nutrient {x}')
                raise TypeError

    findx, findy = getIndex(data_hold,
                            '"' + processing_parameters['nutrientprocessing']['slkcolumnnames']['sampleID'] + '"')
    # Removes double quotes out of the sample ID name
    slk_data.sample_ids = [row[findy].replace('"', '') for row in data_hold[findx + 1:]]

    findx, findy = getIndex(data_hold,
                            '"' + processing_parameters['nutrientprocessing']['slkcolumnnames']['cupNumbers'] + '"')
    slk_data.cup_numbers = [row[findy][:] for row in data_hold[findx + 1:]]

    findx, findy = getIndex(data_hold,
                            '"' + processing_parameters['nutrientprocessing']['slkcolumnnames']['cupTypes'] + '"')
    slk_data.cup_types = [row[findy][1:-1] for row in data_hold[findx + 1:]]

    findx, findy = getIndex(data_hold,
                            '"' + processing_parameters['nutrientprocessing']['slkcolumnnames']['dateTime'] + '"')
    slk_data.epoch_timestamps = [row[findy][1:-1] for row in data_hold[findx + 1:]]
    format = '%d/%m/%Y %I:%M:%S %p'
    structtime = [time.strptime(x, format) for x in slk_data.epoch_timestamps]
    slk_data.epoch_timestamps = [calendar.timegm(x) for x in structtime]

    return slk_data

def getIndex(arr, searchitem):
    for i, x in enumerate(arr):
        for j, y in enumerate(x):
            if y == searchitem:
                return i, j

    logging.error(f'Could not find the searched term {searchitem} in the SLK file')
    return 'no', 'no'
