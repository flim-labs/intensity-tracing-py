import flim_labs
import threading


def stop():
    print("stop")


def process(time, _x, counts):
    seconds = round(time / 1_000_000_000, 5)
    seconds = str(seconds).zfill(5)
    print("[" + seconds + "s] " + str(counts[0]))


def thread_function():
    print("Thread: Start reading from queue")
    flim_labs.read_from_queue(process)
    print("Thread: End reading from queue")


if __name__ == "__main__":
    result = flim_labs.start_photons_tracing(
        enabled_channels=[0],
        bin_width_micros=1000,
        acquisition_time_millis=3000,
        write_bin=False,
        write_data=True
    )
    x = threading.Thread(target=thread_function)
    x.start()
    x.join()
    # print result
    bin_file = result.bin_file
    data_file = result.data_file
    print("Binary file=" + str(bin_file))
    print("Data file=" + str(data_file))

