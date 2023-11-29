import flim_labs
import threading


def stop():
    print("stop")


def process(time, _x, counts):
    seconds = round(time / 1_000_000_000, 5)
    seconds = str(seconds).zfill(5)
    print("[" + seconds + "s] " + str(counts[1]))


def thread_function():
    print("Thread: Start reading from queue")
    flim_labs.read_from_queue(process)
    print("Thread: End reading from queue")


if __name__ == "__main__":
    bin_file = flim_labs.start_photons_tracing(
        enabled_channels=[1],
        bin_width_micros=1000,
        acquisition_time_millis=10000,
        # write_bin=True,
    )
    x = threading.Thread(target=thread_function)
    x.start()
    x.join()
    if bin_file != "":
        print("File bin written in: " + bin_file)
