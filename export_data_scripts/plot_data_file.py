import struct
import json
import matplotlib.pyplot as plt


file_path = "<FILE-PATH>"
print("Using data file: " + file_path)

# Custom channel names (if any)
channel_names_json = '<CHANNEL-NAMES>'
try:
    channel_names = json.loads(channel_names_json) if channel_names_json else {}
except:
    channel_names = {}

def get_channel_name(channel_id):
    """Get custom channel name with channel reference, or default name."""
    custom_name = channel_names.get(str(channel_id), None)
    if custom_name:
        if len(custom_name) > 30:
            custom_name = custom_name[:30] + "..."
        return f"{custom_name} (Ch{channel_id + 1})"
    return f"Channel {channel_id + 1}"

times = []

with open(file_path, 'rb') as f:
    if f.read(4) != b'IT02':
        print("Invalid data file")
        exit(0)

    (json_length,) = struct.unpack('I', f.read(4))
    null = None
    metadata = eval(f.read(json_length).decode("utf-8"))

    if "channels" in metadata and metadata["channels"]:
        print("Enabled channels: " + (", ".join(["Channel " + str(ch + 1) for ch in metadata["channels"]])))

    if "bin_width_micros" in metadata and metadata["bin_width_micros"] is not None:
        print("Bin width: " + str(metadata["bin_width_micros"]) + "\u00B5s")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    number_of_channels = len(metadata["channels"])
    bin_width_seconds = metadata["bin_width_micros"] / 1000000

    # READING DATA
    while True:
        time_data = f.read(8)
        if not time_data or len(time_data) < 8:
            break
        (time,) = struct.unpack('d', time_data)
        times.append(time)
        
        bitmask_data = f.read(1)
        if not bitmask_data:
            break
        (bitmask,) = struct.unpack('B', bitmask_data)
        
        for bit_position in range(number_of_channels):
            if (bitmask & (1 << bit_position)) != 0:
                count_data = f.read(4)
                if not count_data or len(count_data) < 4:
                    break
                (count,) = struct.unpack('I', count_data)
                channel_lines[bit_position].append(count)
            else:
                channel_lines[bit_position].append(0)
    
    # PROCESSING DATA
    # If the last bin has bitmask = 0 (all zeros), it is a marker for the acquisition time
    # and must be removed before visualization
    if times and all(channel_lines[ch][-1] == 0 for ch in range(len(channel_lines))):
        final_time_marker = times[-1]
        times = times[:-1]  # Remove the timestamp marker
        for ch in range(len(channel_lines)):
            channel_lines[ch] = channel_lines[ch][:-1]  # Remove the marker data
    else:
        final_time_marker = None
    
    bin_width_ns = metadata["bin_width_micros"] * 1000
    
    # CALCULATE EXPECTED TIME BINS
    if metadata["acquisition_time_millis"] is not None:
        acq_time_s = metadata["acquisition_time_millis"] / 1000
        print(f"Acquisition time: {acq_time_s}s")
        total_time_ns = metadata["acquisition_time_millis"] * 1_000_000
        expected_bins = int(total_time_ns / bin_width_ns)
    elif final_time_marker is not None:
        # Use the final timestamp marker
        acq_time_s = final_time_marker / 1_000_000_000
        print(f"Acquisition time: {acq_time_s:.3f}s")
        expected_bins = int(final_time_marker / bin_width_ns)
    elif times:
        # Fallback: use the last real timestamp
        acq_time_s = times[-1] / 1_000_000_000
        print(f"Acquisition time: {acq_time_s:.3f}s")
        expected_bins = int(times[-1] / bin_width_ns) + 1
    else:
        print("\n⚠️ WARNING: No data available to reconstruct acquisition time.")
        expected_bins = 0
    
    # RECONSTRUCT FULL TIME BINS
    if expected_bins > 0 and times:
        # Find the first and last bin indices from actual data
        first_bin_index = int(times[0] / bin_width_ns)
        last_bin_index = int(times[-1] / bin_width_ns)
        
        # Reconstruct only from first to last bin with data
        num_bins = last_bin_index - first_bin_index + 1
        full_times = [(first_bin_index + i) * bin_width_ns for i in range(num_bins)]
        full_channel_lines = [[0] * num_bins for _ in range(number_of_channels)]
        
        for i in range(len(times)):
            time_ns = times[i]
            bin_index = int(time_ns / bin_width_ns)
            # Adjust index to start from 0
            adjusted_index = bin_index - first_bin_index
            
            if 0 <= adjusted_index < num_bins:
                for ch in range(number_of_channels):
                    full_channel_lines[ch][adjusted_index] = channel_lines[ch][i]
        
        times = full_times
        channel_lines = full_channel_lines
    elif expected_bins == 0:
        times = []
        channel_lines = [[] for _ in range(number_of_channels)]
    
    # PLOT VISUALIZATION
    times_seconds = [time / 1_000_000_000 for time in times]
    
    for i in range(len(metadata["channels"])):
        channel_line = channel_lines[i]
        plt.plot(
            times_seconds,
            channel_line,
            label=get_channel_name(metadata["channels"][i]),
            linewidth=0.5
        )

    title_str = 'Bin Width: {} us'.format(metadata['bin_width_micros'])
    if metadata['acquisition_time_millis'] is not None:
        title_str += ', Acquisition Time: {} s'.format(metadata['acquisition_time_millis'] / 1000)
    elif final_time_marker is not None:
        title_str += f', Acquisition Time: {acq_time_s:.3f} s'

    plt.title(title_str)
    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (counts)")
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), fancybox=True, shadow=True)
    plt.tight_layout()
    plt.show()