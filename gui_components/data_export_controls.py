

from functools import partial
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from gui_components.file_utilities import MatlabScriptUtils, PythonScriptUtils
from gui_components.format_utilities import FormatUtils
from gui_components.resource_path import resource_path
from gui_components.settings import *
from gui_components.top_bar import TopBar



class ExportDataControl(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        self.info_link_widget, self.export_data_control = self.create_export_data_input()
        self.file_size_info_layout = self.create_file_size_info_row()
        layout = QHBoxLayout()
        layout.addWidget(self.info_link_widget)
        layout.addLayout(self.export_data_control)
        self.export_data_control.addSpacing(10)
        layout.addLayout(self.file_size_info_layout)

        self.setLayout(layout)

    def create_export_data_input(self):        
        info_link_widget, export_data_control, inp = TopBar.create_export_data_input(self.app.write_data, self.toggle_export_data)
        self.app.control_inputs[SETTINGS_WRITE_DATA] = inp
        return info_link_widget, export_data_control 

    def create_file_size_info_row(self):    
        file_size_info_layout = TopBar.create_file_size_info_row(
            self.app.bin_file_size,
            self.app.bin_file_size_label,
            self.app.write_data,
            partial( DataExportActions.calc_exported_file_size, self.app)
           )
        return file_size_info_layout 

    def toggle_export_data(self, state):        
        if state:
            self.app.write_data = True
            self.app.settings.setValue(SETTINGS_WRITE_DATA, True)
            self.app.bin_file_size_label.show()
            DataExportActions.calc_exported_file_size(self.app)
        else:
            self.app.write_data = False
            self.app.settings.setValue(SETTINGS_WRITE_DATA, False)
            self.app.bin_file_size_label.hide()          



class DataExportActions: 
    @staticmethod
    def calc_exported_file_size(app):
        if len(app.enabled_channels) == 0:
             app.bin_file_size_label.setText("")
             return 
        chunk_bytes = 8 + (4 * len(app.enabled_channels))
        chunk_bytes_in_us =  (1000 * (chunk_bytes * 1000)) / app.bin_width_micros
        if app.free_running_acquisition_time is True or app.acquisition_time_millis is None:
            file_size_bytes = int(chunk_bytes_in_us)
            app.bin_file_size = FormatUtils.format_size(file_size_bytes)
            app.bin_file_size_label.setText("File size: " + str(app.bin_file_size) + "/s")
        else:
            file_size_bytes = int(chunk_bytes_in_us * (app.acquisition_time_millis/1000))
            app.bin_file_size = FormatUtils.format_size(file_size_bytes)
            app.bin_file_size_label.setText("File size: " + str(app.bin_file_size))
            
    
  