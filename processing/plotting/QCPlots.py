from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import io
import json
import sqlite3
import statistics
import traceback
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5.QtWidgets import (QMainWindow, QWidget, QDesktopWidget, QApplication, QVBoxLayout, QAction, QLabel,
                             QFileDialog, QTabWidget, QGridLayout, QComboBox, QListWidget, QPushButton, QCheckBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from matplotlib.ticker import MaxNLocator
from pylab import *
import pandas as pd
import style
import hyproicons
from processing.plotting.InteractiveProcPlottingWindow import hyproProcPlotWindow
from dialogs.TraceSelectionDialog import traceSelection
from processing.plotting.PlottingWindow import QMainPlotterTemplate

mpl.rc('font', family = 'Segoe UI Symbol') # Cast Segoe UI font onto all plot text

# File contains classes to produce various specific plots, all classes that utilise QWidget are apart of the
# nutrient processing workflow
# The other classes using QMainWindow are plots that are called on manually and are then displayed in their
# own window

# TODO: Fix RMNS plot so it still works even if nominal RMNS values are not in the database

FLAG_COLORS = {1: '#68C968', 2: '#45D4E8', 3: '#C92724', 4: '#3CB6C9', 5: '#C92724', 6: '#DC9530',
                    91: '#9CCDD6', 92: '#F442D9', 8: '#3CB6C9'}

class redfieldPlot(QMainPlotterTemplate):
    def __init__(self, database):
        super().__init__()
        self. database = database

        self.apply_button.clicked.connect(self.draw_data)

        self.setWindowTitle('Redfield Ratio Plot')

        self.main_plot.set_title('Redfield Ratio', fontsize=18)
        self.main_plot.set_xlabel('[NOx] (uM)', fontsize=15)
        self.main_plot.set_ylabel('[Phosphate] (uM)', fontsize=15)

        self.main_plot.grid(alpha=0.1)
        survey_label = QLabel('Survey to use:', self)
        #survey_label.setFont(QFont('Segoe UI'))
        self.survey_selector = QComboBox()
        self.survey_selector.setFont(QFont('Segoe UI'))

        self.qvbox_layout.insertWidget(0, survey_label)
        self.qvbox_layout.insertWidget(1, self.survey_selector)

        self.populate_fields()
        self.show()

    def populate_fields(self):

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('SELECT DISTINCT runNumber FROM nitrateData')
        nitrate_runs = sorted(list(c.fetchall()))
        c.execute('SELECT DISTINCT runNumber FROM phosphateData')
        phosphate_runs = list(c.fetchall())

        runs = []
        for x in nitrate_runs:
            if x in phosphate_runs:
                runs.append(x[0])
                self.run_list.addItem(str(x[0]))
        query_placeholder = ', '.join('?' for unused in runs)
        c.execute(f'SELECT DISTINCT survey from nitrateData WHERE runNumber in ({query_placeholder})', (runs))
        distinct_surveys = list(c.fetchall())
        c.close()
        for x in distinct_surveys:
            self.survey_selector.addItem(x[0])


    def draw_data(self):
        selected = self.run_list.selectedItems()
        selected_runs = [int(item.text()) for item in selected]

        if selected_runs:
            conn = sqlite3.connect(self.database)
            query_placeholder = ', '.join('?' for unused in selected_runs)
            nox_df = pd.read_sql_query(f"SELECT * FROM nitrateData WHERE runNumber IN ({query_placeholder})", conn,
                                       params=selected_runs)
            phos_df = pd.read_sql_query(f"SELECT * FROM phosphateData WHERE runNumber IN ({query_placeholder})", conn,
                                       params=selected_runs)
            conn.close()
            nox_plottable = []
            phos_plottable = []
            for nox_row in nox_df.itertuples():
                phos_point = phos_df.loc[(phos_df['runNumber'] == nox_row[1]) & (phos_df['peakNumber'] == nox_row[4])]
                nox_plottable.append(nox_row[7])
                phos_plottable.append(float(phos_point['concentration']))

            self.main_plot.scatter(nox_plottable, phos_plottable, marker='o', facecolors='#FFB186', edgecolors='#EF8A68',
                                   alpha=0.75)

            self.canvas.draw()

class rmnsPlotWindowTemplate(QMainPlotterTemplate):
    def __init__(self, database, params_path):
        super().__init__()
        self. database = database
        with open(params_path, 'r') as file:
            self.params = json.loads(file.read())

        self.nut_converter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                             'Ammonia': 'ammonia'}

        self.rmnscols = {'NOx': 5, 'Phosphate': 1, 'Silicate': 3, 'Nitrite': 7, 'Ammonia': 9}

        self.setWindowTitle('HyPro - RMNS')

        self.main_plot.set_title('RMNS', fontsize=18)
        self.main_plot.set_xlabel('Run/Peak Number', fontsize=15)
        self.main_plot.set_ylabel('Concentration (uM)', fontsize=15)

        self.main_plot.grid(alpha=0.1)

        nutrient_label = QLabel('Nutrient', self)
        self.nutrient = QComboBox(self)
        self.nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])
        self.nutrient.currentIndexChanged.connect(self.populate_rmns)

        rmns_type_label = QLabel('RMNS Lot')
        self.rmns_type = QComboBox(self)
        self.rmns_type.currentIndexChanged.connect(self.populate_run_list)

        self.qvbox_layout.insertWidget(0, nutrient_label)
        self.qvbox_layout.insertWidget(1, self.nutrient)
        self.qvbox_layout.insertWidget(2, rmns_type_label)
        self.qvbox_layout.insertWidget(3, self.rmns_type)

        self.apply_button.clicked.connect(self.draw_data)

        self.populate_rmns()
        self.populate_run_list()
        self.show()

    def populate_rmns(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nut_converter[nut]
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()
            rmnsnamelength = len(self.params['nutrientprocessing']['qcsamplenames']['rmns'])
            listofrmns = []
            for i, x in enumerate(data):
                if x[1][:rmnsnamelength] == self.params['nutrientprocessing']['qcsamplenames']['rmns']:
                    listofrmns.append(x)
            rmnslots = set([x[1][rmnsnamelength:(rmnsnamelength + 3)] for x in listofrmns])

            self.rmns_type.clear()
            self.rmns_type.addItems(rmnslots)

        except Exception:
            print(traceback.print_exc())

    def populate_run_list(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nut_converter[nut]
            rmns = self.rmns_type.currentText()

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()

            runnums = []
            for i, x in enumerate(data):
                if rmns in x[1]:
                    runnums.append(x[0])

            self.run_list.clear()
            rn = sorted(list(set(runnums)))
            for x in rn:
                self.run_list.addItem(str(x))
        except Exception:
            print(traceback.print_exc())

    def draw_data(self):
        try:
            del self.main_plot.lines[:]
            nut = self.nutrient.currentText()
            nutq = self.nut_converter[nut]
            rmns = self.rmns_type.currentText()
            selected = self.run_list.selectedItems()
            selected_runs = [item.text() for item in selected]

            queryq = '?'
            queryplaceruns = ', '.join(queryq for unused in selected_runs)
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                'SELECT peakNumber, runNumber, sampleID, concentration, flag FROM %sData WHERE runNumber IN (%s)' % (
                    nutq, queryplaceruns), (selected_runs))
            data = list(c.fetchall())
            c.close()

            self.runs = []
            self.conctoplot = []
            self.peaknums = []
            sampleid = []
            self.flagtoplot = []
            for x in data:
                if rmns in x[2]:
                    self.peaknums.append(x[0])
                    self.runs.append(x[1])
                    sampleid.append(x[2])
                    self.conctoplot.append(x[3])
                    self.flagtoplot.append(x[4])

            runpeaknumhold = []
            self.runpeaknumtoplot = []
            runs = sorted(set(self.runs))

            for x in runs:
                runpeaknumhold.append(self.runs.count(x))

            for i, x in enumerate(runpeaknumhold):
                for y in range(x):
                    if y > 0:
                        self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                    else:
                        self.runpeaknumtoplot.append(runs[i])


            rmns_plot(self.figure, self.main_plot, self.runpeaknumtoplot, self.conctoplot, self.flagtoplot, rmns, nutq)
            self.canvas.draw()
        except Exception:
            print(traceback.print_exc())
    def matchclicktopeak(self, xval, yval):
        found = False
        for i, x in enumerate(self.runpeaknumtoplot):
            if abs(x - xval) < 0.09: # Check x coords to where was clicked
                if abs(self.conctoplot[i] - yval) < 0.01: # Check y coords to where was clicked if less than threshold
                                                           # then pick this peak
                    runnum = self.runs[i]
                    peaknum = self.peaknums[i]
                    found = True
                    break  # Break here because we've found the peak

        if found:  # Complete rest of function because we've found a peak, pull up the peaks information
            nutq = self.nutconverter[self.nutrient.currentText()]
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute(
                'SELECT sampleID, cupType, correctedAD, concentration, flag, dilution '
                'FROM %sData WHERE runNumber=? AND peakNumber=?' % nutq, (runnum, peaknum))
            data = list(c.fetchall())
            c.close()
            # Display the peak information dialog, no point assigning variables just pull from data call of db
            # aka  in SampleID, CupType, CorrAD, Conc, Flag, Dilution, PlotType
            self.selection = traceSelection(sampleid=data[0][0], cuptype=data[0][1], peaknumber=peaknum,
                                            admedian=data[0][2], conc=data[0][3], flag=data[0][4], dil=data[0][5],
                                            type='Plot')
            self.selection.show()

class mdlPlotWindowTemplate(QMainPlotterTemplate):
    def __init__(self, database, params_path):
        super().__init__()
        self. database = database
        with open(params_path, 'r') as file:
            self.params = json.loads(file.read())

        self.nut_converter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                             'Ammonia': 'ammonia'}

        self.setWindowTitle('HyPro - MDL')
        self.main_plot.set_title('MDL', fontsize=18)
        self.main_plot.set_xlabel('Run/Peak Number', fontsize=15)
        self.main_plot.set_ylabel('Concentration (uM)', fontsize=15)

        self.main_plot.grid(alpha=0.1)

        nutrient_label = QLabel('Nutrient', self)
        self.nutrient = QComboBox(self)
        self.nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])
        self.nutrient.currentIndexChanged.connect(self.populate_run_list)


        self.qvbox_layout.insertWidget(0, nutrient_label)
        self.qvbox_layout.insertWidget(1, self.nutrient)

        self.apply_button.clicked.connect(self.draw_data)

        self.populate_run_list()

    def populate_run_list(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nut_converter[nut]

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()

            mdl = self.params['nutrientprocessing']['qcsamplenames']['mdl']
            runnums = []
            for i, x in enumerate(data):
                if mdl in x[1]:
                    runnums.append(x[0])
            self.run_list.clear()
            rn = sorted(list(set(runnums)))
            for x in rn:
                self.run_list.addItem(str(x))

        except Exception:
            print(traceback.print_exc())

    def draw_data(self):
        nut = self.nutrient.currentText()
        nutq = self.nut_converter[nut]
        selected = self.run_list.selectedItems()
        selected_runs = [item.text() for item in selected]

        mdl = self.params['nutrientprocessing']['qcsamplenames']['mdl']

        queryq = '?'
        queryplaceruns = ', '.join(queryq for unused in selected_runs)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute(
            'SELECT peakNumber, runNumber, sampleID, concentration, flag FROM %sData WHERE runNumber IN (%s)' % (
                nutq, queryplaceruns), (selected_runs))
        data = list(c.fetchall())
        c.close()

        self.runs = []
        self.conctoplot = []
        self.peaknums = []
        sampleid = []
        self.flagtoplot = []
        for x in data:
            if mdl in x[2]:
                self.peaknums.append(x[0])
                self.runs.append(x[1])
                sampleid.append(x[2])
                self.conctoplot.append(x[3])
                self.flagtoplot.append(x[4])

        runpeaknumhold = []
        self.runpeaknumtoplot = []
        runs = sorted(set(self.runs))

        stdevs = []
        for x in runs:
            conchold = []
            for i, y in enumerate(self.runs):
                if x == y:
                    conchold.append(self.conctoplot[i])
            stdevs.append(statistics.stdev(conchold))

            runpeaknumhold.append(self.runs.count(x))

        for i, x in enumerate(runpeaknumhold):
            for y in range(x):
                if y > 0:
                    self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                else:
                    self.runpeaknumtoplot.append(runs[i])
        mdl_plot(self.figure, self.main_plot, self.runpeaknumtoplot, self.conctoplot, self.flagtoplot, stdevs=stdevs, run_nums=runs)
        self.canvas.draw()

        #self.figure.axes[1].cla()



def recovery_plot(fig, axes, indexes, concentrations, ids, flags):

    del axes.lines[:]
    del axes.texts[:]

    # Figure out which ones are which, make a sub index number to reference the concentrations and flags
    # The indexes parameter function references the peak index relative to the whole run just FYI

    if indexes:
        # Get the subset indexes as lists, could be case where an analysis has multiple column checks
        nitrite_stds_sub_index = [i for i, x in enumerate(ids) if '2' in x]
        nitrate_stds_sub_index = [i for i, x in enumerate(ids) if '3' in x]

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

def calibration_curve_plot(fig, axes, cal_medians, cal_concs, flags, cal_coefficients):
    if len(axes.lines) > 0:
        del axes.lines[:]
    else:
        axes.set_title('Calibration Curve')
        axes.set_xlabel('A/D Medians')
        axes.set_ylabel('Calibrant Concentrations')
        axes.grid(alpha=0.3, zorder=1)

    fit = np.poly1d(cal_coefficients)

    axes.plot(cal_medians, [fit(x) for x in cal_medians], lw=1, marker='.', ms=4)

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

    #axes.plot(cal_medians, cal_concs, marker='o', mfc='none', lw=0, ms=11)
    fig.set_tight_layout(tight=True)

def calibration_error_plot(fig, axes, cal, cal_error, analyte_error, flags):
    analyte_error = float(analyte_error)
    if len(axes.lines) > 0:
        del axes.lines[1:]
    else:
        axes.set_title('Calibrant Error')
        axes.set_xlabel('Calibrant Concentration')
        axes.set_ylabel('Error from fitted concentration')
        axes.grid(alpha=0.3, zorder=1)

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
    axes.set_xlim((0-(max(cal)*0.05)), max(cal)*1.05)
    axes.set_ylim(min(cal_error)*0.9, max(cal_error)*1.1)

    fig.set_tight_layout(tight=True)

def basedrift_correction_plot(fig, axes1, axes2, type, indexes, correction, medians, flags):
    if len(axes1.lines) > 0:
        del axes1.lines[:]
        del axes2.lines[:]
    else:
        axes1.set_title('%s Peak Height' % type)
        axes1.set_xlabel('Peak Number')
        axes1.set_ylabel('Raw Peak Height (A/D)')
        axes1.grid(alpha=0.3, zorder=1)
        axes2.set_title('%s Correction Percentage' % type)
        axes2.set_xlabel('Peak Number')
        axes2.set_ylabel('Percentage of Top Cal (%)')
        axes2.grid(alpha=0.3, zorder=1)

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
    fig.set_tight_layout(tight=True)

def rmns_plot(fig, axes, indexes, concentrations, flags, rmns, nutrient):
    nut_column = {'phosphate': 1, 'silicate': 3, 'nitrate': 5, 'nitrite': 7, 'ammonia': 9}

    del axes.lines[:]

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

    axes.set_title(str(nutrient).capitalize() + ' RMNS ' + str(rmns), fontsize=12)
    axes.set_xlabel('Peak Number')
    axes.set_ylabel('Concentration (uM)')
    axes.grid(alpha=0.2, zorder=1)

    axes.plot(indexes, concentrations, lw=0.75, linestyle=':', marker='o')
    axes.set_ylim(min(concentrations) * 0.975, max(concentrations) * 1.025)
    axes.set_xlim(min(indexes)-1, max(indexes)+1)

    handles, labels = axes.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    axes.legend(by_label.values(), by_label.keys())

def mdl_plot(fig, axes, indexes, concentrations, flags, stdevs=False, run_nums=False):

    if len(axes.lines) > 0:
        del axes.lines[:]
    else:
        axes.set_title('MDL', fontsize=12)
        axes.set_xlabel('Peak Number')
        axes.set_ylabel('Concentration (uM)')
        axes.grid(alpha=0.2, zorder=2)

    if stdevs: # Used when the across run plot is required - to plot standard deviation per run
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

        axes.plot(indexes, concentrations, linestyle=':', lw=0.25, marker='o', mfc='None', mec='#12BA66', ms=12, label='Measured MDL')

        axes.set_xlim(min(indexes)-1, max(indexes)+1)
        all_lines = mean_mdl_plot + upper_mdl_plot + stdev_runs_plot
        labs = [l.get_label() for l in all_lines]
        axes.legend(all_lines, labs)
    else: # Normal in processing plot
        mdl = 3 * statistics.stdev(concentrations)
        axes.plot(indexes, concentrations, lw=1, linestyle=':', marker='o', label='3x SD: ' + str(round(mdl,3)), ms=12, mfc='none', mec='#12BA66')
        axes.set_ylim(min(concentrations)*0.95, max(concentrations)*1.05)
        axes.legend(fontsize=12)

    fig.set_tight_layout(tight=True)

def bqc_plot(fig, axes, indexes, concentrations, flags):
    if len(axes.lines) > 0:
        del axes.lines[:]
    else:
        axes.set_title('BQC')
        axes.set_xlabel('Peak Number')
        axes.set_ylabel('Concentration (uM)')
        axes.grid(alpha=0.3, zorder=2)

    mean_bqc = statistics.mean(concentrations)

    axes.plot(indexes, [mean_bqc]*4, lw=1, linestyle='--', label = 'Run Mean: ' + str(round(mean_bqc, 3)))

    axes.plot(indexes, concentrations, lw=1, linestyle=':', marker='o', mfc='none')
    axes.set_ylim(min(concentrations)*0.99, max(concentrations)*1.01)

    axes.legend()

    fig.set_tight_layout(tight=True)


def sensor_difference_plot(fig, axes, x_data, difference, max_rp, sensor='Primary', clear_plot=True):

    if (len(axes.lines) > 0) & clear_plot:
        del axes.lines[:]

    if sensor == 'Primary':
        col = '#4068ce'
    else:
        col = '#71ce40'

    axes.plot(x_data, difference, linewidth=0.75, linestyle=':', marker='o', markersize=13, mfc='none',
              color=col, picker=7)

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


def sensor_difference_pressure_plot(fig, axes, difference, pressures, deployments=None):
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
    else:
        axes.plot(difference, pressures, marker='o', lw=0, mfc='None', markersize=5, alpha=0.8)


def sensor_profile_plot(fig, axes, pressure, bottle, flags, flag_indexes, primary=None, secondary=None, deployments=None):
    if deployments:
        for dep in sorted(list(set(deployments))):
            plotting_indexes = []
            for i, x in enumerate(deployments):
                if dep == x:
                    plotting_indexes.append(i)
            bottle_oxy_dep_subset = [bottle[x] for x in plotting_indexes]
            pressure_dep_subset = [pressure[x] for x in plotting_indexes]

            axes.plot(bottle_oxy_dep_subset, pressure_dep_subset, marker='o', lw=1, mfc='None', markersize=0,
                      label=f'Deployment {dep}')

            if primary:
                primary_dep_subset = [primary[x] for x in plotting_indexes]
                axes.plot(primary_dep_subset, pressure_dep_subset, lw=0.75, linestyle='-.', color='#2b9997',
                          alpha=0.8, label=f'Primary Sens: Dep {dep}')

            if secondary:
                secondary_dep_subset = [secondary[x] for x in plotting_indexes]
                axes.plot(secondary_dep_subset, pressure_dep_subset, lw=0.75, linestyle='--', color='#2b9997',
                          alpha=0.8, label=f'Secondary Sens: Dep {dep}')

    else:
        axes.plot(bottle, pressure, marker='o', lw=1, mfc='None', markersize=0)

    for i, ind in enumerate(flag_indexes):
        axes.scatter(bottle[i], pressure[i], alpha=0.8, s=18, color=FLAG_COLORS[flags[ind]], zorder=10)

    axes.plot(bottle, pressure, linewidth=0, linestyle=':', marker='o', markersize=0, mfc='none', picker=5)
    axes.set_ylabel('Pressure (dbar)')
    axes.legend()


class salinityDifferencesPlot(hyproProcPlotWindow):
    def __init__(self, deployment, x_data, bottle, primary, secondary, depths, max_rp, ref_ind, full_data):
        super().__init__(600, 870, 'HyPro - CTD/Bottle Salinity Error', 'Salinity', ref_ind, full_data)

        self.deployment = deployment
        self.x_data = x_data
        self.bottle = bottle
        self.primary = primary
        self.secondary = secondary
        self.depths = depths
        self.max_rp = max_rp
        self.ref_ind = ref_ind
        self.full_data = full_data

        self.plot()

    def plot(self):

        """
        ** Primary sensor comparison plot **
        """
        plottable_flags = []

        primary_difference = [(self.primary[i] - bottle) for i, bottle in enumerate(self.bottle)]

        sensor_difference_plot(self.sensor_one_figure, self.sensor_one_plot, self.x_data, primary_difference,
                               self.max_rp, sensor='Primary')
        sensor_difference_pressure_plot(self.sensor_one_figure, self.sensor_one_depth_plot, primary_difference,
                                        self.depths, deployments=self.deployment)


        """
        ** Secondary sensor comparison plot **
        """
        secondary_difference = [(self.secondary[i] - bottle) for i, bottle in enumerate(self.bottle)]

        sensor_difference_plot(self.sensor_two_figure, self.sensor_two_plot, self.x_data, secondary_difference,
                               self.max_rp, sensor='Secondary')
        sensor_difference_pressure_plot(self.sensor_two_figure, self.sensor_two_depth_plot, secondary_difference,
                                        self.depths, deployments=self.deployment)

        """
        ** Both sensors comparison plot **
        """

        sensor_difference_plot(self.both_sensor_figure, self.both_sensor_plot, self.x_data, primary_difference,
                               self.max_rp, sensor='Primary')
        sensor_difference_plot(self.both_sensor_figure, self.both_sensor_plot, self.x_data, secondary_difference,
                               self.max_rp, sensor='Secondary', clear_plot=False)
        #self.both_sensor_plot.legend()

        """
        ** Profile plot **
        """

        sensor_profile_plot(self.profile_figure, self.profile_plot, self.depths, self.bottle,
                            self.full_data.quality_flag, self.ref_ind, primary=self.primary,
                            secondary=self.secondary, deployments=self.deployment)
        self.profile_plot.set_xlabel('Salinity (PSU)')

        self.redraw.connect(self.redraw_on_update)

    def redraw_on_update(self):
        del self.sensor_one_plot.lines[:]
        del self.sensor_two_plot.lines[:]
        del self.both_sensor_plot.lines[:]
        del self.profile_plot.lines[:]

        self.full_data.quality_flag = self.working_quality_flags

        self.plot()
        self.sensor_one_canvas.draw()
        self.sensor_two_canvas.draw()
        self.both_sensor_canvas.draw()
        self.profile_canvas.draw()


class oxygenDifferencesPlot(hyproProcPlotWindow):
    def __init__(self, deployment, x_data, bottle, primary, secondary, depths, max_rp, ref_ind, full_data):
        super().__init__(600, 870, 'HyPro - CTD/Bottle Oxygen Error', 'Oxygen', ref_ind, full_data)

        self.deployment = deployment
        self.x_data = x_data
        self.bottle = bottle
        self.primary = primary
        self.secondary = secondary
        self.depths = depths
        self.max_rp = max_rp
        self.ref_ind = ref_ind
        self.full_data = full_data

        self.plot()

    def plot(self):

        """
        ** Primary sensor comparison plot **
        """
        plottable_flags = []

        primary_difference = [(self.primary[i] - bottle) for i, bottle in enumerate(self.bottle)]

        sensor_difference_plot(self.sensor_one_figure, self.sensor_one_plot, self.x_data, primary_difference,
                               self.max_rp, sensor='Primary')
        sensor_difference_pressure_plot(self.sensor_one_figure, self.sensor_one_depth_plot, primary_difference,
                                        self.depths, deployments=self.deployment)


        """
        ** Secondary sensor comparison plot **
        """
        secondary_difference = [(self.secondary[i] - bottle) for i, bottle in enumerate(self.bottle)]

        sensor_difference_plot(self.sensor_two_figure, self.sensor_two_plot, self.x_data, secondary_difference,
                               self.max_rp, sensor='Secondary')
        sensor_difference_pressure_plot(self.sensor_two_figure, self.sensor_two_depth_plot, secondary_difference,
                                        self.depths, deployments=self.deployment)

        """
        ** Both sensors comparison plot **
        """

        sensor_difference_plot(self.both_sensor_figure, self.both_sensor_plot, self.x_data, primary_difference,
                               self.max_rp, sensor='Primary')
        sensor_difference_plot(self.both_sensor_figure, self.both_sensor_plot, self.x_data, secondary_difference,
                               self.max_rp, sensor='Secondary', clear_plot=False)
        self.both_sensor_plot.legend()

        """
        ** Profile plot **
        """

        sensor_profile_plot(self.profile_figure, self.profile_plot, self.depths, self.bottle,
                            self.full_data.quality_flag, self.ref_ind, primary=self.primary,
                            secondary=self.secondary, deployments=self.deployment)
        self.profile_plot.set_xlabel('Oxygen Concentration (uM)')

        self.redraw.connect(self.redraw_on_update)

    def redraw_on_update(self):
        del self.sensor_one_plot.lines[:]
        del self.sensor_two_plot.lines[:]
        del self.both_sensor_plot.lines[:]
        del self.profile_plot.lines[:]

        self.full_data.quality_flag = self.working_quality_flags

        self.plot()
        self.sensor_one_canvas.draw()
        self.sensor_two_canvas.draw()
        self.both_sensor_canvas.draw()
        self.profile_canvas.draw()
