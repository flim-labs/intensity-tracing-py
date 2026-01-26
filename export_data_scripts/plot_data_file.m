file_path = '<FILE-PATH>';

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

if ~isempty(metadata.laser_period_ns)
    disp(['Laser period: ' num2str(metadata.laser_period_ns) 'ns']);
end

active_channels = metadata.channels;
number_of_channels = numel(metadata.channels);
channel_lines = cell(1, number_of_channels);

bin_width_seconds = metadata.bin_width_micros / 1e6;
times = [];

% READING DATA 
while true
    time_data = fread(fid, 8, 'uint8=>uint8');
    if isempty(time_data) || numel(time_data) < 8
        break;
    end
    time = typecast(time_data, 'double');
    times = [times, time];
    
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

% PROCESSING DATA
% If the last bin has bitmask = 0 (all zeros), it is a marker for the acquisition time
% and must be removed before visualization
final_time_marker = [];
if ~isempty(times)
    last_bin_is_empty = true;
    for i = 1:number_of_channels
        if channel_lines{i}(end) ~= 0
            last_bin_is_empty = false;
            break;
        end
    end
    
    if last_bin_is_empty
        final_time_marker = times(end);
        times = times(1:end-1);  % Remove the timestamp marker
        for ch = 1:number_of_channels
            channel_lines{ch} = channel_lines{ch}(1:end-1);  % Remove the marker data
        end
    end
end

bin_width_ns = metadata.bin_width_micros * 1000;

% CALCULATE EXPECTED BINS
if ~isempty(metadata.acquisition_time_millis)
    acq_time_s = metadata.acquisition_time_millis / 1000;
    disp(['Acquisition time: ' num2str(acq_time_s) 's']);
    total_time_ns = metadata.acquisition_time_millis * 1e6;
    expected_bins = floor(total_time_ns / bin_width_ns);
elseif ~isempty(final_time_marker)
    % Use the final marker to calculate acquisition time in free-running mode
    acq_time_s = final_time_marker / 1e9;
    disp(['Acquisition time: ' num2str(acq_time_s) 's']);
    expected_bins = floor(final_time_marker / bin_width_ns);
elseif ~isempty(times)
    % Fallback: use the last real timestamp
    acq_time_s = times(end) / 1e9;
    disp(['Acquisition time: ' num2str(acq_time_s) 's']);
    expected_bins = floor(times(end) / bin_width_ns) + 1;
else
    % No bins found
    disp('⚠️WARNING: No data available to reconstruct acquisition time.');
    expected_bins = 0;
end

% RECONSTRUCT FULL TIMELINE
if expected_bins > 0 && ~isempty(times)
    % Find the first and last bin indices from actual data
    first_bin_index = floor(times(1) / bin_width_ns);
    last_bin_index = floor(times(end) / bin_width_ns);
    
    % Reconstruct only from first to last bin with data
    num_bins = last_bin_index - first_bin_index + 1;
    full_times = ((first_bin_index:(first_bin_index + num_bins - 1)) * bin_width_ns) / 1e9;
    full_channel_lines = cell(1, number_of_channels);
    for i = 1:number_of_channels
        full_channel_lines{i} = zeros(1, num_bins);
    end
    
    for i = 1:length(times)
        bin_index = floor(times(i) / bin_width_ns);
        % Adjust index to start from 1 (MATLAB indexing)
        adjusted_index = bin_index - first_bin_index + 1;
        
        if adjusted_index >= 1 && adjusted_index <= num_bins
            for ch = 1:number_of_channels
                full_channel_lines{ch}(adjusted_index) = channel_lines{ch}(i);
            end
        end
    end
    
    times = full_times;
    channel_lines = full_channel_lines;
elseif expected_bins == 0
    times = [];
    channel_lines = cell(1, number_of_channels);
    for i = 1:number_of_channels
        channel_lines{i} = [];
    end
end

% PLOT VISUALIZATION
figure;
hold on;

for i = 1:numel(active_channels)
    plot(times, channel_lines{i}, 'LineWidth', 0.5, 'DisplayName', ['Channel ' num2str(active_channels(i) + 1)]);
end

title_str = sprintf('Bin Width: %s us, Laser Period: %s ns', ...
    num2str(metadata.bin_width_micros), ...
    num2str(metadata.laser_period_ns));

if ~isempty(metadata.acquisition_time_millis)
    title_str = [title_str, sprintf(', Acquisition Time: %s s', num2str(metadata.acquisition_time_millis / 1000))];
elseif ~isempty(final_time_marker)
    title_str = [title_str, sprintf(', Acquisition Time: %.3f s', acq_time_s)];
end

title(title_str);

xlabel('Time (s)');
ylabel('Intensity (counts)');
grid on;

lgd = legend('show');
set(lgd, 'Location', 'southoutside', 'Orientation', 'horizontal');

hold off;