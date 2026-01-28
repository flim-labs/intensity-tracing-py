from functools import partial
import os
import shutil
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QFileDialog
from export_data_scripts.script_files_utils import ScriptFileUtils
from gui_components.file_utilities import FileUtils
from gui_components.format_utilities import FormatUtils
from gui_components.helpers import calc_timestamp
from gui_components.settings import *
from gui_components.top_bar import TopBar


class ExportDataControl(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        from gui_components.buttons import TimeTaggerWidget

        self.app = window
        self.info_link_widget, self.export_data_control = (
            self.create_export_data_input()
        )
        # self.file_size_info_layout = self.create_file_size_info_row()
        layout = QHBoxLayout()
        layout.addWidget(self.info_link_widget)
        layout.addLayout(self.export_data_control)
        self.export_data_control.addSpacing(10)
        # layout.addLayout(self.file_size_info_layout)
        # layout.addSpacing(5)
        # Time Tagger
        time_tagger = TimeTaggerWidget(self.app)
        layout.addWidget(time_tagger)
        self.setLayout(layout)

    def create_export_data_input(self):
        info_link_widget, export_data_control, inp = TopBar.create_export_data_input(
            self.app.write_data, self.toggle_export_data
        )
        self.app.control_inputs[SETTINGS_WRITE_DATA] = inp
        return info_link_widget, export_data_control

    def create_file_size_info_row(self):
        file_size_info_layout = TopBar.create_file_size_info_row(
            self.app.bin_file_size,
            self.app.bin_file_size_label,
            self.app.write_data,
            # partial(DataExportActions.calc_exported_file_size, self.app),
        )
        return file_size_info_layout

    def toggle_export_data(self, state):
        if state:
            self.app.write_data = True
            self.app.settings.setValue(SETTINGS_WRITE_DATA, True)
            # self.app.bin_file_size_label.show()
            # DataExportActions.calc_exported_file_size(self.app)
        else:
            self.app.write_data = False
            self.app.settings.setValue(SETTINGS_WRITE_DATA, False)
            self.app.bin_file_size_label.hide()
        if TIME_TAGGER_WIDGET in self.app.widgets:
            self.app.widgets[TIME_TAGGER_WIDGET].setVisible(state)


class DataExportActions:

    @staticmethod
    def placeholder_function():
        pass
    # def calc_exported_file_size(app):
    #     if len(app.enabled_channels) == 0:
    #         app.bin_file_size_label.setText("")
    #         return
    #     chunk_bytes = 8 + (4 * len(app.enabled_channels))
    #     chunk_bytes_in_us = (1000 * (chunk_bytes * 1000)) / app.bin_width_micros
    #     acquisition_time = (
    #         0 if app.acquisition_time_millis is None else app.acquisition_time_millis
    #     )
    #     if app.free_running_acquisition_time is True:
    #         file_size_bytes = int(chunk_bytes_in_us)
    #         app.bin_file_size = FormatUtils.format_size(file_size_bytes)
    #         app.bin_file_size_label.setText(
    #             "File size: " + str(app.bin_file_size) + "/s"
    #         )
    #     else:
    #         file_size_bytes = int(chunk_bytes_in_us * (acquisition_time / 1000))
    #         app.bin_file_size = FormatUtils.format_size(file_size_bytes)
    #         app.bin_file_size_label.setText("File size: " + str(app.bin_file_size))


class ExportData:

    @staticmethod
    def save_intensity_data(app):
        try:
            timestamp = calc_timestamp()
            time_tagger = app.time_tagger
            intensity_tracing_file = FileUtils.get_recent_intensity_tracing_file()
            new_intensity_file_path, save_dir, save_name = (
                ExportData.rename_and_move_file(
                    intensity_tracing_file,
                    "intensity_tracing",
                    "Save Intensity Tracing files",
                    timestamp,
                    app,
                )
            )
            if not new_intensity_file_path:
                return
            if time_tagger:
                time_tagger_file = FileUtils.get_recent_time_tagger_file()
                new_time_tagger_path = ExportData.copy_file(
                    time_tagger_file,
                    save_name,
                    save_dir,
                    "time_tagger_intensity",
                    timestamp,
                )
            new_time_tagger_path = (
                ""
                if not time_tagger or not new_time_tagger_path
                else new_time_tagger_path
            )

            file_paths = {"intensity_tracing": new_intensity_file_path}
            
            channel_names = getattr(app, 'channel_names', {})
            
            ExportData.download_scripts(
                file_paths,
                save_name,
                save_dir,
                "intensity_tracing",
                timestamp,
                time_tagger=time_tagger,
                time_tagger_file_path=new_time_tagger_path,
                channel_names=channel_names,
            )
        except Exception as e:
            ScriptFileUtils.show_error_message(e)

    @staticmethod
    def download_scripts(
        bin_file_paths,
        file_name,
        directory,
        script_type,
        timestamp,
        time_tagger=False,
        time_tagger_file_path="",
        channel_names=None,
    ):
        if channel_names is None:
            channel_names = {}
        
        file_name = FileUtils.clean_filename(file_name)
        file_name = f"{file_name}_{timestamp}"
        ScriptFileUtils.export_scripts(
            bin_file_paths,
            file_name,
            directory,
            script_type,
            time_tagger,
            time_tagger_file_path,
            channel_names,
        )

    @staticmethod
    def copy_file(
        origin_file_path,
        save_name,
        save_dir,
        file_type,
        timestamp,
        file_extension="bin",
    ):
        new_filename = f"{save_name}_{timestamp}_{file_type}"
        new_filename = f"{FileUtils.clean_filename(new_filename)}.{file_extension}"
        new_file_path = os.path.join(save_dir, new_filename)
        shutil.copyfile(origin_file_path, new_file_path)
        return new_file_path

    @staticmethod
    def rename_and_move_file(
        original_file_path,
        file_type,
        file_dialog_prompt,
        timestamp,
        app,
        file_extension="bin",
    ):
        dialog = QFileDialog()
        save_path, _ = dialog.getSaveFileName(
            app,
            file_dialog_prompt,
            "",
            "All Files (*);;Binary Files (*.bin)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if save_path:
            save_dir = os.path.dirname(save_path)
            save_name = os.path.basename(save_path)
            new_filename = f"{save_name}_{timestamp}_{file_type}"
            new_filename = f"{FileUtils.clean_filename(new_filename)}.{file_extension}"
            new_file_path = os.path.join(save_dir, new_filename)
            shutil.copyfile(original_file_path, new_file_path)
            return new_file_path, save_dir, save_name
        else:
            return None, None, None
