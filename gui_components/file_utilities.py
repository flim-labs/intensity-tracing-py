import os
import shutil

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from gui_components.box_message import BoxMessage
from gui_components.gui_styles import GUIStyles
from gui_components.messages_utilities import MessagesUtilities
from gui_components.resource_path import resource_path

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))


class FileUtils:
    @classmethod
    def export_script_file(cls, file_extension, content_modifier, window):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(None, "Save File", "", f"All Files (*.{file_extension})",
                                                   options=options)
        if not file_name:
            return
        try:
            bin_file_path = cls.get_recent_intensity_tracing_file()
            bin_file_name = os.path.join(os.path.dirname(file_name),
                                         f"{os.path.splitext(os.path.basename(file_name))[0]}.bin").replace('\\', '/')

            shutil.copy(bin_file_path, bin_file_name) if bin_file_path else None

            # write script file
            content_path=resource_path(content_modifier['source_file'])
            content= cls.read_file_content(content_path)
            new_content = cls.manipulate_file_content(content, bin_file_name)
            cls.write_file(file_name, new_content)

            # write requirements file only for python export
            if len(content_modifier['requirements']) > 0:
                requirement_path, requirements_content = cls.create_requirements_file(file_name,
                content_modifier['requirements'])
                cls.write_file(requirement_path, requirements_content)

            cls.show_success_message(file_name)
        except Exception as e:
            cls.show_error_message(str(e))

    @classmethod
    def write_file(cls, file_name, content):
        with open(file_name, 'w') as file:
            file.writelines(content)

    @classmethod
    def create_requirements_file(cls, script_file_name, requirements):
        directory = os.path.dirname(script_file_name)
        requirements_path = os.path.join(directory, 'requirements.txt')
        requirements_content = []

        for requirement in requirements:
            requirements_content.append(f"{requirement}\n")
        return [requirements_path, requirements_content]

    @classmethod
    def read_file_content(cls, file_path):
        with open(file_path, 'r') as file:
            return file.readlines()

    @classmethod
    def manipulate_file_content(cls, content, file_name):

        new_content=[]
        for line in content:
            if "<FILE-PATH>" in line:
                line=line.replace('<FILE-PATH>', f"{file_name.replace('\\', '/')}")
            new_content.append(line)        

        return new_content

    @classmethod
    def show_success_message(cls, file_name):
        info_title, info_msg = MessagesUtilities.info_handler("SavedScriptFile", file_name)
        BoxMessage.setup(
            info_title,
            info_msg,
            QMessageBox.Information,
            GUIStyles.set_msg_box_style(),
        )

    @classmethod
    def show_error_message(cls, error_message):
        error_title, error_msg = MessagesUtilities.error_handler("ErrorSavingScriptFile", error_message)
        BoxMessage.setup(
            error_title,
            error_msg,
            QMessageBox.Critical,
            GUIStyles.set_msg_box_style(),
        )

    @classmethod
    def get_recent_intensity_tracing_file(cls):
        data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
        files = [f for f in os.listdir(data_folder) if f.startswith("intensity-tracing")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True)
        return os.path.join(data_folder, files[0])


class MatlabScriptUtils(FileUtils):
    @staticmethod
    def download_matlab(window):
        content_modifier = {
            'source_file': 'assets/scripts/plot_data_file.m',
            'skip_pattern': '% Get most recent intensity tracing .bin file from your local computer',
            'end_pattern': 'metadata =',
            'replace_pattern': 'metadata =',
            'requirements': []
        }
        FileUtils.export_script_file('m', content_modifier, window)


class PythonScriptUtils(FileUtils):
    @staticmethod
    def download_python(window):
        content_modifier = {
            'source_file': 'assets/scripts/plot_data_file.py',
            'skip_pattern': 'def get_recent_intensity_tracing_file():',
            'end_pattern': 'times =',
            'replace_pattern': 'times =',
            'requirements': ['matplotlib']
        }
        FileUtils.export_script_file('py', content_modifier, window)
