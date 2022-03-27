from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QThread
from processing.data.Structures import WorkingData, SLKData, CHDData
import processing.procdata.ProcessSealNutrients as psn
import processing.readdata.ReadSealNutrients as rsn


class processNutrientsController(QObject):

    startup_routine_completed = pyqtSignal(tuple)
    reprocessing_completed = pyqtSignal(tuple)
    thinking = pyqtSignal()

    def __init__(self, file, file_path, database, processing_parameters):
        super().__init__()

        self.file = file
        self.file_path = file_path
        self.database = database
        self.w_d = WorkingData(file)
        self.processing_parameters = processing_parameters

        self.slk_data = SLKData(file)
        self.chd_data = CHDData(file)
        self.current_nutrient = ""

    def startup_routine(self):
        self.thinking.emit()

        returned_data = rsn.get_data_routine(self.file_path, self.w_d, self.processing_parameters, self.database)

        if returned_data:
            self.slk_data, self.chd_data, self.w_d, self.current_nutrient = returned_data
        else:
            self.startup_routine_completed.emit(())
            return

        self.slk_data.run_number = int \
            (self.file[len(self.processing_parameters['analysis_params']['seal']['file_prefix']):-4])

        self.w_d = psn.processing_routine(self.slk_data, self.chd_data, self.w_d, self.processing_parameters, self.current_nutrient)

        return_package = (self.current_nutrient, self.slk_data, self.chd_data, self.w_d)
        self.startup_routine_completed.emit(return_package)

    def re_process(self):
        self.thinking.emit()
        self.w_d = psn.processing_routine(self.slk_data, self.chd_data, self.w_d,
                                          self.processing_parameters, self.current_nutrient)

        return_package = (self.current_nutrient, self.slk_data, self.chd_data, self.w_d)
        self.reprocessing_completed.emit(return_package)


    """
    These relate to setting data that is changed in the interactive processing window
    """
    def set_current_nutrient(self, curr_nut):
        self.current_nutrient = curr_nut

    def set_peak_starts(self, new_peak_starts):
        self.slk_data.peak_starts[self.current_nutrient] = new_peak_starts

    def set_clean_peak_starts(self, new_peak_starts):
        self.slk_data.clean_peak_starts[self.current_nutrient] = new_peak_starts

    def set_quality_flags(self, new_flags):
        self.w_d.quality_flag = new_flags


    """
    General data getting functions from SLK, CHD and W_D (working data)
    """

    def get_peak_starts(self):
        return self.slk_data.peak_starts[self.current_nutrient]

    def get_adjusted_peak_starts(self):
        return self.w_d.adjusted_peak_starts[self.current_nutrient]

    """
    CHD file surgeons
    """
    def add_to_chd(self, x_time):
        for i in range(3):
            self.chd_data.ad_data[self.current_nutrient].insert(int(x_time), 100)

    def cut_from_chd(self, x_time):
        for i in range(3):
            self.chd_data.ad_data[self.current_nutrient].pop(int(x_time))


    """
    These functions are for setting the values of 1 sample
    """
    def set_one_cup_type(self, index, new_cup_type):
        self.slk_data.cup_types[index] = new_cup_type

    def set_one_dilution_factor(self, index, new_dilution):
        self.w_d.dilution_factor[index] = new_dilution

    def set_one_quality_flag(self, index, new_flag):
        self.w_d.quality_flag[index] = new_flag



    """
    These getters and setters relate to the processing parameters
    """
    def set_window_start(self, new_window_start):
        self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_start'] \
            = new_window_start

    def get_window_start(self):
        return self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_start']

    def set_window_size(self, new_window_size):
        self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_size'] \
            = new_window_size

    def get_window_size(self):
        return self.processing_parameters['nutrient_processing']['processing_pars'][self.current_nutrient]['window_size']


    """
    Functionality for replaying through processing steps
    """

    def replay_processing_step(self, action_step):

        """
        Given an input action, run the appropriate function for processing the data
        """

        if action_step['action'] == 'window_length_set':
            self.set_window_size(action_step['value'])

        if action_step['action'] == 'window_start_set':
            self.set_window_start(action_step['value'])

        if action_step['action'] == 'adjust_peak_starts':
            adjusted_peak_starts = [p_s - action_step['value'] for p_s in
                                    self.slk_data.clean_peak_starts[self.current_nutrient]]
            self.set_clean_peak_starts(adjusted_peak_starts)

        if action_step['action'] == 'add_to_chd':
            self.add_to_chd(action_step['value'])

        if action_step['action'] == 'cut_from_chd':
            self.cut_from_chd(action_step['value'])

        if action_step['action'] == 'update_cup_type':
            self.set_one_cup_type(action_step['peak'], action_step['value'])

        if action_step['action'] == 'update_dilution':
            self.set_one_dilution_factor(action_step['peak'], action_step['value'])

        if action_step['action'] == 'update_flag':
            self.set_one_quality_flag(action_step['peak'], action_step['value'])

    def undo_processing_step(self, action_step):
        """
        Undo a given input action
        """
        if action_step['action'] == 'window_length_set':
            self.set_window_size(action_step['old_value'])

        if action_step['action'] == 'window_start_set':
            self.set_window_start(action_step['old_value'])

        if action_step['action'] == 'adjust_peak_starts':
            adjusted_peak_starts = [p_s + action_step['old_value'] for p_s in
                                    self.slk_data.clean_peak_starts[self.current_nutrient]]
            self.set_clean_peak_starts(adjusted_peak_starts)

        if action_step['action'] == 'add_to_chd':
            self.cut_from_chd(action_step['value'])

        if action_step['action'] == 'cut_from_chd':
            self.add_to_chd(action_step['value'])

        if action_step['action'] == 'update_cup_type':
            self.set_one_cup_type(action_step['peak'], action_step['old_value'])

        if action_step['action'] == 'update_dilution':
            self.set_one_dilution_factor(action_step['peak'], action_step['old_value'])

        if action_step['action'] == 'update_flag':
            self.set_one_quality_flag(action_step['peak'], action_step['old_value'])
