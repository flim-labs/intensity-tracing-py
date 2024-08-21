import json
import struct

def main(file_path):
    print("Checking granularity of intensity tracing file")
    print("==============================================")
    print("File:", file_path)
    with open(file_path, "rb") as f:
        f.seek(0)
        header = f.read(4)

        if header != b"IT02":
            print("Not an intensity tracing file")
            return

        json_length_bytes = f.read(4)
        json_length = struct.unpack("I", json_length_bytes)[0]

        json_bytes = f.read(json_length)
        json_string = json_bytes.decode("utf-8")
        params = json.loads(json_string)

        channels, bin_width_micros, acquisition_time_millis, laser_period_ns = (
            params["channels"],
            params["bin_width_micros"],
            params["acquisition_time_millis"],
            params["laser_period_ns"]
        )

        print("acquisition_time_millis:", acquisition_time_millis)
        print("bin_width_micros:", bin_width_micros)
        print("channels:", channels)
        print("laser_period_ns:", laser_period_ns)

        expected_entries = acquisition_time_millis * 1000 / bin_width_micros

        print("Expected number of entries:", expected_entries)

        data = []
        zeros_entries = 0
        channel_to_check_if_zero = 0

        while True:
            row = f.read(8 + 4 * len(channels))
            if len(row) == 0:
                break
            time_ns, *counts = struct.unpack("d" + ("I" * len(channels)), row)
            data.append({"time_ns": time_ns, "counts": counts})
            if counts[channel_to_check_if_zero] == 0:
                zeros_entries += 1

        print("Number of entries:", len(data))

        if len(data) != expected_entries:
            print("==============================================")
            print("\033[91m x Check Failed \033[0m")
            print("==============================================")
            print("Number of entries does not match expected entries")
            print("Expected number of entries:", expected_entries)
            print("Actual number of entries:", len(data))
        else:
            print("==============================================")
            print("\033[92m ✓ Check Success \033[0m")
            print("==============================================")
            print("Number of entries matches expected entries")

        print("")
        print("Number of zero entries for channel", channel_to_check_if_zero, ":", zeros_entries)
        print("Percentage of zero entries for channel", channel_to_check_if_zero, ":", zeros_entries / len(data) * 100, "%")
        print("")
        print("Note on bin width near 1 microsecond: the granularity of the data may be affected by the bin width, so the percentage of zero entries may be higher than expected")

        print("==============================================")
        print("End of check")




if __name__ == "__main__":
    import os
    from datetime import datetime
    import inquirer

    user_profile = os.environ["USERPROFILE"]
    data_dir = os.path.join(user_profile, ".flim-labs", "data")
    files = os.listdir(data_dir)
    files = [f for f in files if f.startswith("intensity-tracing") and f.endswith(".bin")]
    files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)), reverse=True)
    file_choices = [
        f"{f} (modified: {datetime.fromtimestamp(os.path.getmtime(os.path.join(data_dir, f))).strftime('%Y-%m-%d %H:%M:%S')})"
        for f in files]

    questions = [
        inquirer.List('file',
                      message="Choose a file",
                      choices=file_choices,
                      ),
    ]
    answers = inquirer.prompt(questions)
    answer_index = file_choices.index(answers['file'])
    file_chosen = files[answer_index]
    file_chosen = os.path.join(data_dir, file_chosen)
    main(file_chosen)