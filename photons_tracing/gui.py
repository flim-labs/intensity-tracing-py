import random
import sys
import os

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(project_root)
from threading import Thread
from time import sleep
from math import ceil, floor
from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QApplication,
    QCheckBox,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QMessageBox,
)
import pyqtgraph as pg
from PyQt5.QtGui import QIcon, QPixmap
from flim_labs import flim_labs
from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_axis_range import LiveAxisRange
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget
from gui_styles import GUIStyles
from gui_components.logo_utilities import LogoOverlay, TitlebarIcon
from gui_components.switch_control import SwitchControl
from gui_components.select_control import SelectControl
from gui_components.input_number_control import InputNumberControl
from messages_utilities import MessagesUtilities
from gui_components.layout_utilities import draw_layout_separator
from gui_components.link_widget import LinkWidget
from gui_components.box_message import BoxMessage
from params_configuration import ParamsConfigHandler


class PhotonsTracingWindow(QMainWindow):
    def __init__(self, params_config):
        super(PhotonsTracingWindow, self).__init__()

        ##### GUI PARAMS #####
        self.firmwares = ["intensity_tracing_usb.flim", "intensity_tracing_sma.flim"]
        self.update_rates = ["LOW", "HIGH"]
        self.selected_update_rate = params_config["selected_update_rate"]
        self.conn_channels = ["USB", "SMA"]
        self.selected_conn_channel = params_config["selected_conn_channel"]
        self.selected_firmware = params_config["selected_firmware"]
        self.bin_width_micros = params_config["bin_width_micros"]
        self.time_span = params_config["time_span"]
        self.acquisition_time_millis = params_config["acquisition_time_millis"]
        # draw_frequency suggested range: 10-100
        # (100 requires a fast computer, 10 is suitable for most computers)
        self.draw_frequency = params_config["draw_frequency"]
        # keep_points suggested range: 100-1000
        # (1000 requires a fast computer, 100 is suitable for most computers)
        # depending on the draw_frequency, this will keep the last 1-10 seconds of data
        self.keep_points = 1000
        self.free_running_acquisition_time = params_config[
            "free_running_acquisition_time"
        ]
        self.enabled_channels = params_config["enabled_channels"]
        self.write_data = params_config["write_data"]

        self.flim_thread = None
        self.terminate_thread = False
        self.charts = []

        GUIStyles.customize_theme(self)
        GUIStyles.set_fonts()
        self.setWindowTitle("Intensity tracing v1.1")

        self.resize(1460, 800)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.layout = QVBoxLayout()

        self.connectors = []

        # Header row: save parameters configuration / Link to User Guide
        self.header_layout = QHBoxLayout()

        flim_header_icon = QLabel(
            self,
            pixmap=QPixmap(
                os.path.join(project_root, "assets", "flimlabs-logo.png")
            ).scaledToWidth(60),
        )
        header_title = QLabel("INTENSITY TRACING")
        header_title.setStyleSheet(GUIStyles.set_main_title_style())
        save_icon = QIcon(os.path.join(project_root, "assets", "save-icon.png"))
        self.save_conf_button = QPushButton("SAVE CONFIGURATION")
        self.save_conf_button.setIcon(save_icon)
        GUIStyles.set_config_btn_style(self.save_conf_button)
        self.save_conf_button.clicked.connect(self.save_conf_button_pressed)

        app_guide_link_widget = LinkWidget(
            icon_filename="info-icon.png", text="User Guide"
        )
        self.header_layout.addWidget(flim_header_icon)
        self.header_layout.addWidget(header_title)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.save_conf_button)
        self.header_layout.addWidget(app_guide_link_widget)
        self.layout.addLayout(self.header_layout)

        self.checkbox_layout = QGridLayout()
        self.channels_checkboxes = self.draw_checkboxes()

        toolbar_layout = QVBoxLayout()
        toolbar_layout.addSpacing(10)

        self.blank_space = QWidget()
        self.blank_space.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # CONTROLS
        self.controls_row = QHBoxLayout()

        # Channels type control (USB/SMA)
        (
            self.conn_channel_type_control,
            self.conn_channel_type_input,
        ) = SelectControl.setup(
            "Channel type:",
            self.selected_conn_channel,
            self.controls_row,
            self.conn_channels,
            self.conn_channel_type_value_change,
        )
        self.conn_channel_type_input.setStyleSheet(GUIStyles.set_input_select_style())

        # Bin width micros control

        (
            self.bin_width_micros_control,
            self.bin_width_micros_input,
        ) = InputNumberControl.setup(
            "Bin width (µs):",
            1,
            1000000,
            self.bin_width_micros,
            self.controls_row,
            self.bin_width_micros_value_change,
        )
        self.bin_width_micros_input.setStyleSheet(GUIStyles.set_input_number_style())

        # Update rate control (LOW/HIGH)
        self.update_rate_control, self.update_rate_input = SelectControl.setup(
            "Update rate:",
            self.selected_update_rate,
            self.controls_row,
            self.update_rates,
            self.update_rate_value_change,
        )
        self.update_rate_input.setStyleSheet(GUIStyles.set_input_select_style())

        # Acquisition time mode switch control (Free Running/Fixed)
        self.acquisition_time_control = QVBoxLayout()
        acquisition_time_label = QLabel("Free running acquisition time:")
        self.acquisition_time_mode_switch = SwitchControl(
            active_color="#13B6B4", checked=True
        )
        self.acquisition_time_mode_switch.stateChanged.connect(
            (lambda state: self.toggle_acquisition_time_mode(state))
        )
        self.acquisition_time_control.addWidget(acquisition_time_label)
        self.acquisition_time_control.addSpacing(8)
        self.acquisition_time_control.addWidget(self.acquisition_time_mode_switch)
        self.controls_row.addLayout(self.acquisition_time_control)
        self.controls_row.addSpacing(20)

        # Keep points input number control (configurable when in acquisition time free running mode)
        self.time_span_control, self.time_span_input = InputNumberControl.setup(
            "Time span (s):",
            1,
            300,
            self.time_span,
            self.controls_row,
            self.time_span_value_change,
        )
        self.time_span_input.setStyleSheet(GUIStyles.set_input_number_style())

        # Acquisition time millis input number control (configurable when in acquisition time fixed mode)
        (
            self.acquisition_time_control,
            self.acquisition_time_input,
        ) = InputNumberControl.setup(
            "Acquisition time (s):",
            0,
            10800,
            self.acquisition_time_millis / 1000
            if self.acquisition_time_millis is not None
            else None,
            self.controls_row,
            self.acquisition_time_value_change,
        )
        self.acquisition_time_input.setEnabled(
            not self.acquisition_time_mode_switch.isChecked()
        )
        self.acquisition_time_input.setStyleSheet(GUIStyles.set_input_number_style())

        toolbar_layout.addLayout(self.controls_row)
        toolbar_layout.addWidget(draw_layout_separator())

        # ACTION BUTTONS
        buttons_row_layout = QHBoxLayout()
        buttons_row_layout.addStretch(1)

        # Link to export data documentation
        info_link_widget = LinkWidget(
            icon_filename="info-icon.png",
            link="https://flim-labs.github.io/products/python-flim-labs/intensity-tracing-file-format.html",
        )
        info_link_widget.show()
        buttons_row_layout.addWidget(info_link_widget)

        # Export data switch control
        self.export_data_control = QHBoxLayout()
        export_data_label = QLabel("Export data:")
        self.export_data_switch = SwitchControl(
            active_color="#FB8C00", width=70, height=30, checked=False
        )
        self.export_data_switch.stateChanged.connect(
            (lambda state: self.toggle_export_data(state))
        )
        self.export_data_control.addWidget(export_data_label)
        self.export_data_control.addSpacing(8)
        self.export_data_control.addWidget(self.export_data_switch)
        buttons_row_layout.addLayout(self.export_data_control)
        self.export_data_control.addSpacing(20)

        self.start_button = QPushButton("START")
        GUIStyles.set_start_btn_style(self.start_button)
        self.start_button.clicked.connect(self.start_button_pressed)
        self.start_button.setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )
        buttons_row_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("STOP")
        GUIStyles.set_stop_btn_style(self.stop_button)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_button_pressed)
        buttons_row_layout.addWidget(self.stop_button)

        self.reset_button = QPushButton("RESET")
        GUIStyles.set_reset_btn_style(self.reset_button)
        self.reset_button.setEnabled(True)
        self.reset_button.clicked.connect(self.reset_button_pressed)
        buttons_row_layout.addWidget(self.reset_button)

        toolbar_layout.addSpacing(10)

        toolbar_layout.addLayout(buttons_row_layout)

        toolbar_layout.addSpacing(10)

        self.layout.addLayout(toolbar_layout)
        self.layout.addWidget(self.blank_space)

        widget = QWidget()
        widget.setLayout(self.layout)
        scroll_area.setWidget(widget)
        self.setCentralWidget(scroll_area)

        # Charts grid
        self.charts_grid = QGridLayout()
        self.layout.addLayout(self.charts_grid)

        # Logo overlay
        self.logo_overlay = LogoOverlay(self)
        self.logo_overlay.show()
        self.logo_overlay.update_visibility(self)
        self.logo_overlay.update_position(self.logo_overlay)
        self.logo_overlay.lower()

        # Titlebar logo icon
        TitlebarIcon.setup(self)

    def draw_checkboxes(self):
        channels_checkboxes = []

        for i in range(8):
            self.enabled_channels.sort()
            checkbox = QCheckBox("Channel " + str(i + 1))
            checkbox.setStyleSheet(GUIStyles.set_checkbox_style())
            if i not in self.enabled_channels:
                checkbox.setChecked(False)
            else:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, index=i: self.toggle_channels_checkbox(state, index)
            )

            channels_checkboxes.append(checkbox)

        self.layout.addLayout(self.checkbox_layout)
        self.update_checkbox_layout(channels_checkboxes)
        return channels_checkboxes

    def toggle_channels_checkbox(self, state, index):
        if state:
            self.enabled_channels.append(index)
        else:
            self.enabled_channels.remove(index)
        self.enabled_channels.sort()
        print("Enabled channels: " + str(self.enabled_channels))
        self.start_button.setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )

    def toggle_acquisition_time_mode(self, state):
        if state:
            self.acquisition_time_millis = None
            self.acquisition_time_input.setEnabled(False)
        else:
            self.acquisition_time_input.setEnabled(True)

    def toggle_export_data(self, state):
        if state:
            self.write_data = True
        else:
            self.write_data = False

    def conn_channel_type_value_change(self, index):
        self.selected_conn_channel = self.sender().currentText()
        if self.selected_conn_channel == "USB":
            self.selected_firmware = self.firmwares[0]
        else:
            self.selected_firmware = self.firmwares[1]

    def acquisition_time_value_change(self, value):
        self.start_button.setEnabled(value != 0)
        self.acquisition_time_millis = value * 1000  # convert s to ms

    def time_span_value_change(self, value):
        self.start_button.setEnabled(value != 0)
        self.time_span = value

    def bin_width_micros_value_change(self, value):
        self.start_button.setEnabled(value != 0)
        self.bin_width_micros = value

    def update_rate_value_change(self, index):
        self.selected_update_rate = self.sender().currentText()
        print(self.selected_update_rate)

    def save_conf_button_pressed(self):
        params_config = ParamsConfigHandler(
            self.selected_update_rate,
            self.selected_conn_channel,
            self.selected_firmware,
            self.bin_width_micros,
            self.time_span,
            self.acquisition_time_millis,
            self.draw_frequency,
            self.free_running_acquisition_time,
            self.write_data,
            self.enabled_channels,
        )
        params_config.save()

    def start_button_pressed(self):
        warn_title, warn_msg = MessagesUtilities.invalid_inputs_handler(
            self.bin_width_micros,
            self.time_span,
            self.acquisition_time_millis,
            self.acquisition_time_mode_switch,
            self.enabled_channels,
            self.selected_conn_channel,
            self.selected_update_rate,
        )
        if warn_title and warn_msg:
            BoxMessage.setup(
                warn_title, warn_msg, QMessageBox.Warning, GUIStyles.set_msg_box_style()
            )
            return
        self.set_draw_frequency()
        self.calc_max_points()
        self.terminate_thread = False
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(False)

        for chart in self.charts:
            chart.setVisible(False)

        for channel, curr_conn in self.connectors:
            curr_conn.disconnect()

        self.connectors.clear()
        self.charts.clear()
        self.blank_space.hide()

        for i in range(len(self.enabled_channels)):
            if i < len(self.charts):
                self.charts[i].show()
            else:
                (chart, connector) = self.generate_chart(i)
                row, col = divmod(i, 2)
                self.charts_grid.addWidget(chart, row, col)
                self.charts.append(chart)
                self.connectors.append(connector)

        QApplication.processEvents()
        self.start_photons_tracing()

    def stop_button_pressed(self, thread_join=True):
        self.start_button.setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )
        self.stop_button.setEnabled(False)
        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(True)
        QApplication.processEvents()

        flim_labs.request_stop()

        if thread_join and self.flim_thread is not None and self.flim_thread.is_alive():
            self.flim_thread.join()

        for channel, curr_conn in self.connectors:
            curr_conn.pause()

    def reset_button_pressed(self):
        # reset charts
        self.start_button.setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )
        self.stop_button.setEnabled(False)

        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(True)

        for chart in self.charts:
            chart.setVisible(False)

        self.connectors.clear()
        self.charts.clear()
        QApplication.processEvents()

        flim_labs.request_stop()
        self.terminate_thread = True

        for channel, curr_conn in self.connectors:
            curr_conn.pause()

        self.blank_space.show()

    def set_draw_frequency(self):
        num_enabled_channels = len(self.enabled_channels)
        if (
                self.selected_update_rate not in ["LOW", "HIGH"]
                and num_enabled_channels == 0
        ):
            self.draw_frequency = 10
            return
        if self.selected_update_rate == "LOW":
            min_frequency = 5
            max_frequency = 20
        else:
            min_frequency = 21
            max_frequency = 50

        frequency_range = max_frequency - min_frequency
        step = frequency_range / num_enabled_channels
        adjusted_frequency = max_frequency - step * (num_enabled_channels - 1)
        self.draw_frequency = max(min_frequency, min(max_frequency, adjusted_frequency))

    def calc_max_points(self):
        bin_width_seconds = self.bin_width_micros / 1000000
        max_points_by_bin_width = int(self.time_span / bin_width_seconds)
        draw_interval = 1 / self.draw_frequency
        max_points_by_frequency = int(self.time_span / draw_interval)
        self.keep_points = min(max_points_by_bin_width, max_points_by_frequency)

    def generate_chart(self, channel_index):
        left_axis = LiveAxis("left", axisPen="#cecece", textPen="#FFA726")
        bottom_axis = LiveAxis(
            "bottom",
            axisPen="#cecece",
            textPen="#23F3AB",
            tick_angle=-45,
            **{Axis.TICK_FORMAT: Axis.DURATION, Axis.DURATION_FORMAT: Axis.DF_SHORT},
        )
        plot_widget = LivePlotWidget(
            title="Channel " + str(self.enabled_channels[channel_index] + 1),
            y_label="Photon counts",
            axisItems={"bottom": bottom_axis, "left": left_axis},
            x_range_controller=LiveAxisRange(roll_on_tick=1)
        )

        plot_curve = LiveLinePlot()
        plot_curve.setPen(pg.mkPen(color="#a877f7"))
        plot_widget.addItem(plot_curve)
        connector = DataConnector(
            plot_curve,
            update_rate=self.draw_frequency,
            max_points=self.keep_points,
        )

        plot_widget.setBackground(None)

        return plot_widget, (self.enabled_channels[channel_index], connector)

    def showEvent(self, event):
        super().showEvent(event)
        screen_rect = QDesktopWidget().screenGeometry()
        x = (screen_rect.width() - self.width()) // 2
        y = (screen_rect.height() - self.height()) // 2
        self.move(x, y)

    def update_checkbox_layout(self, channels_checkboxes):
        screen_width = self.width()
        if screen_width < 500:
            num_columns = 1
        elif 500 <= screen_width <= 1200:
            num_columns = 2
        elif 1201 <= screen_width <= 1450:
            num_columns = 4
        else:
            num_columns = 8

        for i, checkbox in enumerate(channels_checkboxes):
            row, col = divmod(i, num_columns)
            self.checkbox_layout.addWidget(checkbox, row, col)

    def resizeEvent(self, event):
        super(PhotonsTracingWindow, self).resizeEvent(event)
        self.logo_overlay.update_position(self)
        self.logo_overlay.update_visibility(self)
        self.update_checkbox_layout(self.channels_checkboxes)

    def process_point(self, time, x, counts):
        for channel, curr_conn in self.connectors:
                curr_conn.cb_append_data_point(y=counts[channel], x=time / 1_000_000_000)

        if self.selected_update_rate == "LOW":
            if x % 1000 == 0:
                QApplication.processEvents()
            else:
                sleep(0.000001)
        else:
            if x % 100 == 0:
                QApplication.processEvents()
            else:
                sleep(0.000001)

    def flim_read(self):
        print("Thread: Start reading from flim queue")
        flim_labs.read_from_queue(self.process_point)
        print("Thread: End reading from flim queue")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.terminate_thread:
            return
        self.stop_button_pressed(thread_join=False)

    def start_photons_tracing(self):
        try:
            acquisition_time_millis = (
                None
                if self.acquisition_time_millis in (0, None)
                else self.acquisition_time_millis
            )
            print("Selected firmware: " + (str(self.selected_firmware)))
            print(
                "Free running enabled: "
                + str(self.acquisition_time_mode_switch.isChecked())
            )
            print("Acquisition time (ms): " + str(acquisition_time_millis))
            print("Time span (s): " + str(self.time_span))
            print("Max points: " + str(self.keep_points))
            print("Bin width (µs): " + str(self.bin_width_micros))
            print("Draw frequency: " + str(self.draw_frequency))

            result = flim_labs.start_intensity_tracing(
                enabled_channels=self.enabled_channels,
                bin_width_micros=self.bin_width_micros,  # E.g. 1000 = 1ms bin width
                write_bin=False,  # True = Write raw data from card in a binary file
                write_data=self.write_data,  # True = Write raw data in a data file
                acquisition_time_millis=acquisition_time_millis,  # E.g. 10000 = Stops after 10 seconds of acquisition
                firmware_file=None,
                # String, if None let flim decide to use intensity tracing Firmware
            )

            file_bin = result.bin_file
            if file_bin != "":
                print("File bin written in: " + str(file_bin))

            self.flim_thread = Thread(target=self.flim_read)
            self.flim_thread.start()

        except Exception as e:
            error_title, error_msg = MessagesUtilities.error_handler(str(e))
            BoxMessage.setup(
                error_title,
                error_msg,
                QMessageBox.Critical,
                GUIStyles.set_msg_box_style(),
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    params_config = ParamsConfigHandler().load()

    window = PhotonsTracingWindow(params_config)
    window.show()
    exit_code = app.exec()
    window.stop_button_pressed()
    sys.exit(exit_code)
