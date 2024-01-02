import struct
import matplotlib.pyplot as plt

file_path = 'INSERT DATA FILE PATH HERE'

times = []

with open(file_path, 'rb') as f:

    # first 4 bytes must be IT01
    if f.read(4) != b'IT01':
        print("Invalid data file")
        exit(0)

    # read metadata from file
    (json_length,) = struct.unpack('I', f.read(4))
    metadata = eval(f.read(json_length).decode("utf-8"))

    print("Enabled channels: " + (", ".join(["Channel " + str(ch + 1) for ch in metadata["channels"]])))
    print("Bin width: " + str(metadata["bin_width_micros"]) + "\u00B5s")
    print("Acquisition time: " + str(metadata["acquisition_time_millis"] / 1000) + "s")
    print("Laser period: " + str(metadata["laser_period_ns"]) + "ns")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    while True:
        data = f.read(40)
        if not data:
            break
        (time, ) = struct.unpack('d', data[:8])
        channel_values = struct.unpack('IIIIIIII', data[8:])
        for i in range(len(channel_lines)):
            channel_lines[i].append(channel_values[i])
        times.append(time)


for i in range(len(channel_lines)):
    channel_line = channel_lines[i]
    plt.plot(
        times,
        channel_line,
        label="Channel " + str(metadata["channels"][i] + 1),
        linewidth=0.5
    )

plt.show()
