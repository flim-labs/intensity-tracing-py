import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from gui_components.buttons import PlotsConfigPopup
from gui_components.controls_bar import ControlsBar
from gui_components.data_export_controls import DataExportActions
from gui_components.resource_path import resource_path
from gui_components.gui_styles import GUIStyles
from gui_components.settings import *
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path))


class ChannelsControl(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        self.channels_grid = QHBoxLayout()
        layout.addLayout(self.channels_grid)
        self.setLayout(layout)
        self.ch_checkboxes = []
        self.create_channel_type_control(self.channels_grid)
        self.plots_config_btn = QPushButton("PLOTS CONFIG")
        self.plots_config_btn.setIcon(QIcon(resource_path("assets/chart-icon.png")))
        self.plots_config_btn.setFixedWidth(150)
        self.plots_config_btn.setFixedHeight(40)
        self.plots_config_btn.setStyleSheet(GUIStyles.channels_btn_style(base="#FB8C00", hover="#FFA726", pressed="#FB8C00", text="white"))
        self.plots_config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plots_config_btn.clicked.connect(self.open_plots_config_popup) 
        self.widgets = [self.app.control_inputs[SETTINGS_CONN_CHANNEL]] + self.ch_checkboxes + [self.plots_config_btn] 
        self.init_ch_grid()
        

    def create_channel_type_control(self, layout):        
        inp = ControlsBar.create_channel_type_control(
            layout,
            self.app.selected_conn_channel,
            self.conn_channel_type_value_change,
            self.app.conn_channels)
        inp.setFixedHeight(40)
        self.app.control_inputs[SETTINGS_CONN_CHANNEL] = inp     
        

    def conn_channel_type_value_change(self, index):       
        self.app.selected_conn_channel = self.sender().currentText()
        if self.app.selected_conn_channel == "USB":
            self.app.selected_firmware = self.app.firmwares[0]
        else:
            self.app.selected_firmware = self.app.firmwares[1]
        self.app.settings.setValue(SETTINGS_FIRMWARE, self.app.selected_firmware)
        self.app.settings.setValue(SETTINGS_CONN_CHANNEL, self.app.selected_conn_channel)            
 

    def init_ch_grid(self):
        self.update_ch_checkboxes()
        self.channels_grid.addWidget(self.plots_config_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        return 

    def update_ch_checkboxes(self):
        for i in range(MAX_CHANNELS):
            from gui_components.fancy_checkbox import FancyCheckbox
            ch_checkbox_wrapper = QWidget() 
            ch_checkbox_wrapper.setObjectName(f"ch_checkbox_wrapper")
            checkbox = FancyCheckbox(text=f"Channel {i + 1}")
            checkbox.setStyleSheet(GUIStyles.set_checkbox_style())
            checked = i in self.app.enabled_channels
            checkbox.set_checked(checked)
            checkbox.toggled.connect(lambda state, index=i: self.on_ch_toggled(state, index))
            row = QHBoxLayout()
            row.addWidget(checkbox)
            ch_checkbox_wrapper.setLayout(row)
            ch_checkbox_wrapper.setStyleSheet(GUIStyles.checkbox_wrapper_style())
            ch_checkbox_wrapper.setFixedHeight(40)
            self.ch_checkboxes.append(ch_checkbox_wrapper)
            self.widgets = [self.app.control_inputs[SETTINGS_CONN_CHANNEL]] + self.ch_checkboxes + [self.plots_config_btn]
        for checkbox in  self.ch_checkboxes:
            self.channels_grid.addWidget(checkbox, alignment=Qt.AlignmentFlag.AlignBottom)    
    

    def on_ch_toggled(self, state, index):
        intensity_plot_to_show = self.app.intensity_plots_to_show
        if state:
            if index not in self.app.enabled_channels:
                self.app.enabled_channels.append(index)
                if not(index in self.app.intensity_plots_to_show) and len(self.app.intensity_plots_to_show) < 4:
                    self.app.intensity_plots_to_show.append(index)
                    self.app.intensity_plots_to_show.sort()
                    self.app.settings.setValue(SETTINGS_INTENSITY_PLOTS_TO_SHOW, json.dumps(self.app.intensity_plots_to_show))
        else:
            if index in self.app.enabled_channels:
                self.app.enabled_channels.remove(index)
                filtered_intensity_plot_to_show = list(filter(lambda x: x != index, intensity_plot_to_show))
                self.app.intensity_plots_to_show = filtered_intensity_plot_to_show
                self.app.intensity_plots_to_show.sort()
                self.app.settings.setValue(SETTINGS_INTENSITY_PLOTS_TO_SHOW, json.dumps(filtered_intensity_plot_to_show))
        self.app.settings.setValue(SETTINGS_ENABLED_CHANNELS, json.dumps(self.app.enabled_channels))
        DataExportActions.calc_exported_file_size(self.app)
 

    def open_plots_config_popup(self):
        self.popup = PlotsConfigPopup(self.app, start_acquisition=False)
        self.popup.show()