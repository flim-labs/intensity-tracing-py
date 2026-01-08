import struct
import matplotlib.pyplot as plt


file_path = "<FILE-PATH>"
print("Using data file: " + file_path)

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
        print("Bin width: " + str(metadata["bin_width_micros"]) + "\u00B5s")

    if "acquisition_time_millis" in metadata and metadata["acquisition_time_millis"] is not None:
        print("Acquisition time: " + str(metadata["acquisition_time_millis"] / 1000) + "s")

    if "laser_period_ns" in metadata and metadata["laser_period_ns"] is not None:
        print("Laser period: " + str(metadata["laser_period_ns"]) + "ns")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    number_of_channels = len(metadata["channels"])
    bin_width_seconds = metadata["bin_width_micros"] / 1000000

    # Formato BITMASK: [time_ns(8B)] [bitmask(1B)] [count(4B)]* (solo canali con bit=1)
    while True:
        # Leggi timestamp (8 bytes)
        time_data = f.read(8)
        if not time_data or len(time_data) < 8:
            break
        (time,) = struct.unpack('d', time_data)
        times.append(time)
        
        # Leggi bitmask (1 byte)
        bitmask_data = f.read(1)
        if not bitmask_data:
            break
        (bitmask,) = struct.unpack('B', bitmask_data)
        
        # Leggi counts solo per canali con bit=1
        for bit_position in range(number_of_channels):
            if (bitmask & (1 << bit_position)) != 0:
                # Bit acceso: leggi count
                count_data = f.read(4)
                if not count_data or len(count_data) < 4:
                    break
                (count,) = struct.unpack('I', count_data)
                channel_lines[bit_position].append(count)
            else:
                # Bit spento: canale omesso, inserisci 0
                channel_lines[bit_position].append(0)
        
    
    # Plot data
    for i in range(len(metadata["channels"])):
        channel_line = channel_lines[i]
        times = [time / 1_000_000_000 for time in times]
        plt.plot(
            times,
            channel_line,
            label="Channel " + str(metadata["channels"][i] + 1),
            linewidth=0.5
        )

    # Set plot title with metadata information
    title_str = 'Bin Width: {} us'.format(
        metadata['bin_width_micros']
    )

    if metadata['acquisition_time_millis'] is not None:
        title_str += ', Acquisition Time: {} s'.format(metadata['acquisition_time_millis'] / 1000)

    plt.title(title_str)

    # Set x and y axis labels
    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (counts)")

    # Display grid
    plt.grid(True)

    # Set legend
    plt.legend(bbox_to_anchor = (1.05, 1), fancybox=True, shadow=True)
    plt.tight_layout()


    # Show the plot
    plt.show()