import sys
from threading import Thread
from time import sleep
from PyQt6.QtWidgets import QMainWindow, QApplication, QCheckBox, QWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QGridLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from flim_labs import flim_labs
from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget
from gui_styles import GUIStyles, LogoOverlay
import pyqtgraph as pg




class PhotonsTracingWindow(QMainWindow):
    def __init__(self, enabled_channels, draw_frequency, keep_points):
        super(PhotonsTracingWindow, self).__init__()

        self.draw_frequency = draw_frequency
        self.keep_points = keep_points

        self.flim_thread = None
        self.terminate_thread = False
        self.charts = []
        
        GUIStyles.customize_theme(self)
        GUIStyles.set_fonts()
        self.setWindowTitle("Intensity tracing")

        self.setBaseSize(100, 1024)
        self.resize(800, 400)

        self.layout = QVBoxLayout()

        self.connectors = []
        self.enabled_channels = enabled_channels

        self.checkboxes = self.draw_checkboxes()

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch(1)
      
        self.start_button = QPushButton("START")
        GUIStyles.set_start_btn_style(self.start_button)
        self.start_button.clicked.connect(self.start_button_pressed)
        self.start_button.setEnabled(not all(not checkbox.isChecked() for checkbox in self.checkboxes))
        
        toolbar_layout.addWidget(self.start_button)
      

        self.stop_button = QPushButton("STOP")
        GUIStyles.set_stop_btn_style(self.stop_button)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_button_pressed)
        toolbar_layout.addWidget(self.stop_button)
        
        self.reset_button = QPushButton("RESET")
        GUIStyles.set_reset_btn_style(self.reset_button)
        self.reset_button.setEnabled(True)
        self.reset_button.clicked.connect(self.reset_button_pressed)
        toolbar_layout.addWidget(self.reset_button)


        self.layout.addLayout(toolbar_layout)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.charts_grid = QGridLayout()
        self.layout.addLayout(self.charts_grid)

        # Logo overlay
        self.logo_overlay = LogoOverlay(self)
        self.logo_overlay.show()
        self.logo_overlay.update_visibility(self)
        self.logo_overlay.update_position(self.logo_overlay)
        self.logo_overlay.lower()

        # Titlebar logo icon
        self.guibar_icon = "flimlabs-icon.png"
        self.setWindowIcon(QIcon(self.guibar_icon))


    def draw_checkboxes(self):
        checkboxes = []
        checkbox_layout = QHBoxLayout()

        for i in range(8):
            self.enabled_channels.sort()
            checkbox = QCheckBox("Channel " + str(i + 1))
            checkbox.setStyleSheet(GUIStyles.set_checkbox_style())
            if i not in self.enabled_channels:
                checkbox.setChecked(False)
            else:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, index=i: self.toggle_checkbox(state, index))
            checkbox_layout.addWidget(checkbox)
            checkboxes.append(checkbox)

        self.layout.addLayout(checkbox_layout)
        return checkboxes



    def toggle_checkbox(self, state, index):
        if state:
            self.enabled_channels.append(index)
        else:
            self.enabled_channels.remove(index)
        self.enabled_channels.sort()
        print("Enabled channels: " + str(self.enabled_channels))
        self.start_button.setEnabled(not all(not checkbox.isChecked() for checkbox in self.checkboxes))



    def stop_button_pressed(self, thread_join=True):
        self.start_button.setEnabled(not all(not checkbox.isChecked() for checkbox in self.checkboxes))
        self.stop_button.setEnabled(False)
        for checkbox in self.checkboxes:
            checkbox.setEnabled(True)
        QApplication.processEvents()

        flim_labs.request_stop()

        if thread_join and self.flim_thread is not None and self.flim_thread.is_alive():
            self.flim_thread.join()

        for (channel, curr_conn) in self.connectors:
            curr_conn.pause()



    def reset_button_pressed(self): 
        self.start_button.setEnabled(not all(not checkbox.isChecked() for checkbox in self.checkboxes))
        self.stop_button.setEnabled(False)
        for checkbox in self.checkboxes:
            checkbox.setEnabled(True)
            checkbox.setChecked(False)
            
        for chart in self.charts:    
            chart.setVisible(False)
       
        QApplication.processEvents()
        
        flim_labs.request_stop()
        self.terminate_thread = True
        
        for (channel, curr_conn) in self.connectors:
            curr_conn.pause()



    def generate_chart(self, channel_index):
        left_axis = LiveAxis("left", axisPen="#cecece", textPen="#FFA726")
        bottom_axis = LiveAxis("bottom",
                               axisPen="#cecece",
                               textPen="#23F3AB",
                               tick_angle=-45,
                               **{
                                   Axis.TICK_FORMAT: Axis.DURATION,
                                   Axis.DURATION_FORMAT: Axis.DF_SHORT}
                               )

        plot_widget = LivePlotWidget(
            title="Channel " + str(self.enabled_channels[channel_index] + 1),
            y_label="Photon counts",
            axisItems={'bottom': bottom_axis, 'left': left_axis}
        )

        plot_curve = LiveLinePlot()
        plot_curve.setPen(pg.mkPen(color="#a877f7"))
        plot_widget.addItem(plot_curve)
        connector = DataConnector(plot_curve, update_rate=self.draw_frequency, max_points=self.keep_points)

        plot_widget.setBackground(None)

        return plot_widget, (self.enabled_channels[channel_index], connector)



    def resizeEvent(self, event):
        super(PhotonsTracingWindow, self).resizeEvent(event)
        self.logo_overlay.update_position(self)
        self.logo_overlay.update_visibility(self)



    def start_button_pressed(self):
        terminate_thread = False
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        for checkbox in self.checkboxes:
            checkbox.setEnabled(False)

        for chart in self.charts:
            chart.setVisible(False)

        for (channel, curr_conn) in self.connectors:
            curr_conn.disconnect()

        self.connectors.clear()
        self.charts.clear()

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



    def process_point(self, time, x, counts):
        for (channel, curr_conn) in self.connectors:
            curr_conn.cb_append_data_point(
                y=counts[channel],
                x=time / 1_000_000_000
            )
        if x % 1000 == 0:
            QTimer.singleShot(0, QApplication.processEvents)
        else:
            sleep(0.000001)



    def flim_read(self):
        print("Thread: Start reading from flim queue")
        flim_labs.read_from_queue(self.process_point)
        print("Thread: End reading from flim queue")

        if self.terminate_thread:
            return 

        self.stop_button_pressed(thread_join=False)



    def start_photons_tracing(self):
        file_bin = flim_labs.start_photons_tracing(
            enabled_channels=self.enabled_channels,
            bin_width_micros=1000,  # 1000 = 1ms bin width
            write_bin=False, # True = Write raw data from card in a binary file
            acquisition_time_millis=None,  # 10000 = Stops after 10 seconds of acquisition
            firmware_file=None,  # String, if None let flim decide to use intensity tracing Firmware
        )

        if file_bin != "":
            print("File bin written in: " + file_bin)

        self.flim_thread = Thread(target=self.flim_read)
        self.flim_thread.start()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # draw_frequency suggested range: 10-100
    # (100 requires a fast computer, 10 is suitable for most computers)
    default_draw_frequency = 100
    # keep_points suggested range: 100-1000
    # (1000 requires a fast computer, 100 is suitable for most computers)
    # depending on the draw_frequency, this will keep the last 1-10 seconds of data
    default_keep_points = 1000
    window = PhotonsTracingWindow(
        enabled_channels=[1],
        draw_frequency=default_draw_frequency,
        keep_points=default_keep_points
    )
    window.show()
    exit_code = app.exec()
    window.stop_button_pressed()
    sys.exit(exit_code)