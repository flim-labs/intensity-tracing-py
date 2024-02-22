import queue
import sys
import os
import threading
import time
import json

from PyQt5.QtCore import QTimer,QPoint, Qt, QSize, QSettings

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(project_root)

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
    QMenu,
    QAction,
)
import pyqtgraph as pg
from PyQt5.QtGui import QIcon, QPixmap, QFont
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
from gui_components.gradient_text import GradientText
from messages_utilities import MessagesUtilities
from gui_components.layout_utilities import draw_layout_separator, init_ui, create_logo_overlay
from gui_components.link_widget import LinkWidget
from gui_components.box_message import BoxMessage
from settings import *
from format_utilities import FormatUtils
from file_utilities import FileUtils, MatlabScriptUtils, PythonScriptUtils
from gui_components.controls_bar import ControlsBar
from gui_components.top_bar import TopBar


class PhotonsTracingWindow(QMainWindow):
    def __init__(self, params_config=None):
        super(PhotonsTracingWindow, self).__init__()

        # Initialize settings config
        self.settings = self.init_settings()

        ##### GUI PARAMS #####
        self.firmwares = ["intensity_tracing_usb.flim", "intensity_tracing_sma.flim"]

        self.update_rates = ["LOW", "HIGH"]
        self.selected_update_rate = self.settings.value(SETTINGS_UPDATE_RATE, DEFAULT_UPDATE_RATE)

        self.conn_channels = ["USB", "SMA"]
        self.selected_conn_channel = self.settings.value(SETTINGS_CONN_CHANNEL, DEFAULT_CONN_CHANNEL)
        self.selected_firmware = self.settings.value(SETTINGS_FIRMWARE, DEFAULT_FIRMWARE)

        self.bin_width_micros = int(self.settings.value(SETTINGS_BIN_WIDTH_MICROS, DEFAULT_BIN_WIDTH_MICROS))
        self.time_span = int(self.settings.value(SETTINGS_TIME_SPAN, DEFAULT_TIME_SPAN))
        
        default_acquisition_time_millis = self.settings.value(SETTINGS_ACQUISITION_TIME_MILLIS)
        self.acquisition_time_millis = int(default_acquisition_time_millis) if default_acquisition_time_millis is not None else DEFAULT_ACQUISITION_TIME_MILLIS

        self.draw_frequency = int(self.settings.value(SETTINGS_DRAW_FREQUENCY, DEFAULT_DRAW_FREQUENCY))

        self.free_running_acquisition_time = self.settings.value(SETTINGS_FREE_RUNNING_MODE, DEFAULT_FREE_RUNNING_MODE) in ['true', True]

        default_enabled_channels = self.settings.value(SETTINGS_ENABLED_CHANNELS, DEFAULT_ENABLED_CHANNELS)
        self.enabled_channels = json.loads(default_enabled_channels) if default_enabled_channels is not None else []

        self.show_cps = self.settings.value(SETTINGS_SHOW_CPS, DEFAULT_SHOW_CPS) in ['true', True]

        self.write_data = self.settings.value(SETTINGS_WRITE_DATA, DEFAULT_WRITE_DATA) in ['true', True]
        self.acquisition_stopped = False


        self.charts = []
        self.cps = []
        self.connectors = []
        self.control_inputs = {}

        self.channel_checkbox_layout = QGridLayout()
        self.top_utilities_layout = QVBoxLayout()
        self.channels_checkboxes = []
        self.blank_space = QWidget()
        
        self.bin_file_size = ''
        self.bin_file_size_label = QLabel("")
      
        
        self.pull_from_queue_timer = QTimer()
        self.pull_from_queue_timer.timeout.connect(self.pull_from_queue)

        self.realtime_queue_thread = None
        self.realtime_queue_worker_stop = False

        self.realtime_queue = queue.Queue()
        
        self.init_ui() 
        
    
    @staticmethod 
    def init_settings():
        settings = QSettings('settings.ini', QSettings.Format.IniFormat)
        return settings


    def init_ui(self):
        self.create_top_utilities_layout()
        main_layout, logo_overlay, charts_grid = init_ui(self, self.top_utilities_layout) 
        self.main_layout = main_layout
        self.logo_overlay = logo_overlay
        self.charts_grid = charts_grid


    def create_top_utilities_layout(self):    
        self.top_utilities_layout = QVBoxLayout()
        header_layout = self.create_header_layout() 
        self.top_utilities_layout.addLayout(header_layout)
        
        channel_checkbox_layout = self.create_channels_controls_layout()
        self.channel_checkbox_layout = channel_checkbox_layout
        
        controls_layout = self.create_controls_layout()
        self.top_utilities_layout.addLayout(controls_layout)
        
        self.top_utilities_layout.addWidget(self.blank_space)
     

    def create_header_layout(self): 
        title_row = self.create_logo_and_title()
        info_link_widget, export_data_control = self.create_export_data_input()
        file_size_info_layout = self.create_file_size_info_row()
        download_button, download_menu = self.create_download_files_menu()
        header_layout = TopBar.create_header_layout(
            title_row,
            file_size_info_layout,
            info_link_widget,
            export_data_control,
            download_button,
            download_menu
        )
        return header_layout


    def create_export_data_input(self): 
        info_link_widget, export_data_control, inp = TopBar.create_export_data_input(self.write_data, self.toggle_export_data)
        self.control_inputs[SETTINGS_WRITE_DATA] = inp  
        return info_link_widget, export_data_control


    def create_file_size_info_row(self):
        file_size_info_layout = TopBar.create_file_size_info_row(
            self.bin_file_size, 
            self.bin_file_size_label, 
            self.write_data, 
            self.calc_exported_file_size)     
        return file_size_info_layout    


    def create_download_files_menu(self):
        download_button, download_menu = TopBar.create_download_files_menu(
            self,
            self.write_data,
            self.acquisition_stopped,
            self.show_download_options,
            self.download_matlab,
            self.download_python
        )
        self.control_inputs[DOWNLOAD_BUTTON] = download_button
        self.control_inputs[DOWNLOAD_MENU] = download_menu
        self.set_download_button_icon() 
        
        return download_button, download_menu
        
 
    def create_channels_controls_layout(self):    
        channel_checkbox_layout = QGridLayout()
        self.channel_checkbox_layout = channel_checkbox_layout
        self.channels_checkboxes = self.draw_checkboxes()
        return channel_checkbox_layout


    def create_controls_layout(self): 
        controls_row = self.create_controls() 
        buttons_row_layout = self.create_buttons()  
        blank_space, controls_layout = ControlsBar.init_gui_controls_layout(controls_row, buttons_row_layout)
        self.blank_space = blank_space
        return controls_layout


    def create_controls(self):    
        controls_row = QHBoxLayout()
        self.create_channel_type_control(controls_row)
        self.create_bin_width_control(controls_row)
        self.create_update_rate_control(controls_row)
        running_mode_control = self.create_running_mode_control()
        controls_row.addLayout(running_mode_control)
        controls_row.addSpacing(15)
        self.create_time_span_control(controls_row)
        self.create_acquisition_time_control(controls_row)
        return controls_row


    def create_buttons(self):
        show_cps_control =  self.create_show_cps_control()  

        buttons_row_layout, start_button, stop_button, reset_button = ControlsBar.create_buttons(
            show_cps_control,
            self.start_button_pressed,
            self.stop_button_pressed,
            self.reset_button_pressed,
            self.channels_checkboxes
        )
        self.control_inputs[START_BUTTON] = start_button
        self.control_inputs[STOP_BUTTON] = stop_button
        self.control_inputs[RESET_BUTTON] = reset_button
        return buttons_row_layout


    def create_channel_type_control(self, controls_row): 
        inp = ControlsBar.create_channel_type_control(
            controls_row, 
            self.selected_conn_channel, 
            self.conn_channel_type_value_change, 
            self.conn_channels)
        self.control_inputs[SETTINGS_CONN_CHANNEL] = inp   
        

    def create_bin_width_control(self, controls_row):
        inp = ControlsBar.create_bin_width_control(
            controls_row, 
            self.bin_width_micros, 
            self.bin_width_micros_value_change,)
        self.control_inputs[SETTINGS_BIN_WIDTH_MICROS] = inp    


    def create_update_rate_control(self, controls_row): 
        inp = ControlsBar.create_update_rate_control(
            controls_row, 
            self.selected_update_rate, 
            self.update_rate_value_change,
            self.update_rates
            )
        self.control_inputs[SETTINGS_UPDATE_RATE] = inp    


    def create_running_mode_control(self):
        running_mode_control, inp  = ControlsBar.create_running_mode_control(
            self.free_running_acquisition_time, 
            self.toggle_acquisition_time_mode,
            )
        self.control_inputs[SETTINGS_FREE_RUNNING_MODE] = inp    
        return running_mode_control

      
    def create_time_span_control(self, controls_row):
        inp = ControlsBar.create_time_span_control(
            controls_row, 
            self.time_span, 
            self.time_span_value_change,)
        self.control_inputs[SETTINGS_TIME_SPAN] = inp    
       

    def create_acquisition_time_control(self, controls_row):
        inp = ControlsBar.create_acquisition_time_control(
            controls_row, 
            self.acquisition_time_millis, 
            self.acquisition_time_value_change,
            self.control_inputs[SETTINGS_FREE_RUNNING_MODE]
            )
        self.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS] = inp    


    def create_show_cps_control(self):
        show_cps_control, inp = ControlsBar.create_show_cps_control(
            self.show_cps, 
            self.toggle_show_cps,
            )
        self.control_inputs[SETTINGS_SHOW_CPS] = inp    
        return show_cps_control
    

    def create_logo_and_title(self):  
        title_row = TopBar.create_logo_and_title(self) 
        return title_row   

    def draw_checkboxes(self):
        channels_checkboxes = []
        for i in range(8):
            self.enabled_channels.sort()
            checkbox = QCheckBox("Channel " + str(i + 1))
            checkbox.setStyleSheet(GUIStyles.set_checkbox_style())
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
            if i not in self.enabled_channels:
                checkbox.setChecked(False)
            else:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, index=i: self.toggle_channels_checkbox(state, index)
            )
            channels_checkboxes.append(checkbox)
        self.top_utilities_layout.addLayout(self.channel_checkbox_layout)
        self.update_checkbox_layout(channels_checkboxes)
        return channels_checkboxes

    def toggle_channels_checkbox(self, state, index):
        if state:
            self.enabled_channels.append(index)
        else:
            self.enabled_channels.remove(index)
        self.enabled_channels.sort()
        #print("Enabled channels: " + str(self.enabled_channels))
        self.calc_exported_file_size()
        self.settings.setValue(SETTINGS_ENABLED_CHANNELS, json.dumps(self.enabled_channels))
        self.control_inputs[START_BUTTON].setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )

    def toggle_acquisition_time_mode(self, state):
        if state:
            self.acquisition_time_millis = None
            self.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(False)
            self.free_running_acquisition_time = True
            self.settings.setValue(SETTINGS_FREE_RUNNING_MODE, True)
        else:
            self.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS].setEnabled(True)
            self.free_running_acquisition_time = False
            self.settings.setValue(SETTINGS_FREE_RUNNING_MODE, False)
        self.calc_exported_file_size()    

    def toggle_show_cps(self, state):
        if state:
            self.show_cps = True
            self.settings.setValue(SETTINGS_SHOW_CPS, True)
        else:
            self.show_cps = False
            self.settings.setValue(SETTINGS_SHOW_CPS, False)

    def toggle_export_data(self, state):
        if state:
            self.write_data = True
            self.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.write_data and self.acquisition_stopped)
            self.set_download_button_icon()
            self.settings.setValue(SETTINGS_WRITE_DATA, True)
            self.bin_file_size_label.show()
            self.calc_exported_file_size()
        else:
            self.write_data = False
            self.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.write_data and self.acquisition_stopped)
            self.set_download_button_icon()
            self.settings.setValue(SETTINGS_WRITE_DATA, False)
            self.bin_file_size_label.hide()

    def conn_channel_type_value_change(self, index):
        self.selected_conn_channel = self.sender().currentText()
        if self.selected_conn_channel == "USB":
            self.selected_firmware = self.firmwares[0]
        else:
            self.selected_firmware = self.firmwares[1]   
        self.settings.setValue(SETTINGS_FIRMWARE, self.selected_firmware) 
        self.settings.setValue(SETTINGS_CONN_CHANNEL, self.selected_conn_channel)     

    def acquisition_time_value_change(self, value):
        self.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.acquisition_time_millis = value * 1000  # convert s to ms
        self.settings.setValue(SETTINGS_ACQUISITION_TIME_MILLIS, self.acquisition_time_millis)
        self.calc_exported_file_size()

    def time_span_value_change(self, value):
        self.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.time_span = value
        self.settings.setValue(SETTINGS_TIME_SPAN, value)

    def bin_width_micros_value_change(self, value):
        self.control_inputs[START_BUTTON].setEnabled(value != 0)
        self.bin_width_micros = value
        self.settings.setValue(SETTINGS_BIN_WIDTH_MICROS, value)
        self.calc_exported_file_size()

    def update_rate_value_change(self, index):
        self.selected_update_rate = self.sender().currentText()
        self.draw_frequency = 10 if self.selected_update_rate == 'LOW' else 40
        self.settings.setValue(SETTINGS_UPDATE_RATE, self.selected_update_rate)
        self.settings.setValue(SETTINGS_DRAW_FREQUENCY, self.draw_frequency)

    def start_button_pressed(self):
        self.acquisition_stopped=False
        self.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.write_data and self.acquisition_stopped)
        self.set_download_button_icon()
        warn_title, warn_msg = MessagesUtilities.invalid_inputs_handler(
            self.bin_width_micros,
            self.time_span,
            self.acquisition_time_millis,
            self.control_inputs[SETTINGS_FREE_RUNNING_MODE],
            self.enabled_channels,
            self.selected_conn_channel,
            self.selected_update_rate,
        )
        if warn_title and warn_msg:
            BoxMessage.setup(
                warn_title, warn_msg, QMessageBox.Warning, GUIStyles.set_msg_box_style()
            )
            return
        self.control_inputs[START_BUTTON].setEnabled(False)
        self.control_inputs[STOP_BUTTON].setEnabled(True)
        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(False)
            checkbox.setCursor(Qt.CursorShape.ArrowCursor)


        for chart in self.charts:
            chart.setVisible(False)

        for channel, curr_conn in self.connectors:
            curr_conn.disconnect()

        self.connectors.clear()
        self.charts.clear()
        self.cps.clear()

        for i in range(len(self.enabled_channels)):
            if i < len(self.charts):
                self.charts[i].show()
            else:
                (chart, connector, cps) = self.generate_chart(i)
                row, col = divmod(i, 2)
                self.charts_grid.addWidget(chart, row, col)
                self.charts.append(chart)
                self.cps.append(cps)
                self.connectors.append(connector)

        QApplication.processEvents()
        self.start_photons_tracing()

    def stop_button_pressed(self):
        self.acquisition_stopped = True
        self.control_inputs[DOWNLOAD_BUTTON].setEnabled(self.write_data and self.acquisition_stopped)
        self.set_download_button_icon()
        self.control_inputs[START_BUTTON].setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )
        self.control_inputs[STOP_BUTTON].setEnabled(False)
        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(True)
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        QApplication.processEvents()

        flim_labs.request_stop()

        self.realtime_queue.queue.clear()
        self.realtime_queue_worker_stop = True
        if self.realtime_queue_thread is not None:
            self.realtime_queue_thread.join()
        self.pull_from_queue_timer.stop()

        for channel, curr_conn in self.connectors:
            curr_conn.pause()


    def reset_button_pressed(self):
        flim_labs.request_stop()
        self.blank_space.show()

        self.control_inputs[DOWNLOAD_BUTTON].setEnabled(False)
       
        self.control_inputs[START_BUTTON].setEnabled(
            not all(not checkbox.isChecked() for checkbox in self.channels_checkboxes)
        )
        self.control_inputs[STOP_BUTTON].setEnabled(False)
        for checkbox in self.channels_checkboxes:
            checkbox.setEnabled(True)
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)

        for chart in self.charts:
            self.charts_grid.removeWidget(chart)
            chart.deleteLater()

        self.connectors.clear()
        self.charts.clear()
        QApplication.processEvents()


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
            y_label="AVG. Photon counts",
            orientation='vertical',
            axisItems={"bottom": bottom_axis, "left": left_axis},
            x_range_controller=LiveAxisRange(roll_on_tick=1),
        )

        plot_widget.getAxis('left').setLabel('AVG. Photon counts', color='#FFA726', orientation='vertical')


        plot_curve = LiveLinePlot()
        plot_curve.setPen(pg.mkPen(color="#a877f7"))
        plot_widget.addItem(plot_curve)

        self.time_span = self.control_inputs[SETTINGS_TIME_SPAN].value()
        connector = DataConnector(
            plot_curve,
            update_rate=REALTIME_HZ,
            max_points=int(REALTIME_HZ / 2) * self.time_span,
            plot_rate=REALTIME_HZ,
        )

        # plot_widget.showGrid(x=True, y=True, alpha=0.5)
        plot_widget.setBackground(None)

        # cps indicator
        cps_label = QLabel("0 CPS", plot_widget)
        cps_label.setFixedWidth(200)
        cps_label.setStyleSheet(GUIStyles.set_cps_label_style())
        cps_label.move(60, 5)

        if not self.show_cps:
            cps_label.hide()
        return plot_widget, (self.enabled_channels[channel_index], connector), cps_label

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
            self.channel_checkbox_layout.addWidget(checkbox, row, col)

    def resizeEvent(self, event):
        super(PhotonsTracingWindow, self).resizeEvent(event)
        self.logo_overlay.update_position(self)
        self.logo_overlay.update_visibility(self)
        self.update_checkbox_layout(self.channels_checkboxes)

    def calc_exported_file_size(self):
        if  self.free_running_acquisition_time is True or self.acquisition_time_millis is None:
            self.bin_file_size = 'XXXMB' 
        else:
            file_size_MB = int((self.acquisition_time_millis / 1000) * len(self.enabled_channels) * (self.bin_width_micros / 1000))
            self.bin_file_size = FormatUtils.format_size(file_size_MB * 1024 * 1024) 
            
        self.bin_file_size_label.setText("File size: " + str(self.bin_file_size))        


    def pull_from_queue(self):
        val = flim_labs.pull_from_queue()
        if len(val) > 0:
            for v in val:
                if v == ('end',):  # End of acquisition
                    self.stop_button_pressed()
                    self.control_inputs[START_BUTTON].setEnabled(True)
                    self.control_inputs[STOP_BUTTON].setEnabled(False)
                    break
                ((current_time,), (ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8)) = v
                counts = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]
                self.realtime_queue.put((current_time, counts))

    def realtime_queue_worker(self):
        cps_counts = [0] * 8
        next_second = 1
        while self.realtime_queue_worker_stop is False:
            try:
                (current_time_ns, counts) = self.realtime_queue.get(timeout=REALTIME_MS / 1000)
            except queue.Empty:
                continue
            adjustment = REALTIME_ADJUSTMENT / self.bin_width_micros
            seconds = current_time_ns / NS_IN_S
            for channel, curr_conn in self.connectors:
                curr_conn.cb_append_data_point(y=(counts[channel] / adjustment), x=seconds)
                cps_counts[channel] += counts[channel] / adjustment
                if seconds >= next_second:
                    self.cps[channel].setText(FormatUtils.format_cps(round(cps_counts[channel])) + " CPS")
                    cps_counts[channel] = 0
            if seconds >= next_second:
                next_second += 1

            QApplication.processEvents()
            time.sleep(REALTIME_SECS / 2)
        else:
            print("Realtime queue worker stopped")
            self.realtime_queue.queue.clear()
            self.realtime_queue_worker_stop = False

    def start_photons_tracing(self):
        try:
            acquisition_time_millis = (
                None
                if self.acquisition_time_millis in (0, None)
                else self.acquisition_time_millis
            )
            print("Selected firmware: " + (str(self.selected_firmware)))
            print("Free running enabled: " + str(self.control_inputs[SETTINGS_FREE_RUNNING_MODE].isChecked()))
            print("Acquisition time (ms): " + str(acquisition_time_millis))
            print("Time span (s): " + str(self.time_span))
            print("Max points: " + str(40 * self.time_span))
            print("Bin width (µs): " + str(self.bin_width_micros))
            output_frequency_ms = 100 if self.selected_update_rate == 'LOW' else 25
            print("Output frequency ms: " + str(output_frequency_ms))

            result = flim_labs.start_intensity_tracing(
                enabled_channels=self.enabled_channels,
                bin_width_micros=self.bin_width_micros,  # E.g. 1000 = 1ms bin width
                write_bin=False,  # True = Write raw output from card in a binary file
                write_data=self.write_data,  # True = Write data in a binary file
                acquisition_time_millis=acquisition_time_millis,  # E.g. 10000 = Stops after 10 seconds of acquisition
                firmware_file=self.selected_firmware,
                # String, if None let flim decide to use intensity tracing Firmware
                output_frequency_ms=output_frequency_ms  # Based on Update Rate (100=LOW, 25=HIGH)
            )

            self.realtime_queue_worker_stop = False
            self.realtime_queue_thread = threading.Thread(target=self.realtime_queue_worker)
            self.realtime_queue_thread.start()

            file_bin = result.bin_file
            if file_bin != "":
                print("File bin written in: " + str(file_bin))

            self.blank_space.hide()

            self.pull_from_queue_timer.start(1)

        except Exception as e:
            error_title, error_msg = MessagesUtilities.error_handler(str(e))
            BoxMessage.setup(
                error_title,
                error_msg,
                QMessageBox.Critical,
                GUIStyles.set_msg_box_style(),
            )

    def show_download_options(self):    
      self.control_inputs[DOWNLOAD_MENU].exec_(
        self.control_inputs[DOWNLOAD_BUTTON].mapToGlobal(QPoint(0, self.control_inputs[DOWNLOAD_BUTTON].height()))
        )

    def download_matlab(self):
       MatlabScriptUtils.download_matlab(self)
       self.control_inputs[DOWNLOAD_BUTTON].setEnabled(False)
       self.control_inputs[DOWNLOAD_BUTTON].setEnabled(True)

    def download_python(self):
       PythonScriptUtils.download_python(self)
       self.control_inputs[DOWNLOAD_BUTTON].setEnabled(False)
       self.control_inputs[DOWNLOAD_BUTTON].setEnabled(True)

    def set_download_button_icon(self):
        if self.control_inputs[DOWNLOAD_BUTTON].isEnabled():
            icon = os.path.join(project_root, "assets", "arrow-down-icon-white.png")
            self.control_inputs[DOWNLOAD_BUTTON].setIcon(QIcon(icon))
        else:
            icon = os.path.join(project_root, "assets", "arrow-down-icon-grey.png")
            self.control_inputs[DOWNLOAD_BUTTON].setIcon(QIcon(icon))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PhotonsTracingWindow()
    window.show()
    exit_code = app.exec()
    window.stop_button_pressed()
    sys.exit(exit_code)