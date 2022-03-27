import json
import sqlite3
import traceback
import pandas as pd
from PyQt5.QtWidgets import (QLabel, QComboBox, QCheckBox)
from dialogs.plotting.PlottingWindow import QMainPlotterTemplate
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

COMBO_BOX_CONVERTER = {'Pressure': {'db': 'ctd', 'col': 'pressure', 'plot_name': 'Pressure (db)'},
                       'CTD Salinity #1': {'db': 'ctd', 'col': 'salt1', 'plot_name': 'Primary CTD Salinity (psu)'},
                       'CTD Salinity #2': {'db': 'ctd', 'col': 'salt2', 'plot_name': 'Secondary CTD Salinity (psu)'},
                       'CTD Oxygen #1': {'db': 'ctd', 'col': 'oxygen1', 'plot_name': 'Primary CTD Oxygen (uM)'},
                       'CTD Oxygen #2': {'db': 'ctd', 'col': 'oxygen2', 'plot_name': 'Secondary CTD Oxygen (uM)'},
                       'CTD Fluorometer': {'db': 'ctd', 'col': 'fluoro', 'plot_name': 'CTD Fluorometer (ug/L)'},
                       'CTD Temperature #1': {'db': 'ctd', 'col': 'temp1', 'plot_name': 'Primary CTD Temperature (C)'},
                       'CTD Temperature #2': {'db': 'ctd', 'col': 'temp2', 'plot_name': 'Secondary CTD Temperature (C)'},
                       'Rosette Position': {'db': 'ctd', 'col': 'rosettePosition', 'plot_name': 'Rosette Position'},
                       'NOx': {'db': 'nitrate', 'col': 'concentration', 'plot_name': 'NOx (uM)'},
                       'Phosphate': {'db': 'phosphate', 'col': 'concentration', 'plot_name': 'Phosphate (uM)'},
                       'Silicate': {'db': 'silicate', 'col': 'concentration', 'plot_name': 'Silicate (uM)'},
                       'Ammonia': {'db': 'ammonia', 'col': 'concentration', 'plot_name': 'Ammonia (uM)'},
                       'Nitrite': {'db': 'nitrite', 'col': 'concentration', 'plot_name': 'Nitrite (uM'},
                       'Bottle Salinity': {'db': 'salinity', 'col': 'salinity', 'plot_name': 'Salinity (psu)'},
                       'Bottle Oxygen': {'db': 'oxygen', 'col': 'oxygenMoles', 'plot_name': 'Oxygen (uM)'}
                       }

COLOR_CONVERTER = {'Auto': None, 'Blue': '#5975a4', 'Green': '#5f9e6e', 'Orange': '#cc8963',  'Red': '#b55d60'}

COMBO_ITEMS =['Pressure', 'CTD Salinity #1', 'CTD Salinity #2', 'CTD Oxygen #1', 'CTD Oxygen #2',
                'CTD Fluorometer', 'Rosette Position', 'NOx', 'Phosphate', 'Silicate',
                'Ammonia', 'Nitrite', 'Bottle Salinity', 'Bottle Oxygen']

class paramPlotWindowTemplate(QMainPlotterTemplate):
    def __init__(self, database, params_path):
        super().__init__(database)

        self. database = database
        with open(params_path, 'r') as file:
            self.params = json.loads(file.read())

        self.nut_converter = {'NOx': 'nitrate', 'Phosphate': 'phosphate', 'Silicate': 'silicate', 'Nitrite': 'nitrite',
                             'Ammonia': 'ammonia'}

        self.rmnscols = {'NOx': 5, 'Phosphate': 1, 'Silicate': 3, 'Nitrite': 7, 'Ammonia': 9}

        self.already_inverted = False

        self.setWindowTitle('HyPro - Parameter/Parameter Plot')

        self.main_plot.set_title('HyPro Plot', fontsize=18)
        self.main_plot.set_xlabel('X Axis', fontsize=15)
        self.main_plot.set_ylabel('Y Axis', fontsize=15)

        self.main_plot.grid(alpha=0.1)

        self.secondary_plot = self.main_plot.twiny()

        # For the parameter plot I will put in the navigation toolbar because people might want to zoom in etc
        self.toolbar = NavigationToolbar(self.canvas, self)

        y_axis_combo_label = QLabel('Y Axis', self)
        self.y_axis_combo = QComboBox(self)
        self.y_axis_combo.addItems(COMBO_ITEMS)
        self.y_axis_combo.currentIndexChanged.connect(self.populate_deployment_list)

        self.invert_y_axis_check = QCheckBox('Invert Y Axis')
        self.invert_y_axis_check.setChecked(True)

        x_axis_1_combo_label = QLabel('X Axis #1 (⚪)', self)
        self.x_axis_1_combo = QComboBox(self)
        self.x_axis_1_combo.addItems(COMBO_ITEMS)

        self.x_axis_1_color = QComboBox(self)
        self.x_axis_1_color.addItems(COLOR_CONVERTER.keys())

        x_axis_2_combo_label = QLabel('X Axis #2 (⬜)', self)
        self.x_axis_2_combo = QComboBox(self)
        self.x_axis_2_combo.addItem('N/A')
        self.x_axis_2_combo.addItems(COMBO_ITEMS)

        self.x_axis_2_color = QComboBox(self)
        self.x_axis_2_color.addItems(COLOR_CONVERTER.keys())

        self.qvbox_layout.insertWidget(0, y_axis_combo_label)
        self.qvbox_layout.insertWidget(1, self.y_axis_combo)

        self.qvbox_layout.insertWidget(2, self.invert_y_axis_check)

        self.qvbox_layout.insertWidget(3, x_axis_1_combo_label)
        self.qvbox_layout.insertWidget(4, self.x_axis_1_combo)
        self.qvbox_layout.insertWidget(5, self.x_axis_1_color)

        self.qvbox_layout.insertWidget(6, x_axis_2_combo_label)
        self.qvbox_layout.insertWidget(7, self.x_axis_2_combo)
        self.qvbox_layout.insertWidget(8, self.x_axis_2_color)

        self.grid_layout.addWidget(self.toolbar, 1, 1)

        self.apply_button.clicked.connect(self.draw_data)

        self.run_list_label.setText('Select Deployment:')

        self.populate_deployment_list()

        self.show()

        self.canvas.mpl_connect('pick_event', self.on_pick)


    def populate_deployment_list(self):
        try:
            self.run_list.clear()

            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute('SELECT DISTINCT deployment from ctdData')
            data = list(c.fetchall())
            c.close()

            for x in data:
                self.run_list.addItem(str(x[0]))

        except Exception:
            print(traceback.print_exc())

    def draw_data(self):
        """
        Look kind of long and needs refactoring but gist here is that we grab the input the comboboxes
        parse those, create a SQL query based on the selections the draw those to the plot axes
        """

        try:
            # Delete any lines that already exist
            del self.main_plot.lines[:]
            del self.secondary_plot.lines[:]

            # Get the inputs
            y_axis_selection = self.y_axis_combo.currentText()
            x_axis_selection = self.x_axis_1_combo.currentText()
            x_axis_two_selection = self.x_axis_2_combo.currentText()
            selected = self.run_list.selectedItems()
            selected_runs = [item.text() for item in selected]

            query_placeholder = ', '.join('?' for unused in selected_runs)
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Conver the inputs to to the fields needed for the DB queries
            y_axis_db = COMBO_BOX_CONVERTER[y_axis_selection]['db']
            y_axis_col = COMBO_BOX_CONVERTER[y_axis_selection]['col']
            y_axis_name = COMBO_BOX_CONVERTER[y_axis_selection]['plot_name']

            x_axis_db = COMBO_BOX_CONVERTER[x_axis_selection]['db']
            x_axis_col = COMBO_BOX_CONVERTER[x_axis_selection]['col']
            x_axis_name = COMBO_BOX_CONVERTER[x_axis_selection]['plot_name']

            x_two_param = ''
            x_two_join = ''

            # If a selection is made for the secondary X axis, then we create part of a SQL query which
            # will be added to the full query later on
            if x_axis_two_selection != 'N/A':
                x_axis_db_2 = COMBO_BOX_CONVERTER[x_axis_two_selection]['db']
                x_axis_col_2 = COMBO_BOX_CONVERTER[x_axis_two_selection]['col']
                x_axis_name_2 = COMBO_BOX_CONVERTER[x_axis_two_selection]['plot_name']

                x_two_param = f', x_two_param.{x_axis_col_2}'

                x_two_join = f"""
                left join
                (select * from {x_axis_db_2}Data)
                as x_two_param
                on
                x_two_param.deployment = {y_axis_db}Data.deployment
                and
                x_two_param.rosettePosition = {y_axis_db}Data.rosettePosition
                """

                self.secondary_plot.set_xlabel(x_axis_name_2, fontsize=15)

            self.main_plot.set_title('HyPro Param/Param Plot', fontsize=18)
            self.main_plot.set_xlabel(x_axis_name, fontsize=15)
            self.main_plot.set_ylabel(y_axis_name, fontsize=15)

            q = f"""
            select
            {y_axis_db}Data.deployment,
            {y_axis_db}Data.{y_axis_col},
            x_param.{x_axis_col}
            {x_two_param}

            from {y_axis_db}Data

            left join 
            (select * from {x_axis_db}Data) 
            as x_param

            on 
            x_param.deployment = {y_axis_db}Data.deployment 
            and 
            x_param.rosettePosition = {y_axis_db}Data.rosettePosition

            {x_two_join}

            where {y_axis_db}Data.deployment in ({query_placeholder})
            """
            c.execute(q, selected_runs)

            data = list(c.fetchall())
            c.close()

            # Pull out our data and structure it for plotting
            deployment = [x[0] for x in data if x[2] != None]
            y = [x[1] for x in data if x[2] != None]
            x = [x[2] for x in data if x[2] != None]
            df = pd.DataFrame({'deployment': deployment, 'y': y, 'x': x})

            # Sort our data by deployment
            for dep in sorted(set(deployment)):
                subset = df.loc[df['deployment'] == dep]
                # Plot each deployment separately, label accordingly
                self.main_plot.plot(subset['x'], subset['y'],
                                    marker='o', mfc='None', ms=10, ls=':', label=f'X1 Dep #{dep}',
                                    color=COLOR_CONVERTER[self.x_axis_1_color.currentText()]
                                    )

            # Do the same for the secondary axis, if there is a selection for it
            if x_axis_two_selection != 'N/A':
                self.secondary_plot.plot([], [])
                deployment = [x[0] for x in data if x[3] != None]
                y = [x[1] for x in data if x[3] != None]
                x = [x[3] for x in data if x[3] != None]
                df = pd.DataFrame({'deployment': deployment, 'y': y, 'x': x})

                for dep in sorted(set(deployment)):
                    subset = df.loc[df['deployment'] == dep]
                    self.secondary_plot.plot(subset['x'], subset['y'],
                                             lw=0.5, marker='s', mfc='None', ms=10, ls='-.', label=f'X2 Dep #{dep}',
                                             color=COLOR_CONVERTER[self.x_axis_2_color.currentText()]
                                             )

            # Decide whether a legend is necessary
            if len(set(deployment)) > 1 or x_axis_two_selection !='N/A':
                self.main_plot.legend()

            # Invert the y axis based on the check box
            if self.invert_y_axis_check.isChecked() and self.already_inverted == False:
                self.main_plot.invert_yaxis()
                self.already_inverted = True

            if not self.invert_y_axis_check.isChecked():
                if self.already_inverted == True:
                    self.main_plot.invert_yaxis()
                    self.already_inverted = False

            self.main_plot.relim()
            self.canvas.draw()
            self.main_plot.set_prop_cycle(None)

        except Exception:
            print(traceback.print_exc())

    def on_pick(self, event):
        self.base_on_pick(event, self.runs, self.peak_nums, nutrient=self.nutq)