import struct
import matplotlib.pyplot as plt


file_path = "<FILE-PATH>"
print("Using data file: " + file_path)

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

    if "acquisition_time_millis" in metadata and metadata["acquisition_time_millis"] is not None:
        print("Acquisition time: " + str(metadata["acquisition_time_millis"] / 1000) + "s")

    if "laser_period_ns" in metadata and metadata["laser_period_ns"] is not None:
        print("Laser period: " + str(metadata["laser_period_ns"]) + "ns")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    number_of_channels = len(metadata["channels"])
    bin_width_seconds = metadata["bin_width_micros"] / 1000000

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
    
    bin_width_ns = metadata["bin_width_micros"] * 1000
    
    if metadata["acquisition_time_millis"] is not None:
        total_time_ns = metadata["acquisition_time_millis"] * 1_000_000
        expected_bins = int(total_time_ns / bin_width_ns)
    elif times:
        expected_bins = int(times[-1] / bin_width_ns) + 1
    else:
        print("\n⚠️  ATTENZIONE: Nessun bin con fotoni trovato!")
        print("   Impossibile ricostruire la timeline senza acquisition_time.")
        expected_bins = 0
    
    if expected_bins > 0:
        full_times = [i * bin_width_ns for i in range(expected_bins)]
        full_channel_lines = [[0] * expected_bins for _ in range(number_of_channels)]
        
        if times:
            for i, time in enumerate(times):
                calculated = int(round(time / bin_width_ns))
                bin_index = max(0, calculated - 1)
                if 0 <= bin_index < expected_bins:
                    for ch in range(number_of_channels):
                        full_channel_lines[ch][bin_index] = channel_lines[ch][i]
        
        times = full_times
        channel_lines = full_channel_lines
    
    for i in range(len(metadata["channels"])):
        channel_line = channel_lines[i]
        times = [time / 1_000_000_000 for time in times]
        plt.plot(
            times,
            channel_line,
            label="Channel " + str(metadata["channels"][i] + 1),
            linewidth=0.5
        )

    title_str = 'Bin Width: {} us'.format(
        metadata['bin_width_micros']
    )

    if metadata['acquisition_time_millis'] is not None:
        title_str += ', Acquisition Time: {} s'.format(metadata['acquisition_time_millis'] / 1000)

    plt.title(title_str)

    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (counts)")

    plt.grid(True)

    plt.legend(bbox_to_anchor = (1.05, 1), fancybox=True, shadow=True)
    plt.tight_layout()

    plt.show()