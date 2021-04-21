import json
import sqlite3
import traceback
import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLabel, QComboBox)
from processing.plotting.PlottingWindow import QMainPlotterTemplate
from processing.plotting.QCPlots import rmns_plot


class rmnsPlotWindowTemplate(QMainPlotterTemplate):
    def __init__(self, database, params_path):
        super().__init__(database)

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

        self.canvas.mpl_connect('pick_event', self.on_pick)

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
            self.nut = self.nutrient.currentText()
            self.nutq = self.nut_converter[self.nut]
            self.rmns = self.rmns_type.currentText()
            selected = self.run_list.selectedItems()
            selected_runs = [item.text() for item in selected]

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
                if self.rmns in x[2]:
                    self.peak_nums.append(x[0])
                    self.runs.append(x[1])
                    sampleid.append(x[2])
                    self.conctoplot.append(x[3])
                    self.flagtoplot.append(x[4])

            runpeaknumhold = []
            self.runpeaknumtoplot = []
            self.run_number = []
            runs = sorted(set(self.runs))
            for x in runs:
                runpeaknumhold.append(self.runs.count(x))
            for i, x in enumerate(runpeaknumhold):
                for y in range(x):
                    if y > 0:
                        self.runpeaknumtoplot.append(runs[i] + (y / ((x - 1) * 1.6)))
                    else:
                        self.runpeaknumtoplot.append(runs[i])

            rmns_plot(self.figure, self.main_plot, self.runpeaknumtoplot, self.conctoplot, self.flagtoplot,
                      self.rmns, self.nutq)
            self.main_plot.set_xlabel('Analysis Number:')

            self.canvas.draw()

        except Exception:
            print(traceback.print_exc())

    def on_pick(self, event):
        self.base_on_pick(event, self.runs, self.peak_nums, nutrient=self.nutq)