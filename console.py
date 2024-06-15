import threading
import time
import flim_labs


REALTIME_MS = 10
REALTIME_ADJUSTMENT = REALTIME_MS * 1000
REALTIME_SECS = REALTIME_MS / 1000


def stop():
    print("stop")

def process(time):
    seconds = round(time / 1_000_000_000, 5)
    return "[" + str(seconds) + "s]"

def process_data(time_ns, counts, bin_width_micros):
    adjustment = REALTIME_ADJUSTMENT / bin_width_micros
    time_s = process(time_ns)
    adjusted_counts = [round(count / adjustment) for count in counts]
    channels = [f"Ch{i}={v}" for i, v in enumerate(adjusted_counts, start=1) if v != 0]
    if channels:
        print(time_s + " " + " ".join(channels))
    time.sleep(REALTIME_SECS / 1.1)
    

def thread_function(bin_width_micros):
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
                counts = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]
                process_data(time, counts, bin_width_micros)
   
                    


if __name__ == "__main__":
    
    #CONFIGURABLE PARAMS
    enabled_channels=[7, 5]
    bin_width_micros = 1
    acquisition_time_millis=3000
    write_bin=False
    write_data=True
    firmware_file="intensity_tracing_usb.flim"
    
    result = flim_labs.start_intensity_tracing(
        enabled_channels=enabled_channels,
        bin_width_micros=bin_width_micros,
        acquisition_time_millis=acquisition_time_millis,
        write_bin=write_bin,
        write_data=write_data,
        firmware_file=firmware_file
    )
    x = threading.Thread(target=thread_function, args=(bin_width_micros,))
    x.start()
    x.join()
  
    bin_file = result.bin_file
    data_file = result.data_file
    print("Binary file=" + str(bin_file))
    print("Data file=" + str(data_file))