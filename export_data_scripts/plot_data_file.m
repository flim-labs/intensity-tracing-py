file_path = "<FILE-PATH>";

% Open the file  
metadata = struct('channels', [], 'bin_width_micros', [], 'acquisition_time_millis', [], 'laser_period_ns', []);

fid = fopen(file_path, 'rb');


if fid == -1
    error('Unable to open the file');
end

%% Reading headers and metadata
% First 4 bytes must be IT02
first_bytes = fread(fid, 4, 'char')';

if ~isequal(first_bytes, 'IT02')
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
    disp(['Bin width: ' num2str(metadata.bin_width_micros) ' us']);
end

if ~isempty(metadata.acquisition_time_millis)
    disp(['Acquisition time: ' num2str(metadata.acquisition_time_millis / 1000) 's']);
end

if ~isempty(metadata.laser_period_ns)
    disp(['Laser period: ' num2str(metadata.laser_period_ns) 'ns']);
end

active_channels = metadata.channels;
number_of_channels = numel(metadata.channels);
bin_width_seconds = metadata.bin_width_micros / 1e6;

%% Main data processing
% Parameters
bytes_per_sample = 4 * number_of_channels + 8;

% Determine how much data remains
current_pos = ftell(fid);
fseek(fid, 0, 'eof');
end_pos = ftell(fid);
fseek(fid, current_pos, 'bof');
bytes_remaining = end_pos - current_pos;

% Number of complete samples
num_samples = floor(bytes_remaining / bytes_per_sample);
total_bytes = num_samples * bytes_per_sample;

% Read all remaining data
raw_data = fread(fid, total_bytes, 'uint8=>uint8');

% Reshape into [bytes_per_sample x num_samples]
raw_data = reshape(raw_data, bytes_per_sample, num_samples);

% Parse time (first 8 bytes of each sample)
time_bytes = raw_data(1:8, :);
time_vals = typecast(reshape(time_bytes, [], 1), 'double');
times = time_vals.' / 1e9;

% Parse channel values (remaining bytes of each sample)
channel_bytes = raw_data(9:end, :);
channel_vals = typecast(reshape(channel_bytes, [], 1), 'uint32');
channel_vals = reshape(channel_vals, number_of_channels, num_samples);

fclose(fid);
clear bytes_per_sample bytes_remaining channel_bytes current_pos end_pos...
    time_bytes time_vals raw_data total_bytes num_samples;
%% Plotting
figure;
hold on;

% Plot data
for i = 1:numel(active_channels)
    plot(times, channel_vals(i, :), 'LineWidth', 0.5, 'DisplayName', ['Channel ' num2str(active_channels(i) + 1)]);
end

% Set plot title with metadata information
title_str = sprintf('Bin Width: %s us, Laser Period: %s ns',...
    num2str(metadata.bin_width_micros),...
    num2str(metadata.laser_period_ns));

if ~isempty(metadata.acquisition_time_millis)
    title_str = [title_str, sprintf(', Acquisition Time: %s s', num2str(metadata.acquisition_time_millis / 1000))];
end

title(title_str);

% Plot legend
lgd = legend('show');
set(lgd, 'Location', 'southoutside', 'Orientation', 'horizontal');

hold off;
