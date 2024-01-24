% Get most recent intensity tracing .bin file from your local computer
data_folder = fullfile(getenv('USERPROFILE'), '.flim-labs', 'data');
files = dir(fullfile(data_folder, 'intensity-tracing*'));

[~, idx] = sort([files.datenum], 'descend');
most_recent_file = files(idx(1)).name;

file_path = fullfile(data_folder, most_recent_file);

metadata = struct('channels', [], 'bin_width_micros', [], 'acquisition_time_millis', [], 'laser_period_ns', []);

fid = fopen(file_path, 'rb');

if fid == -1
    error('Unable to open the file');
end

% First 4 bytes must be IT01
first_bytes = fread(fid, 4, 'uint8=>char')';

if ~strcmp(first_bytes, 'IT02')
    fprintf('Invalid data file\n');
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
