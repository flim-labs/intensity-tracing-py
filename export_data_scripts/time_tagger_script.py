import struct
import pandas as pd
import os
import json
from tqdm import tqdm
import pyarrow as pa
import pyarrow.parquet as pq
from colorama import Fore, init
import warnings  

file_path = "<FILE-PATH>"

init(autoreset=True)  
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

def read_time_tagger_bin(file_path, chunk_size=100000):
    """
    Reads data from a Intensity Tracing Time Tagger binary file (.bin) and yields data in chunks as DataFrames.
    The .bin file consists of records with a length of 9 bytes, where 1 byte represents the event type (Channel, Pixel, Line, Frame), 
    and 8 bytes represent the time (ns) value. 
    The first 4 bytes are magic bytes used to uniquely identify an "intensity tracing time tagger" .bin file. 
    The .bin file also has a variable-length header containing information about the enabled channels and 
    the laser period of the acquisition.

    Parameters:
        file_path (str): Path to the .bin file.
        chunk_size (int): Number of records per chunk (default is 100000).

    Yields:
        pd.DataFrame: A DataFrame containing the data (Event, Time) for each chunk.
        str: Enabled channels information.
        str: Laser period information.
    """
    if not os.path.exists(file_path):
        print(Fore.RED + f"File not found: {file_path}")
        return
    record_size = 9  # 1 byte per channel, 8 bytes per time (f64), 

    def read_header(f):
        """
        Reads and parses the header from the binary file.

        Parameters:
            f (file object): File object for reading the binary file.

        Returns:
            dict: Parsed header information in JSON format.
        """
        if f.read(4) != b"ITT1":
            print(Fore.RED + "Invalid data file")
            exit(0)
        header_length_bytes = f.read(4)
        header_length = struct.unpack("<I", header_length_bytes)[0]
        header_json = f.read(header_length).decode("utf-8")
        header = json.loads(header_json)
        return header

    def record_generator(file_path, record_size):
        """
        Generator that yields records from the binary file.

        Parameters:
            file_path (str): Path to the .bin file.
            record_size (int): Size of each record in bytes.

        Yields:
            tuple: A tuple containing the unpacked record data, enabled channels, and laser period.
        """
        with open(file_path, "rb") as f:
            header = read_header(f)
            if "channels" in header and header["channels"] is not None:
                enabled_channels = ", ".join(
                    ["Channel " + str(ch + 1) for ch in header["channels"]]
                )
            if "laser_period_ns" in header and header["laser_period_ns"] is not None:
                laser_period = str(header["laser_period_ns"]) + "ns"
            while True:
                record = f.read(record_size)
                if len(record) < record_size:
                    break
                yield struct.unpack("<Bd", record), enabled_channels, laser_period

    records = []
    for i, (record, enabled_channels, laser_period) in enumerate(
        record_generator(file_path, record_size)
    ):
        event, time = record
        event_string = ""
        if event == 70:
            event_string = "F" # Frame
        elif event == 76:
            event_string = "L"  # Line
        elif event == 80:
            event_string = "P"  # Pixel
        else:
            event_string = f"ch{event + 1}" # Channel          
        records.append((event_string, time))

        if (i + 1) % chunk_size == 0:
            yield pd.DataFrame(
                records, columns=["Event", "Time (ns)"]
            ), enabled_channels, laser_period
            records = []
    if records:
        yield pd.DataFrame(
            records, columns=["Event", "Time (ns)"]
        ), enabled_channels, laser_period


def save_to_parquet(file_path, output_file):
    """
    Saves the data from the binary file to a Parquet file with optional metadata.

    Parameters:
        file_path (str): Path to the .bin file.
        output_file (str): Path to the output .parquet file.
    """
    if not os.path.exists(file_path):
        print(Fore.RED + f"File not found: {file_path}")
        return

    # Check if the Parquet file already exists
    if os.path.exists(output_file):
        print(Fore.YELLOW + f"{output_file} already exists. Skipping save.")
        return  # If it exists, skip saving

    print(Fore.CYAN + f"Saving data to {output_file}...")

    # Initialize variables for collecting data
    records_list = []
    enabled_channels = laser_period = None

    # Set up an indeterminate progress bar (total=None)
    with tqdm(
        desc="Processing chunks...",
        unit="chunk",
        total=None,  # Indeterminate progress bar
    ) as pbar:
        # Process chunks and update the progress bar
        for chunk, channels, period in read_time_tagger_bin(file_path):
            records_list.append(chunk)
            enabled_channels = channels
            laser_period = period
            pbar.update(1)  # Increment the progress bar for each chunk processed

    # Concatenate all data and sort
    existing_data = pd.concat(records_list, ignore_index=True)
    existing_data.sort_values(by="Time (ns)", inplace=True)

    # Save the DataFrame as Parquet and add metadata (enabled_channels and laser_period)
    table = pa.Table.from_pandas(existing_data)
    metadata = {"enabled_channels": enabled_channels, "laser_period": laser_period}
    table = table.replace_schema_metadata(
        {**table.schema.metadata, **{k: v.encode() for k, v in metadata.items()}}
    )
    pq.write_table(table, output_file, compression="snappy")
    print(Fore.GREEN + f"Data and metadata saved to {output_file}.")


def read_from_parquet(parquet_file):
    """
    Reads data and metadata from a Parquet file.

    Parameters:
        parquet_file (str): Path to the .parquet file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the Parquet file.
        str: Enabled channels information.
        str: Laser period information.
    """
    if not os.path.exists(parquet_file):
        print(Fore.RED + f"File not found: {parquet_file}")
        return

    print(Fore.CYAN + f"Reading data from {parquet_file}...")

    # Read the Parquet file
    table = pq.read_table(parquet_file)
    metadata = table.schema.metadata

    # Retrieve metadata
    enabled_channels = (
        metadata.get(b"enabled_channels").decode()
        if b"enabled_channels" in metadata
        else None
    )
    laser_period = (
        metadata.get(b"laser_period").decode() if b"laser_period" in metadata else None
    )

    print("\n")
    print(Fore.GREEN + f"Enabled channels: {enabled_channels}")
    print(Fore.GREEN + f"Laser period: {laser_period}")
    print("\n")

    # Convert the table to a DataFrame
    df = table.to_pandas()
    return df, enabled_channels, laser_period


def display_data(df):
    """
    Displays the data from the DataFrame according to user preferences.

    Parameters:
        df (pd.DataFrame): DataFrame containing the data to be displayed.
    """
    # Choose the display option
    print(Fore.CYAN + "Choose display option:")
    print(Fore.YELLOW + "1. Overview (first and last rows)")
    print(
        Fore.YELLOW
        + "2. Read full data (may take time if you select many rows per chunk)"
    )
    choice = input(Fore.CYAN + "Enter your choice (1 or 2): ")

    if choice == "1":
        print(Fore.CYAN + "Showing an overview of the data:")
        print("\n")
        print(Fore.GREEN + df.head().to_string(index=False))
        print("\n...\n")
        print(Fore.GREEN + df.tail().to_string(index=False))
        print("\n")
    elif choice == "2":
        # Ask the user for the maximum number of rows per chunk
        max_rows = int(
            input(Fore.CYAN + "Enter the maximum number of rows to read per chunk: ")
        )

        # Display the data in chunks to avoid memory overload
        for start in range(0, len(df), max_rows):
            end = min(start + max_rows, len(df))
            print("\n")
            print(Fore.GREEN + df.iloc[start:end].to_string(index=False))
            print("\n")
            if end < len(df):
                # Wait for the user to press Enter before loading the next chunk or type 'exit' to quit
                user_input = input(
                    Fore.CYAN
                    + "Press Enter to load the next chunk or type 'exit' to quit: "
                )
                if user_input.lower() == "exit":
                    print(Fore.RED + "Exiting...")
                    break
    else:
        print(Fore.RED + "Invalid choice. Showing default overview.")
        print("\n")
        print(Fore.GREEN + df.head().to_string(index=False))
        print("\n...\n")
        print(Fore.GREEN + df.tail().to_string(index=False))
        print("\n")


def read_bin_and_display(file_path):
    """
    Reads data directly from the binary file and displays it.

    Parameters:
        file_path (str): Path to the .bin file.
    """
    records_list = []
    enabled_channels = laser_period = None

    # Set up an indeterminate progress bar (total=None)
    with tqdm(
        desc="Processing chunks...",
        unit="chunk",
        total=None,  # Indeterminate progress bar
    ) as pbar:
        # Process chunks
        for chunk, channels, period in read_time_tagger_bin(file_path):
            records_list.append(chunk)
            enabled_channels = channels
            laser_period = period
            pbar.update(1)  # Increment the progress bar for each chunk processed

    # Concatenate all data and sort
    existing_data = pd.concat(records_list, ignore_index=True)
    existing_data.sort_values(by="Time (ns)", inplace=True)

    print("\n")
    print(Fore.GREEN + f"Enabled channels: {enabled_channels}")
    print(Fore.GREEN + f"Laser period: {laser_period}")
    print("\n")

    # Display the data
    display_data(existing_data)


def main():
    """
    Main function that drives the script. It handles user input for saving data as Parquet
    and loading data from the appropriate file format.
    """
    parquet_file = file_path.replace(".bin", ".parquet")

    # Ask the user if they want to save the file as Parquet
    save_choice = input(
        Fore.CYAN
        + "Do you want to save an optimized data version in Parquet format? (yes/no): "
    ).lower()

    if save_choice == "yes":
        save_to_parquet(file_path, parquet_file)
        df, enabled_channels, laser_period = read_from_parquet(parquet_file)
        display_data(df)
    else:
        if os.path.exists(parquet_file):
            print(Fore.CYAN + f".parquet file found: {parquet_file}.")
            df, enabled_channels, laser_period = read_from_parquet(parquet_file)
            display_data(df)
        else:
            print(Fore.CYAN + f"Loading data from .bin file...")
            read_bin_and_display(file_path)


if __name__ == "__main__":
    main()

