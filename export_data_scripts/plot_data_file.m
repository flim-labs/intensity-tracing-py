file_path = '<FILE-PATH>';

% Open the file  
metadata = struct('channels', [], 'bin_width_micros', [], 'acquisition_time_millis', [], 'laser_period_ns', []);

fid = fopen(file_path, 'rb');


if fid == -1
    error('Unable to open the file');
end

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
channel_lines = cell(1, number_of_channels);

bin_width_seconds = metadata.bin_width_micros / 1e6;
times = [];

% Formato BITMASK: [time_ns(8B)] [bitmask(1B)] [count(4B)]* (solo canali con bit=1)
while true
    % Leggi timestamp (8 bytes)
    time_data = fread(fid, 8, 'uint8=>uint8');
    if isempty(time_data) || numel(time_data) < 8
        break;
    end
    time = typecast(time_data, 'double');
    times = [times, time / 1e9];
    
    % Leggi bitmask (1 byte)
    bitmask_data = fread(fid, 1, 'uint8=>uint8');
    if isempty(bitmask_data)
        break;
    end
    bitmask = bitmask_data(1);
    
    % Leggi counts solo per canali con bit=1
    for bit_position = 0:(number_of_channels-1)
        if bitand(bitmask, bitshift(1, bit_position)) ~= 0
            % Bit acceso: leggi count
            count_data = fread(fid, 4, 'uint8=>uint8');
            if isempty(count_data) || numel(count_data) < 4
                break;
            end
            count = typecast(count_data, 'uint32');
            channel_lines{bit_position + 1} = [channel_lines{bit_position + 1}, count];
        else
            % Bit spento: canale omesso, inserisci 0
            channel_lines{bit_position + 1} = [channel_lines{bit_position + 1}, 0];
        end
    end
end

fclose(fid);

figure;
hold on;

% Plot data
for i = 1:numel(active_channels)
    plot(times, channel_lines{i}, 'LineWidth', 0.5, 'DisplayName', ['Channel ' num2str(active_channels(i) + 1)]);
end

% Set plot title with metadata information
title_str = sprintf('Bin Width: %s us, Laser Period: %s ns',
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