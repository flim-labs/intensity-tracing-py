file_path = '<FILE-PATH>';

% Custom channel names (if any)
channel_names_json = '<CHANNEL-NAMES>';
try
    channel_names = jsondecode(channel_names_json);
catch
    channel_names = struct();
end

% Helper function to get channel name with custom name support
function name = get_channel_name(channel_id, custom_names)
    field_name = sprintf('x%d', channel_id);
    if isfield(custom_names, field_name)
        custom_name = custom_names.(field_name);
        if length(custom_name) > 30
            custom_name = [custom_name(1:30) '...'];
        end
        name = sprintf('%s (Ch%d)', custom_name, channel_id + 1);
    else
        name = sprintf('Channel %d', channel_id + 1);
    end
end

metadata = struct('channels', [], 'bin_width_micros', [], 'acquisition_time_millis', [], 'laser_period_ns', []);

fid = fopen(file_path, 'rb');


if fid == -1
    error('Unable to open the file');
end

first_bytes = fread(fid, 4, 'char')';

if ~isequal(first_bytes, 'IT02')
    fprintf('Invalid data file');
    fclose(fid);
    return;
end

json_length = fread(fid, 1, 'uint32');

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
elseif ~isempty(times)
    % Calcola dall'ultimo timestamp se acquisition_time è null
    calculated_acq_time_s = times(end);
    disp(['Acquisition time (calculated): ' num2str(calculated_acq_time_s) 's']);
end

if ~isempty(metadata.laser_period_ns)
    disp(['Laser period: ' num2str(metadata.laser_period_ns) 'ns']);
end

active_channels = metadata.channels;

number_of_channels = numel(metadata.channels);
channel_lines = cell(1, number_of_channels);

bin_width_seconds = metadata.bin_width_micros / 1e6;
times = [];

while true
    time_data = fread(fid, 8, 'uint8=>uint8');
    if isempty(time_data) || numel(time_data) < 8
        break;
    end
    time = typecast(time_data, 'double');
    times = [times, time / 1e9];
    
    bitmask_data = fread(fid, 1, 'uint8=>uint8');
    if isempty(bitmask_data)
        break;
    end
    bitmask = bitmask_data(1);
    
    for bit_position = 0:(number_of_channels-1)
        if bitand(bitmask, bitshift(1, bit_position)) ~= 0
            count_data = fread(fid, 4, 'uint8=>uint8');
            if isempty(count_data) || numel(count_data) < 4
                break;
            end
            count = typecast(count_data, 'uint32');
            channel_lines{bit_position + 1} = [channel_lines{bit_position + 1}, count];
        else
            channel_lines{bit_position + 1} = [channel_lines{bit_position + 1}, 0];
        end
    end
end

fclose(fid);

bin_width_ns = metadata.bin_width_micros * 1000;

% Calcola expected_bins
if ~isempty(metadata.acquisition_time_millis)
    % Se acquisition_time è definito, usalo
    total_time_ns = metadata.acquisition_time_millis * 1e6;
    expected_bins = floor(total_time_ns / bin_width_ns);
elseif ~isempty(times)
    % Se acquisition_time è null, calcolalo dall'ultimo timestamp
    % Se l'ultimo bin ha tutti zeri, usa il penultimo timestamp
    last_bin_is_empty = true;
    for i = 1:number_of_channels
        if channel_lines{i}(end) ~= 0
            last_bin_is_empty = false;
            break;
        end
    end
    
    if last_bin_is_empty && length(times) > 1
        % Usa il penultimo timestamp
        expected_bins = floor((times(end-1) * 1e9) / bin_width_ns) + 1;
    else
        % Usa l'ultimo timestamp
        expected_bins = floor((times(end) * 1e9) / bin_width_ns) + 1;
    end
else
    % Nessun bin trovato
    expected_bins = 0;
end

if expected_bins > 0
    full_times = ((0:(expected_bins-1)) * bin_width_ns) / 1e9;
    full_channel_lines = cell(1, number_of_channels);
    for i = 1:number_of_channels
        full_channel_lines{i} = zeros(1, expected_bins);
    end
    
    if ~isempty(times)
        % Se l'ultimo bin è vuoto, non includerlo nella ricostruzione
        last_bin_is_empty = true;
        for i = 1:number_of_channels
            if channel_lines{i}(end) ~= 0
                last_bin_is_empty = false;
                break;
            end
        end
        
        if last_bin_is_empty && length(times) > 1
            num_bins_to_process = length(times) - 1;
        else
            num_bins_to_process = length(times);
        end
        
        for i = 1:num_bins_to_process
            calculated = round((times(i) * 1e9) / bin_width_ns);
            bin_index = max(1, calculated);
            if bin_index >= 1 && bin_index <= expected_bins
                for ch = 1:number_of_channels
                    full_channel_lines{ch}(bin_index) = channel_lines{ch}(i);
                end
            end
        end
    end
    
    times = full_times;
    channel_lines = full_channel_lines;
end

figure;
hold on;

for i = 1:numel(active_channels)
    plot(times, channel_lines{i}, 'LineWidth', 0.5, 'DisplayName', get_channel_name(active_channels(i), channel_names));
end

title_str = sprintf('Bin Width: %s us, Laser Period: %s ns',
    num2str(metadata.bin_width_micros),
    num2str(metadata.laser_period_ns));

if ~isempty(metadata.acquisition_time_millis)
    title_str = [title_str, sprintf(', Acquisition Time: %s s', num2str(metadata.acquisition_time_millis / 1000))];
end

title(title_str);

lgd = legend('show');
set(lgd, 'Location', 'southoutside', 'Orientation', 'horizontal');

hold off;