import os
import shutil

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from gui_components.box_message import BoxMessage
from gui_components.gui_styles import GUIStyles
from gui_components.messages_utilities import MessagesUtilities

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
            content = content_modifier['source_file']
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
        return content.replace("<FILE-PATH>", file_name.replace('\\', '/'))

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
            'source_file': """most_recent_file = '<FILE-PATH>';

file_path = fullfile(data_folder, most_recent_file);

metadata = struct('channels', [], 'bin_width_micros', [], 'acquisition_time_millis', [], 'laser_period_ns', []);

fid = fopen(file_path, 'rb');

if fid == -1
    error('Unable to open the file');
end

% First 4 bytes must be IT01
first_bytes = fread(fid, 4, 'uint8=>char')';

if ~strcmp(first_bytes, 'IT02')
    fprintf('Invalid data file');
    fclose(fid);
    return;
end

% Read json length
json_length = fread(fid, 1, 'uint32');

% Read metadata from file
json_data = fread(fid, json_length, 'char')';
json_str = char(json_data);
metadata = jsondecode(json_str);

if ~isempty(metadata.channels)
    disp(['Enabled channels: ' strjoin(arrayfun(@(ch) ['Channel ' num2str(ch + 1)], metadata.channels, 'UniformOutput', false), ', ')]);
end

if ~isempty(metadata.bin_width_micros)
    disp(['Bin width: ' num2str(metadata.bin_width_micros) ' µs']);
end

if ~isempty(metadata.acquisition_time_millis)
    disp(['Acquisition time: ' num2str(metadata.acquisition_time_millis / 1000) 's']);
end

if ~isempty(metadata.laser_period_ns)
    disp(['Laser period: ' num2str(metadata.laser_period_ns) 'ns']);
end

active_channels = metadata.channels;

number_of_channels = numel(metadata.channels);
channel_lines = cell(1, number_of_channels);

bin_width_seconds = metadata.bin_width_micros / 1e6;
times = []

while true
    data = fread(fid, 4 * number_of_channels + 8);

    if isempty(data)
        break;
    end

    time = typecast(data(1:8), 'double');
    channel_values = typecast(data(8:end), 'uint32');

    for i = 1:numel(channel_lines)
        channel_lines{i} = [channel_lines{i}, channel_values(i)];
    end

    times = [times, time / 1e9];

end


fclose(fid);

figure;
hold on;

% Plot data
for i = 1:numel(active_channels)
    plot(times, channel_lines{i}, 'LineWidth', 0.5, 'DisplayName', ['Channel ' num2str(active_channels(i) + 1)]);
end

% Set plot title with metadata information
title_str = sprintf('Bin Width: %s µs, Laser Period: %s ns',
num2str(metadata.bin_width_micros),
num2str(metadata.laser_period_ns));

if ~isempty(metadata.acquisition_time_millis)
    title_str = [title_str, sprintf(', Acquisition Time: %s s', num2str(metadata.acquisition_time_millis / 1000))];
end

title(title_str);

% Plot legend
lgd = legend('show');
set(lgd, 'Location', 'southoutside', 'Orientation', 'horizontal');

hold off;
            
            """,
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
            'source_file': """import os
import struct

import matplotlib.pyplot as plt

file_path = "<FILE-PATH>"

times = []

with open(file_path, 'rb') as f:
    # first 4 bytes must be IT01
    if f.read(4) != b'IT02':
        print("Invalid data file")
        exit(0)

    # read metadata from file
    (json_length,) = struct.unpack('I', f.read(4))
    null = None
    metadata = eval(f.read(json_length).decode("utf-8"))

    if "channels" in metadata and metadata["channels"]:
        print("Enabled channels: " + (", ".join(["Channel " + str(ch + 1) for ch in metadata["channels"]])))

    if "bin_width_micros" in metadata and metadata["bin_width_micros"] is not None:
        print("Bin width: " + str(metadata["bin_width_micros"]) + "micros")

    if "acquisition_time_millis" in metadata and metadata["acquisition_time_millis"] is not None:
        print("Acquisition time: " + str(metadata["acquisition_time_millis"] / 1000) + "s")

    if "laser_period_ns" in metadata and metadata["laser_period_ns"] is not None:
        print("Laser period: " + str(metadata["laser_period_ns"]) + "ns")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    number_of_channels = len(metadata["channels"])
    channel_values_unpack_string = 'I' * number_of_channels
    bin_width_seconds = metadata["bin_width_micros"] / 1000000

    while True:
        data = f.read(4 * number_of_channels + 8)
        if not data:
            break
        (time,) = struct.unpack('d', data[:8])
        channel_values = struct.unpack(channel_values_unpack_string, data[8:])

        for i in range(len(channel_lines)):
            channel_lines[i].append(channel_values[i])

        times.append(time / 1_000_000_000)

plt.xlabel("Time (s)")
plt.ylabel("Intensity (counts)")
plt.title("Intensity tracing")
plt.grid(True)
# background dark


for i in range(len(channel_lines)):
    channel_line = channel_lines[i]
    plt.plot(
        times,
        channel_line,
        label="Channel " + str(metadata["channels"][i] + 1),
        linewidth=0.5
    )

plt.show()

            """,
            'skip_pattern': 'def get_recent_intensity_tracing_file():',
            'end_pattern': 'times =',
            'replace_pattern': 'times =',
            'requirements': ['matplotlib']
        }
        FileUtils.export_script_file('py', content_modifier, window)
