import os
import struct
import matplotlib.pyplot as plt


def get_recent_intensity_tracing_file():
    data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
    files = [f for f in os.listdir(data_folder) if f.startswith("intensity-tracing")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True)
    return os.path.join(data_folder, files[0])


file_path = get_recent_intensity_tracing_file()
# file_path = "INSERT DATA FILE PATH HERE" # You can also manually insert the path to the data file here

times = []

with open(file_path, 'rb') as f:
    # first 4 bytes must be IT01
    if f.read(4) != b'IT01':
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

    while True:
        data = f.read(40)
        if not data:
            break
        (time,) = struct.unpack('d', data[:8])
        channel_values = struct.unpack('IIIIIIII', data[8:])
        for i in range(len(channel_lines)):
            channel_lines[i].append(channel_values[i])
        times.append(time / 1_000_000_000)

plt.xlabel("Time (s)")
plt.ylabel("Intensity (counts)")
plt.title("Intensity tracing (" + str(len(times)) + " points)")

for i in range(len(channel_lines)):
    channel_line = channel_lines[i]
    plt.plot(
        times,
        channel_line,
        label="Channel " + str(metadata["channels"][i] + 1),
        linewidth=0.5,
    )

plt.show()
