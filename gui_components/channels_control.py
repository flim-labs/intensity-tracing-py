import os
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from gui_components.buttons import PlotsConfigPopup
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
        self.plots_config_btn = QPushButton("PLOTS CONFIG")
        self.plots_config_btn.setIcon(QIcon(resource_path("assets/chart-icon.png")))
        self.plots_config_btn.setFixedWidth(150)
        self.plots_config_btn.setStyleSheet(GUIStyles.channels_btn_style(base="#FB8C00", hover="#FFA726", pressed="#FB8C00", text="white"))
        self.plots_config_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.plots_config_btn.clicked.connect(self.open_plots_config_popup) 
        self.widgets = self.ch_checkboxes + [self.plots_config_btn] 
        self.init_ch_grid()
 

    def init_ch_grid(self):
        self.update_ch_checkboxes()
        self.channels_grid.addWidget(self.plots_config_btn)
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
            self.ch_checkboxes.append(ch_checkbox_wrapper)
            self.widgets = self.ch_checkboxes + [self.plots_config_btn]
        for checkbox in  self.ch_checkboxes:
            self.channels_grid.addWidget(checkbox)    
    

    def on_ch_toggled(self, state, index):
        intensity_plot_to_show = self.app.intensity_plots_to_show
        if state:
            if index not in self.app.enabled_channels:
                self.app.enabled_channels.append(index)
        else:
            if index in self.app.enabled_channels:
                self.app.enabled_channels.remove(index)
                filtered_intensity_plot_to_show = list(filter(lambda x: x != index, intensity_plot_to_show))
                self.app.intensity_plots_to_show = filtered_intensity_plot_to_show
                self.app.settings.setValue(SETTINGS_INTENSITY_PLOTS_TO_SHOW, json.dumps(filtered_intensity_plot_to_show))
        self.app.settings.setValue(SETTINGS_ENABLED_CHANNELS, json.dumps(self.app.enabled_channels))
        DataExportActions.calc_exported_file_size(self.app)
 

    def open_plots_config_popup(self):
        self.popup = PlotsConfigPopup(self.app, start_acquisition=False)
        self.popup.show()