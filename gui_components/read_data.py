from functools import partial
import json
import os
import re
import struct

from matplotlib import pyplot as plt
import numpy as np
from gui_components.box_message import BoxMessage
from gui_components.gui_styles import GUIStyles
from gui_components.helpers import extract_channel_from_label
from gui_components.input_text_control import InputTextControl
from gui_components.layout_utilities import clear_layout
from gui_components.logo_utilities import TitlebarIcon
from gui_components.messages_utilities import MessagesUtilities
from gui_components.resource_path import resource_path
from gui_components.channel_name_utils import get_channel_name
from gui_components.settings import (
    BIN_METADATA_BUTTON,
    CHECK_CARD_WIDGET,
    COLLAPSE_BUTTON,
    EXPORT_PLOT_IMG_BUTTON,
    READ_FILE_BUTTON,
    READER_METADATA_POPUP,
    READER_POPUP,
    RESET_BUTTON,
    SETTINGS_ACQUISITION_TIME_MILLIS,
    SETTINGS_BIN_WIDTH_MICROS,
    SETTINGS_CPS_THRESHOLD,
    SETTINGS_ENABLED_CHANNELS,
    SETTINGS_FREE_RUNNING_MODE,
    SETTINGS_INTENSITY_PLOTS_TO_SHOW,
    SETTINGS_TIME_SPAN,
    START_BUTTON,
    STOP_BUTTON,
    TOP_COLLAPSIBLE_WIDGET,
)
from PyQt6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGridLayout,
    QWidget,
    QCheckBox,
    QApplication,
)
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QColor, QIcon

from load_data import plot_intensity_data

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path))


class ReadData:
    @staticmethod
    def read_bin_data(window, app, file_type="intensity"):
        ReadData.read_intensity_bin(window, app)

    @staticmethod
    def read_intensity_bin(window, app, filter_string = None):
        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        if filter_string:
            filter_pattern = f"Bin files (*{filter_string}*.bin)"
        else:
            filter_pattern = "Bin files (*.bin)"
        dialog.setNameFilter(filter_pattern)            
        file_name, _ = dialog.getOpenFileName(
            window,
            f"Load Intensity Tracing file",
            "",
            filter_pattern,
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if not file_name:
            return None
        if file_name is not None and not file_name.endswith(".bin"):        
            ReadData.show_warning_message(
                "Invalid extension", "Invalid extension. File should be a .bin"
            )
            return None
        try:
            app.loading_overlay.set_loading_text("Processing data...")
            app.loading_overlay.toggle_overlay()
            signals = ProcessBinDataWorkerSignals()
            signals.success.connect(
                partial(ReadData.handle_intensity_bin_data_result, app)
            )
            signals.error.connect(
                partial(
                    ReadData.show_warning_message,
                    "Error reading file",
                    f"Error reading Intensity Tracing file",
                )
            )
            task = DataReaderWorker(file_name, signals)
            QThreadPool.globalInstance().start(task)
        except Exception as e:
            ReadData.show_warning_message(
                "Error reading file", f"Error reading Intensity Tracing file"
            )
            return None

    @staticmethod
    def handle_intensity_bin_data_result(app, result):
        if not result:
            return
        file_name, *data, metadata = result
        app.reader_data["intensity"]["plots"] = []
        app.reader_data["intensity"]["metadata"] = metadata
        app.reader_data["intensity"]["files"]["intensity"] = file_name
        times, channels_lines = data
        app.reader_data["intensity"]["data"] = {
            "times": times,
            "channels_lines": channels_lines,
        }
        last_time_s = round(times[-1] / 1_000_000_000, 5)
        app.reader_data["intensity"]["metadata"]["last_time_s"] = last_time_s
        
        if "channel_names" in metadata:
            app.reader_data["intensity"]["metadata"]["channel_names"] = metadata["channel_names"]
        else:
            app.reader_data["intensity"]["metadata"]["channel_names"] = {}
        
        ReaderPopup.handle_bin_file_result_ui(app.widgets[READER_POPUP])

    @staticmethod
    def show_warning_message(title, message):
        BoxMessage.setup(
            title, message, QMessageBox.Icon.Warning, GUIStyles.set_msg_box_style()
        )

    @staticmethod
    def plot_intensity_data(app):
        data = app.reader_data["intensity"]["data"]
        metadata = app.reader_data["intensity"]["metadata"]
        if "channels_lines" in data and "times" in data and "channels" in metadata:
            # Create a mapping from channel index to position in channels_lines
            enabled_channels = metadata["channels"]
            channel_to_position = {ch: i for i, ch in enumerate(enabled_channels)}
            
            for channel_index, intensity_line in app.intensity_lines.items():
                # Check if this channel exists in the data
                if channel_index not in channel_to_position:
                    continue
                    
                position = channel_to_position[channel_index]
                percent = 0.004
                step = max(1, int(len(data["channels_lines"][position]) * percent))
                channel_line = data["channels_lines"][position][::step]
                times = data["times"][::step]
                x = [time / 1_000_000_000 for time in times]
                x = np.array(x)
                y = np.array(channel_line)
                intensity_line.setData(x, y)
                QApplication.processEvents()

    @staticmethod
    def prepare_intensity_data_for_export_img(app):
        metadata = app.reader_data["intensity"]["metadata"]
        channels_lines = app.reader_data["intensity"]["data"]["channels_lines"]
        times = app.reader_data["intensity"]["data"]["times"]
        return channels_lines, times, metadata

    @staticmethod
    def save_plot_image(app, plot):
        dialog = QFileDialog()
        base_path, _ = dialog.getSaveFileName(
            None,
            "Save plot image",
            "",
            "PNG Files (*.png);;EPS Files (*.eps)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )

        def show_success_message():
            app.loading_overlay.toggle_overlay()
            info_title, info_msg = MessagesUtilities.info_handler("SavedPlotImage")
            BoxMessage.setup(
                info_title,
                info_msg,
                QMessageBox.Icon.Information,
                GUIStyles.set_msg_box_style(),
            )

        def show_error_message(error):
            ReadData.show_warning_message(
                "Error saving images", f"Error saving plot images: {error}"
            )

        if base_path:
            app.loading_overlay.set_loading_text("Processing image...")
            app.loading_overlay.toggle_overlay()
            signals = PostSavePlotImageWorkerSignals()
            signals.success.connect(show_success_message)
            signals.error.connect(show_error_message)
            task = SavePlotTask(plot, base_path, signals)
            QThreadPool.globalInstance().start(task)


class ReadDataControls:
    @staticmethod
    def handle_widgets_visibility(app, read_mode):
        app.controls_set_enabled(not read_mode)
        bin_metadata_btn_visible = ReadDataControls.read_bin_metadata_enabled(app)
        app.control_inputs[BIN_METADATA_BUTTON].setVisible(bin_metadata_btn_visible)
        app.control_inputs[START_BUTTON].setVisible(not read_mode)
        app.control_inputs[STOP_BUTTON].setVisible(not read_mode)
        app.control_inputs[RESET_BUTTON].setVisible(not read_mode)
        app.control_inputs[READ_FILE_BUTTON].setVisible(read_mode)
        app.control_inputs[EXPORT_PLOT_IMG_BUTTON].setVisible(bin_metadata_btn_visible)
        app.widgets[TOP_COLLAPSIBLE_WIDGET].setVisible(not read_mode)
        app.widgets[COLLAPSE_BUTTON].setVisible(not read_mode)
        app.control_inputs[SETTINGS_BIN_WIDTH_MICROS].setEnabled(not read_mode)
        app.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(
            not read_mode and not app.free_running_acquisition_time
        )
        app.control_inputs[SETTINGS_FREE_RUNNING_MODE].setEnabled(not read_mode)
        app.control_inputs[SETTINGS_CPS_THRESHOLD].setEnabled(not read_mode)
        app.control_inputs[SETTINGS_TIME_SPAN].setEnabled(not read_mode)
        if CHECK_CARD_WIDGET in app.widgets:
            app.widgets[CHECK_CARD_WIDGET].setVisible(not read_mode)            

    @staticmethod
    def read_bin_metadata_enabled(app):
        metadata = app.reader_data["intensity"]["metadata"]
        return not (metadata == {}) and app.acquire_read_mode == "read"


class ReaderPopup(QWidget):
    def __init__(self, window):
        super().__init__()
        self.app = window
        self.widgets = {}
        self.layouts = {}
        self.channels_checkboxes = []
        self.channels_checkbox_first_toggle = True
        self.setWindowTitle("Read data")
        TitlebarIcon.setup(self)
        GUIStyles.customize_theme(self, bg=QColor(20, 20, 20))
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # PLOT BUTTON ROW
        plot_btn_row = self.create_plot_btn_layout()
        # LOAD FILE ROW
        load_file_row = self.init_file_load_ui()
        self.layout.addSpacing(10)
        self.layout.insertLayout(1, load_file_row)
        # LOAD CHANNELS GRID
        self.layout.addSpacing(20)
        channels_layout = self.init_channels_layout()
        if channels_layout is not None:
            self.layout.insertLayout(2, channels_layout)
        self.layout.addSpacing(20)
        self.layout.insertLayout(3, plot_btn_row)
        self.setLayout(self.layout)
        self.setStyleSheet(GUIStyles.plots_config_popup_style())
        self.app.widgets[READER_POPUP] = self
        self.center_window()

    def init_file_load_ui(self):
        v_box = QVBoxLayout()
        files = self.app.reader_data["intensity"]["files"]
        for file_type, file_path in files.items():
            input_desc = QLabel(f"LOAD AN INTENSITY TRACING FILE:")
            input_desc.setStyleSheet("font-size: 16px; font-family: 'Montserrat'")
            control_row = QHBoxLayout()
            file_extension = ".bin"

            def on_change(file_type=file_type):
                def callback(text):
                    self.on_loaded_file_change(text, file_type)

                return callback

            _, input = InputTextControl.setup(
                label="",
                placeholder=f"Load {file_extension} file",
                event_callback=on_change(),
                text=file_path,
            )
            input.setStyleSheet(GUIStyles.set_input_text_style())
            widget_key = f"load_{file_type}_input"
            self.widgets[widget_key] = input
            load_file_btn = QPushButton()
            load_file_btn.setIcon(QIcon(resource_path("assets/folder-white.png")))
            load_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            GUIStyles.set_start_btn_style(load_file_btn)
            load_file_btn.setFixedHeight(36)
            load_file_btn.clicked.connect(partial(self.on_load_file_btn_clicked))
            control_row.addWidget(input)
            control_row.addWidget(load_file_btn)
            v_box.addWidget(input_desc)
            v_box.addSpacing(10)
            v_box.addLayout(control_row)
            v_box.addSpacing(10)
        return v_box

    def init_channels_layout(self):
        self.channels_checkboxes.clear()
        file_metadata = self.app.reader_data["intensity"]["metadata"]
        plots_to_show = self.app.reader_data["intensity"]["plots"]
        if "channels" in file_metadata and file_metadata["channels"] is not None:
            selected_channels = file_metadata["channels"]
            selected_channels.sort()
            self.app.enabled_channels = selected_channels
            for i, ch in enumerate(self.app.channels_checkboxes):
                ch.set_checked(i in self.app.enabled_channels)
            self.app.settings.setValue(
                SETTINGS_ENABLED_CHANNELS, json.dumps(self.app.enabled_channels)
            )
            if len(plots_to_show) == 0:
                plots_to_show = selected_channels[:2]
            self.app.intensity_plots_to_show = plots_to_show
            self.app.settings.setValue(
                SETTINGS_INTENSITY_PLOTS_TO_SHOW, json.dumps(plots_to_show)
            )
            channels_layout = QVBoxLayout()
            desc = QLabel("CHOOSE MAX 4 PLOTS TO DISPLAY:")
            desc.setStyleSheet("font-size: 16px; font-family: 'Montserrat'")
            grid = QGridLayout()
            # Get channel_names from file metadata
            channel_names_from_file = file_metadata.get("channel_names", {})
            for ch in selected_channels:
                channel_display_name = get_channel_name(ch, channel_names_from_file)
                checkbox, checkbox_wrapper = self.set_checkboxes(channel_display_name)
                isChecked = ch in plots_to_show
                checkbox.setChecked(isChecked)
                if len(plots_to_show) >= 4 and ch not in plots_to_show:
                    checkbox.setEnabled(False)
                grid.addWidget(checkbox_wrapper)
            channels_layout.addWidget(desc)
            channels_layout.addSpacing(10)
            channels_layout.addLayout(grid)
            self.layouts["ch_layout"] = channels_layout
            return channels_layout
        else:
            return None

    def create_plot_btn_layout(self):
        row_btn = QHBoxLayout()
        # PLOT BTN
        plot_btn = QPushButton("")
        plot_btn.setText("PLOT DATA")
        plot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plot_btn.setObjectName("btn")
        GUIStyles.set_stop_btn_style(plot_btn)
        plot_btn.setFixedHeight(40)
        plot_btn.setFixedWidth(150)
        plots_to_show = self.app.reader_data["intensity"]["plots"]
        plot_btn.setEnabled(len(plots_to_show) > 0)
        plot_btn.clicked.connect(self.on_plot_data_btn_clicked)
        self.widgets["plot_btn"] = plot_btn
        row_btn.addStretch(1)
        row_btn.addWidget(plot_btn)
        return row_btn

    def remove_channels_grid(self):
        if "ch_layout" in self.layouts:
            clear_layout(self.layouts["ch_layout"])
            del self.layouts["ch_layout"]

    def set_checkboxes(self, text):
        checkbox_wrapper = QWidget()
        checkbox_wrapper.setObjectName(f"simple_checkbox_wrapper")
        row = QHBoxLayout()
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet(GUIStyles.set_simple_checkbox_style(color="#8d4ef2"))
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.toggled.connect(
            lambda state, checkbox=checkbox: self.on_channel_toggled(state, checkbox)
        )
        row.addWidget(checkbox)
        checkbox_wrapper.setLayout(row)
        checkbox_wrapper.setStyleSheet(GUIStyles.checkbox_wrapper_style())
        return checkbox, checkbox_wrapper

    def on_channel_toggled(self, state, checkbox):
        label_text = checkbox.text()
        ch_index = extract_channel_from_label(label_text)
        if state:
            if ch_index not in self.app.intensity_plots_to_show:
                self.app.intensity_plots_to_show.append(ch_index)
        else:
            if ch_index in self.app.intensity_plots_to_show:
                self.app.intensity_plots_to_show.remove(ch_index)
        self.app.intensity_plots_to_show.sort()
        self.app.settings.setValue(
            SETTINGS_INTENSITY_PLOTS_TO_SHOW,
            json.dumps(self.app.intensity_plots_to_show),
        )
        self.app.reader_data["intensity"]["plots"] = self.app.intensity_plots_to_show
        if len(self.app.intensity_plots_to_show) >= 4:
            for checkbox in self.channels_checkboxes:
                if checkbox.text() != label_text and not checkbox.isChecked():
                    checkbox.setEnabled(False)
        else:
            for checkbox in self.channels_checkboxes:
                checkbox.setEnabled(True)
        if "plot_btn" in self.widgets:
            plot_btn_enabled = len(self.app.intensity_plots_to_show) > 0
            self.widgets["plot_btn"].setEnabled(plot_btn_enabled)
        from gui_components.buttons import ButtonsActionsController

        ButtonsActionsController.clear_plots(self.app)

    def on_loaded_file_change(self, text, file_type="intensity"):
        if text != self.app.reader_data["intensity"]["files"][file_type]:
            from gui_components.buttons import ButtonsActionsController

            ButtonsActionsController.clear_plots(self.app)
        self.app.reader_data["intensity"]["files"][file_type] = text

    @classmethod
    def handle_bin_file_result_ui(cls, instance):
        app = instance.app
        app.loading_overlay.toggle_overlay()
        file_name = app.reader_data["intensity"]["files"]["intensity"]
        if file_name is not None and len(file_name) > 0:
            bin_metadata_btn_visible = ReadDataControls.read_bin_metadata_enabled(app)
            app.control_inputs[BIN_METADATA_BUTTON].setVisible(bin_metadata_btn_visible)
            app.control_inputs[EXPORT_PLOT_IMG_BUTTON].setVisible(
                bin_metadata_btn_visible
            )
            widget_key = "load_intensity_input"
            instance.widgets[widget_key].setText(file_name)
            instance.remove_channels_grid()
            channels_layout = instance.init_channels_layout()
            if channels_layout is not None:
                instance.layout.insertLayout(2, channels_layout)

    def on_load_file_btn_clicked(self):
        ReadData.read_bin_data(self, self.app)

    def on_plot_data_btn_clicked(self):
        from gui_components.buttons import ButtonsActionsController

        ButtonsActionsController.intensity_tracing_start(self.app, read_data=True)
        ReadData.plot_intensity_data(self.app)
        self.close()

    def center_window(self):
        self.setMinimumWidth(500)
        window_geometry = self.frameGeometry()
        screen_geometry = QApplication.primaryScreen().availableGeometry().center()
        window_geometry.moveCenter(screen_geometry)
        self.move(window_geometry.topLeft())



class ReaderMetadataPopup(QWidget):
    def __init__(self, window):
        super().__init__()
        self.app = window
        self.setWindowTitle(f"INTENSITY TRACING file metadata")
        TitlebarIcon.setup(self)
        GUIStyles.customize_theme(self, bg=QColor(20, 20, 20))
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # METADATA TABLE
        self.metadata_table = self.create_metadata_table()
        layout.addSpacing(10)
        layout.addLayout(self.metadata_table)
        layout.addSpacing(10)
        self.setLayout(layout)
        self.setStyleSheet(GUIStyles.plots_config_popup_style())
        self.app.widgets[READER_METADATA_POPUP] = self
        self.center_window()

    def get_metadata_keys_dict(self):
        return {
            "channels": "Enabled Channels",
            "bin_width_micros": "Bin width (μs)",
            "acquisition_time_millis": "Acquisition time (s)",
            "channel_names": "Channel Names",
        }

    def create_metadata_table(self):
        metadata_keys = self.get_metadata_keys_dict()
        metadata = self.app.reader_data["intensity"]["metadata"]
        file = self.app.reader_data["intensity"]["files"]["intensity"]
        v_box = QVBoxLayout()
        if metadata:
            title = QLabel(f"INTENSITY TRACING FILE METADATA")
            title.setStyleSheet("font-size: 16px; font-family: 'Montserrat'")

            def get_key_label_style(bg_color):
                return f"width: 200px; font-size: 14px; border: 1px solid  {bg_color}; padding: 8px; color: white; background-color: {bg_color}"

            def get_value_label_style(bg_color):
                return f"width: 500px; font-size: 14px; border: 1px solid  {bg_color}; padding: 8px; color: white"

            v_box.addWidget(title)
            v_box.addSpacing(10)
            h_box = QHBoxLayout()
            h_box.setContentsMargins(0, 0, 0, 0)
            h_box.setSpacing(0)
            key_label = QLabel("File")
            key_label.setStyleSheet(get_key_label_style("#E65100"))
            value_label = QLabel(file)
            value_label.setStyleSheet(get_value_label_style("#E65100"))
            h_box.addWidget(key_label)
            h_box.addWidget(value_label)
            v_box.addLayout(h_box)
            for key, value in metadata_keys.items():
                if key in metadata:
                    metadata_value = str(metadata[key])
                    if key == "channels":
                        # Get channel_names from metadata for display
                        channel_names_from_file = metadata.get("channel_names", {})
                        metadata_value = ", ".join(
                            [get_channel_name(ch, channel_names_from_file) for ch in metadata[key]]
                        )
                    if key == "acquisition_time_millis":
                        if metadata[key] is not None:
                            metadata_value = str(metadata[key] / 1000)
                        else:
                            metadata_value = str(metadata["last_time_s"])
                    if key == "channel_names":
                        if isinstance(metadata[key], dict) and len(metadata[key]) > 0:
                            channel_names_list = [f"{ch_id}: {ch_name}" for ch_id, ch_name in metadata[key].items()]
                            metadata_value = ", ".join(channel_names_list)
                        else:
                            metadata_value = "No custom channel names"   
                h_box = QHBoxLayout()
                h_box.setContentsMargins(0, 0, 0, 0)
                h_box.setSpacing(0)
                key_label = QLabel(value)
                value_label = QLabel(metadata_value)
                key_label.setStyleSheet(get_key_label_style("#6b3da5"))
                value_label.setStyleSheet(get_value_label_style("#6b3da5"))
                h_box.addWidget(key_label)
                h_box.addWidget(value_label)
                v_box.addLayout(h_box)
        return v_box

    def center_window(self):
        self.setMinimumWidth(500)
        window_geometry = self.frameGeometry()
        screen_geometry = QApplication.primaryScreen().availableGeometry().center()
        window_geometry.moveCenter(screen_geometry)
        self.move(window_geometry.topLeft())


class ProcessBinDataWorkerSignals(QObject):
    success = pyqtSignal(object)
    error = pyqtSignal(str)


class DataReaderWorker(QRunnable):
    def __init__(self, file_name, signals):
        super().__init__()
        self.file_name = file_name
        self.signals = signals

    def run(self):
        try:
            with open(self.file_name, "rb") as file:
                if file.read(4) != b"IT02":
                    self.signals.error.emit(
                        "The file is not a valid Intensity Tracing file"
                    )
                    return

                json_length = struct.unpack("I", file.read(4))[0]
                metadata = json.loads(file.read(json_length).decode("utf-8"))
                number_of_channels = len(metadata["channels"])
                channels_lines = [[] for _ in range(len(metadata["channels"]))]
                times = []
                
                # READING DATA WITH BITMASK
                while True:
                    time_data = file.read(8)
                    if not time_data or len(time_data) < 8:
                        break
                    (time,) = struct.unpack("d", time_data)
                    times.append(time)
                    
                    bitmask_data = file.read(1)
                    if not bitmask_data:
                        break
                    (bitmask,) = struct.unpack("B", bitmask_data)
                    
                    for bit_position in range(number_of_channels):
                        if (bitmask & (1 << bit_position)) != 0:
                            count_data = file.read(4)
                            if not count_data or len(count_data) < 4:
                                break
                            (count,) = struct.unpack("I", count_data)
                            channels_lines[bit_position].append(count)
                        else:
                            channels_lines[bit_position].append(0)
                
                # PROCESSING DATA
                # If the last bin has bitmask = 0 (all zeros), it is a marker for the acquisition time
                # and must be removed before visualization
                if times and all(channels_lines[ch][-1] == 0 for ch in range(len(channels_lines))):
                    final_time_marker = times[-1]
                    times = times[:-1]  # Remove the timestamp marker
                    for ch in range(len(channels_lines)):
                        channels_lines[ch] = channels_lines[ch][:-1]  # Remove the marker data
                else:
                    final_time_marker = None
                
                bin_width_ns = metadata["bin_width_micros"] * 1000
                
                # CALCULATE EXPECTED TIME BINS
                if metadata["acquisition_time_millis"] is not None:
                    total_time_ns = metadata["acquisition_time_millis"] * 1_000_000
                    expected_bins = int(total_time_ns / bin_width_ns)
                elif final_time_marker is not None:
                    # Use the final timestamp marker
                    expected_bins = int(final_time_marker / bin_width_ns)
                elif times:
                    # Fallback: use the last real timestamp
                    expected_bins = int(times[-1] / bin_width_ns) + 1
                else:
                    expected_bins = 0
                
                # RECONSTRUCT FULL TIME BINS
                if expected_bins > 0 and times:
                    # Find the first and last bin indices from actual data
                    first_bin_index = int(times[0] / bin_width_ns)
                    last_bin_index = int(times[-1] / bin_width_ns)
                    
                    # Reconstruct only from first to last bin with data
                    num_bins = last_bin_index - first_bin_index + 1
                    full_times = [(first_bin_index + i) * bin_width_ns for i in range(num_bins)]
                    full_channel_lines = [[0] * num_bins for _ in range(number_of_channels)]
                    
                    for i in range(len(times)):
                        time_ns = times[i]
                        bin_index = int(time_ns / bin_width_ns)
                        # Adjust index to start from 0
                        adjusted_index = bin_index - first_bin_index
                        
                        if 0 <= adjusted_index < num_bins:
                            for ch in range(number_of_channels):
                                full_channel_lines[ch][adjusted_index] = channels_lines[ch][i]
                    
                    times = full_times
                    channels_lines = full_channel_lines
                elif expected_bins == 0:
                    times = []
                    channels_lines = [[] for _ in range(number_of_channels)]
                
                self.signals.success.emit(
                    (self.file_name, times, channels_lines, metadata)
                )
        except Exception as e:
            self.signals.error.emit(f"Error reading Intensity Tracing file: {e}")


class BuildIntensityPlotWorkerSignals(QObject):
    success = pyqtSignal(object)
    error = pyqtSignal(str)


class BuildIntensityPlotTask(QRunnable):
    def __init__(self, channels_lines, times, metadata, show_plot, signals):
        super().__init__()
        self.channels_lines = channels_lines
        self.times = times
        self.metadata = metadata
        self.show_plot = show_plot
        self.signals = signals

    @pyqtSlot()
    def run(self):
        try:
            plot = plot_intensity_data(
                self.channels_lines, self.times, self.metadata, show_plot=self.show_plot
            )
            self.signals.success.emit(plot)
        except Exception as e:
            plt.close(self.plot)
            self.signals.error.emit(str(e))


class PostSavePlotImageWorkerSignals(QObject):
    success = pyqtSignal(str)
    error = pyqtSignal(str)


class SavePlotTask(QRunnable):
    def __init__(self, plot, base_path, signals):
        super().__init__()
        self.plot = plot
        self.base_path = base_path
        self.signals = signals

    @pyqtSlot()
    def run(self):
        try:
            # png
            png_path = (
                f"{self.base_path}.png"
                if not self.base_path.endswith(".png")
                else self.base_path
            )
            self.plot.savefig(png_path, format="png")
            # eps
            eps_path = (
                f"{self.base_path}.eps"
                if not self.base_path.endswith(".eps")
                else self.base_path
            )
            self.plot.savefig(eps_path, format="eps")
            plt.close(self.plot)
            self.signals.success.emit(
                f"Plot images saved successfully as {png_path} and {eps_path}"
            )
        except Exception as e:
            plt.close(self.plot)
            self.signals.error.emit(str(e))
