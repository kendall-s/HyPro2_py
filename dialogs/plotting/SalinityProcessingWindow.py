from dialogs.plotting.InteractiveProcPlottingWindow import hyproProcPlotWindow
from dialogs.plotting.QCPlots import sensor_difference_plot, sensor_difference_pressure_plot, sensor_profile_plot

"""
This is the interactive processing window for salinity, providing the user with the ability to compare bottle data 
to the sensor and flag measurements as necessary
"""


class salinityDifferencesPlot(hyproProcPlotWindow):
    def __init__(self, deployment, x_data, bottle, primary, secondary, depths, max_rp, ref_ind, full_data):
        super().__init__(600, 870, 'HyPro - CTD/Bottle Salinity Error', 'Salinity', ref_ind, depths, full_data)

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
        # self.both_sensor_plot.legend()

        """
        ** Profile plot **
        """

        sensor_profile_plot(self.profile_figure, self.profile_plot, self.depths, self.bottle,
                            self.full_data.quality_flag, flag_ref_inds=self.ref_ind, primary=self.primary,
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
