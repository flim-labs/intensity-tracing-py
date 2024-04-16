

from functools import partial
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QHBoxLayout, QWidget
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
            self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.app.write_data and self.app.acquisition_stopped)
            DataExportActions.set_download_button_icon(self.app)
            self.app.settings.setValue(SETTINGS_WRITE_DATA, True)
            self.app.bin_file_size_label.show()
            DataExportActions.calc_exported_file_size(self.app)
        else:
            self.app.write_data = False
            self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.app.write_data and self.app.acquisition_stopped)
            DataExportActions.set_download_button_icon(self.app)
            self.app.settings.setValue(SETTINGS_WRITE_DATA, False)
            self.app.bin_file_size_label.hide()          


class DownloadDataControl(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        self.download_button, self.download_menu = self.create_download_files_menu()
        layout = QHBoxLayout()
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def create_download_files_menu(self):    
        download_button, download_menu = TopBar.create_download_files_menu(
            self.app,
            self.app.write_data,
            self.app.acquisition_stopped,
            self.show_download_options,
            self.download_matlab,
            self.download_python
        )
        self.app.control_inputs[DOWNLOAD_BUTTON] = download_button
        self.app.control_inputs[DOWNLOAD_MENU] = download_menu
        DataExportActions.set_download_button_icon(self.app)
        return download_button, download_menu 
    
    
    def show_download_options(self):
        self.app.control_inputs[DOWNLOAD_MENU].exec_(
            self.app.control_inputs[DOWNLOAD_BUTTON].mapToGlobal(QPoint(0, self.app.control_inputs[DOWNLOAD_BUTTON].height()))
        )
       
    def download_matlab(self):    
        MatlabScriptUtils.download_matlab(self)
        self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(False)
        self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(True)

    def download_python(self):
        PythonScriptUtils.download_python(self)
        self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(False)
        self.app.control_inputs[DOWNLOAD_BUTTON].setEnabled(True) 

   

class DataExportActions: 
    @staticmethod
    def calc_exported_file_size(app):
        if app.free_running_acquisition_time is True or app.acquisition_time_millis is None:
            file_size_bytes = int(EXPORTED_DATA_BYTES_UNIT *
                                  (1000 / app.bin_width_micros) * len(app.enabled_channels))
            app.bin_file_size = FormatUtils.format_size(file_size_bytes)
            app.bin_file_size_label.setText("File size: " + str(app.bin_file_size) + "/s")
        else:
            file_size_bytes = int(EXPORTED_DATA_BYTES_UNIT *
                                  (app.acquisition_time_millis / 1000) *
                                  (1000 / app.bin_width_micros) * len(app.enabled_channels))
            app.bin_file_size = FormatUtils.format_size(file_size_bytes)
            app.bin_file_size_label.setText("File size: " + str(app.bin_file_size))
            
    
    @staticmethod
    def set_download_button_icon(app):    
        if app.control_inputs[DOWNLOAD_BUTTON].isEnabled():
            icon = resource_path("assets/arrow-down-icon-white.png")
            app.control_inputs[DOWNLOAD_BUTTON].setIcon(QIcon(icon))
        else:
            icon = resource_path("assets/arrow-down-icon-grey.png")
            app.control_inputs[DOWNLOAD_BUTTON].setIcon(QIcon(icon))        