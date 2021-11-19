import sqlite3
import statistics
import pandas as pd
from collections import defaultdict

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QComboBox
from matplotlib.ticker import MaxNLocator

from processing.plotting.PlottingWindow import QMainPlotterTemplate
from processing.procdata.ProcessSealNutrients import find_duplicate_indexes, find_duplicate_samples

class duplicatesPlot(QMainPlotterTemplate):
    def __init__(self, database, processing_parameters):
        super().__init__(database)
        self. database = database
        self.processing_parameters = processing_parameters

        self.retrieved_data = []
        self.runs_max_peak = {}
        self.cutoff = 0

        self.runs =[]
        self.peak_nums = []

        self.nut_converter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                              'Ammonia': 'ammonia'}

        self.apply_button.clicked.connect(self.draw_data)

        self.setWindowTitle('Duplicates Plot')

        self.main_plot.set_title('Duplicates Difference', fontsize=18)
        self.main_plot.set_xlabel('Run/Peak No.', fontsize=15)
        self.main_plot.set_ylabel('|Sample - Duplicate Mean|', fontsize=15)

        self.main_plot.grid(alpha=0.1)

        nutrient_label = QLabel('Nutrient', self)
        self.nutrient = QComboBox(self)
        self.nutrient.addItems(['NOx', 'Phosphate', 'Silicate', 'Nitrite', 'Ammonia'])

        self.nutrient.currentTextChanged.connect(self.find_duplicates)

        self.qvbox_layout.insertWidget(0, nutrient_label)
        self.qvbox_layout.insertWidget(1, self.nutrient)

        self.show()

        self.canvas.mpl_connect('pick_event', self.on_pick)

        self.find_duplicates()

    def find_duplicates(self):
        nutrient = self.nutrient.currentText()
        nutq = self.nut_converter[nutrient]

        self.cutoff = self.processing_parameters['nutrient_processing']['processing_pars'][nutq]['duplicate_error']

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute(f"""SELECT * from {nutq}Data i join 
                    (SELECT runNumber, sampleID, cupType, count(*) as cnt FROM {nutq}Data GROUP BY runNumber, sampleID) k 
                    on k.runNumber = i.runNumber and k.sampleID = i.sampleID where k.cnt > 1 and k.cupType='SAMP' ORDER BY i.runNumber""")

        runs_with_duplicates = list(c.fetchall())
        self.retrieved_data = runs_with_duplicates


        c.execute(f"""SELECT runNumber, MAX(peakNumber) FROM {nutq}Data GROUP BY runNumber""")
        runs_max_peak = list(c.fetchall())
        conn.close()

        # Turn it into a dict (key is run number, val is max peak number)
        for x in runs_max_peak:
            self.runs_max_peak[x[0]] = x[1]

        runs = set([x[0] for x in runs_with_duplicates])
        self.run_list.clear()
        for x in runs:
            self.run_list.addItem(str(x))

        self.main_plot.set_title(f'{nutrient} Duplicates Difference', fontsize=18)
        self.canvas.draw()

    def draw_data(self):

        del self.main_plot.lines[:]

        selected = self.run_list.selectedItems()
        selected_runs = [int(item.text()) for item in selected]

        if selected_runs:
            qc_list = ['StandardQC', 'MDL', 'BQC', 'IntQC', 'RMNS', 'Test']
            selected_retrieved_data = [x for x in self.retrieved_data if (x[0] in selected_runs and x[8] not in qc_list)]

            # Get the matching duplicates and determine the difference between them
            set_sample_ids = set([x[2] for x in selected_retrieved_data])

            # Get the difference to the sample mean for the sample
            y_plot = []
            x_plot = []
            for sample_id in  set_sample_ids:
                replicates = [x for x in selected_retrieved_data if x[2] == sample_id]

                mean_concentration = statistics.mean([x[6] for x in replicates])
                differences = [abs(x[6]-mean_concentration) for x in replicates]
                peak_run_x_axes = [x[0]+ (self.runs_max_peak[x[0]] / x[3]) for x in replicates]

                runs = [x[0] for x in replicates]
                peak_nums = [x[3] for x in replicates]

                # Put the differences into a 1D list for plotting
                for i, samp_diff in enumerate(differences):
                    y_plot.append(samp_diff)
                    x_plot.append(peak_run_x_axes[i])

                    self.runs.append(runs[i])
                    self.peak_nums.append(peak_nums[i])


            self.main_plot.plot(x_plot, y_plot, lw=0, marker='o', ms=11, picker=5, mec="#3C3F41", mfc='None')
            self.main_plot.plot(x_plot, y_plot, lw=0, marker='.', ms=4, mec="#3C3F41", mfc='None')

            self.main_plot.xaxis.set_major_locator(MaxNLocator(integer=True))

            # Plot the duplicates cutoff line for the selected nutrient
            self.main_plot.plot([int(min(x_plot)), int(max(x_plot))+1], [self.cutoff, self.cutoff],
                                lw=1.5, color="#B03E45", label="Cutoff")

            self.main_plot.legend()

            self.canvas.draw()

    def on_pick(self, event):
        nutrient = self.nutrient.currentText()
        nutq = self.nut_converter[nutrient]
        self.base_on_pick(event, self.runs, self.peak_nums, nutq)
