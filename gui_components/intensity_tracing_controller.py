import queue
import threading
import time
import pyqtgraph as pg
from flim_labs import flim_labs
from functools import partial
from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_axis_range import LiveAxisRange
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget
from gui_components.box_message import BoxMessage
from gui_components.data_export_controls import DataExportActions
from gui_components.format_utilities import FormatUtils
from gui_components.messages_utilities import MessagesUtilities
from gui_components.gui_styles import GUIStyles
from gui_components.settings import *
from PyQt5.QtCore import QTimer
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

            result = flim_labs.start_intensity_tracing(
                enabled_channels=app.enabled_channels,
                bin_width_micros=app.bin_width_micros, 
                write_bin=False,  
                write_data=app.write_data,  
                acquisition_time_millis=acquisition_time_millis, 
                firmware_file=app.selected_firmware,
            )
            app.realtime_queue_worker_stop = False
            app.realtime_queue_thread = threading.Thread(target=partial(IntensityTracing.realtime_queue_worker, app))
            app.realtime_queue_thread.start()

            file_bin = result.bin_file
            if file_bin != "":
                print("File bin written in: " + str(file_bin))
            app.blank_space.hide()
            app.pull_from_queue_timer.start(1)
            app.last_cps_update_time.start()
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
                ((time_ns), (intensities)) = v
                #print(intensities)
                app.realtime_queue.put((time_ns[0], intensities))
                
                
    @staticmethod            
    def calculate_cps(app, time_ns, counts):
        if app.last_cps_update_time.elapsed() >= app.cps_update_interval:
            cps_counts = [0] * 8
            for channel, cps in app.cps_ch.items():
                cps_counts[channel] += counts[channel]
                #print(f"{channel} - {cps_counts[channel]}")
                app.cps_ch[channel].setText(FormatUtils.format_cps(round(cps_counts[channel])) + " CPS")
                app.last_cps_update_time.restart()
        for channel, curr_conn in app.connectors.items():
            curr_conn.cb_append_data_point(y=(counts[channel]), x=(time_ns / NS_IN_S))
        QApplication.processEvents()           

            
    @staticmethod            
    def realtime_queue_worker(app):
        while app.realtime_queue_worker_stop is False:
            try:
                (current_time_ns, counts) = app.realtime_queue.get(timeout=REALTIME_MS / 1000)
            except queue.Empty:
                continue
            IntensityTracing.calculate_cps(app, current_time_ns, counts)
            time.sleep(REALTIME_SECS / 2)
        else:
            print("Realtime queue worker stopped")
            app.realtime_queue.queue.clear()
            app.realtime_queue_worker_stop = False



    @staticmethod    
    def stop_button_pressed(app):
        app.acquisition_stopped = True
        app.last_cps_update_time.invalidate() 
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        app.control_inputs[DOWNLOAD_BUTTON].setEnabled(app.write_data and app.acquisition_stopped)
        DataExportActions.set_download_button_icon(app)
        QApplication.processEvents()
        flim_labs.request_stop()
        app.realtime_queue.queue.clear()
        app.realtime_queue_worker_stop = True
        if app.realtime_queue_thread is not None:
            app.realtime_queue_thread.join()
        app.pull_from_queue_timer.stop() 
        for channel, curr_conn in app.connectors.items():     
            curr_conn.pause()         
        
 


class IntensityTracingPlot:
    
    @staticmethod
    def generate_chart(channel_index, app):
        left_axis = LiveAxis("left", axisPen="#cecece", textPen="#FFA726")
        bottom_axis = LiveAxis(
            "bottom",
            axisPen="#cecece",
            textPen="#23F3AB",
            tick_angle=-45,
            **{Axis.TICK_FORMAT: Axis.DURATION, Axis.DURATION_FORMAT: Axis.DF_SHORT},
        )
        plot_widget = LivePlotWidget(
            title="Channel " + str(channel_index + 1),
            y_label="AVG. Photon counts",
            orientation='vertical',
            axisItems={"bottom": bottom_axis, "left": left_axis},
            x_range_controller=LiveAxisRange(roll_on_tick=1),
        )
        plot_widget.getAxis('left').setLabel('AVG. Photon counts', color='#FFA726', orientation='vertical')
        plot_curve = LiveLinePlot()
        plot_curve.setPen(pg.mkPen(color="#a877f7"))
        plot_widget.addItem(plot_curve)
        app.time_span = app.control_inputs[SETTINGS_TIME_SPAN].value()
        connector = DataConnector(
            plot_curve,
            update_rate=REALTIME_HZ,
            max_points=int(REALTIME_HZ) * app.time_span,
            plot_rate=REALTIME_HZ,
        )
        plot_widget.setBackground("#171717")
        plot_widget.setStyleSheet("border: 1px solid #3b3b3b;")
        return plot_widget, connector
    

    @staticmethod
    def create_cps_label():    
        # cps indicator
        cps_label = QLabel("0 CPS")
        return cps_label   


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
           app.connectors[app.intensity_plots_to_show[index]] = connector
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