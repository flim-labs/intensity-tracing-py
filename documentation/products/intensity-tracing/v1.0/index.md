<a name="readme-top"></a>

<div align="center">
  <h1>Intensity Tracing v1.0</h1>
</div>
<div align="center">
  <a href="https://www.flimlabs.com/">
    <img src="../../../assets/images/shared/flimlabs-logo.png" alt="Logo" width="120" height="120">
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
    <li><a href="#draw-frequency">Draw Frequency</a></li>
    </ul>
    </li>
    <li><a href="#console-usage">Console Usage</a></li>
     <li><a href="#exported-data-visualization">Exported Data Visualization</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## Introduction

Welcome to [FLIM LABS Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py) _v1.0_ usage guide. In this documentation section, you will find all the necessary information for the proper use of the application's **graphical user interface** (GUI).
For a general introduction to the aims and technical requirements of the project, read the [Intensity Tracing Homepage](../index.md). You can also follow the [Console mode](../../python-flim-labs/intensity-tracing-console.md) and [Data export](../../python-flim-labs/intensity-tracing-file-format.md) dedicated guides links.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## GUI Usage

<div align="center">
    <img src="../../../assets/images/python/intensity-tracing-gui-1.0.png" alt="GUI" width="100%">
</div>

The GUI mode provides advanced functionality for configuring analysis **parameters** and displaying live-streamed photon data. It allows simultaneous acquisition from up to **8 channels**, offering real-time data visualization in the form of plots:

- **X** Axis: represents _acquisition time_
- **Y** Axis: represents _photons intensity_

Here a table summary of the configurable parameters:

|                                 | data-type   | config                                                                            | default   | explanation                                                                                                                                                                                        |
| ------------------------------- | ----------- | --------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `enabled_channels`              | number[]    | set a list of enabled acquisition data channels (up to 8). e.g. [0,1,2,3,4,5,6,7] | []        | the list of enabled channels for photons data acquisition                                                                                                                                          |
| `selected_conn_channel`         | string      | set the selected connection type for acquisition (USB or SMA)                     | "USB"     | If USB is selected, USB firmware is automatically used. If SMA is selected, SMA firmware is automatically used.                                                                                    |
| `bin_width_micros`              | number      | Set the numerical value in microseconds                                           | 1000 (ms) | the time duration to wait for photons count accumulation.                                                                                                                                          |
| `selected_update_rate`          | string      | Set the chart update frequency (**"LOW"** or **"HIGH"**)                          | "LOW"     | Based on the **selected_update_rate** value and the number of **enabled_channels** an algorithm determines the **draw_frequency** value assuring a balanced chart data visualization               |
| `free_running_acquisition_time` | boolean     | Set the acquisition time mode (**True** or **False**)                             | True      | If set to True, the _acquisition_time_millis_ is indeterminate, but _keep_points_ param needs to be specified. If set to False, the acquisition_time_millis param is needed (acquisition duration) |
| `keep_points`                   | number      | Set how many charts points to keep on the screen                                  | 1000      | This option sets the upper limit for the number of points visible in the chart display, aiming to prevent visual clutter and enhance readability                                                   |
| `acquisition_time_millis`       | number/None | Set the data acquisition duration                                                 | None      | The acquisition duration is indeterminate (None) if _free_running_acquisition_time_ is set to True.                                                                                                |
| `write_data`                    | boolean     | Set export data option to True/False                                              | False     | if set to _True_, the acquired raw data will be exported locally to the computer                                                                                                                   |

<br/>

### Draw Frequency

The purpose of `set_draw_frequency` function is is to determine and set the charts drawing frequency based on certain conditions, taking into account the selected _update rate_ and the _number of enabled channels_.

- If the `selected_update_rate` is set to "LOW" the `draw_frequency` value will fall within a range between **5** and **20**, depending on the number of active channels.
- If the `selected_update_rate` is set to "HIGH" the `draw_frequency` value will fall within a range between **21** and **100**, depending on the number of active channels.

```python
def set_draw_frequency(self):
    num_enabled_channels = len(self.enabled_channels)

    # Set default draw frequency when no channels are enabled and update rate is not "LOW" or "HIGH"
    if self.selected_update_rate not in ["LOW", "HIGH"] and num_enabled_channels == 0:
        self.draw_frequency = 10
        return

    # Define minimum and maximum frequencies based on the selected update rate
    if self.selected_update_rate == "LOW":
        min_frequency = 5
        max_frequency = 20
    else:
        min_frequency = 21
        max_frequency = 100

    # Calculate the frequency range and step based on the number of enabled channels
    frequency_range = max_frequency - min_frequency
    step = frequency_range / num_enabled_channels

    # Adjust the frequency considering the number of enabled channels
    adjusted_frequency = max_frequency - step * (num_enabled_channels - 1)

    # Set the draw frequency within the specified range
    self.draw_frequency = max(min_frequency, min(max_frequency, adjusted_frequency))
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Console Usage

For a detailed guide about console mode usage follow this link:

- [Intensity Tracing Console guide ](../../python-flim-labs/intensity-tracing-console.md)

 <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Exported Data Visualization

The application GUI allows the user to export the analysis data in `binary file format`. For a detailed guide about data export and binary file structure see:

- [Intensity Tracing Data Export guide ](../../python-flim-labs/intensity-tracing-file-format.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

FLIM LABS: info@flimlabs.com

Project Link: [FLIM LABS - Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
