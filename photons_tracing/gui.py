import os
import sys
from threading import Thread
from time import sleep

from PyQt6.QtWidgets import QMainWindow, QApplication, QCheckBox, QWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout
from flim_labs import flim_labs
from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget


class PhotonsTracingWindow(QMainWindow):
    def __init__(self, enabled_channels: list[int], draw_frequency: int, keep_points: int):
        super(PhotonsTracingWindow, self).__init__()

        self.draw_frequency = draw_frequency
        self.keep_points = keep_points

        self.flim_thread = None
        self.charts = []
        self.setWindowTitle("Photons tracing")

        self.setBaseSize(100, 1024)

        self.layout = QVBoxLayout()
        self.connectors = []
        self.enabled_channels = enabled_channels

        self.checkboxes = self.draw_checkboxes()

        toolbar_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_button_pressed)
        self.start_button.setEnabled(True)
        toolbar_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_button_pressed)
        toolbar_layout.addWidget(self.stop_button)
        self.layout.addLayout(toolbar_layout)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def draw_checkboxes(self):
        checkboxes = []
        checkbox_layout = QHBoxLayout()

        for i in range(8):
            self.enabled_channels.sort()
            checkbox = QCheckBox("Channel " + str(i + 1))
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

    def stop_button_pressed(self, thread_join: bool = True):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        for checkbox in self.checkboxes:
            checkbox.setEnabled(True)
        QApplication.processEvents()

        flim_labs.request_stop()

        if thread_join and self.flim_thread is not None and self.flim_thread.is_alive():
            self.flim_thread.join()

        for (channel, curr_conn) in self.connectors:
            curr_conn.pause()

    def generate_chart(self, channel_index):
        left_axis = LiveAxis("left", axisPen="red", textPen="red")
        bottom_axis = LiveAxis("bottom",
                               axisPen="green",
                               textPen="green",
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
        plot_widget.addItem(plot_curve)
        connector = DataConnector(plot_curve, update_rate=self.draw_frequency, max_points=self.keep_points)

        return plot_widget, (self.enabled_channels[channel_index], connector)

    def start_button_pressed(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        for checkbox in self.checkboxes:
            checkbox.setEnabled(False)

        # remove old charts
        for i in range(len(self.charts)):
            self.layout.removeWidget(self.charts[i])
            self.charts[i].deleteLater()
            QApplication.processEvents()

        self.connectors.clear()
        self.charts.clear()

        for i in range(len(self.enabled_channels)):
            (chart, connector) = self.generate_chart(i)
            self.layout.addWidget(chart)
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
            QApplication.processEvents()
        else:
            sleep(0.000001)

    def flim_read(self):
        print("Thread: Start reading from flim queue")
        flim_labs.read_from_queue(self.process_point)
        print("Thread: End reading from flim queue")
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
