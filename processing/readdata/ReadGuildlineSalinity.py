import xlrd
import sqlite3
import pandas as pd
from processing.data.Structures import SalinityData

def parse_guildline_excel(excel_path):

    file = xlrd.open_workbook(excel_path)

    data_sheet = file.sheet_by_index(0)

    salt_data = SalinityData()

    salt_data.sample_id = [str(x) for x in data_sheet.col_values(0)[1:]]
    salt_data.bottle_id = [str(x) for x in data_sheet.col_values(1)[1:]]
    salt_data.date_time = data_sheet.col_values(2)[1:]
    salt_data.uncorrected_ratio = data_sheet.col_values(4)[1:]
    salt_data.uncorrected_ratio_stdev = data_sheet.col_values(5)[1:]
    salt_data.salinity = data_sheet.col_values(8)[1:]
    salt_data.salinity_stdev = data_sheet.col_values(9)[1:]
    salt_data.comments = data_sheet.col_values(10)[1:]

    salt_data.quality_flag = [1 for x in salt_data.bottle_id]

    return salt_data
