import sqlite3
import statistics
from matplotlib.collections import LineCollection
from pylab import *
import numpy as np

theme_color_converter = {'normal': '#191919', 'dark': '#F5F5F5'}

mpl.rc('font', family='Segoe UI Symbol') # Cast Segoe UI font onto all plot text
FLAG_COLORS = {1: '#68C968', 2: '#45D4E8', 3: '#C92724', 4: '#3CB6C9', 5: '#C92724', 6: '#DC9530',
                    91: '#9CCDD6', 92: '#F442D9', 8: '#3CB6C9'}
'''

File contains methods to produce various specific plots if you pass the Matplotlib figure, axes and data
These are just all functions that will apply to data and changes to an axes or figure

'''

# TODO: Fix RMNS plot so it still works even if nominal RMNS values are not in the database

def draw_trace(fig, axes, ad_data, trace_redraw=None, theme='normal'):

    if len(axes.lines) == 0:
        axes.grid(alpha=0.1)
        axes.set_xlabel('Time (s)')
        axes.set_ylabel('A/D Value')

        axes.plot(range(len(ad_data)), ad_data, lw=0.9, label='trace', color=theme_color_converter[theme])

        axes.set_xlim(0, len(ad_data))
        axes.set_ylim(0, max(ad_data))

    if len(axes.lines) > 1:
        del axes.lines[1:]
        del axes.artists[1:]

    if trace_redraw:
        del axes.lines[:]
        axes.plot(range(len(ad_data)), ad_data, lw=0.9, label='trace', color=theme_color_converter[theme])

def draw_peak_windows(fig, axes, time_values, window_values, flags):

    for i, time_arr in enumerate(time_values):
        axes.plot(time_arr, window_values[i], color=FLAG_COLORS[flags[i]], linewidth=2.5, label='p_windows')

def draw_drifts_baselines(fig, axes, basl_peak_st, basl_medians, drift_peak_st, drift_medians):

    axes.plot(basl_peak_st, basl_medians, linewidth=1, color="#d69f20", label='baseline')
    axes.plot(drift_peak_st, drift_medians, linewidth=1, color="#c6c600", label='drift')


def recovery_plot(fig, axes, indexes, concentrations, ids, flags, title_append=''):

    del axes.lines[:]
    del axes.texts[:]

    # Figure out which ones are which, make a sub index number to reference the concentrations and flags
    # The indexes parameter function references the peak number index relative to the whole run just FYI

    if indexes:
        # Get the subset indexes as lists, could be case where an analysis has multiple column checks
        nitrite_stds_sub_index = [i for i, x in enumerate(ids) if 'NO2' in x]
        nitrate_stds_sub_index = [i for i, x in enumerate(ids) if 'NO3' in x]
        conversion_efficiency = []
        plottable_index = []
        flags_to_plot = []

        for i, std in enumerate(nitrite_stds_sub_index):
            eff_pct = (concentrations[std] / concentrations[nitrate_stds_sub_index[i]]) * 100
            conversion_efficiency.append(eff_pct)
            plottable_index.append(indexes[std]+1)
            flags_to_plot.append(flags[std])

        axes.grid(alpha=0.2, zorder=1)
        # Loop through so different colours can be easily applied
        for i, x in enumerate(conversion_efficiency):
            axes.plot(plottable_index[i], conversion_efficiency[i], lw=0, marker='o', ms=25, color=FLAG_COLORS[flags_to_plot[i]])
            axes.annotate(f'{round(conversion_efficiency[i], 1)}', [plottable_index[i], conversion_efficiency[i]],
                          fontsize=10, ha='center', va='center', color='#FFFFFF', fontfamily='Arial')

        axes.set_title(f'Mean efficiency: {round(statistics.mean(conversion_efficiency), 3)} %', fontsize=12)
        axes.set_xlabel('Peak Number')
        axes.set_ylabel('NO3 to NO2 Conversion Efficiency (%)')

        # Add lines for reference to good and bad conversion efficiency
        hundred_percent = [(0, 100), (100, 100)]
        ninety_eight_percent = [(0, 98), (100, 98)]
        axes.add_collection(LineCollection([hundred_percent], color='#7AAD84', lw=2, linestyle='--'))
        axes.add_collection(LineCollection([ninety_eight_percent], color='#AD804A', lw=2, linestyle='--'))

    else:
        # Instead of not plotting at all - this error message was implemented so the user is aware
        at = axes.annotate('No column recovery peaks were found. If this message is unexpected, check the '
                      'project parameters and ensure the recovery cup type matches what is in the .SLK file.',
                      [0.02, 0.5], xycoords='axes fraction', fontsize=14, wrap=True, fontname='Segoe UI Symbol',
                    bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1'))
        axes.set_axis_off()
    fig.set_tight_layout(tight=True)

def calibration_curve_plot(fig, axes, cal_medians, cal_concs, flags, cal_coefficients, r_score=0, title_append=''):
    if len(axes.lines) > 0:
        del axes.lines[:]
        del axes.texts[:]

    else:
        axes.set_xlabel('A/D Medians', fontsize=12)
        axes.set_ylabel('Calibrant Concentrations', fontsize=12)
        axes.grid(alpha=0.3, zorder=1)

    axes.set_title(f'Calibration Curve {title_append}', fontsize=14)

    fit = np.poly1d(cal_coefficients)

    axes.plot(cal_medians, [fit(x) for x in cal_medians], lw=1, marker='.', ms=4, color='C0')

    for i, flag in enumerate(flags):
        if flag == 1:
            colour = "#12ba66"
            size = 14
            mark = 'o'
            lab = 'Good'
        elif flag == 2:
            colour = '#63d0ff'
            size = 16
            mark = '+'
            lab = 'Suspect'
        elif flag == 3 or flag == 5:
            colour = "#d11b1b"
            size = 16
            mark = '+'
            lab = 'Bad'
        else:
            colour = "#d11b1b"
            size = 19
            mark = 'o'
            lab = 'Bad'
        axes.plot(cal_medians[i], cal_concs[i], marker=mark, color=colour, ms=size, lw=0, mfc='none', label=lab)

    handles, labels = axes.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    axes.legend(by_label.values(), by_label.keys())
    axes.set_ylim((0-(max(cal_concs)*0.05)), max(cal_concs)*1.05)
    axes.set_xlim((0-(max(cal_medians)*0.05)), max(cal_medians)*1.05)

    axes.annotate(f'R Squared: {round(r_score,4)}', xy=(0.76, 0.05), xycoords="axes fraction", fontsize=11)

    #axes.plot(cal_medians, cal_concs, marker='o', mfc='none', lw=0, ms=11)
    fig.set_tight_layout(tight=True)

def calibration_error_plot(fig, axes, cal, cal_error, analyte_error, flags, title_append=''):
    analyte_error = float(analyte_error)
    if len(axes.lines) > 0:
        del axes.lines[1:]
    else:
        axes.set_xlabel('Calibrant Index', fontsize=12)
        axes.set_ylabel('Error from fitted concentration', fontsize=12)
        axes.grid(alpha=0.3, zorder=1)

    axes.set_title(f'Calibrant Error {title_append}', fontsize=14)

    axes.plot([0, max(cal)], [0, 0], lw=1.75, linestyle='--', alpha=0.7, zorder=2, color='#14E43E')

    axes.plot([0, max(cal)], [analyte_error, analyte_error], color='#5AD3E2', lw=1.25)
    axes.plot([0, max(cal)], [-abs(analyte_error), -abs(analyte_error)], color='#5AD3E2', lw=1.25, label = '1X Analyte Error')

    axes.plot([0, max(cal)], [(2*analyte_error), (2*analyte_error)], color='#F375E9', lw=1.25)
    axes.plot([0, max(cal)], [(-2 * analyte_error), (-2 * analyte_error)], color='#F375E9', lw=1.25, label='2X Analyte Error')

    for i, x in enumerate(flags):
        if x == 1:
            colour = "#12ba66"
            size = 6
            mark = 'o'
            lab = 'Good'
        if x == 2 or x==4 or x == 91:
            colour = '#63d0ff'
            size = 14
            mark = '+'
            lab = 'Suspect'
        if x == 3 or x == 5 or x == 92:
            colour = "#d11b1b"
            size = 14
            mark = '+'
            lab = 'Bad'
        try:
            axes.plot(cal[i], cal_error[i], marker=mark, mfc=colour, linewidth=0, markersize=size,
                       color=colour, alpha=0.8, label = lab)
        except IndexError:
            pass

    handles, labels = axes.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    axes.legend(by_label.values(), by_label.keys())
    #axes.set_xlim((0-(max(cal)*0.05)), 0+max(cal)*1.05)
    axes.set_xlim(min(cal)-1, max(cal)+ 1)

    if max(cal_error) < analyte_error:
        axes.set_ylim((analyte_error*1.4)*-1, (analyte_error*1.4))
    else:
        axes.set_ylim(0-max(cal_error)*1.4, max(cal_error)*1.4)

    fig.set_tight_layout(tight=True)

def basedrift_correction_plot(fig, axes1, axes2, type, indexes, correction, medians, flags, title_append=''):
    if len(axes1.lines) > 0:
        del axes1.lines[:]
        del axes2.lines[:]
    else:
        axes1.set_xlabel('Peak Number')
        axes1.set_ylabel('Raw Peak Height (A/D)')
        axes1.grid(alpha=0.3, zorder=1)
        axes2.set_title('%s Correction Percentage' % type)
        axes2.set_xlabel('Peak Number')
        axes2.set_ylabel('Percentage of Top Cal (%)')
        axes2.grid(alpha=0.3, zorder=1)

    axes1.set_title(f'{type} Peak Height {title_append}')

    axes1.plot(indexes, medians, mfc='none', linewidth=1.25, linestyle=':', color="#8C8C8C", alpha=0.9)
    for i, x in enumerate(flags):
        if x == 1:
            colour = "#12ba66"
            size = 14
            mark = 'o'
        elif x == 3:
            colour = '#63d0ff'
            size = 16
            mark = '+'
        elif x == 2:
            colour = "#d11b1b"
            size = 16
            mark = '+'
        else:
            colour = "#d11b1b"
            size = 19
            mark = 'o'
        axes1.plot(indexes[i], medians[i], linewidth=1.25, linestyle=':', mfc='none', mec=colour,
                   marker=mark, markersize=size, color="#25543b")

        axes1.set_ylim(min(medians) * 0.975, max(medians) * 1.025)

    axes2.plot(indexes, correction, lw=1.25, marker='s', ms=8, mfc='none', color='#6986e5')
    axes2.relim()
    fig.set_tight_layout(tight=True)

def rmns_plot(fig, axes, indexes, concentrations, flags, rmns, nutrient, show_flags=None, show_bad=None,
              title_append=''):
    nut_column = {'phosphate': 1, 'silicate': 3, 'nitrate': 5, 'nitrite': 7, 'ammonia': 9}

    del axes.lines[:]
    del axes.texts[:]

    conn = sqlite3.connect('C:/HyPro/Settings/hypro.db')
    c = conn.cursor()
    c.execute('SELECT * from rmnsData')
    rmns_data = c.fetchall()
    rmns = (rmns.lower().replace("rmns", "").replace(" ", "")).swapcase()

    current_rmns = [x for x in rmns_data if x[0] in rmns]
    if current_rmns:
        conc = current_rmns[0][nut_column[nutrient]]
        axes.plot([min(indexes)-1, max(indexes)+1], [conc]*2, lw=1, linestyle='--', color='#8B8B8B', label='Certified Value')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*1.01]*2, lw=1, color= '#12ba66', label = '1% Concentration Error')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*0.99]*2, lw=1, color= '#12ba66', label = '1% Concentration Error')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*1.02]*2, lw=1, color= '#63d0ff', label = '2% Concentration Error')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*0.98]*2, lw=1, color= '#63d0ff', label = '2% Concentration Error')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*1.03]*2, lw=1, color= '#E54580', label = '3% Concentration Error')
        axes.plot([min(indexes)-1, max(indexes)+1], [conc*0.97]*2, lw=1, color= '#e56969', label = '3% Concentration Error')

    else:
        axes.annotate('No RMNS values found', [0.05, 0.05], xycoords='axes fraction')

    if current_rmns:
        axes.set_title(f'{nutrient.capitalize()} RMNS {rmns} (Cert. Val: {conc} )', fontsize=12)
    else:
        axes.set_title(str(nutrient).capitalize() + ' RMNS ' + str(rmns), fontsize=12)

    axes.set_xlabel('Peak Number')
    axes.set_ylabel('Concentration (uM)')
    axes.grid(alpha=0.2, zorder=1)

    for i, ind in enumerate(indexes):
        axes.plot(ind, concentrations[i], lw=0, marker='o', ms=6, color=FLAG_COLORS[flags[i]])

    axes.plot(indexes, concentrations, lw=0.75, linestyle=':', marker='o', ms=10, picker=5, mfc='None',  color='C0')

    axes.set_ylim(min(concentrations) * 0.975, max(concentrations) * 1.025)
    axes.set_xlim(min(indexes)-1, max(indexes)+1)

    if current_rmns:
        handles, labels = axes.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        axes.legend(by_label.values(), by_label.keys())

    axes.annotate(f'Average: {round(statistics.mean(concentrations), 3)}', [0.02, 0.96],
                  xycoords='axes fraction', fontsize=11)
    axes.annotate(f'St. Dev.: {round(statistics.stdev(concentrations), 3)}', [0.02, 0.92],
                  xycoords='axes fraction', fontsize=11)


def mdl_plot(fig, axes, indexes, concentrations, flags, stdevs=None, run_nums=None, show_flags=None, show_bad=None,
             title_append=''):

    if len(axes.lines) > 0:
        del axes.lines[:]
        del axes.texts[:]

    axes.set_title(f'MDL {title_append}', fontsize=12)
    axes.set_xlabel('Peak Number')
    axes.set_ylabel('Concentration (uM)')
    axes.grid(alpha=0.2, zorder=2)

    # Used when the across voyage plot is required - plots standard deviation per run
    if stdevs:
        if len(fig.axes) > 1:
            fig.axes[1].remove()

        stdev_plot = axes.twinx()

        mean_conc = statistics.mean(concentrations)
        stdev_conc = statistics.mean(concentrations)

        mean_mdl_plot = axes.plot((-999, 999), (mean_conc, mean_conc), linewidth=0.5, linestyle='--', color='#4286f4', label='Mean MDL')
        upper_mdl_plot = axes.plot((-999, 999), ((stdev_conc * 2) + mean_conc, (stdev_conc * 2) + mean_conc), linewidth=0.5, color='#2baf69', label='Lower/Upper 2xSD')
        lower_mdl_plot = axes.plot((-999, 999), (mean_conc - (stdev_conc * 2), (mean_conc - stdev_conc * 2)), linewidth=0.5, color='#2baf69')

        stdev_runs_plot = stdev_plot.plot(run_nums, stdevs, linewidth=0, marker='s', markersize=5, mec='#949fb2', mfc='#949fb2', alpha=0.8, label='MDL SD per run')
        stdev_plot.set_ylabel('Standard Deviation per Run (µM)', fontsize=12)

        for i, ind in enumerate(indexes):
            axes.plot(ind, concentrations[i], lw=0, marker='o', ms=5, color=FLAG_COLORS[flags[i]])

        axes.plot(indexes, concentrations, linestyle=':', lw=0.25, marker='o', mfc='None', mec='#12BA66', ms=12,
                  label='Measured MDL', picker=5, color='C0')

        # These two lines required to make sure main axes is in front of the secondary axis, for the pick event to work
        axes.set_zorder(stdev_plot.get_zorder() + 1)
        axes.patch.set_visible(False)

        #axes.set_xlim(min(indexes)-1, max(indexes)+1)
        all_lines = mean_mdl_plot + upper_mdl_plot + stdev_runs_plot
        labs = [l.get_label() for l in all_lines]
        axes.legend(all_lines, labs)
    # Normal in processing plot
    else:
        mdl = 3 * statistics.stdev(concentrations)
        axes.plot(indexes, concentrations, linestyle=':', lw=0.25, marker='o', mfc='None', mec='#12BA66', ms=12,
                  picker=5, color='C0', label=f'3x St.Dev.: {round(mdl, 3)}')
        #axes.set_ylim(min(concentrations)-0.05, max(concentrations)+0.05)

        axes.annotate(f'Average: {round(statistics.mean(concentrations), 3)}', [0.02, 0.96],
                      xycoords='axes fraction', fontsize=11)
        axes.annotate(f'3x Standard Deviation: {round(mdl, 3)}', [0.02, 0.92],
                      xycoords='axes fraction', fontsize=11)

        #axes.legend(fontsize=12)

    axes.set_xlim(min(indexes) - 1, max(indexes) + 1)

    fig.set_tight_layout(tight=True)

def bqc_plot(fig, axes, indexes, concentrations, flags, title_append=''):
    if len(axes.lines) > 0:
        del axes.lines[:]
        del axes.texts[:]

    else:
        axes.set_title('BQC')
        axes.set_xlabel('Peak Number')
        axes.set_ylabel('Concentration (uM)')
        axes.grid(alpha=0.3, zorder=2)

    mean_bqc = statistics.mean(concentrations)

    axes.plot(indexes, [mean_bqc]*len(indexes), lw=1, linestyle='--', label = f'Run Mean: {str(round(mean_bqc, 3))}')

    axes.plot(indexes, concentrations, lw=1, linestyle=':', marker='o', mfc='none')
    axes.set_ylim(min(concentrations)*0.99, max(concentrations)*1.01)

    #axes.legend(fontsize=12)
    axes.annotate(f'Average: {round(mean_bqc, 3)}', [0.02, 0.96], xycoords='axes fraction', fontsize=11)
    axes.annotate(f'Standard Deviation: {round(statistics.stdev(concentrations), 3)}', [0.02, 0.92],
                  xycoords='axes fraction', fontsize=11)

    fig.set_tight_layout(tight=True)


def sensor_difference_plot(fig, axes, x_data, difference, max_rp, flags=None, show_flags=None, flag_ref_inds=None,
                           show_bad=None, sensor='Primary', clear_plot=True):

    if (len(axes.lines) > 0) & clear_plot:
        del axes.lines[:]

    if sensor == 'Primary':
        col = '#4068ce'
    else:
        col = '#71ce40'

    if show_flags:
        if not flag_ref_inds:
            for i, x_dat in enumerate(x_data):
                axes.plot(x_dat, difference[i], lw=0, ms=5, marker='o', color=FLAG_COLORS[flags[i]])
        else:
            for i, ind in enumerate(flag_ref_inds):
                axes.plot(x_data[i], difference[i], lw=0, ms=5, marker='o', color=FLAG_COLORS[flags[ind]])

    axes.plot(x_data, difference, linewidth=0.75, linestyle=':', marker='o', markersize=13, mfc='none',
              color=col, picker=7, gid='picking_line', label=sensor)

    labels = axes.get_xticks().tolist()
    new_labels = []
    for x_tick_label in labels:
        deployment_label = int(x_tick_label / max_rp) + 1
        new_label = str(deployment_label) + '/' + str(int(x_tick_label - ((deployment_label - 1) * max_rp)))
        new_labels.append(new_label)

    axes.set_xticklabels(new_labels)
    axes.plot([-9999, 9999], [0, 0], linewidth=1.2, linestyle='--', color='#303030')
    axes.set_xlim(min(x_data) - 3, max(x_data) + 3)

    fig.set_tight_layout(tight=True)


def sensor_difference_pressure_plot(fig, axes, difference, pressures, flags=None, deployments=None):
    if len(axes.lines) > 0:
        del axes.lines[:]

    if deployments:
        for dep in sorted(list(set(deployments))):
            plotting_indexes = []
            for i, x in enumerate(deployments):
                if dep == x:
                    plotting_indexes.append(i)
            pressure_dep_subset = [pressures[x] for x in plotting_indexes]
            difference_dep_subset = [difference[x] for x in plotting_indexes]
            axes.plot(difference_dep_subset, pressure_dep_subset, marker='o', lw=0.3, mfc='None', markersize=5,
                      linestyle=':', label=f'Deployment {dep}')
        axes.legend()

        axes.plot(difference, pressures, linewidth=0, marker='o', markersize=0, picker=5, gid='picking_line')
    else:
        axes.plot(difference, pressures, marker='o', lw=0, mfc='None', markersize=5, alpha=0.8, gid='picking_line')


def sensor_profile_plot(fig, axes, pressure, bottle, flags, flag_ref_inds=None, primary=None, secondary=None, deployments=None):
    if deployments:
        for dep in sorted(list(set(deployments))):
            plotting_indexes = []
            for i, x in enumerate(deployments):
                if dep == x:
                    plotting_indexes.append(i)
            bottle_oxy_dep_subset = [bottle[x] for x in plotting_indexes]
            pressure_dep_subset = [pressure[x] for x in plotting_indexes]

            temp = axes.plot(bottle_oxy_dep_subset, pressure_dep_subset, marker='o', lw=1.2, mfc='None', markersize=0,
                      label=f'Deployment {dep}')

            # Get the plotted bottle profile color, so that the CTD profile matches
            current_axes_color = temp[0].get_color()

            if primary:
                primary_dep_subset = [primary[x] for x in plotting_indexes]
                axes.plot(primary_dep_subset, pressure_dep_subset, lw=0.75, linestyle='-.', color=current_axes_color,
                          alpha=0.8, label=f'Primary Sens: Dep {dep}')

            if secondary:
                secondary_dep_subset = [secondary[x] for x in plotting_indexes]
                axes.plot(secondary_dep_subset, pressure_dep_subset, lw=0.75, linestyle='--', color=current_axes_color,
                          alpha=0.8, label=f'Secondary Sens: Dep {dep}')

    else:
        axes.plot(bottle, pressure, marker='o', lw=1, mfc='None', markersize=0)

    if flag_ref_inds:
        for i, ind in enumerate(flag_ref_inds):
            axes.scatter(bottle[i], pressure[i], alpha=0.8, s=18, color=FLAG_COLORS[flags[ind]], zorder=10)

    else:
        for i, bot in enumerate(bottle):
            axes.scatter(bot, pressure[i], alpha=0.8, s=18, color=FLAG_COLORS[flags[i]], zorder=10)

    axes.plot(bottle, pressure, linewidth=0, marker='o', markersize=0, picker=5, gid='picking_line')

    axes.set_ylabel('Pressure (dbar)')
    axes.legend()


