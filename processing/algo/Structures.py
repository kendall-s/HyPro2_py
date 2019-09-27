class CalibratedData:
    def __init__(self, run):

        self.run = run

        self.sample_ids = []
        self.cup_numbers = []
        self.cup_types = []
        self.epoch_timestamps = []

        self.raw_window_medians = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.corr_window_medians = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.calculated_concentrations = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}

        self.quality_flag = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.dilution_factor = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.calculated_dilution = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}

        self.survey = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.deployment = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}


class WorkingData:
    def __init__(self, run):
        self.run = run

        self.channel = 0
        self.analyte = 'Krill Me'

        self.window_values = []
        self.time_values = []
        self.quality_flag = []
        self.dilution_factor = []
        self.raw_window_medians = []
        self.corr_window_medians = []

        self.calculated_concentrations = []

        self.baseline_indexes = []
        self.baseline_peak_starts = []
        self.baseline_medians = []
        self.baseline_flags = []
        self.baseline_corr_percent = []

        self.high_index = []
        self.low_indexes = []
        self.carryover_coefficient = 0

        self.drift_indexes = []
        self.drift_peak_starts = []
        self.drift_medians = []
        self.drift_flags = []
        self.drift_corr_percent = []
        self.raw_drift_medians = []

        self.calibrant_indexes = []
        self.calibrant_medians = []
        self.calibrant_medians_minuszero = []
        self.calibrant_concentrations = []
        self.calibrant_weightings = []
        self.calibrant_residuals = []
        self.calibrant_zero_mean = 0
        self.calibrant_flags = []
        self.calibration_coefficients = []

class SLKData:
    def __init__(self, run):
        self.run = run

        self.operator = 'Chemist'
        self.date = '01/01/1990'
        self.time = '000000'
        self.active_nutrients = []

        self.sample_ids = []
        self.cup_numbers = []
        self.cup_types = []
        self.epoch_timestamps = []

        self.survey = []
        self.deployment = []
        self.rosette_position = []

        self.gains = {'silicate': 0, 'phosphate': 0, 'nitrate': 0, 'nitrite': 0, 'ammonia': 0}
        self.bases = {'silicate': 0, 'phosphate': 0, 'nitrate': 0, 'nitrite': 0, 'ammonia': 0}
        self.calibrants = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.peak_starts = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}
        self.channel = {'silicate': 0, 'phosphate': 0, 'nitrate': 0, 'nitrite': 0, 'ammonia': 0}


class CHDData:
    def __init__(self, run):
        self.run = run

        self.ad_data = {'silicate': [], 'phosphate': [], 'nitrate': [], 'nitrite': [], 'ammonia': []}


class OxygenData:
    def __init__(self):

        self.run = ''
        self.iodate_normality = ''
        self.iodate_temperature = ''
        self.iodate_volume = ''
        self.thio_normality = ''
        self.thio_temperature = ''
        self.standard_titer = ''
        self.blank = ''

        self.station = []
        self.cast = []
        self.rosette = []
        self.bottle_id = []
        self.flask_vol = []
        self.raw_titer = []
        self.titer = []
        self.oxygen = []
        self.thio_temp = []
        self.draw_temp = []
        self.final_volts = []
        self.time = []
        self.oxygen_mols = []

        self.quality_flag = []

        self.deployment = []
        self.rosette_position = []
        self.survey = []


class SalinityData:
    def __init__(self):

        self.run = ''

        self.sample_id = []
        self.bottle_id = []
        self.date_time = []
        self.uncorrected_ratio = []
        self.uncorrected_ratio_stdev = []
        self.salinity = []
        self.salinity_stdev = []
        self.comments = []

        self.quality_flag = []

        self.deployment = []
        self.rosette_position = []
        self.survey = []

