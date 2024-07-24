import queue
import threading
import time
import numpy as np
import pyqtgraph as pg
from flim_labs import flim_labs
from functools import partial
from gui_components.box_message import BoxMessage
from gui_components.data_export_controls import DataExportActions
from gui_components.format_utilities import FormatUtils
from gui_components.messages_utilities import MessagesUtilities
from gui_components.gui_styles import GUIStyles
from gui_components.settings import *
from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
)
from PyQt5.QtGui import QPixmap
from gui_components.resource_path import resource_path


class IntensityTracing:
    @staticmethod
    def start_photons_tracing(app):
        try:
            free_running_mode = app.control_inputs[SETTINGS_FREE_RUNNING_MODE].isChecked()
            acquisition_time_millis = (
                None if app.acquisition_time_millis in (0, None) or
                        free_running_mode
                else app.acquisition_time_millis
            )
            print("Selected firmware: " + (str(app.selected_firmware)))
            print("Free running enabled: " + str(free_running_mode))
            print("Acquisition time (ms): " + str(acquisition_time_millis))
            print("Time span (s): " + str(app.time_span))
            print("Max points: " + str(40 * app.time_span))
            print("Bin width (µs): " + str(app.bin_width_micros))
            
            app.cached_time_span_seconds = float(app.settings.value(SETTINGS_TIME_SPAN, DEFAULT_TIME_SPAN))

            result = flim_labs.start_intensity_tracing(
                enabled_channels=app.enabled_channels,
                bin_width_micros=app.bin_width_micros, 
                write_bin=False,  
                write_data=app.write_data,  
                acquisition_time_millis=acquisition_time_millis, 
                firmware_file=app.selected_firmware,
            )

            file_bin = result.bin_file
            if file_bin != "":
                print("File bin written in: " + str(file_bin))
            app.blank_space.hide()
            app.pull_from_queue_timer.start(1)
            #app.pull_from_queue_timer2.start(1)

        except Exception as e:
            error_title, error_msg = MessagesUtilities.error_handler(str(e))
            BoxMessage.setup(
                error_title,
                error_msg,
                QMessageBox.Critical,
                GUIStyles.set_msg_box_style(),
                app.test_mode
            )

    @staticmethod
    def pull_from_queue(app):
        val = flim_labs.pull_from_queue()
        if len(val) > 0:
            for v in val:
                if v == ('end',):  # End of acquisition
                    IntensityTracing.stop_button_pressed(app)
                    break
                if app.acquisition_stopped:
                    break
                ((time_ns), (intensities)) = v
                IntensityTracing.process_data(app, time_ns[0], intensities)
                
                
    @staticmethod            
    def process_data(app, time_ns, counts):
        adjustment = REALTIME_ADJUSTMENT / app.bin_width_micros
        for channel, cps in app.cps_ch.items():
            IntensityTracing.update_cps(app, time_ns, counts, channel)
        for i, channel in enumerate(app.intensity_plots_to_show):
            intensity = counts[channel] / adjustment
            IntensityTracingPlot.update_plots2(channel, i, time_ns, intensity, app)  
            
              
    @staticmethod
    def update_cps(app, time_ns, counts, channel_index):
        if channel_index in app.cps_counts:
            cps = app.cps_counts[channel_index]
            if cps["last_time_ns"] == 0:
                cps["last_time_ns"] = time_ns
                cps["last_count"] = counts[channel_index]
                cps["current_count"] = counts[channel_index]
                return
            cps["current_count"] = cps["current_count"] + counts[channel_index]
            time_elapsed = time_ns - cps["last_time_ns"]
            if time_elapsed > 330_000_000:
                cps_value = (cps["current_count"] - cps["last_count"]) / (
                    time_elapsed / 1_000_000_000
                )
                app.cps_ch[channel_index].setText(FormatUtils.format_cps(cps_value) + " CPS")
                cps["last_time_ns"] = time_ns
                cps["last_count"] = cps["current_count"]
             
                

    @staticmethod    
    def stop_button_pressed(app):
        app.acquisition_stopped = True
        app.cps_counts.clear()
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        app.control_inputs[DOWNLOAD_BUTTON].setEnabled(app.write_data and app.acquisition_stopped)
        DataExportActions.set_download_button_icon(app)
        QApplication.processEvents()
        flim_labs.request_stop()
        app.pull_from_queue_timer.stop() 

class IntensityTracingPlot:
    
    @staticmethod
    def generate_chart(channel_index, app):
        x = np.arange(1)
        y = x * 0
        intensity_widget = pg.PlotWidget()
        intensity_widget.setLabel('left', 'AVG. Photon counts', units='')
        intensity_widget.setLabel('bottom', 'Time', units='s')
        intensity_widget.setTitle("Channel " + str(channel_index + 1))
        intensity_plot = intensity_widget.plot(x, y, pen="#23F3AB")
        intensity_widget.setStyleSheet("border: 1px solid #3b3b3b")
        intensity_widget.setBackground("#141414")
        intensity_widget.getAxis('left').setTextPen('#FFA726')
        intensity_widget.getAxis('bottom').setTextPen("#a877f7")
        
        return intensity_widget, intensity_plot  
        

    @staticmethod
    def create_cps_label():    
        # cps indicator
        cps_label = QLabel("0 CPS")
        return cps_label  

    
    
    @staticmethod        
    def update_plots2(channel_index, plots_to_show_index, time_ns, intensity, app):
        if plots_to_show_index < len(app.intensity_lines):
            intensity_line = app.intensity_lines[channel_index]
            x, y = intensity_line.getData()
            if x is None or (len(x) == 1 and x[0] == 0):
                x = np.array([time_ns / 1_000_000_000])
                y = np.array([np.sum(intensity)])
            else:
                x = np.append(x, time_ns / 1_000_000_000)
                y = np.append(y, np.sum(intensity))  
            if len(x) > 2:
                while x[-1] - x[0] > app.cached_time_span_seconds: 
                    x = x[1:]  
                    y = y[1:]
            intensity_line.setData(x, y)  
            QApplication.processEvents()
            time.sleep(0.01)         


    @staticmethod
    def create_chart_widget(app, index, channel):
           chart, connector = IntensityTracingPlot.generate_chart(app.intensity_plots_to_show[index], app)
           cps = IntensityTracingPlot.create_cps_label()
           cps.setStyleSheet(GUIStyles.set_cps_label_style())
           chart_widget = QWidget()
           chart_layout = QVBoxLayout()
           chart_layout.addWidget(cps)
           chart_layout.addWidget(chart)
           chart_widget.setLayout(chart_layout)
           cps.setVisible(app.show_cps)
           row, col = divmod(index, 2)
           app.layouts[INTENSITY_PLOTS_GRID].addWidget(chart_widget, row, col)
           app.intensity_charts.append(chart)
           app.intensity_lines[app.intensity_plots_to_show[index]] = connector
           app.intensity_charts_wrappers.append(chart_widget)
           app.cps_ch[channel] = cps
           app.cps_charts_widgets.append(cps)
         


class IntensityTracingOnlyCPS:
    @staticmethod
    def create_only_cps_widget(app, index, channel):
        only_cps_widget = QWidget()
        only_cps_widget.setObjectName("container")
        row_cps = QHBoxLayout()
        cps = IntensityTracingPlot.create_cps_label()
        cps.setObjectName("cps")
        channel_label = QLabel(f"Channel {channel + 1}")
        channel_label.setObjectName("ch")
        row_cps.addWidget(channel_label)
        arrow_icon = QLabel()
        arrow_icon.setPixmap(QPixmap(resource_path("assets/arrow-right-grey.png")).scaledToWidth(30))
        row_cps.addWidget(arrow_icon)
        row_cps.addWidget(cps)
        row_cps.addStretch(1)
        only_cps_widget.setLayout(row_cps)
        only_cps_widget.setStyleSheet(GUIStyles.only_cps_widget())
        app.cps_ch[channel] = cps
        row, col = divmod(index, 1)
        app.layouts[INTENSITY_ONLY_CPS_GRID].addWidget(only_cps_widget, row, col)
        app.only_cps_widgets.append(only_cps_widget)