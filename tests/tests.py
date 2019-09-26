import pytest
import processing.procdata.ProcessSealNutrients as psn


def test_drift_correction():
    drift_indexes = [0, 4, 6, 9, 11, 13]
    drift_medians = [10001, 10000, 10010, 10030, 10005, 10005]
    correction_type = 'Piecewise'
    window_medians = [10001, 3005, 5000, 7500, 10000, 2500, 10010, 7600, 5500, 10030, 13000, 10005, 9000, 10005]

    corr_medians = psn.drift_correction(drift_indexes, drift_medians, correction_type, window_medians)

    assert corr_medians == [10011.25, 3008.155019013724, 5005.374743775623, 7508.249807831716, 10011.25,
                            2501.562343906094, 10011.249999999998, 7595.896908010566, 5493.374501039008,
                            10011.25, 12991.909422905695, 10011.25, 9005.622188905547, 10011.25]


def test_drif_indexes():
    drift_cup_name = 'DRIF'
    cup_names = ['SAMP', 'NULL', 'CSIRO', 'DRIF', 'AMPERSAND', 'DRIF']
    drift_indexes = psn.find_cup_indexes(drift_cup_name, cup_names)

    assert drift_indexes == [3, 5]


def test_carryover_correction():
    high_index = [3]
    low_indexes = [4, 5]
    window_medians = [3005, 5000, 7500, 10000, 2500, 2490, 7600, 5500, 10030, 13000, 10005, 9000]

    corr_medians, carryover_coef = psn.carryover_correction(high_index, low_indexes, window_medians)

    assert corr_medians == [3005, 4995.993333333333, 7493.333333333333,
                            9990.0, 2486.6666666666665, 2486.6666666666665,
                            7596.68, 5489.866666666667, 10022.666666666666,
                            12986.626666666667, 9987.666666666666, 8986.66]
    assert carryover_coef == 0.0013333333333333333


def test_baseline_correction():
    base_indexes = [0, 3, 5, 8, 10, 12]
    baseline_medians = [4000, 4000, 5010, 5500, 5005, 5005]
    correction_type = 'Piecewise'
    window_medians = [3005, 5000, 7500, 4000, 2500, 5010, 7600, 5500, 4430, 13000, 5005, 9000]

    corr_medians = psn.baseline_correction(base_indexes, baseline_medians, correction_type, window_medians)

    assert corr_medians == [-995.0, 1000.0, 3500.0, 0.0, -2005.0, 0.0, 2426.666666666667,
                            163.33333333333303, -1070.0, 7747.5, 0.0, 3995.0]


def test_window_medians():
    window_values = [[4000, 4001, 4002, 4003, 4004], [1234, 4321, 2134, 3212, 4333], [5555, 5556, 5553, 5055, 5532]]

    window_median = psn.window_medians(window_values)

    assert window_median == [4002.0, 3212.0, 5553.0]


def test_peak_shape_qc():
    window_values = [[4001, 4002, 4005, 4020], [7005, 7070, 7020, 7010], [12000, 11900, 12200], [5000, 6000, 7000, 8000]]
    quality_flags = [1, 1, 1, 1]

    new_quality_flags = psn.peak_shape_qc(window_values, quality_flags)

    assert new_quality_flags == [1, 1, 5, 5]


def test_find_duplicate_indexes():
    sample_ids = ['RMNS', 'RMNS', '101', 'QUASI', 'LNSW', 'Drift', '911', '101', 'Cal 0']

    indexes = [x for x in psn.find_duplicate_indexes(sample_ids)]

    assert indexes == [('RMNS', [0, 1]), ('101', [2, 7])]


def test_find_duplicate_samples():
    indexes = [('101', [2, 3]), ('103', [6, 7, 9]), ('Drift', [1, 11])]
    samples_ids = ['Primer', 'Drift', '101', '101', 'RMNS CD', 'MDL', '103', '103', 'LNSW', '103', 'Null', 'Drift', 'Drift Sample']
    cup_types = ['PRIM', 'DRIF', 'SAMP', 'SAMP', 'SAMP', 'SAMP', 'SAMP', 'SAMP', 'SAMP', 'SAMP', 'NULL', 'DRIF', 'SAMP']
    sample_cup_type = 'SAMP'
    qc_sample_ids = ['RMNS', 'MDL', 'LNSW', 'Drift Sample']
    duplicate_samples = psn.find_duplicate_samples(indexes, samples_ids, cup_types, sample_cup_type, qc_sample_ids)

    assert duplicate_samples == [('101', [2, 3]), ('103', [6, 7, 9])]


def test_determine_duplicate_error():
    duplicate_samples =  [('101', [2, 3]), ('103', [6, 7, 9]), ('B99', [0, 12])]
    calculated_concentrations = [12, 10, 5.5, 5.55, 6, 3, 9.1, 9.2, 9.5, 9.5, 30, 50.5, 12.5]
    quality_flags = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    analyte_tolerance = 0.2

    flags = psn.determine_duplicate_error(duplicate_samples, calculated_concentrations, quality_flags, analyte_tolerance)
    assert flags == [8, 1, 1, 1, 1, 1, 8, 8, 1, 8, 1, 1, 8]

def test_reset_calibrant_flags():
    quality_flags = [1, 1, 1, 1, 2, 3, 5, 1, 6, 91, 3, 4, 92, 92, 92, 91, 1, 2, 1, 1, 1]

    new_flags = psn.reset_calibrant_flags(quality_flags)

    assert new_flags == [1, 1, 1, 1, 2, 3, 5, 1, 6, 1, 3, 4, 1, 1, 1, 1, 1, 2, 1, 1, 1]

def test_get_calibrant_medians():
    calibrant_indexes = [0, 1, 4, 5, 6]
    window_medians = [4000, 5000, 4500, 6000, 5000, 3000, 7000]

    calibrant_medians = psn.get_calibrant_medians(calibrant_indexes, window_medians)

    assert calibrant_medians == [4000, 5000, 5000, 3000, 7000]

def test_get_calibrant_concs():
    calibrant_indexes = [1, 3, 4, 6]
    nominal_concs = [0, 0, 1, 2, 3, 4, 5]

    calibrant_concs = psn.get_calibrant_concentrations(calibrant_indexes, nominal_concs)

    assert calibrant_concs == [0, 2, 3, 5]

def test_get_calibrant_flags():
    calibrant_indexes = [0, 2, 3, 4, 6]
    quality_flags = [1, 1, 2, 3, 1, 2, 1]

    calibrant_flags = psn.get_calibrant_flags(calibrant_indexes, quality_flags)

    assert calibrant_flags == [1, 2, 3, 1, 1]

def test_calibrant_zero_mean():
    window_medians = [4000, 5000, 4500, 3000, 1500]
    sample_ids = ['Cal 0', 'Cal 1', 'Cal 0', 'Cal0', 'Cal 2']
    cal_zero_label = 'Cal 0'
    cal_zero_mean = psn.get_calibrant_zero_mean(window_medians, sample_ids, cal_zero_label)

    assert cal_zero_mean == 4250

def test_remove_cal_zero():
    calibrant_medians = [3300, 3500, 5250, 5500, 7400, 7600]
    cal_zero_mean = 3400

    cal_medians_minus_zero = psn.remove_calibrant_zero(calibrant_medians, cal_zero_mean)

    assert cal_medians_minus_zero == [-100, 100, 1850, 2100, 4000, 4200]

def test_calibration_weightings():
    calibrant_concentrations = [0.0, 1.2, 1.2, 2.4, 0.0, 2.4, 3.2]

    calibrant_weightings = psn.get_calibrant_weightings(calibrant_concentrations)

    assert calibrant_weightings == [2, 1, 1, 1, 2, 1, 1]
