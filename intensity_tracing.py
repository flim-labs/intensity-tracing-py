from functools import partial
import json
import os
import sys
from PyQt6.QtCore import QTimer, Qt, QSettings, QEvent
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
)
from gui_components.buttons import ActionButtons, CollapseButton, ReadAcquireModeButton
from gui_components.channels_control import ChannelsControl
from gui_components.controls_bar import ControlsBar
from gui_components.data_export_controls import ExportDataControl
from gui_components.input_params_controls import InputParamsControls
from gui_components.intensity_tracing_controller import IntensityTracing
from gui_components.layout_utilities import init_ui
from gui_components.loading import LoadingOverlay
from gui_components.logo_utilities import LogoOverlay
from gui_components.read_data import ReadDataControls
from gui_components.settings import *
from gui_components.top_bar import TopBar

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(project_root)


class PhotonsTracingWindow(QMainWindow):
    def __init__(self):
        super(PhotonsTracingWindow, self).__init__()

        # Initialize settings config
        self.settings = self.init_settings()

        # Acquire/Read mode
        self.reader_data = READER_DATA
        self.acquire_read_mode = self.settings.value(
            SETTINGS_ACQUIRE_READ_MODE, DEFAULT_ACQUIRE_READ_MODE
        )

        ##### GUI PARAMS #####
        self.firmwares = ["intensity_tracing_usb.flim", "intensity_tracing_sma.flim"]
        self.conn_channels = ["USB", "SMA"]
        self.selected_conn_channel = self.settings.value(
            SETTINGS_CONN_CHANNEL, DEFAULT_CONN_CHANNEL
        )
        self.selected_firmware = self.settings.value(
            SETTINGS_FIRMWARE, DEFAULT_FIRMWARE
        )
        self.bin_width_micros = int(
            self.settings.value(SETTINGS_BIN_WIDTH_MICROS, DEFAULT_BIN_WIDTH_MICROS)
        )
        self.time_span = int(self.settings.value(SETTINGS_TIME_SPAN, DEFAULT_TIME_SPAN))
        default_acquisition_time_millis = self.settings.value(
            SETTINGS_ACQUISITION_TIME_MILLIS
        )
        self.acquisition_time_millis = (
            int(default_acquisition_time_millis)
            if default_acquisition_time_millis is not None
            else DEFAULT_ACQUISITION_TIME_MILLIS
        )
        self.free_running_acquisition_time = self.settings.value(
            SETTINGS_FREE_RUNNING_MODE, DEFAULT_FREE_RUNNING_MODE
        ) in ["true", True]
        default_enabled_channels = self.settings.value(
            SETTINGS_ENABLED_CHANNELS, DEFAULT_ENABLED_CHANNELS
        )
        self.enabled_channels = (
            json.loads(default_enabled_channels)
            if default_enabled_channels is not None
            else []
        )
        self.show_cps = self.settings.value(SETTINGS_SHOW_CPS, DEFAULT_SHOW_CPS) in [
            "true",
            True,
        ]
        
        self.cps_threshold = int(self.settings.value(SETTINGS_CPS_THRESHOLD, DEFAULT_CPS_THRESHOLD))
        
        self.write_data = self.settings.value(
            SETTINGS_WRITE_DATA, DEFAULT_WRITE_DATA
        ) in ["true", True]
        self.cached_time_span_seconds = 3

        self.acquisition_stopped = False
        self.control_inputs = {}
        self.widgets = {}
        self.layouts = {}
        default_intensity_plots_to_show = self.settings.value(
            SETTINGS_INTENSITY_PLOTS_TO_SHOW, DEFAULT_INTENSITY_PLOTS_TO_SHOW
        )
        self.intensity_plots_to_show = (
            json.loads(default_intensity_plots_to_show)
            if default_intensity_plots_to_show is not None
            else []
        )
        self.plots_to_show_popup_already_shown = False
        self.channel_checkbox_layout = QGridLayout()
        self.top_utilities_layout = QVBoxLayout()
        self.channels_checkboxes = []
        self.blank_space = QWidget()
        self.bin_file_size = ""
        self.bin_file_size_label = QLabel("")
        self.warning_box = None
        self.test_mode = False
        self.cps_ch = {}
        self.cps_counts = {}
        self.cps_widgets_animation = {}
        self.cps_charts_widgets = []
        self.intensity_charts = []
        self.intensity_charts_wrappers = []
        self.only_cps_widgets = []
        self.intensity_lines = {}
        self.acquisition_time_countdown_widgets = {}

        self.pull_from_queue_timer = QTimer()
        self.pull_from_queue_timer.timeout.connect(
            partial(IntensityTracing.pull_from_queue, self)
        )
        self.overlay = LogoOverlay(self)
        self.installEventFilter(self)
        self.init_ui()
        ReadDataControls.handle_widgets_visibility(
            self, self.acquire_read_mode == "read")
        # Loading overlay
        self.loading_overlay = LoadingOverlay(self)


    @staticmethod
    def init_settings():
        settings = QSettings("settings.ini", QSettings.Format.IniFormat)
        return settings

    def init_ui(self):
        self.create_top_utilities_layout()
        main_layout, _ = init_ui(self, self.top_utilities_layout)
        self.main_layout = main_layout

    def create_top_utilities_layout(self):
        top_collapsible_widget = QWidget()
        self.widgets[TOP_COLLAPSIBLE_WIDGET] = top_collapsible_widget
        qv_box = QVBoxLayout()
        qv_box.setSpacing(0)
        qv_box.setContentsMargins(0, 0, 0, 0)
        self.top_utilities_layout = QVBoxLayout()
        self.top_utilities_layout.setSpacing(0)
        self.top_utilities_layout.setContentsMargins(0, 0, 0, 0)
        header_layout = self.create_header_layout()
        channels_component = self.create_channels_grid()
        self.widgets[CHANNELS_COMPONENT] = channels_component
        ch_widget = QWidget()
        ch_box = QVBoxLayout()
        ch_box.setSpacing(0)
        ch_widget.setLayout(ch_box)
        ch_box.addWidget(channels_component)
        self.widgets[CHECKBOX_CONTROLS] = ch_widget
        qv_box.addWidget(ch_widget, 0, Qt.AlignmentFlag.AlignTop)
        top_collapsible_widget.setLayout(qv_box)
        controls_layout = self.create_controls_layout()
        qv_box_2 = QVBoxLayout()
        qv_box_2.setSpacing(0)
        qv_box_2.setContentsMargins(0, 0, 0, 0)
        qv_box_2.addLayout(header_layout)
        qv_box_2.addWidget(top_collapsible_widget, 0, Qt.AlignmentFlag.AlignTop)
        qv_box_2.addLayout(controls_layout)
        self.top_utilities_layout.addLayout(qv_box_2)
        self.top_utilities_layout.addWidget(
            self.blank_space, 0, Qt.AlignmentFlag.AlignTop
        )

    def create_header_layout(self):
        title_row = self.create_logo_and_title()
        export_data_widget = ExportDataControl(self)
        # Acquire/read mode buttons
        acquire_read_mode_buttons = ReadAcquireModeButton(self)
        header_layout = TopBar.create_header_layout(
            title_row, export_data_widget, acquire_read_mode_buttons
        )
        return header_layout

    def create_logo_and_title(self):
        title_row = TopBar.create_logo_and_title(self)
        return title_row

    def create_channels_grid(self):
        channels_component = ChannelsControl(self)
        return channels_component

    def create_controls_layout(self):
        controls_row = self.create_controls()
        buttons_row_layout = QHBoxLayout()
        buttons_widget = self.create_buttons()
        buttons_row_layout.addStretch(1)
        buttons_row_layout.addWidget(buttons_widget)
        collapse_button = CollapseButton(self.widgets[TOP_COLLAPSIBLE_WIDGET])
        self.widgets[COLLAPSE_BUTTON] = collapse_button
        buttons_row_layout.addWidget(collapse_button)
        buttons_row_layout.addSpacing(10)
        blank_space, controls_layout = ControlsBar.init_gui_controls_layout(
            controls_row, buttons_row_layout
        )
        self.blank_space = blank_space
        return controls_layout

    def create_controls(self):
        controls_row = InputParamsControls(self)
        return controls_row

    def create_buttons(self):
        buttons_row_layout = ActionButtons(self)
        return buttons_row_layout

    def controls_set_enabled(self, enabled: bool):
        for key in self.control_inputs:
            excluded = [
                START_BUTTON,
                STOP_BUTTON,
                RESET_BUTTON,
                ACQUIRE_BUTTON,
                READ_BUTTON,
                EXPORT_PLOT_IMG_BUTTON,
                READ_FILE_BUTTON,
                BIN_METADATA_BUTTON  
            ]
            if key not in excluded:
                widget = self.control_inputs[key]
                if isinstance(widget, QWidget):
                    widget.setEnabled(enabled)
        if enabled:
            self.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(
                not self.free_running_acquisition_time
            )

    def showEvent(self, event):
        super().showEvent(event)
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        x = (screen_rect.width() - self.width()) // 2
        y = (screen_rect.height() - self.height()) // 2
        self.move(x, y)
        self.loading_overlay.resize_overlay(self.rect())

    def closeEvent(self, event):
        if PLOTS_CONFIG_POPUP in self.widgets:
            self.widgets[PLOTS_CONFIG_POPUP].close()
        if READER_POPUP in self.widgets:
            self.widgets[READER_POPUP].close()        
        if READER_METADATA_POPUP in self.widgets:
            self.widgets[READER_METADATA_POPUP].close()                   
        event.accept()

    def eventFilter(self, source, event):
        try:
            if event.type() in (
                QEvent.Type.Resize,
                QEvent.Type.MouseButtonPress,
                QEvent.Type.MouseButtonRelease,
            ):
                self.overlay.raise_()
                self.overlay.resize(self.size())
            return super().eventFilter(source, event)
        except:
            pass
        
    def resizeEvent(self, event):
        self.loading_overlay.resize_overlay(self.rect())
        super().resizeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PhotonsTracingWindow()
    window.showMaximized()
    window.show()
    exit_code = app.exec()
    IntensityTracing.stop_button_pressed(window)
    sys.exit(exit_code)
