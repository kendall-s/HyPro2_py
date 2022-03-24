import sqlite3
import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLabel, QComboBox)
from processing.plotting.PlottingWindow import QMainPlotterTemplate

class redfieldPlot(QMainPlotterTemplate):
    def __init__(self, database):
        super().__init__(database)
        self. database = database

        self.peak_numbers = []
        self.run_numbers = []

        self.apply_button.clicked.connect(self.draw_data)

        self.setWindowTitle('Redfield Ratio Plot')

        self.main_plot.set_title('Redfield Ratio', fontsize=18)
        self.main_plot.set_xlabel('[NOx] (uM)', fontsize=15)
        self.main_plot.set_ylabel('[Phosphate] (uM)', fontsize=15)

        self.main_plot.grid(alpha=0.1)
        survey_label = QLabel('Survey to use:', self)

        self.survey_selector = QComboBox()
        self.survey_selector.setFont(QFont('Segoe UI'))

        self.qvbox_layout.insertWidget(0, survey_label)
        self.qvbox_layout.insertWidget(1, self.survey_selector)

        self.populate_fields()
        self.show()

        self.canvas.mpl_connect('pick_event', self.on_pick)

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

        del self.main_plot.collections[:]
        del self.main_plot.texts[:]

        selected = self.run_list.selectedItems()
        selected_runs = [int(item.text()) for item in selected]

        if selected_runs:
            conn = sqlite3.connect(self.database)
            query_placeholder = ', '.join('?' for unused in selected_runs)
            nox_df = pd.read_sql_query(f"SELECT * FROM nitrateData WHERE runNumber IN ({query_placeholder})", conn,
                                       params=selected_runs)
            phos_df = pd.read_sql_query(f"SELECT * FROM phosphateData WHERE runNumber IN ({query_placeholder})", conn,
                                       params=selected_runs)

            nox_df = nox_df.loc[nox_df['cupType'] == 'SAMP']

            conn.close()
            nox_plottable = []
            phos_plottable = []
            self.runs = []
            self.peak_nums = []
            for nox_row in nox_df.itertuples():
                phos_point = phos_df.loc[(phos_df['runNumber'] == nox_row[1]) & (phos_df['peakNumber'] == nox_row[4])]
                self.runs.append(nox_row[1])
                self.peak_nums.append(nox_row[4])
                nox_plottable.append(nox_row[7])
                phos_plottable.append(float(phos_point['concentration']))

            self.main_plot.scatter(nox_plottable, phos_plottable, marker='o', facecolors='#FFB186', edgecolors='#EF8A68',
                                   alpha=0.75, picker=5)

            self.main_plot.annotate(f'Ratio: {round(sum(nox_plottable) / sum(phos_plottable), 2)}', [0.02, 0.96],
                          xycoords='axes fraction', fontsize=11)

            self.canvas.draw()

    def on_pick(self, event):
        self.base_on_pick(event, self.runs, self.peak_nums, 'nitrate')