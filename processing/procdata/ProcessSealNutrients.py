import calendar
import logging
import os
import sqlite3
import statistics
import time
from collections import defaultdict

from numpy import array as nparray
from numpy import median as npmedian
from numpy import where as npwhere
from numpy import interp as npinterp
from numpy import poly1d as nppoly1d
from numpy import argmax as npargmax
from numpy import abs as npabs
from numpy import mean as npmean

import xarray as xr
from pylab import polyfit


# TODO: need small sub routine for resetting values on a RE-process
# TODO: There may be a double up on functions that find flags and medians between drift/baseline and calibrants

def processing_routine(slk_data, chd_data, w_d, processing_parameters, current_nutrient):
    """
    Function that runs through all the steps of processing a nutrient run, it is broken up as much as possible
    to make each individual calculation function as manageable and testable as possible
    :param slk_data:
    :param chd_data:
    :param w_d:
    :param processing_parameters:
    :param current_nutrient:
    :return: w_d
    """

    st = time.time()

    # ----------- Read in latest configurable processing parameters (in order of use) ------------------------
    window_size = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['windowSize']
    window_start = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['windowStart']
    null_cup_type = processing_parameters['nutrientprocessing']['cupnames']['null']
    baseline_cup_type = processing_parameters['nutrientprocessing']['cupnames']['baseline']
    baseline_corr_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['baseCorrType']
    high_cup_type = processing_parameters['nutrientprocessing']['cupnames']['high']
    low_cup_type = processing_parameters['nutrientprocessing']['cupnames']['low']
    drift_cup_type = processing_parameters['nutrientprocessing']['cupnames']['drift']
    drift_corr_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['driftCorrType']
    calibrant_cup_type = processing_parameters['nutrientprocessing']['cupnames']['calibrant']
    cal_zero_label = processing_parameters['nutrientprocessing']['calibrants']['cal0']
    cal_type = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['calibration']
    cal_error_limit = processing_parameters['nutrientprocessing']['processingpars'][current_nutrient]['calerror']
    mdl_cup = processing_parameters['nutrientprocessing']['qcsamplenames']['mdl']
    sample_cup_type = processing_parameters['nutrientprocessing']['cupnames']['sample']
    qc_cup_ids = [processing_parameters['nutrientprocessing']['qcsamplenames'][x] for x in
                  processing_parameters['nutrientprocessing']['qcsamplenames'].keys()]
    qc_cups = processing_parameters['nutrientprocessing']['qcsamplenames']

    # ----------- Match peaks to CHD data ---------------------------------------------------------------------
    # Match the SLK peak start data to the CHD A/D data
    w_d.window_values, w_d.time_values = get_peak_values(slk_data.peak_starts[current_nutrient],
                                                         chd_data.ad_data[current_nutrient],
                                                         window_size, window_start)

    w_d.quality_flag = flag_null_samples(slk_data.cup_types, null_cup_type, w_d.quality_flag)
    w_d.quality_flag = flag_hashed_samples(slk_data.peak_starts[current_nutrient], w_d.quality_flag)

    # w_d = matchup_peaks(slk_data, chd_data, processing_parameters, current_nutrient, w_d)

    # ----------- Check peaks for peak shape - apply quality control -------------------------------------------
    w_d.quality_flag = peak_shape_qc(w_d.window_values, w_d.quality_flag)

    # ----------- Calculate the peak window medians for all peaks ----------------------------------------------
    w_d.raw_window_medians = window_medians(w_d.window_values)

    # ----------- Find the baseline peaks - apply baseline correction ------------------------------------------
    w_d.baseline_indexes = find_cup_indexes(baseline_cup_type, slk_data.cup_types)
    w_d.baseline_peak_starts = [int(slk_data.peak_starts[current_nutrient][x]) for x in w_d.baseline_indexes]
    w_d.baseline_medians, w_d.baseline_indexes = organise_basedrift_medians(w_d.baseline_indexes,
                                                                            w_d.raw_window_medians)
    w_d.baseline_flags = get_basedrift_flags(w_d.baseline_indexes, w_d.quality_flag)
    w_d.corr_window_medians = baseline_correction(w_d.baseline_indexes, w_d.baseline_medians, baseline_corr_type,
                                                  w_d.raw_window_medians)

    # ----------  Find carryover peaks - apply carryover correction ---------------------------------------------
    w_d.high_index, w_d.low_indexes = find_carryover_indexes(high_cup_type, low_cup_type, slk_data.cup_types)
    w_d.corr_window_medians, w_d.carryover_coefficient = carryover_correction(w_d.high_index, w_d.low_indexes,
                                                                              w_d.corr_window_medians)

    # ----------- Find drift peaks - apply drift correction -----------------------------------------------------
    w_d.drift_indexes = find_cup_indexes(drift_cup_type, slk_data.cup_types)
    w_d.drift_peak_starts = [int(slk_data.peak_starts[current_nutrient][x]) for x in w_d.drift_indexes]
    w_d.raw_drift_medians = [w_d.raw_window_medians[x] for x in w_d.drift_indexes]
    w_d.drift_medians, w_d.drift_indexes = organise_basedrift_medians(w_d.drift_indexes, w_d.corr_window_medians)
    w_d.drift_flags = get_basedrift_flags(w_d.drift_indexes, w_d.quality_flag)
    w_d.drift_corr_percent = get_basedrift_corr_percent(w_d.drift_medians, statistics.mean(w_d.drift_medians[1:-1]))
    w_d.corr_window_medians = drift_correction(w_d.drift_indexes, w_d.drift_medians, drift_corr_type,
                                               w_d.corr_window_medians)

    # ----------- Find calibrant peaks --------------------------------------------------------------------------
    w_d.calibrant_indexes = find_cup_indexes(calibrant_cup_type, slk_data.cup_types)

    # ----------- Prepare calibrants and various paramters ------------------------------------------------------
    w_d.calibrant_medians = get_calibrant_medians(w_d.calibrant_indexes, w_d.corr_window_medians)
    # Side note for baseline plot - get highest cal median and determine a percentage corr from that
    w_d.baseline_corr_percent = get_basedrift_corr_percent(w_d.baseline_medians, max(w_d.calibrant_medians))
    w_d.calibrant_concs = get_calibrant_concentrations(w_d.calibrant_indexes, slk_data.calibrants[current_nutrient])
    w_d.calibrant_flags = get_calibrant_flags(w_d.calibrant_indexes, w_d.quality_flag)
    w_d.calibrant_zero_mean = get_calibrant_zero_mean(w_d.corr_window_medians, slk_data.sample_ids, cal_zero_label)
    w_d.calibrant_medians_minuszero = remove_calibrant_zero(w_d.calibrant_medians, w_d.calibrant_zero_mean)
    w_d.calibrant_weightings = get_calibrant_weightings(w_d.calibrant_concs)

    # ------------ Create calibration ---------------------------------------------------------------------------
    w_d.calibration_coefficients, w_d.calibrant_flags, w_d.calibrants_weightings, \
    w_d.calibrant_residuals = create_calibration(cal_type, w_d.calibrant_medians_minuszero, w_d.calibrant_concs,
                                                 w_d.calibrant_weightings, cal_error_limit, w_d.calibrant_flags)

    # ------------ Apply calibration ----------------------------------------------------------------------------
    w_d.calculated_concentrations = apply_calibration(cal_type, w_d.corr_window_medians, w_d.calibration_coefficients)

    # ------------ Apply dilution factors -----------------------------------------------------------------------
    mdl_indexes = find_cup_indexes(mdl_cup, slk_data.sample_ids)
    w_d.calculated_concentrations = apply_dilution(mdl_indexes, w_d.dilution_factor, w_d.calculated_concentrations)

    # ----- Find duplicates and flag if outside analyte tolerance ------------------------------------------------
    duplicate_indexes = find_duplicate_indexes(slk_data.sample_ids)
    sample_duplicate_indexes = find_duplicate_samples(duplicate_indexes, slk_data.sample_ids, slk_data.cup_types,
                                                      sample_cup_type, qc_cup_ids)
    w_d.quality_flag = determine_duplicate_error(sample_duplicate_indexes, w_d.calculated_concentrations,
                                                 w_d.quality_flag, cal_error_limit)

    # ------ Pull out the data for the QC samples that were measured ---------------------------------------------
    w_d.qc_present = find_qc_present(qc_cups, slk_data.sample_ids)
    for qc in w_d.qc_present:
        indexes = get_qc_index(qc, slk_data.sample_ids)
        medians, flags = get_qc_data(indexes, w_d.calculated_concentrations, w_d.quality_flag)
        qc_name = ''.join(i for i in qc.replace(" ", "") if not i.isdigit())
        setattr(w_d, "{}".format(qc_name + '_indexes'), indexes)
        setattr(w_d, "{}".format(qc_name + '_concentrations'), medians)
        setattr(w_d, "{}".format(qc_name + '_flags'), flags)

    print('Proc time: ' + str((time.time()) - st))

    return w_d


def get_peak_values(peak_starts, ad_data, window_size, window_start):
    """
    Gets the peak height values from the A/D data for each point included in the peak window
    Pulls out the time values as well, which are required for plotting on the interactive screen
    :param peak_starts:
    :param ad_data:
    :param window_size:
    :param window_start:
    :return:
    """

    window_end = int(window_start) + int(window_size)
    # This looks ugly, but it is 10x faster than an expanded for if else statement to accomplish the same thing
    window_values = [
        [ad_data[ind] for ind in list(range((int(p_s) + int(window_start)), (int(p_s) + window_end)))] if p_s[0] != '#'
        else [ad_data[ind] for ind in list(range((int(p_s[1:]) + int(window_start)), (int(p_s) + window_end)))] for p_s
        in peak_starts[:-1]]
    time_values = [
        [ind for ind in list(range((int(p_s) + int(window_start)), (int(p_s) + window_end)))] if p_s[0] != '#'
        else [ind for ind in list(range((int(p_s[1:]) + int(window_start)), (int(p_s) + window_end)))] for p_s in
        peak_starts[:-1]]
    return window_values, time_values


def flag_hashed_samples(peak_starts, quality_flags):
    """
    If a peak start value begins with a HASH(#) then it should be flagged as bad
    :param peak_starts:
    :param quality_flags:
    :return: quality_flags
    """

    quality_flags = [quality_flags[i] if x[0] != '#' else 3 for i, x in enumerate(peak_starts)]
    return quality_flags


def flag_null_samples(analysis_cups, null_cup, quality_flags):
    """
    To better differentiate the NULL peaks in a run, they are flagged bad so that in interactive processing
    they appear as a Red peak window. This is fine to do as NULL peaks are never samples
    :param analysis_cups:
    :param null_cup:
    :param quality_flags:
    :return: quality_flags
    """
    quality_flags = [quality_flags[i] if x != null_cup else 3 for i, x in enumerate(analysis_cups)]

    return quality_flags


def peak_shape_qc(window_values, quality_flags):
    """
    Apply a QC on the peak shape to determine if it is of an acceptable shape
    :param window_values:
    :param quality_flags:
    :return:
    """
    first_slopes = []
    second_slopes = []

    for x in window_values:
        median = npmedian(x)
        normalised = [y / median for y in x]

        fit = polyfit(range(len(x)), normalised, 2)
        first_slopes.append(fit[0])
        second_slopes.append(fit[1])

    for i, x in enumerate(first_slopes):
        if abs(x) > 0.005:
            quality_flags[i] = 5
        elif abs(x) > 0.005 and quality_flags[i] == 5:
            quality_flags[i] = 1
        elif abs(second_slopes[i]) > 0.009:
            quality_flags[i] = 5
        elif abs(second_slopes[i]) < 0.009 and quality_flags[i] == 5:
            quality_flags[i] = 1

    for i, x in enumerate(window_values):
        if npmedian(x) < 3800:
            quality_flags[i] = 1

    return quality_flags


def window_medians(window_values):
    """
    Calculates the window medians for each peak window
    :param window_values:
    :return: window_medians
    """
    window_medians_temp_array = nparray(window_values)

    window_medians_temp_array = npmedian(window_medians_temp_array, axis=1)

    window_medians = list(window_medians_temp_array)

    return window_medians


def find_cup_indexes(specified_cup, analysis_cups):
    """
    Finds the indexes of a cup type of interest, e.g. indexes of DRIF returns peak indexes for Drift samples
    :param specified_cup:
    :param analysis_cups:
    :return: clean_indexes
    """
    a_c = nparray(analysis_cups)

    indexes = npwhere(a_c == specified_cup)

    clean_indexes = [int(x) for x in indexes[0]]
    return clean_indexes


def find_carryover_indexes(high_cup_name, low_cup_name, analysis_cups):
    """
    Finds the indexes for the carryover samples, has to be slightly different to accomodate both
    :param high_cup_name:
    :param low_cup_name:
    :param analysis_cups:
    :return:
    """
    # TODO: could get rid of this function and just use find_cup_indexes twice for both of the carryover samples...
    a_c = nparray(analysis_cups)

    high_index = npwhere(a_c == high_cup_name)
    low_indexes = npwhere(a_c == low_cup_name)

    clean_high = [x for x in high_index[0]]
    clean_low = [x for x in low_indexes[0]]

    return clean_high, clean_low


def organise_basedrift_medians(relevant_indexes, window_medians):
    """
    Due to how nutrient runs are processed, an additional baseline or drift needs to be added to the start and end,
    this function completes that task
    :param relevant_indexes:
    :param window_medians:
    :return: medians, indexes
    """
    medians = [window_medians[x] for x in relevant_indexes]

    if relevant_indexes[0] != 0:
        relevant_indexes.insert(0, 0)
        medians.insert(0, medians[0])

    if relevant_indexes[-1] != len(window_medians):
        relevant_indexes.insert(-1, len(window_medians) - 1)
        medians.insert(-1, medians[-1])
        relevant_indexes.sort()

    return medians, relevant_indexes


def get_basedrift_flags(relevant_indexes, quality_flags):
    """
    Finds and returns flags, used for the baseline and drifts
    :param relevant_indexes:
    :param quality_flags:
    :return:
    """

    flags = [quality_flags[x] for x in relevant_indexes]

    return flags


def get_basedrift_corr_percent(medians, comparator):
    """
    Calculates the correction percent after applying a drift/baseline correction
    Baseline comparator is the top cal
    Drift comparator is the mean of all drifts
    :param medians:
    :param comparator:
    :return: corr
    """

    correction_percent = [(x / comparator) * 100 for x in medians]

    return correction_percent


def baseline_correction(baseline_indexes, baseline_medians, correction_type, window_medians):
    """
    Applies the baseline correction to the all the run peaks
    :param baseline_indexes:
    :param baseline_medians:
    :param correction_type:
    :param window_medians:
    :return: window_medians
    """
    if correction_type == 'Piecewise':

        baseline_interpolation = list(npinterp(range(len(window_medians)), baseline_indexes, baseline_medians))

        new_window_medians = [x - baseline_interpolation[i] for i, x in enumerate(window_medians)]

        return new_window_medians

    else:
        logging.info('Baseline correction not applied')
        return window_medians


def carryover_correction(high_index, low_indexes, window_medians):
    """
    Applies the carryover correction across all the run peaks
    :param high_index:
    :param low_indexes:
    :param window_medians:
    :return:
    """
    high_median = [window_medians[x] for x in high_index]
    low_medians = [window_medians[x] for x in low_indexes]
    carryover_coefficient = (low_medians[0] - low_medians[1]) / (high_median[0] - low_medians[0])

    new_window_medians = [float(x - (window_medians[i - 1] * carryover_coefficient)) if i > 0 else x for i, x in
                          enumerate(window_medians)]
    # new_window_medians = [x - ((x-1) * carryover_coefficient) for x in window_medians]
    return new_window_medians, carryover_coefficient


def find_drift_indexes(drift_cup_name, analysis_cups):
    # TODO: Can I delete this ?
    a_c = nparray(analysis_cups)

    drift_indexes = npwhere(a_c == drift_cup_name)

    clean_indexes = [x for x in drift_indexes[0]]
    return clean_indexes


def drift_correction(drift_indexes, drift_medians, correction_type, window_medians):
    """
    Applies the drift correction across all the run peaks
    :param drift_indexes:
    :param drift_medians:
    :param correction_type:
    :param window_medians:
    :return: window_medians
    """
    if correction_type == 'Piecewise':
        drift_mean = statistics.mean(drift_medians[1:-1])

        drift_calculated = []
        for x in drift_medians:
            drift_calculated.append(drift_mean / x)

        drift_interpolation = npinterp(range(len(window_medians)), drift_indexes, drift_calculated)

        new_window_medians = [x * drift_interpolation[i] for i, x in enumerate(window_medians)]

        return new_window_medians

    else:
        logging.info('Drift correction not applied')
        return window_medians


def get_calibrant_medians(calibrant_indexes, window_medians):
    """
    Finds and returns the peak height medians for the calibrants
    :param calibrant_indexes:
    :param window_medians:
    :return:
    """
    calibrant_medians = [window_medians[ind] for ind in calibrant_indexes]

    return calibrant_medians


def get_calibrant_concentrations(calibrant_indexes, nominal_concentrations):
    """
    Finds and returns the nominal concentrations for the calibrants, i.e. their expected concentrations
    :param calibrant_indexes:
    :param nominal_concentrations:
    :return:
    """
    calibrant_concs = [float(nominal_concentrations[ind]) for ind in calibrant_indexes]

    return calibrant_concs


def get_calibrant_flags(calibrant_indexes, quality_flags):
    """
    Finds and returns the flags for the calibrants
    :param calibrant_indexes:
    :param quality_flags:
    :return:
    """
    calibrant_flags = [quality_flags[ind] for ind in calibrant_indexes]

    return calibrant_flags


def get_calibrant_zero_mean(window_medians, sample_ids, cal_zero_label):
    """
    Calculates the mean height for cal 0 and returns it
    :param window_medians:
    :param sample_ids:
    :param cal_zero_label:
    :return:
    """
    calibrant_zero_mean = statistics.mean(
        median for ind, median in enumerate(window_medians) if sample_ids[ind] == cal_zero_label)

    return calibrant_zero_mean


def remove_calibrant_zero(calibrant_medians, cal_zero_mean):
    """
    Removes the calibrant 0 mean height from all other calibrants
    :param calibrant_medians:
    :param cal_zero_mean:
    :return:
    """
    calibrants_minus_zero = [(cal_median - cal_zero_mean) for cal_median in calibrant_medians]

    return calibrants_minus_zero


def get_calibrant_weightings(calibrant_concentrations):
    """
    Calculates the weightings for calibrants in preparation for making a calibration curve
    :param calibrant_concentrations:
    :return:
    """
    calibration_weightings = [2 if x == 0.0 else 1 for x in calibrant_concentrations]

    return calibration_weightings


def create_calibration(cal_type, calibrant_medians, calibrant_concentrations, calibrant_weightings, calibrant_error,
                       calibrant_flags):
    """
    Completes a iterative calibration that checks if the calibrants fall within the specified limits, otherwise
    the calibrants are flagged and not used and a recalibration takes place. This goes until all calibrants are within
    specification, or there is only 30% left.
    :param cal_type:
    :param calibrant_medians:
    :param calibrant_concentrations:
    :param calibrant_weightings:
    :param calibrant_error:
    :param calibrant_flags:
    :return:
    """
    repeat_calibration = True
    calibration_iteration = 0
    # TODO: Massive todo I've f'd this up royally, it works and works well, but it is not clean at all.
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

            fp = nppoly1d(cal_coefficients)
            y_fitted = [fp(x) for x in calibrant_medians]

            cal_coefficients = list(cal_coefficients)

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

        max_residual_index = int(npargmax(npabs(nparray(calibrant_residuals))))

        if abs(calibrant_residuals[max_residual_index]) > (2 * calibrant_error) and flags_to_fit[
            max_residual_index] != 92:
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

        if calibrant_error < abs(calibrant_residuals[max_residual_index]) < (2 * calibrant_error) and flags_to_fit[
            max_residual_index] != 6:
            repeat_calibration = True
            weightings_to_fit[max_residual_index] = 0.5
            flags_to_fit[max_residual_index] = 92
            calibrant_flags[original_indexes[max_residual_index]] = 92
            calibrant_weightings[original_indexes[max_residual_index]] = 0.5

        if calibration_iteration > 7:
            repeat_calibration = False

    return cal_coefficients, calibrant_flags, calibrant_weightings, calibrant_residuals


def apply_calibration(cal_type, window_medians, calibration_coefficients):
    """
    Applies the calibration to calculate the concentrations of all peaks
    :param cal_type:
    :param window_medians:
    :param calibration_coefficients:
    :return:
    """
    if cal_type == 'Linear':
        calculated_concentrations = [(x * calibration_coefficients[0]) + calibration_coefficients[1] for x in
                                     window_medians]

        return calculated_concentrations


def apply_dilution(mdl_indexes, dilution_factors, calculated_concentrations):
    """
    Calculates the concentration before dilution
    :param mdl_indexes:
    :param dilution_factors:
    :param calculated_concentrations:
    :return:
    """
    cc = nparray(calculated_concentrations)
    df = nparray(dilution_factors[:-1])
    mdl_concs = cc[mdl_indexes]
    mdl = npmean(mdl_concs)

    cc_2 = cc * df - (df - 1) * mdl

    calculated_concentrations = list(cc_2)

    return calculated_concentrations


def find_duplicate_indexes(sample_ids):
    """
    Determines if there are duplicate samples and returns their indexes
    :param sample_ids:
    :return:
    """
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
    """
    Determine the error between the duplicate samples, if outside tolerance level then flag
    :param duplicate_samples:
    :param calculated_concentrations:
    :param quality_flags:
    :param analyte_tolerance:
    :return:
    """
    for sample_indexes in duplicate_samples:
        tested_concentrations = [calculated_concentrations[i] for i in sample_indexes[1]]
        for i, conc in enumerate(tested_concentrations):
            if i > 0:
                difference = conc - tested_concentrations[i - 1]
                if difference > analyte_tolerance:
                    for ind in sample_indexes[1]:
                        quality_flags[ind] = 8

    return quality_flags


def reset_calibrant_flags(quality_flags):
    """
    Reset the calibrant flags on an interactive processing update, essentially removes the flags put in place from the
    calibration reoutine
    :param quality_flags:
    :return:
    """
    for i, x in enumerate(quality_flags):
        if x in [91, 92]:
            quality_flags[i] = 1

    return quality_flags


def pack_data(slk_data, working_data, database):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    run_list = [working_data.run for x in slk_data.sample_ids]
    peak_number = [i for i, x in enumerate(slk_data.sample_ids)]

    package = tuple(zip(run_list, slk_data.cup_types, slk_data.sample_ids, peak_number,
                        working_data.raw_window_medians, working_data.corr_window_medians,
                        working_data.calculated_concentrations, slk_data.survey, slk_data.deployment,
                        slk_data.rosette_position, working_data.quality_flag, working_data.dilution_factor,
                        slk_data.epoch_timestamps))

    c.executemany('INSERT OR REPLACE INTO %sData VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)' % working_data.analyte, package)
    conn.commit()

    package = (working_data.analyte, working_data.run, working_data.channel,
                        slk_data.gains[working_data.analyte], slk_data.bases[working_data.analyte],
                        working_data.carryover_coefficient, working_data.calibrant_zero_mean,
                        working_data.calibration_coefficients[0], working_data.calibration_coefficients[1])

    c.execute('INSERT OR REPLACE INTO nutrientHeader VALUES(?,?,?,?,?,?,?,?,?)', package)
    conn.commit()

    anl = [working_data.analyte for x in working_data.calibrant_indexes]
    run = [working_data.run for x in working_data.calibrant_indexes]
    package = tuple(zip(anl, run, working_data.calibrant_indexes,
                        working_data.calibrant_medians, working_data.calibrant_medians_minuszero,
                        working_data.calibrant_concs, working_data.calibrant_weightings,
                        working_data.calibrant_residuals, working_data.calibrant_flags))

    c.executemany('INSERT OR REPLACE INTO nutrientCalibrants VALUES(?,?,?,?,?,?,?,?,?)', package)
    conn.commit()

    anl = [working_data.analyte for x in working_data.baseline_indexes]
    run = [working_data.run for x in working_data.baseline_indexes]
    package = tuple(zip(anl, run, working_data.baseline_indexes,
                        working_data.baseline_medians, working_data.baseline_flags))

    c.executemany('INSERT OR REPLACE INTO nutrientBaselines VALUES(?,?,?,?,?)', package)
    conn.commit()

    anl = [working_data.analyte for x in working_data.drift_indexes]
    run = [working_data.run for x in working_data.drift_indexes]
    package = tuple(zip(anl, run, working_data.drift_indexes,
                        working_data.drift_medians, working_data.drift_flags))
    print(package)

    c.executemany('INSERT OR REPLACE INTO nutrientDrifts VALUES (?,?,?,?,?)', package)
    conn.commit()


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


# TODO: Finding a nutrient survey needs fixing, this is messy and does not account for all cases!
def determine_nutrient_survey(database, params, sample_id):
    """
    Algorithm for determining the survey of a sample, just has a lot of different checks that need to take place to
    account for all cases
    :param database:
    :param params:
    :param sample_id:
    :return: deployment, rosette, survey
    """
    conn = sqlite3.connect(database)
    c = conn.cursor()

    if sample_id[0:3].lower() == 'test':
        return 'Test', 'Test', 'Test'

    surveys = list(params['surveyparams'].keys())
    for surv in surveys:
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
                            sampleprefisurv = sample_id[
                                              0:len(params['surveyparams'][surv]['seal']['surveyprefisurv'])]
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


def find_qc_present(qc_cups, sample_ids):
    """
    Determine what QC samples are in the analysis
    :param qc_cups:
    :param sample_ids:
    :return:
    """
    qc_present = []
    sample_ids_set = set(sample_ids)
    for qc in qc_cups:
        if any(qc_cups[qc] in s_id for s_id in sample_ids_set):
            if not qc == 'driftsample':
                if qc == 'rmns':
                    [qc_present.append(x) for x in sample_ids_set if qc_cups[qc] in x]
                else:
                    qc_present.append(qc_cups[qc])
    return qc_present


def get_qc_index(qc, sample_ids):
    """
    Get the index of the QC samples
    :param qc:
    :param sample_ids:
    :return:
    """
    indexes = []
    for i, s_id in enumerate(sample_ids):
        if qc in s_id:
            indexes.append(i)
    return indexes


def get_qc_data(indexes, medians, flags):
    """
    Get the data for the QC samples
    :param indexes:
    :param medians:
    :param flags:
    :return:
    """
    qc_medians = [medians[x] for x in indexes]
    qc_flags = [flags[x] for x in indexes]

    return qc_medians, qc_flags


#
# Functions relevant to matching underway nutrient files to RVI merged underway data
#

def generate_rvi_timestamps(epoch_date, length):
    """
    Generates time stamps for every point in the RV Investigator underway NetCDF
    :param epoch_date:
    :param length:
    :return:
    """
    date_to_convert = epoch_date[-22:-3]
    date_format = '%Y-%m-%d %H:%M:%S'
    try:
        epoch_seconds = float(epoch_date[0:8])
    except ValueError:
        epoch_seconds = float(epoch_date[0:7])

    time_stamp = calendar.timegm(time.strptime(date_to_convert, date_format))

    rvi_start_time = time_stamp + epoch_seconds

    rvi_times = []
    rvi_times.append(rvi_start_time)
    for x in range(length):
        rvi_times.append(rvi_times[x] + 5)

    return rvi_times


def match_lat_lons_routine(path, project, database, current_nut, parameters, working_data, slk_data):
    """
    This is the routine that handles the processing workflow of matching up underway data to the RV Investigator
    merged underway instrument file. Completes te time matching, finding Latitude/Longitudes and then packages the
    data to be stored in the database.
    :param path:
    :param project:
    :param database:
    :param current_nut:
    :param parameters:
    :param working_data:
    :param slk_data:
    :return:
    """
    rvi_uwy_path = path + '/' + project + 'uwy.nc'

    if not os.path.isfile(rvi_uwy_path):
        logging.error('There is no RV Investigator file with correct name. Make sure the name matches the project '
                      'name and is suffixed with uwy, e.g. in2019_v01uwy.nc')
        return False

    rvi_uwy = xr.open_dataset(rvi_uwy_path)
    epoch_date = rvi_uwy.Epoch

    rvi_lon = rvi_uwy.longitude.values
    rvi_lat = rvi_uwy.latitude.values

    rvi_times = generate_rvi_timestamps(epoch_date, len(rvi_lon))

    sample_times, sample_concs = extract_underway_samples(slk_data.cup_types, working_data.quality_flag,
                                                          slk_data.epoch_timestamps,
                                                          working_data.calculated_concentrations,
                                                          parameters['nutrientprocessing']['cupnames']['sample'])

    rvi_start, rvi_end = find_rvi_time_subset(sample_times, rvi_times)

    matched_rvi_indexes = find_time_matches(rvi_start, rvi_end, rvi_times, sample_times)

    matched_lats, matched_lons = find_location_matches(matched_rvi_indexes, rvi_lat, rvi_lon)

    file = [working_data.run for x in sample_times]
    packaged_underway_data = tuple(zip(matched_lats, matched_lons, sample_times, sample_concs, file))

    store_underway_data(packaged_underway_data, database, current_nut)


def extract_underway_samples(cup_types, quality_flags, time_stamps, concentrations, sample_name):
    """
    Finds the underway samples and pulls out the time stamps and the relevant concentrations from the run data
    :param cup_types:
    :param quality_flags:
    :param time_stamps:
    :param concentrations:
    :param sample_name:
    :return: sample_times, sample_concentrations
    """


    sample_times = []
    sample_concs = []
    for i, x in enumerate(cup_types):
        if x == sample_name:
            if quality_flags[i] == 1:
                sample_times.append(time_stamps[i])
                sample_concs.append(concentrations[i])

    return sample_times, sample_concs


def find_rvi_time_subset(sample_times, rvi_times):
    """
    Finds the time stamps in the RV Investigator underway file that intersect with the analysis timestamps
    This is used to speed up the process of finding each time stamp by creating a small subset from the entire file
    :param sample_times:
    :param rvi_times:
    :return:
    """
    sample_start_time = min(sample_times)
    sample_end_time = max(sample_times)

    rvi_time_start_index = 0
    rvi_time_end_index = 0

    for i, x in enumerate(rvi_times):
        if abs(x - sample_start_time) < 3:
            rvi_time_start_index = i
        if abs(x - sample_end_time) < 4:
            rvi_time_end_index = i
            break

    return rvi_time_start_index, rvi_time_end_index


def find_time_matches(rvi_start_index, rvi_end_index, rvi_times, sample_times):
    """
    Finds the relevant indexes in the RV Investigator underway file where the time stamp matches the analysis time
    stamp. Creates a list of index points to maintain the original index numbering for after the subsetting
    :param rvi_start_index:
    :param rvi_end_index:
    :param rvi_times:
    :param sample_times:
    :return: matching_indexes
    """

    # A list of indexes is created so that it can be related back to the original file for pulling out the Lat/Lons
    rvi_indexes = [i for i, x in enumerate(rvi_times)]

    rvi_time_subset = rvi_times[rvi_start_index : rvi_end_index]
    rvi_index_subset = rvi_indexes[rvi_start_index : rvi_end_index]

    matched_rvi_indexes = []
    for i, x in enumerate(rvi_time_subset):
        for y in sample_times:
            if abs(x - y) < 5: # Less than 5 because there is a RVI underway point every 5 seconds
                matched_rvi_indexes.append(rvi_index_subset[i])
                break

    return matched_rvi_indexes


def find_location_matches(matched_rvi_indexes, rvi_lats, rvi_lons):
    """
    Finds the latitude and longitude that matches the index of the underway timestamp which was matched up with the
    analysis time stamp
    :param matched_rvi_indexes:
    :param rvi_lats:
    :param rvi_lons:
    :return:
    """
    matched_lats = [rvi_lats[x] for x in matched_rvi_indexes]
    matched_lons = [rvi_lons[x] for x in matched_rvi_indexes]

    return matched_lats, matched_lons


def store_underway_data(packaged_data, database, current_nutrient):
    """
    Interfaces the sqlite database to store the data. Completes a check to see if data is already entered from another
    analyte, i.e when there are multiple channels in one analysis. If there is already data from another analyte, 
    it changes the database entry to update the data and not overwrite what is already entered. 
    :param packaged_data: 
    :param database: 
    :param current_nutrient: 
    :return: 
    """
    conn = sqlite3.connect(database)
    c = conn.cursor()

    file_check = packaged_data[0][4]

    c.execute('SELECT * from underwayNutrients WHERE file=?', (file_check,))
    check_data = c.fetchall()
    if check_data:
        # If some data from the other channel already in, then just update columns with this analytes data
        # Little messy but it shall do
        concs = [x[3] for x in packaged_data]
        times = [x[2] for x in packaged_data]
        shortened_data = tuple(zip(concs, times))
        c.executemany('UPDATE underwayNutrients SET %s=? WHERE time=?' % current_nutrient, shortened_data)
    else:
        c.executemany('INSERT or REPLACE into underwayNutrients(latitude, longitude, time, %s, file) '
                      'VALUES (?, ?, ?, ?, ?)' % current_nutrient, packaged_data)
    
    conn.commit()
    conn.close()        
    
    logging.info('Underway data successfully matched with Investigator data. Correctly packaged and stored in database.')
