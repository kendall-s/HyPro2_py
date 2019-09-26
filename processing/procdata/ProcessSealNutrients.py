import logging, json
import numpy as np
import statistics, time
import sqlite3
from scipy.interpolate import interp1d
from scipy.stats import linregress
from pylab import polyfit
from collections import defaultdict
from processing.algo.Structures import WorkingData, CalibratedData
import processing.readdata.ReadSealNutrients as rsn

def processing_routine(slk_data, w_d, processing_parameters, current_nutrient):
    st = time.time()

    # ----------- Check peaks for peak shape - apply quality control -------------------------------------------
    w_d.quality_flag = peak_shape_qc(w_d.window_values, w_d.quality_flag)

    # ----------- Calculate the peak window medians for all peaks ----------------------------------------------
    w_d.raw_window_medians = window_medians(w_d.window_values)

    # ----------- Find the baseline peaks - apply baseline correction ------------------------------------------
    baseline_cup_type = processing_parameters['nutrientprocessing']['cupnames']['baseline']
    w_d.baseline_indexes = find_cup_indexes(baseline_cup_type, slk_data.cup_types)

    w_d.baseline_peak_starts = [int(slk_data.peak_starts[current_nutrient][x]) for x in w_d.baseline_indexes]
    baseline_correction_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient][
        'baseCorrType']

    w_d.baseline_medians, w_d.baseline_indexes = organise_basedrift_medians(w_d.baseline_indexes,
                                                                                w_d.raw_window_medians)

    w_d.corr_window_medians = baseline_correction(w_d.baseline_indexes,
                                                      w_d.baseline_medians,
                                                      baseline_correction_type,
                                                      w_d.raw_window_medians)

    # ----------  Find carryover peaks - apply carryover correction ---------------------------------------------
    high_cup_type = processing_parameters['nutrientprocessing']['cupnames']['high']
    low_cup_type = processing_parameters['nutrientprocessing']['cupnames']['low']
    w_d.high_index, w_d.low_indexes = find_carryover_indexes(high_cup_type, low_cup_type, slk_data.cup_types)
    w_d.corr_window_medians, w_d.carryover_coefficient = carryover_correction(w_d.high_index,
                                                                                  w_d.low_indexes,
                                                                                  w_d.corr_window_medians)

    # ----------- Find drift peaks - apply drift correction -----------------------------------------------------
    drift_cup_type = processing_parameters['nutrientprocessing']['cupnames']['drift']
    w_d.drift_indexes = find_cup_indexes(drift_cup_type, slk_data.cup_types)
    drift_correction_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient][
        'driftCorrType']

    w_d.drift_medians, w_d.drift_indexes = organise_basedrift_medians(w_d.drift_indexes, w_d.corr_window_medians)

    w_d.corr_window_medians = drift_correction(w_d.drift_indexes,
                                                   w_d.drift_medians,
                                                   drift_correction_type,
                                                   w_d.corr_window_medians)

    # ----------- Find calibrant peaks --------------------------------------------------------------------------
    calibrant_cup_type = processing_parameters['nutrientprocessing']['cupnames']['calibrant']
    w_d.calibrant_indexes = find_cup_indexes(calibrant_cup_type, slk_data.cup_types)

    # ----------- Prepare calibrants and various paramters ------------------------------------------------------
    cal_zero_label = processing_parameters['nutrientprocessing']['calibrants']['cal0']
    w_d.calibrant_medians = get_calibrant_medians(w_d.calibrant_indexes, w_d.corr_window_medians)
    w_d.calibrant_concs = get_calibrant_concentrations(w_d.calibrant_indexes, slk_data.calibrants[current_nutrient])
    w_d.calibrant_flags = get_calibrant_flags(w_d.calibrant_indexes, w_d.quality_flag)
    w_d.calibrant_zero_mean = get_calibrant_zero_mean(w_d.corr_window_medians, slk_data.sample_ids, cal_zero_label)
    w_d.calibrant_medians = remove_calibrant_zero(w_d.calibrant_medians, w_d.calibrant_zero_mean)
    w_d.calibrant_weightings = get_calibrant_weightings(w_d.calibrant_concs)


    # ------------ Create calibration ---------------------------------------------------------------------------
    calibration_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient][
        'calibration']
    calibration_error_limit = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient][
        'calerror']
    w_d.calibration_coefficients, w_d.calibrant_flags, w_d.calibrants_weightings, \
    w_d.calibrant_residuals = create_calibration(calibration_type,
                                                     w_d.calibrant_medians,
                                                     w_d.calibrant_concs,
                                                     w_d.calibrant_weightings,
                                                     calibration_error_limit,
                                                     w_d.calibrant_flags)

    # ------------ Apply calibration ----------------------------------------------------------------------------
    w_d.calculated_concentrations = apply_calibration(calibration_type, w_d.corr_window_medians,
                                                          w_d.calibration_coefficients)

    # ------------ Apply dilution factors -----------------------------------------------------------------------
    mdl_cup = processing_parameters['nutrientprocessing']['qcsamplenames']['mdl']
    mdl_indexes = find_cup_indexes(mdl_cup, slk_data.sample_ids)
    w_d.calculated_concentrations = apply_dilution(mdl_indexes, w_d.dilution_factor, w_d.calculated_concentrations)

    # ----- Find duplicates and flag if outside analyte tolerance ------------------------------------------------
    sample_cup_type = processing_parameters['nutrientprocessing']['cupnames']['sample']
    qc_cup_ids = [processing_parameters['nutrientprocessing']['qcsamplenames'][x] for x in
                  processing_parameters['nutrientprocessing']['qcsamplenames'].keys()]
    duplicate_indexes = find_duplicate_indexes(slk_data.sample_ids)
    sample_duplicate_indexes = find_duplicate_samples(duplicate_indexes, slk_data.sample_ids,
                                                          slk_data.cup_types, sample_cup_type, qc_cup_ids)

    w_d.quality_flag = determine_duplicate_error(sample_duplicate_indexes, w_d.calculated_concentrations,
                                                     w_d.quality_flag, calibration_error_limit)

    return w_d

    ft = time.time()
    print('Proc time: ' + str(ft - st))


def matchup_peaks(slk_data, chd_data, processing_parameters, current_nutrient, working_data):
    """
    Takes in the slk and chd data and created a matched dictionary
    :param slk_data:
    :param chd_data:
    :param processing_parameters:
    :param current_nutrient:
    :return: matched_data
    """
    peak_period = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['peakPeriod']
    wash_period = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['washPeriod']
    window_size = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['windowSize']
    window_start = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['windowStart']

    peak_length = int(peak_period) + int(wash_period)

    peak_starts = slk_data.peak_starts[current_nutrient]
    chd_values = chd_data.ad_data[current_nutrient]

    window_values = [[0 for x in range(int(window_size))] for y in range(len(peak_starts))]
    time_values = [[0 for x in range(int(window_size))] for y in range(len(peak_starts))]

    working_data.quality_flag = [1 for x in range(len(peak_starts))]
    working_data.dilution_factor = [1 for x in range(len(peak_starts))]

    for i, x in enumerate(range(len(peak_starts) - 1)):
        if peak_starts[x][1] == '#':
            working_data.quality_flag[i] = 3
        for y in range(int(window_size)):
            if peak_starts[x][1] == '#':
                window_values[x][y] = chd_values[
                    (int(peak_starts[x][2:-1]) + int(window_start) + y)]
                time_values[x][y] = (int(peak_starts[x][2:-1]) + int(window_start) + y)
            else:
                window_values[x][y] = chd_values[(int(peak_starts[x]) + int(window_start) + y)]
                time_values[x][y] = (int(peak_starts[x]) + int(window_start) + y)

    for i, x in enumerate(slk_data.cup_types):
        if x == processing_parameters['nutrientprocessing']['cupnames']['null']:
            working_data.quality_flag[i] = 3

    working_data.window_values = window_values
    working_data.time_values = time_values

    return working_data


def peak_shape_qc(window_values, quality_flags):

    first_slopes = []
    second_slopes = []

    for x in window_values:
        median = np.median(x)
        normalised = [y / median for y in x]

        fit = np.polyfit(range(len(x)), normalised, 2)
        first_slopes.append(fit[0])
        second_slopes.append(fit[1])

    for i, x in enumerate(first_slopes):
        if abs(x) > 0.005:
            quality_flags[i] = 5
        if abs(second_slopes[i]) > 0.009:
            quality_flags[i] = 5

    for i, x in enumerate(window_values):
        if np.median(x) < 3800:
            quality_flags[i] = 1

    return quality_flags


def window_medians(window_values):

    window_medians_temp_array = np.array(window_values)

    window_medians_temp_array = np.median(window_medians_temp_array, axis=1)

    window_medians = list(window_medians_temp_array)

    return window_medians


def find_cup_indexes(specified_cup, analysis_cups):
    a_c = np.array(analysis_cups)

    drift_indexes = np.where(a_c == specified_cup)

    clean_indexes = [x for x in drift_indexes[0]]
    return clean_indexes


def find_carryover_indexes(high_cup_name, low_cup_name, analysis_cups):
    a_c = np.array(analysis_cups)

    high_index = np.where(a_c == high_cup_name)
    low_indexes = np.where(a_c == low_cup_name)

    clean_high = [x for x in high_index[0]]
    clean_low = [x for x in low_indexes[0]]

    return clean_high, clean_low


def organise_basedrift_medians(relevant_indexes, window_medians):

    medians = [window_medians[x] for x in relevant_indexes]
    if relevant_indexes[0] != 0:
        relevant_indexes.insert(0, 0)
        medians.insert(0, medians[0])
    if relevant_indexes[-1] != len(window_medians):
        relevant_indexes.insert(-1, len(window_medians) - 1)
        medians.insert(-1, medians[-1])
        relevant_indexes.sort()

    return medians, relevant_indexes


def baseline_correction(baseline_indexes, baseline_medians, correction_type, window_medians):

    if correction_type == 'Piecewise':

        baseline_interpolation = interp1d(baseline_indexes, baseline_medians)

        new_window_medians = [x - baseline_interpolation(i) for i, x in enumerate(window_medians)]

        return new_window_medians

    else:
        logging.info('Baseline correction not applied')
        return window_medians


def carryover_correction(high_index, low_indexes, window_medians):
    high_median = [window_medians[x] for x in high_index]
    low_medians = [window_medians[x] for x in low_indexes]
    carryover_coefficient = (low_medians[0] - low_medians[1]) / (high_median[0] - low_medians[0])

    new_window_medians = [float(x - (window_medians[i-1] * carryover_coefficient)) if i > 0 else x for i, x in enumerate(window_medians)]
    #new_window_medians = [x - ((x-1) * carryover_coefficient) for x in window_medians]
    return new_window_medians, carryover_coefficient


def find_drift_indexes(drift_cup_name, analysis_cups):
    a_c = np.array(analysis_cups)

    drift_indexes = np.where(a_c == drift_cup_name)

    clean_indexes = [x for x in drift_indexes[0]]
    return clean_indexes


def drift_correction(drift_indexes, drift_medians, correction_type, window_medians):

    if correction_type == 'Piecewise':
        drift_mean = statistics.mean(drift_medians[1:-1])

        drift_calculated = []
        for x in drift_medians:
            drift_calculated.append(drift_mean / x)

        drift_interpolation = interp1d(drift_indexes, drift_calculated)

        new_window_medians = [x * drift_interpolation(i) for i, x in enumerate(window_medians)]

        return new_window_medians
    else:
        logging.info('Drift correction not applied')
        return window_medians


def get_calibrant_medians(calibrant_indexes, window_medians):

    calibrant_medians = [window_medians[ind] for ind in calibrant_indexes]

    return calibrant_medians

def get_calibrant_concentrations(calibrant_indexes, nominal_concentrations):

    calibrant_concs = [float(nominal_concentrations[ind]) for ind in calibrant_indexes]

    return calibrant_concs

def get_calibrant_flags(calibrant_indexes, quality_flags):

    calibrant_flags = [quality_flags[ind] for ind in calibrant_indexes]

    return calibrant_flags

def get_calibrant_zero_mean(window_medians, sample_ids, cal_zero_label):

    calibrant_zero_mean = statistics.mean(median for ind, median in enumerate(window_medians) if sample_ids[ind] == cal_zero_label)

    return calibrant_zero_mean


def remove_calibrant_zero(calibrant_medians, cal_zero_mean):

    calibrants_minus_zero = [(cal_median - cal_zero_mean) for cal_median in calibrant_medians]

    return calibrants_minus_zero

def get_calibrant_weightings(calibrant_concentrations):

    calibration_weightings = [2 if x == 0.0 else 1 for x in calibrant_concentrations]

    return calibration_weightings


def create_calibration(cal_type, calibrant_medians, calibrant_concentrations, calibrant_weightings, calibrant_error, calibrant_flags):
    repeat_calibration = True
    calibration_iteration = 0
    # TODO: Massive todo I've fcked this up royally, it works and works well, but it is not clean at all.
    # Subset on if the flag isn't bad
    medians_to_fit = [x for i, x in enumerate(calibrant_medians) if calibrant_flags[i] in [1, 2, 4, 6]]
    concs_to_fit = [x for i, x in enumerate(calibrant_concentrations) if calibrant_flags[i] in [1, 2, 4, 6]]
    weightings_to_fit = [x for i, x in enumerate(calibrant_weightings) if calibrant_flags[i] in [1, 2, 4, 6]]
    original_indexes = [x for i, x in enumerate(range(len(calibrant_medians))) if calibrant_flags[i] in [1, 2, 4, 6]]
    flags_to_fit = [x for x in calibrant_flags]

    while repeat_calibration:

        calibration_iteration += 1

        if cal_type == 'Linear':
            cal_coefficients = polyfit(medians_to_fit, concs_to_fit, 1, w=weightings_to_fit)

            fp = np.poly1d(cal_coefficients)
            y_fitted = [fp(x) for x in calibrant_medians]

        elif cal_type == 'Quadratic':
            pass

        else:
            logging.error('ERROR: No calibration type specified for nutrient')
            raise NameError('No calibration type could be applied')

        repeat_calibration = False

        calibrant_residuals = []
        for i, x in enumerate(concs_to_fit):
            cal_residual = x - fp(medians_to_fit[i])
            calibrant_residuals.append(cal_residual)

        max_residual_index = int(np.argmax(np.abs(np.array(calibrant_residuals))))

        if abs(calibrant_residuals[max_residual_index]) > (2 * calibrant_error) and flags_to_fit[max_residual_index] != 92:
            repeat_calibration = True
            weightings_to_fit[max_residual_index] = 0
            flags_to_fit[max_residual_index] = 91
            medians_to_fit.pop(max_residual_index)
            concs_to_fit.pop(max_residual_index)
            weightings_to_fit.pop(max_residual_index)
            original_indexes.pop(max_residual_index)
            flags_to_fit.pop(max_residual_index)
            calibrant_flags[original_indexes[max_residual_index]] = 91
            calibrant_weightings[original_indexes[max_residual_index]] = 0

        if calibrant_error < abs(calibrant_residuals[max_residual_index]) < (2 * calibrant_error) and flags_to_fit[max_residual_index] != 6:
            repeat_calibration = True
            weightings_to_fit[max_residual_index] = 0.5
            flags_to_fit[max_residual_index] = 92
            calibrant_flags[original_indexes[max_residual_index]] = 92
            calibrant_weightings[original_indexes[max_residual_index]] = 0.5

        if calibration_iteration > 7:
            repeat_calibration = False

    return cal_coefficients, calibrant_flags, calibrant_weightings, calibrant_residuals


def apply_calibration(cal_type, window_medians, calibration_coefficients):
    if cal_type == 'Linear':
        calculated_concentrations = [(x * calibration_coefficients[0]) + calibration_coefficients[1] for x in window_medians]

        return calculated_concentrations


def apply_dilution(mdl_indexes, dilution_factors, calculated_concentrations):
    cc = np.array(calculated_concentrations)
    df = np.array(dilution_factors)
    mdl_concs = cc[mdl_indexes]
    mdl = np.mean(mdl_concs)

    cc_2 = cc * df - (df - 1) * mdl

    calculated_concentrations = list(cc_2)

    return calculated_concentrations

def find_duplicate_indexes(sample_ids):
    tally = defaultdict(list)

    for i, item in enumerate(sample_ids):
        tally[item].append(i)

    return ((sample_id, indexes) for sample_id, indexes in tally.items() if len(indexes) > 1)


def find_duplicate_samples(duplicate_indexes, sample_ids, cup_types, sample_cup_type, qc_samples_names):
    duplicate_samples = []
    for indices_list in duplicate_indexes:
        # Logic here, make sure sample ID doesn't correspond to a QC sample e.g. RMNS or MDL
        # Then got to also make sure cup type is a sample, otherwise Nulls would be listed
        # Keeping the duplicate indexes in the dictionary structure as well to differentiate
        if not any(qc_name in sample_ids[indices_list[1][0]] for qc_name in qc_samples_names):
            if cup_types[indices_list[1][0]] == sample_cup_type:
                duplicate_samples.append(indices_list)

    return duplicate_samples


def determine_duplicate_error(duplicate_samples, calculated_concentrations, quality_flags, analyte_tolerance):
    for sample_indexes in duplicate_samples:
        tested_concentrations = [calculated_concentrations[i] for i in sample_indexes[1]]
        for i, conc in enumerate(tested_concentrations):
            if i > 0:
                difference = conc - tested_concentrations[i-1]
                if difference > analyte_tolerance:
                    for ind in sample_indexes[1]:
                        quality_flags[ind] = 8


    return quality_flags



def reset_calibrant_flags(quality_flags):

    for i, x in enumerate(quality_flags):
        if x in [91, 92]:
            quality_flags[i] = 1

    return quality_flags

def pack_data(slk_data, working_data, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    run_list = [working_data.run for x in slk_data.sample_ids]

    package = tuple(zip(run_list, slk_data.cup_types, slk_data.sample_ids, slk_data.cup_numbers,
                        working_data.raw_window_medians, working_data.corr_window_medians,
                        working_data.calculated_concentrations, slk_data.survey, slk_data.deployment,
                        slk_data.rosette_position, working_data.quality_flag, working_data.dilution_factor,
                        slk_data.epoch_timestamps))


    c.executemany('INSERT OR REPLACE INTO %sData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)' % working_data.analyte)

    c.commit()

    package = tuple(zip(working_data.analyte, working_data.run, working_data.channel,
                        slk_data.gains[working_data.analyte], slk_data.bases[working_data.analyte],
                        working_data.calibrant_zero_mean, working_data.carryover_coefficient,
                        working_data.calibration_coefficients[0], working_data.calibration_coefficients[1]))

    c.executemany('INSERT OR REPLACE INTO nutrientHeader VALUES(?,?,?,?,?,?,?,?,?)')

    c.commit()

    package = tuple(zip(working_data.analyte, working_data.run, working_data.calibrant_indexes,
                        working_data.calibrant_medians, working_data.calibrant_medians_minuszero,
                        working_data.calibrant_concentrations, working_data.calibrant_weightings,
                        working_data.calibrant_residuals, working_data.calibrant_flags))

    c.executemany('INSERT OR REPLACE INTO nutrientCalibrants VALUES(?,?,?,?,?,?,?,?,?)')

    c.commit()

    package = tuple(zip(working_data.analyte, working_data.run, working_data.baseline_indexes,
                        working_data.baseline_peak_starts, working_data.baseline_medians))


def populate_nutrient_survey(database, params, sample_id):
    deployments = []
    rosette_positions = []
    survey = []

    for i, s_id in enumerate(sample_id):
        try:
            dep, rp, surv = determine_nutrient_survey(database, params, s_id)
        except TypeError:
            # TODO: fix this so this error is accounted for in the determining survey, something is being missed
            dep = 'Unknown'
            rp = 'Unknown'
            surv = 'Unknown'

        deployments.append(dep)
        rosette_positions.append(rp)
        survey.append(surv)

    return deployments, rosette_positions, survey

def determine_nutrient_survey(database, params, sample_id):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    surveys = list(params['surveyparams'].keys())
    for surv in surveys:
        if 'seal' == 'seal':
            if params['surveyparams'][surv]['seal']['activated']:
                if params['surveyparams'][surv]['seal']['usesampleid']:
                    return 'usingID', 'usingID', 'usingID'
                else:
                    if str(sample_id).isdigit():  # CTD sample is only numbers in name
                        if params['surveyparams'][surv]['seal']['matchlogsheet']:
                            survey = surv
                            if params['surveyparams'][surv]['seal']['decodedepfromid']:
                                depformat = params['surveyparams'][surv]['seal']['depformat']
                                depformatlength = depformat.count('D')
                                rpformatlength = depformat.count('B')
                                if depformatlength > 0:
                                    deployment = sample_id[0:depformatlength]
                                    rosettepos = sample_id[depformatlength:(depformatlength + rpformatlength)]
    
                                    return deployment, rosettepos, survey
                            else:
                                print('TODO pull dep/rp from logsheet instead')
                                # TODO: pull dep/rp from logsheet option
                    else:  # Sample id has more than just numbers in it
                        if params['surveyparams'][surv]['seal']['decodesampleid']:  # Decode the sample ID, needs a prefisurv too
                            surveyprefisurv = params['surveyparams'][surv]['seal']['surveyprefisurv']
                            if len(params['surveyparams'][surv]['seal'][
                                       'surveyprefisurv']) > 0:  # Check theres actually a prefisurv
                                sampleprefisurv = sample_id[0:len(params['surveyparams'][surv]['seal']['surveyprefisurv'])]
                                if surveyprefisurv == sampleprefisurv:
                                    survey = surv
                                else:
                                    logging.error('Sample: ' + str(sample_id) + ' does not match esurvisting surveys.')
                                    break
                                if params['surveyparams'][surv]['seal']['decodedepfromid']:  # Decode a dep/rp
                                    depformat = params['surveyparams'][surv]['seal']['depformat']
                                    depformatlength = depformat.count('D')
                                    rpformatlength = depformat.count('B')
                                    if depformatlength > 0:
                                        deployment = sample_id[len(survey):depformatlength]
                                        rosettepos = sample_id[len(survey) + depformatlength:]
    
                                        return deployment, rosettepos, survey
                                else:
                                    rosettepos = int(sample_id[len(surveyprefisurv):])
                                    deployment = surv
                                    survey = surv
                                    return deployment, rosettepos, survey
    
