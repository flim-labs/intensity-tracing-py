<a name="readme-top"></a>

<div align="center">
  <h1>Intensity Tracing v2.2</h1>
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
    <li><a href="#gui-usage">GUI Usage</a>
    <ul>
    <li><a href="#acquisition-channels">Acquisition channels</a></li>
    <li><a href="#connection-type">Connection type</a></li>
    <li><a href="#bin-width">Bin width</a></li>
    <li><a href="#update-rate">Update rate</a></li>
    <li><a href="#acquisition-mode">Acquisition mode</a></li>
    <li><a href="#acquisition-time">Acquisition time</a></li>
    <li><a href="#time-span">Time span</a></li>
    <li><a href="#show-cps">Show CPS</a></li>
    <li><a href="#cps-threshold">Pile-up threshold (CPS)</a></li>
    <li><a href="#export-data">Export data</a></li>
    <li><a href="#time-tagger">Time Tagger</a></li>
    <li><a href="#download-scripts-and-data-files">Download scripts and data files</a></li>
    <li><a href="#parameters-table-summary">Parameters table summary</a></li>
    </ul>
    </li>
    <li><a href="#parameters-configuration-saving">Parameters Configuration Saving</a></li>
    <li><a href="#long-time-acquisitions-and-ring-buffers">Long Time Acquisitions and Ring Buffers</a></li>
       <li><a href="#card-connection-detection">Card Connection Detection</a></li>
           <li><a href="#channels-connections-detection">Channels Connections Detection</a></li>  
    <li><a href="#reader-mode">Reader Mode</a></li>
    <li><a href="#console-usage">Console Usage</a></li>
     <li><a href="#exported-data-visualization">Exported Data Visualization</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## Introduction

Welcome to [FLIM LABS Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py) _v2.2_ usage guide. In this documentation section, you will find all the necessary information for the proper use of the application's **graphical user interface** (GUI).
For a general introduction to the aims, technical requirements and installation of the project, read the [Intensity Tracing Homepage](../index.md). You can also follow the [Console mode](../python-flim-labs/intensity-tracing-console.md) and [Data export](../python-flim-labs/intensity-tracing-file-format.md) dedicated guides links.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## GUI Usage

<div align="center">
    <img src="../assets/images/python/intensity-tracing-gui-2.2.png" alt="GUI" width="100%">
</div>

The GUI mode provides advanced functionality for configuring analysis **parameters** and displaying live-streamed photon data. It allows simultaneous acquisition from up to **8 channels**, offering real-time data visualization in the form of plots:

- **X** Axis: represents _acquisition time_
- **Y** Axis: represents _photons intensity_

Here an overview of each available feature:

#### Acquisition channels

The software allows for data acquisition in **single-channel** or **multi-channel** mode, with the user able to activate up to _8_ channels simultaneously.

For each activated channel, its respective real-time acquisition plot will be displayed on the interface.

The number of active channels affects the _size of the exported data file_. With the same values set for `bin width ` and `acquisition time `, the file size _grows proportionally to the number of activated channels_.

To start acquisition, at least one channel must be activated.

_Note: Ensure that the channel activated in the software corresponds to the channel number being used for acquisition on the [FLIM LABS Data Acquisition Card](https://www.flimlabs.com/products/data-acquisition-card/)._

<hr>

#### Connection type

The user can choose the type of connection for data acquisition between **SMA** and **USB** connections.

_Note: The connection type set in the software must match the actual connection type activated on the [FLIM LABS Data Acquisition Card](https://www.flimlabs.com/products/data-acquisition-card/)._

<hr>

#### Bin width

The user can set a **bin width** value ranging from _1_ to _1,000,000_ microseconds (μs). Bin width represents the duration of time to wait for accumulating photon counts in the exported data file. In the interface plots, this value is adjusted to maintain real-time visualization.

The configured bin width value affects the size of the exported data file. With the number of `active channels` and `acquisition time` unchanged, the _file size grows inversely proportional to the bin width value_.

<hr>

#### Acquisition mode

Users can choose between two data acquisition modes: **free running** or **fixed acquisition time**.

In free running mode, the total acquisition time is _not specified_. If users deactivate free running mode, they must set a specific acquisition time value.

The chosen acquisition mode impacts the size of the exported data file. Refer to the [Export Data](#export-data) section for details.

<hr>

#### Acquisition time

When the free running acquisition mode is disabled, users must specify the **acquisition time** parameter to set the total data acquisition duration. Users can choose a value between _1_ and _1800_ s (seconds).

For example, if a value of 10 is set, the acquisition will stop after 10 seconds.

The acquisition time value directly affects the final size of the exported data file. Keeping the `bin width` and `active channels` values unchanged, the _file size increases proportionally to the acquisition time value_.

<hr>

#### Time span

**Time span** set the time interval, in seconds, for the _last visible data range on the duration x-axis_. For instance, if this value is set to 5s, the x-axis will scroll to continuously display the latest 5 seconds of real-time data on the chart.
Users can choose a value from _1_ to _300_ s (seconds).

<hr>

#### Show CPS

Users can choose to enable the **Show CPS** option to display real-time average _Photon Count per Second (CPS)_ in the left-upper corner of active acquisition channel charts.
This feature offers an instant insight into signal intensity even when the traces are not actively observed.

<hr>

#### CPS threshold

Users can set a numeric value for the **Pile-up threshold (CPS)** input to highlight it in red with a vibrant effect when the CPS for a specific channel _exceeds that threshold_.

<hr>

#### Export data

Users can choose to **export acquired data** in _.bin_ file format for further analysis.
Refers to this section for more details:

- [Intensity Tracing Data Export guide ](../python-flim-labs/intensity-tracing-file-format.md)

<hr>

#### Time Tagger

If the user chooses to export the acquired data, they can also opt to enable or disable the export of **Time Tagger data**. When enabled, a .bin file will be exported (along with a Python script to read the .bin file) containing information on the type of _event_ and the _time_ (in ns) at which it was recorded.

<hr>

#### Parameters table summary

Here a table summary of the configurable parameters:

|                                 | data-type   | config                                                                                        | default   | explanation                                                                                                                                              |
| ------------------------------- | ----------- | --------------------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enabled_channels`              | number[]    | set a list of enabled acquisition data channels (up to 8). e.g. [0,1,2,3,4,5,6,7]             | []        | the list of enabled channels for photons data acquisition                                                                                                |
| `selected_conn_channel`         | string      | set the selected connection type for acquisition (USB or SMA)                                 | "USB"     | If USB is selected, USB firmware is automatically used. If SMA is selected, SMA firmware is automatically used.                                          |
| `bin_width_micros`              | number      | Set the numerical value in microseconds. Range: _1-1000000µs_                                 | 1000 (µs) | the time duration to wait for photons count accumulation.                                                                                                |
| `free_running_acquisition_time` | boolean     | Set the acquisition time mode (_True_ or _False_)                                             | True      | If set to True, the _acquisition_time_millis_ is indeterminate. If set to False, the acquisition_time_millis param is needed (acquisition duration)      |
| `time_span`                     | number      | Time interval, in seconds, for the visible data range on the duration x-axis. Range: _1-300s_ | 5         | For instance, if `time_span` is set to _5s_, the _x-axis_ will scroll to continuously display the latest 5 seconds of real-time data on the chart        |
| `acquisition_time_millis`       | number/None | Set the data acquisition duration. Range: _1-1800s_                                           | None      | The acquisition duration is indeterminate (None) if _free_running_acquisition_time_ is set to True.                                                      |
| `write_data`                    | boolean     | Set export data option to True/False                                                          | False     | if set to _True_, the acquired raw data will be exported locally to the computer along with scripts files (Python/Matlab)                                |
| `show_cps`                      | boolean     | Set show cps option to True/False                                                             | False     | if set to _True_, user can visualize cps value (average photon count per second) on charts for each active channel                                       |
| `cps_threshold`                 | number      | Set the CPS threshold                                                                         | 0         | If set to a value greater than 0, the user will see the CPS for each channel highlighted in red with a vibrant effect when they exceed the set threshold |
| `time_tagger`                   | boolean     | Set export Time Tagger data option to True/False                                              | True      | if set to _True_, the Time Tagger data will be processed and exported locally to the computer (along with a reader script in Python)                     |

<br/>

### Parameters Configuration Saving

Starting from _Intensity Tracing v.1.4_, the saving of GUI configuration parameters has been **automated**. Each interaction with the parameters results in the relative value change being stored in a `settings.ini` internal file.

The configurable parameters which can be stored in the settings file include:

- `enabled_channels`
- `selected_conn_channel`
- `selected_firmware`
- `bin_width_micros`
- `time_span`
- `acquisition_time_millis`
- `free_running_acquisition_time`
- `write_data`
- `show_cps`
- `cps_threshold`

On application restart, the saved configuration is automatically loaded. If the `settings.ini` file is not found, or a specific parameter has not been configured yet, a default configuration will be set.

Here an example of the `settings.ini` structure:

```json
[General]
show_cps=true
free_running_mode=false
acquisition_time_millis=100000
bin_width_micros=2000
enabled_channels="[0, 1, 2]"
acquisition_stopped=true
write_data=true
time_span=10
cps_threshold=250000
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Long Time Acquisitions and Ring Buffers

The software employs **ring buffers** to ensure seamless long-time acquisition of photon counts. A ring buffer, also known as a circular buffer, is utilized for efficient handling of cyclic data streams.

A ring buffer is a data structure implemented as a circular array, allowing continuous and cyclic storage of data. It is particularly useful when dealing with repetitive data streams without the need to fill or empty the entire buffer at once. This characteristic makes it well-suited for scenarios requiring constant data access and management.

It's important to note that, due to the continuous nature of long-time acquisition, the system may consume a significant amount of RAM. In practice, for extended acquisition sessions, we estimate a potential consumption of up to **4 gigabytes of RAM**. Users should be mindful of their system's memory capabilities to ensure smooth operation during extended experiments.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### Card Connection Detection

Since version _2.0_, the software supports **automatic detection of the Flim Card connection**.
The detection is performed automatically when the app starts and when acquisition begins. The user can also manually run this check at any time by clicking the _CHECK DEVICE_ button. If the card is connected, its ID will be displayed next to the button; otherwise, an error message will appear.

<hr>

#### Channels Connections Detection

Since version _2.1_, the software supports **automatic detection of channels connections**, simply clicking on the _Detect Channels_ button.
If connections are found, the system allows the user to update the configuration settings (Channel Type and enabled channels) in an automated way.

<hr>

## Reader mode

<div align="center">
    <img src="../assets/images/python/intensity-tracing-reader.gif" alt="GUI" width="100%">
</div>

The user can choose to use the software in **Reader mode**, loading .bin files from external intensity data acquisitions. The user can configure which plots to display, with up to 4 channels shown simultaneously. Additionally, they can view the _metadata_ related to the acquisition and download an image in _.png_ and _.eps_ format that replicates the acquisition graphs.

 <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Console Usage

For a detailed guide about console mode usage follow this link:

- [Intensity Tracing Console guide ](../python-flim-labs/intensity-tracing-console.md)

 <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Exported Data Visualization

The application GUI allows the user to export the analysis data in `binary file format`.

The user can also preview the final file size on the GUI. Since the calculation of the size depends on the values of the parameters `enabled_channels`, `bin_width_micros`, `free_running_acquisition_time`, `time_span`, and `acquisition_time_millis`, the value will be displayed if the following actions have been taken:

- At least one acquisition channel has been activated (`enabled_channels` has a length greater than 0).
- Values have been set for `time_span`, `acquisition_time_millis`, and `bin_width_micros`.

Here is a code snippet which illustrates the algorithm used for the calculation:

```python
def calc_exported_file_size(app):
    if len(app.enabled_channels) == 0:
        app.bin_file_size_label.setText("")
        return
    chunk_bytes = 8 + (4 * len(app.enabled_channels))
    chunk_bytes_in_us =  (1000 * (chunk_bytes * 1000)) / app.bin_width_micros
    if app.free_running_acquisition_time is True or app.acquisition_time_millis is None:
        file_size_bytes = int(chunk_bytes_in_us)
        app.bin_file_size = FormatUtils.format_size(file_size_bytes)
        app.bin_file_size_label.setText("File size: " + str(app.bin_file_size) + "/s")
    else:
        file_size_bytes = int(chunk_bytes_in_us * (app.acquisition_time_millis/1000))
        app.bin_file_size = FormatUtils.format_size(file_size_bytes)
        app.bin_file_size_label.setText("File size: " + str(app.bin_file_size))
```

For a detailed guide about data export and binary file structure see:

- [Intensity Tracing Data Export guide ](../python-flim-labs/intensity-tracing-file-format.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Download Acquired Data

If the _Export data_ option is enabled, the acquisition .bin file and the **Python** and **Matlab** scripts for manipulating and displaying the acquired data are automatically downloaded at the end of the acquisition, after the user selects a name for the files.

Note: a requirements.txt file — indicating the dependencies needed to run the Python script - will also be automatically downloaded.

Refer to these sections for more details:

- [Download Acquired Data](#download-acquired-data)
- [Intensity Tracing Data Export guide ](../python-flim-labs/intensity-tracing-file-format.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

FLIM LABS: info@flimlabs.com

Project Link: [FLIM LABS - Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
