import json
import sqlite3
import traceback
import statistics
from PyQt5.QtWidgets import (QLabel, QComboBox)
from dialogs.plotting.PlottingWindow import QMainPlotterTemplate
from dialogs.plotting.QCPlots import mdl_plot

class mdlPlotWindowTemplate(QMainPlotterTemplate):
    def __init__(self, database, params_path):
        super().__init__(database)
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

        self.show()

        self.canvas.mpl_connect('pick_event', self.on_pick)

    def populate_run_list(self):
        try:
            nut = self.nutrient.currentText()
            nutq = self.nut_converter[nut]

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT runNumber, sampleID FROM %sData' % nutq)
            data = list(c.fetchall())
            c.close()

            mdl = self.params['nutrient_processing']['qc_sample_names']['mdl']
            runnums = []
            for i, x in enumerate(data):
                if mdl in x[1]:
                    runnums.append(int(x[0]))
            self.run_list.clear()
            rn = sorted(list(set(runnums)))
            for x in rn:
                self.run_list.addItem(str(x))

        except Exception:
            print(traceback.print_exc())

    def draw_data(self):
        nut = self.nutrient.currentText()
        self.nutq = self.nut_converter[nut]
        selected = self.run_list.selectedItems()
        selected_runs = [item.text() for item in selected]

        mdl = self.params['nutrient_processing']['qc_sample_names']['mdl']

        queryq = '?'
        queryplaceruns = ', '.join(queryq for unused in selected_runs)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute(
            'SELECT peakNumber, runNumber, sampleID, concentration, flag FROM %sData WHERE runNumber IN (%s)' % (
                self.nutq, queryplaceruns), (selected_runs))
        data = list(c.fetchall())
        c.close()

        self.runs = []
        self.conctoplot = []
        self.peak_nums = []
        sampleid = []
        self.flagtoplot = []
        for x in data:
            if mdl in x[2]:
                self.peak_nums.append(x[0])
                self.runs.append(x[1])
                sampleid.append(x[2])
                self.conctoplot.append(x[3])
                self.flagtoplot.append(x[4])

        run_peaknum_temp = []
        self.runpeaknumtoplot = []
        runs = sorted(set(self.runs))

        stdevs = []
        for x in runs:
            conc_temp = []
            for i, y in enumerate(self.runs):
                if x == y:
                    conc_temp.append(self.conctoplot[i])
            stdevs.append(statistics.stdev(conc_temp))

            run_peaknum_temp.append(self.runs.count(x))

        for i, x in enumerate(run_peaknum_temp):
            for y in range(x):
                if y > 0:
                    self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                else:
                    self.runpeaknumtoplot.append(runs[i])
        mdl_plot(self.figure, self.main_plot, self.runpeaknumtoplot, self.conctoplot, self.flagtoplot,
                 stdevs=stdevs, run_nums=runs)
        self.canvas.draw()

    def on_pick(self, event):
        self.base_on_pick(event, self.runs, self.peak_nums, nutrient=self.nutq)

