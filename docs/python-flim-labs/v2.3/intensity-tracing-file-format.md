<a name="readme-top"></a>

<div align="center">
  <h1>Intensity Tracing - File Format </h1>
</div>
<div align="center">
  <a href="https://www.flimlabs.com/">
    <img src="../assets/images/shared/intensity-tracing-logo.png" alt="Logo" width="120" height="120">
  </a>
</div>
<br>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#introduction">Introduction</a>
    </li>
    <li><a href="#file-format">File Format</a></li>
    <li><a href="#data-visualization">Data Visualization</a>
    </li>
    </ul>
    </li>
    <li><a href="#useful-links">Useful links</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Introduction

[![Intensity Tracing Export Data](../assets/images/python/intensity-tracing-export-data-video-thumbnail.png)](https://www.youtube.com/watch?v=WYTV987AXl0)

The [Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py) tool allows seamless export of photons counts analyzed data to binary files, with convenient plotting and visualization capabilities. This guide provides an in-depth exploration of the **binary file structure**, offering a comprehensive understanding of how exported data is formatted and can be leveraged.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## File Format


<div align="center">
    <img src="../assets/images/python/exported-data-visualization.png" alt="GUI" width="100%">
</div>

Below is the updated structure of the exported binary data file as implemented in the latest Intensity Tracing version:

#### Header (4 bytes)

- The first 4 bytes are the ASCII string `IT02`. This serves as a file format identifier. If this check fails, the file is considered invalid.

#### Metadata Section (variable length)

Immediately after the header, the file contains metadata:

- **JSON length (4 bytes):** An unsigned integer specifying the length (in bytes) of the JSON metadata string.
- **JSON metadata (variable):** A UTF-8 encoded JSON string of the specified length. This contains fields such as:
  - `channels`: List of enabled channel indices (e.g., `[0, 1]`)
  - `bin_width_micros`: Bin width in microseconds
  - `acquisition_time_millis`: Total acquisition time in milliseconds (optional)
  - `laser_period_ns`: Laser period in nanoseconds (optional)

#### Data Records (repeated until end of file)

After the metadata, the file contains a sequence of data records, each corresponding to a time bin:

- **Timestamp (8 bytes):** A double (IEEE 754) representing the time (in nanoseconds) from the start of the acquisition for this bin.
- **Bitmask (1 byte):** An unsigned byte. Each bit indicates whether the corresponding channel (as listed in `channels`) has a nonzero count in this bin:
  - If bit `n` is set, a count value for channel `n` follows.
  - If bit `n` is not set, no value is written for channel `n` (count is implicitly zero).
- **Channel Counts (variable):** For each channel where the bitmask is set, a 4-byte unsigned integer follows, representing the photon count for that channel in this bin. Channels with bitmask unset are considered to have a count of zero and are not stored.

This structure is repeated for each time bin until the end of the file.

##### Example Data Record Layout

| Field         | Size (bytes) | Description                                  |
|---------------|--------------|-----------------------------------------------|
| Timestamp     | 8            | double, nanoseconds from acquisition start    |
| Bitmask       | 1            | 1 bit per channel (max 8 channels supported)  |
| Channel Count | 4 * N        | For each set bit, 4 bytes (unsigned int)      |

Where N is the number of channels with a set bit in the bitmask for that bin.


##### Example Metadata JSON

```json
{
  "channels": [0, 1],
  "bin_width_micros": 100,
  "acquisition_time_millis": 5000,
  "laser_period_ns": 50000
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Data Visualization

The script files are automatically downloaded along with the acquisition .bin file once the acquisition is complete and a file name has been chosen. Follow one of the guides below if you wish to use the Python or Matlab script:

- **Python script**:

  - Open the terminal and navigate to the directory where the saved files are located (it is advisable to save and group them in a folder):

    ```sh
    cd YOUR_DOWNLOADED_DATA_ROOT_FOLDER
    ```

  - Create a virtual environment using the command:
    ```sh
    python -m venv venv
    ```
  - Activate the virtual environment with the command:
    ```sh
    venv\Scripts\activate
    ```
  - Install the necessary dependencies listed in the automatically downloaded _requirements.txt_ with:
    ```sh
    pip install -r requirements.txt
    ```
  - Run your script with:
    ```sh
    python YOUR_SCRIPT_NAME.py
    ```
    <br>

- **Matlab script**:  
   Simply open your MATLAB command window prompt and, after navigating to the folder containing the script, type the name of the script to launch it.


## Useful Links

For more details about the project follow these links:

- [Intensity Tracing introduction](../index.md)
- [Intensity Tracing GUI guide](../v2.3/index.md)
- [Intensity Tracing Console guide ](./intensity-tracing-console.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

FLIM LABS: info@flimlabs.com

Project Link: [FLIM LABS - Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
