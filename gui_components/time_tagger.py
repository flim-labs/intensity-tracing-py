from functools import partial
from PyQt6.QtCore import (
    QRunnable,
    QThreadPool,
    pyqtSignal,
    QObject,
    pyqtSlot,
    QTimer,
)
from PyQt6.QtWidgets import QMessageBox
import flim_labs
from gui_components.box_message import BoxMessage
from gui_components.data_export_controls import ExportData
from gui_components.gui_styles import GUIStyles
from gui_components.settings import TIME_TAGGER_PROGRESS_BAR


class TimeTaggerWorkerSignals(QObject):
    success = pyqtSignal()
    error = pyqtSignal(str)


class TimeTaggerProcessingTask(QRunnable):
    def __init__(self, bin_width_micros, enabled_channels, signals):
        super().__init__()
        self.bin_width_micros = bin_width_micros
        self.enabled_channels = enabled_channels
        self.signals = signals

    @pyqtSlot()
    def run(self):
        try:
            flim_labs.intensity_time_tagger(
                bin_width_micros=self.bin_width_micros,
                enabled_channels=self.enabled_channels,
            )
            self.signals.success.emit()
        except Exception as e:
            self.signals.error.emit(f"Error processing time tagger: {str(e)}")


class TimeTaggerController:
    @staticmethod
    def init_time_tagger_processing(app):
        bin_width_micros = app.bin_width_micros
        enabled_channels = app.enabled_channels
        signals = TimeTaggerWorkerSignals()
        signals.success.connect(
            lambda: TimeTaggerController.handle_success_processing(app)
        )
        signals.error.connect(
            lambda error: TimeTaggerController.show_error_message(app, error)
        )
        task = TimeTaggerProcessingTask(
            bin_width_micros, enabled_channels, signals
        )
        QThreadPool.globalInstance().start(task)

    @staticmethod
    def show_error_message(app, error):
        app.widgets[TIME_TAGGER_PROGRESS_BAR].set_visible(False)
        BoxMessage.setup(
            "Error", error, QMessageBox.Icon.Warning, GUIStyles.set_msg_box_style()
        )

    @staticmethod
    def handle_success_processing(app):
        app.widgets[TIME_TAGGER_PROGRESS_BAR].set_visible(False)
        QTimer.singleShot(
            300,
            partial(ExportData.save_intensity_data, app),
        )
