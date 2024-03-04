<a name="readme-top"></a>

<div align="center">
  <h1>Intensity Tracing - File Format </h1>
</div>
<div align="center">
  <a href="https://www.flimlabs.com/">
    <img src="../assets/images/shared/flimlabs-logo.png" alt="Logo" width="120" height="120">
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
    <li><a href="#data-visualization">Data Visualization</a></li>
    <li><a href="#download-example-files">Download Example Files </a></li>
    <li><a href="#useful-links">Useful links</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## Introduction

The [Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py) tool allows seamless export of photons counts analyzed data to binary files, with convenient plotting and visualization capabilities. This guide provides an in-depth exploration of the **binary file structure**, offering a comprehensive understanding of how exported data is formatted and can be leveraged.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## File Format

<div align="center">
    <img src="../assets/images/python/exported-data-visualization.png" alt="GUI" width="100%">
</div>

To plot and visualize previously exported raw data (with GUI or console mode) you can launch the`plot_data_file.py` script.
This script reads binary data from the local saved file and utilizes the `matplotlib` library to visualize photons intensity informations.

Here a detailed explanation of the exported binary data file structure:

##### Header (4 bytes):

The first 4 bytes of the file must be `IT02`. This serves as a validation check to ensure the correct format of the file. If the check fails, the script prints "Invalid data file" and exits.

##### Metadata Section (Variable length):

Following the header, metadata is stored in the file. This includes:

- `JSON length (4 bytes)`: an unsigned integer representing the length of the JSON metadata.
- `JSON metadata`: this is a variable-length string that contains information about the data, including _enabled channels_, _bin width_, _acquisition time_, and _laser period_. This information is printed to the console.

##### Data Records (Variable length):

After the metadata, the script enters a loop to read and process data in chunks of variable length, depending on the number of active channels. Each chunk represents a data record containing:

- `Timestamp (8 bytes)`: A double representing the photons' data acquisition time in seconds.
- `Channel Values (variable length)`: variable number of unsigned integers (4 bytes each) representing photon counts for each active channel at the corresponding timestamp.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Data Visualization

To visualize/plot your saved data, replace `file_path` value with the local path of your file:
(_Skip this step if you generated the export via the `DOWNLOAD` button, the `file_path` is already updated_)

```python
file_path = 'INSERT DATA FILE PATH HERE'
```

You can find your file at this path:

```python
file_path = 'C:\\Users\\YOUR_USER\\.flim-labs\\data'
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Download Example Files

By clicking on this [link](../assets/data/intensity-tracing-export-data-example.zip) you can download a compressed folder containing an example _Python script_, a _binary file of exported data_ and a _requirements.txt_ file with the needed libraries.

Here the steps to make your tests:

1. Move **intensity-tracing-export-data-example.bin** file to this path:
   ```sh
   C:\Users\YOUR_USER\.flim-labs\data
   ```
2. In the **intensity_tracing_plot_data_file_example.py** file, comment out this line of code:
   ```python
   file_path = get_recent_intensity_tracing_file()
   ```
3. Uncomment this line of code:

   ```python
   # file_path = "INSERT DATA FILE PATH HERE" # You can also manually insert the path to the data file here
   ```

   and set the correct file path pointing to the .bin file:

   ```python
   file_path = "C:\\Users\\YOUR_USER\\.flim-labs\\data\\intensity-tracing-export-data-example.bin"
   ```

4. Set the virtual environment in the root downloaded unzipped folder:
   ```sh
   python -m venv venv
   ```
5. Activate the virtual environment:
   ```sh
   venv\Scripts\activate
   ```
6. Install the dependencies
   ```sh
   pip install -r requirements.txt
   ```
7. Run the example Python script:
   ```sh
   python intensity_tracing_plot_data_file_example.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Useful Links

For more details about the project follow these links:

- [Intensity Tracing introduction](../intensity-tracing/index.md)
- [Intensity Tracing GUI guide](../intensity-tracing/v1.4/index.md)
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
