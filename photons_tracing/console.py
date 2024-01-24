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
    continue_reading = True
    while continue_reading:
        val = flim_labs.pull_from_queue()

        if len(val) > 0:
            for v in val:
                if v == ('end',):
                    print("Experiment ended")
                    continue_reading = False
                    break
                ((time,), (ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8)) = v
                print("Time=" + str(time) + " Channel 1=" + str(ch1))


if __name__ == "__main__":
    result = flim_labs.start_intensity_tracing(
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
