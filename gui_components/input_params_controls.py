import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from gui_components.controls_bar import ControlsBar
from gui_components.data_export_controls import DataExportActions
from gui_components.settings import *
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path))


class InputParamsControls(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.create_bin_width_control(layout)
        running_mode_control = self.create_running_mode_control()
        layout.addLayout(running_mode_control)
        layout.addSpacing(15)
        self.create_time_span_control(layout)
        self.create_acquisition_time_control(layout)
        show_cps_control = self.create_show_cps_control()
        layout.addSpacing(15)
        layout.addLayout(show_cps_control)
        layout.addSpacing(20)
        self.create_cps_threshold_control(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)


    def create_bin_width_control(self, layout):        
        inp = ControlsBar.create_bin_width_control(
            layout,
            self.app.bin_width_micros,
            self.bin_width_micros_value_change, )
        self.app.control_inputs[SETTINGS_BIN_WIDTH_MICROS] = inp
  

    def create_running_mode_control(self):        
        running_mode_control, inp = ControlsBar.create_running_mode_control(
            self.app.free_running_acquisition_time,
            self.toggle_acquisition_time_mode,
        )
        self.app.control_inputs[SETTINGS_FREE_RUNNING_MODE] = inp
        return running_mode_control


    def create_time_span_control(self, layout):        
        inp = ControlsBar.create_time_span_control(
            layout,
            self.app.time_span,
            self.time_span_value_change, )
        self.app.control_inputs[SETTINGS_TIME_SPAN] = inp 


    def create_acquisition_time_control(self, layout):  
        inp = ControlsBar.create_acquisition_time_control(
            layout,
            self.app.acquisition_time_millis,
            self.acquisition_time_value_change,
            self.app.control_inputs[SETTINGS_FREE_RUNNING_MODE]
        )
        self.app.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS] = inp  
        
        
    def create_cps_threshold_control(self, layout):
        value = int(self.app.settings.value(SETTINGS_CPS_THRESHOLD, DEFAULT_CPS_THRESHOLD))
        inp = ControlsBar.create_cps_threshold_control(
            layout,
            value,
            self.cps_threshold_value_change,
            self.app.show_cps  
        )
        self.app.control_inputs[SETTINGS_CPS_THRESHOLD] = inp
            
    
    def create_show_cps_control(self):    
        show_cps_control, inp = ControlsBar.create_show_cps_control(
            self.app.show_cps,
            self.toggle_show_cps,
        )
        self.app.control_inputs[SETTINGS_SHOW_CPS] = inp
        return show_cps_control     

    def toggle_acquisition_time_mode(self, state):       
        if state:
            self.app.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(False)
            self.app.free_running_acquisition_time = True
            self.app.settings.setValue(SETTINGS_FREE_RUNNING_MODE, True)
        else:
            self.app.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(True)
            self.app.free_running_acquisition_time = False
            self.app.settings.setValue(SETTINGS_FREE_RUNNING_MODE, False)
        # DataExportActions.calc_exported_file_size(self.app)    

    def acquisition_time_value_change(self, value):        
        self.app.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.app.acquisition_time_millis = value * 1000  # convert s to ms
        self.app.settings.setValue(SETTINGS_ACQUISITION_TIME_MILLIS, self.app.acquisition_time_millis)
        # DataExportActions.calc_exported_file_size(self.app)    

    def time_span_value_change(self, value):        
        self.app.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.app.time_span = value
        self.app.settings.setValue(SETTINGS_TIME_SPAN, value)
        
    def cps_threshold_value_change(self, value):
        self.app.cps_threshold = value
        self.app.settings.setValue(SETTINGS_CPS_THRESHOLD, value)  
        

    def bin_width_micros_value_change(self, value):
        self.app.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.app.bin_width_micros = value
        self.app.settings.setValue(SETTINGS_BIN_WIDTH_MICROS, value)
        # DataExportActions.calc_exported_file_size(self.app)
        
    
    def toggle_show_cps(self, state):
        if state:
            self.app.show_cps = True
            self.app.settings.setValue(SETTINGS_SHOW_CPS, True)
            self.app.control_inputs[SETTINGS_CPS_THRESHOLD].setEnabled(True)
        else:
            self.app.show_cps = False
            self.app.settings.setValue(SETTINGS_SHOW_CPS, False)
            self.app.control_inputs[SETTINGS_CPS_THRESHOLD].setEnabled(False)
            
        if len(self.app.cps_charts_widgets) > 0:
            for widget in self.app.cps_charts_widgets:
                widget.setVisible(state)    
           