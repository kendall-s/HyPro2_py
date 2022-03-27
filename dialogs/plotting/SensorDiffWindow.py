import sqlite3
import numpy as np
import pandas as pd
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLabel, QComboBox)
from processing.util.NutrientProcessUtilities import get_max_rp
from dialogs.plotting.PlottingWindow import QMainPlotterTemplate
from dialogs.plotting.QCPlots import sensor_difference_plot

class ctdSensorDifferencePlot(QMainPlotterTemplate):
    def __init__(self, database, type):
        super().__init__(database)

        self.database = database
        self.type = type

        self.apply_button.clicked.connect(self.draw_data)

        self.setWindowTitle(f'CTD {type} Sensor to Bottle Difference')

        self.main_plot.set_title('CTD Sensor - Bottle', fontsize=18)
        self.main_plot.set_xlabel('Deployment / Rosette Position', fontsize=15)
        self.main_plot.set_ylabel('Difference (CTD Sensor - Bottle)', fontsize=15)

        self.main_plot.grid(alpha=0.1)

        self.run_list_label.setText('Select Deployment:')

        sensor_label = QLabel('Sensor:', self)
        self.sensor_selector = QComboBox()
        self.sensor_selector.setFont(QFont('Segoe UI'))
        self.sensor_selector.addItems(['Salinity', 'Oxygen'])
        self.sensor_selector.setEditable(True)
        self.sensor_selector.setEditable(False)
        #self.sensor_selector.currentTextChanged.connect(self.populate_fields)

        sensor_number_label = QLabel('# Sensor:')
        self.sensor_number_selector = QComboBox()
        self.sensor_number_selector.setFont(QFont('Segoe UI'))
        self.sensor_number_selector.addItems(['Primary', 'Secondary', 'Both'])
        self.sensor_number_selector.setEditable(True)
        self.sensor_number_selector.setEditable(False)

        self.sensor_selector.setCurrentText(type)

        self.qvbox_layout.insertWidget(0, sensor_label)
        self.qvbox_layout.insertWidget(1, self.sensor_selector)

        self.qvbox_layout.insertWidget(2, sensor_number_label)
        self.qvbox_layout.insertWidget(3, self.sensor_number_selector)

        self.populate_fields()
        self.show()

        self.need_update.connect(self.draw_data)

        self.canvas.mpl_connect('pick_event', self.on_pick)

    def populate_fields(self):

        sensor = self.sensor_selector.currentText()
        print(sensor)
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        c.execute('SELECT DISTINCT deployment from %sData' % sensor.lower())

        # Drop any rows that aren't an integer value, those won't be deployments anyway
        data = list(c.fetchall())
        available_deployments = sorted([x[0] for x in data if str(x[0]).isdigit()])

        conn.close()

        for dep in available_deployments:
            # Have to cast as string to add as item
            self.run_list.addItem(str(dep))

    def draw_data(self):

        sensor = self.sensor_selector.currentText()
        sensor_number = self.sensor_number_selector.currentText()

        analyte_db_converter = {'Salinity': 'salinity', 'Oxygen': 'oxygenMoles'}
        ctd_db_converter = {'Salinity': 'salt', 'Oxygen': 'oxygen'}
        sensor_converter = {'Primary': 1, 'Secondary': 2}

        mark_bad_data = self.mark_bad_data.isChecked()

        selected = self.run_list.selectedItems()
        selected_deps = [int(item.text()) for item in selected]

        if selected_deps:
            # Get data from database for both bottles and CTD
            conn = sqlite3.connect(self.database)
            query_placeholder = ', '.join('?' for unused in selected_deps)
            bottle_data_df = pd.read_sql_query(f'SELECT * FROM %sData WHERE deployment IN ({query_placeholder})'
                                       %sensor.lower(), conn, params=selected_deps)

            ctd_data_df = pd.read_sql_query(f'SELECT deployment, rosettePosition, salt1, salt2, oxygen1, oxygen2 '
                                            f'FROM ctdData '
                                            f'WHERE deployment IN ({query_placeholder})', conn, params=selected_deps)

            self.bottle_deps = list(bottle_data_df['deployment'])
            self.bottle_rps = list(bottle_data_df['rosettePosition'])
            self.bottle_flags = list(bottle_data_df['flag'])

            # Match up the CTD data to the bottle data, as there will always be less bottle data...
            matched_ctd_data = pd.DataFrame()
            for i, dep in enumerate(self.bottle_deps):
                rp = self.bottle_rps[i]
                matched = ctd_data_df.loc[(ctd_data_df['deployment'] == dep) & (ctd_data_df['rosettePosition'] == rp)]
                matched_ctd_data = matched_ctd_data.append(matched, ignore_index=True)

            bottle_data = np.asarray(bottle_data_df[analyte_db_converter[sensor]])

            bottle_flags = bottle_data_df['flag']

            difference_two = []
            # If both sensors are to be plotted, use the correct data
            if sensor_number != 'Both':
                sensor_one = np.asarray(list(matched_ctd_data[str(ctd_db_converter[sensor]) +
                                                              str(sensor_converter[sensor_number])]))
            else:
                sensor_one = np.asarray(list(matched_ctd_data[str(ctd_db_converter[sensor]) + '1']))
                sensor_two = np.asarray(list(matched_ctd_data[str(ctd_db_converter[sensor]) + '2']))
                difference_two = sensor_two - bottle_data

            # Plotted the same as in oxygen processing
            difference_one = sensor_one - bottle_data

            max_rp = get_max_rp(self.bottle_rps)

            # Create the X axis values which spaces deployment/rp equally along
            plottable_dep_rp = [(((dep - 1) * max_rp) + self.bottle_rps[i]) for i, dep in enumerate(self.bottle_deps)]

            sensor_difference_plot(self.figure, self.main_plot, plottable_dep_rp, difference_one, max_rp,
                                   flags=bottle_flags, show_flags=mark_bad_data)

            if sensor_number == 'Both':
                sensor_difference_plot(self.figure, self.main_plot, plottable_dep_rp, difference_two, max_rp,
                                       flags=bottle_flags, sensor='Secondary', clear_plot=False,
                                       show_flags=mark_bad_data)
                self.main_plot.legend()

            self.canvas.draw()

    def on_pick(self, event):
        if self.sensor_selector.currentText() == 'Salinity':
            self.base_on_pick(event, self.bottle_deps, self.bottle_rps, salinity=True)
        elif self.sensor_selector.currentText() == 'Oxygen':
            self.base_on_pick(event, self.bottle_deps, self.bottle_rps, oxygen=True)
