<a name="readme-top"></a>

<div align="center">
  <h1>Intensity Tracing - Console mode </h1>
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
      <a href="#console-usage">Console Usage</a>
    </li>
    <li><a href="#useful-links">Useful links</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Console usage

<div align="center">
    <img src="../assets/images/python/intensity-tracing-console.png" alt="GUI" width="100%">
</div>

The [Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py) Console mode provides live-streaming data representation directly in the console, without an interface intermediary and charts data visualization processes.
The data displayed on the console screen indicates **the moment of acquisition** (in seconds) and the corresponding **number of photons** detected during that time.

Here a table summary of the configurable parameters on code side:

|                           | data-type   | config                                                                            | default   | explanation                                                                               |
| ------------------------- | ----------- | --------------------------------------------------------------------------------- | --------- | ----------------------------------------------------------------------------------------- |
| `enabled_channels`        | number[]    | set a list of enabled acquisition data channels (up to 8). e.g. [0,1,2,3,4,5,6,7] | [1]       | the list of enabled channels for photons data acquisition                                 |
| `bin_width_micros`        | number      | Set the numerical value in microseconds                                           | 1000 (ms) | the time duration to wait for photons count accumulation.                                 |
| `acquisition_time_millis` | number/None | Set the data acquisition duration                                                 | None      | The acquisition duration could be determinate (_numeric value_) or indeterminate (_None_) |
| `write_data`              | boolean     | Set export data option to True/False                                              | True      | if set to _True_, the acquired raw data will be exported locally to the computer          |

 <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Useful Links

For more details about the project follow these links:

- [Intensity Tracing introduction](../intensity-tracing/index.md)
- [Intensity Tracing GUI guide](../intensity-tracing/v1.4/index.md)
- [Intensity Tracing Data Export guide ](./intensity-tracing-file-format.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

FLIM LABS: info@flimlabs.com

Project Link: [FLIM LABS - Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
