import logging
import csv
import json
from processing.algo.Structures import OxygenData

def parse_lst(lst_path, current_path, current_project, file_name):
    try:
        with open(lst_path) as file:
            data = list(file)

        data_list = []
        for row in data:
            data_list.append(row.split())

        with open(current_path + '/' + current_project + 'Params.json', 'r') as file:
            params = json.loads(file.read())

        oxygen_data = OxygenData()

        oxygen_data.file = file_name

        prefixlength = len(params['analysis_params']['scripps']['file_prefix'])
        runformatlength = len(params['analysis_params']['scripps']['run_format'])
        oxygen_data.run = file_name[prefixlength: (prefixlength + runformatlength)]

        iodatenormx, iodatenormy = get_index(data_list, 'N(20)IO3:')
        oxygen_data.iodate_normality = [data_list[iodatenormx][iodatenormy + 1]]

        iodatevolx, iodatevoly = get_index(data_list, 'Vol(20):')
        oxygen_data.iodate_volume = [data_list[iodatevolx][iodatevoly + 1]]

        stdtiterx, stdtitery = get_index(data_list, 'Titer')
        oxygen_data.standard_titer = [data_list[stdtiterx][stdtitery + 4]]

        blankx, blanky = get_index(data_list, 'Blk:')
        oxygen_data.blank = [data_list[blankx][blanky + 1]]

        iodatetempx, iodatetempy = get_index(data_list, 'IO3')
        oxygen_data.iodate_temperature = [data_list[iodatetempx][iodatetempy + 3]]

        thionormx, thionormy = get_index(data_list, '(20C)')
        oxygen_data.thio_normality = [data_list[thionormx][thionormy + 1]]

        thiotempx, thiotempy = get_index(data_list, 'stdize:')
        oxygen_data.thio_temperature = [data_list[thiotempx][thiotempy + 1]]

        # Pull out the data section below the header info

        stax, stay = get_index(data_list, 'Sta')

        results = data_list[stax + 2:]

        oxygen_data.station = [int(x[0]) for x in results]
        oxygen_data.cast = [int(x[1]) for x in results]
        oxygen_data.niskin = [int(x[2]) for x in results]
        oxygen_data.bottle_id = [int(x[3]) for x in results]
        oxygen_data.flask_vol = [float(x[4]) for x in results]
        oxygen_data.raw_titer = [float(x[5]) for x in results]
        oxygen_data.titer = [float(x[6]) for x in results]
        oxygen_data.oxygen = [float(x[7]) for x in results]
        oxygen_data.thio_temp = [float(x[8]) for x in results]
        oxygen_data.draw_temp = [float(x[9]) for x in results]
        oxygen_data.final_volts = [float(x[10]) for x in results]
        oxygen_data.time = [float(x[11]) for x in results]

        oxygen_data.oxygen_mols = [(x*44.66) for x in oxygen_data.oxygen]

        oxygen_data.quality_flag = [1 for x in oxygen_data.bottle_id]


        return oxygen_data


    except FileNotFoundError:
        logging.error('Could not find the nutrient file, is it in the right spot? Does a Oxygen folder exist?')
        
def get_index(arr, searchitem):
    for i, x in enumerate(arr):
        for j, y in enumerate(x):
            if y == searchitem:
                return i, j
    return "negative"

