import threading
import flim_labs


def stop():
    print("stop")

def process(time):
    seconds = round(time / 1_000_000_000, 5)
    seconds = str(seconds).zfill(5)
    return "[" + seconds + "s]"

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
                channels = [f"Ch{i}={v}" for i, v in enumerate((ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8), start=1) if v != 0]
                if channels:
                    print(process(time) + " " + " ".join(channels))


if __name__ == "__main__":
    result = flim_labs.start_intensity_tracing(
        enabled_channels=[1],
        bin_width_micros=1000,
        acquisition_time_millis=3000,
        write_bin=False,
        write_data=True
    )
    x = threading.Thread(target=thread_function)
    x.start()
    x.join()
  
    bin_file = result.bin_file
    data_file = result.data_file
    print("Binary file=" + str(bin_file))
    print("Data file=" + str(data_file))