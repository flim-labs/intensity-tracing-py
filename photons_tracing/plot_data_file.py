import struct
import matplotlib.pyplot as plt

file_path = 'INSERT DATA FILE PATH HERE'

# Open a photons tracing data file and plot data
times = []
ch_values = []

with open(file_path, 'rb') as f:
    while True:
        data = f.read(40)
        if not data:
            break
        (time, ch_1, ch_2, ch_3, ch_4, ch_5, ch_6, ch_7, ch_8) = struct.unpack('dIIIIIIII', data)
        times.append(time)
        ch_values.append(ch_1)

plt.plot(times, ch_values)
plt.show()
