
# Intensity Tracing

Welcome to [FLIM LABS Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py), a Python application designed to **analyze single-photon counts as a function of time** and plotting the intensity trace. Facilitated by an underlying data processor developed in Rust, responsible for data retrieval from the hardware component, this application enables real-time data analysis and visualization. Users can seamlessly transition between the graphical user interface (**GUI**) and **console** mode to navigate through the analytical capabilities. Whether your focus is on rigorous data analysis or dynamic visualizations, Intensity Tracing serves as a flexible tool for the precise measurement and exploration of photon intensity.


### Built With

* [Python](https://www.python.org/)
* [PyQt5](https://pypi.org/project/PyQt5/)
* [pglive](https://pypi.org/project/pglive/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [flim-labs](https://pypi.org/project/flim-labs/)


<!-- GETTING STARTED -->
## Getting Started
To directly test the application, skipping the prerequisites and installation requirements you can download an installer at this [link](https://github.com/flim-labs/intensity-tracing-py/releases/tag/v1.2) (_Note: you still need to have the FLIM LABS acquisition card_). 

To get a local copy up and running follow these steps.

### Prerequisites

To be able to run this project locally on your machine you need to satisfy these requirements:
* Possess a [FLIM LABS acquisition card](https://www.flimlabs.com/products/data-acquisition-card/) to be able to acquire your data
* ZestSC3 drivers installed
* Python version >= 3.8
* Windows OS

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/flim-labs/intensity-tracing-py.git
   ```
2. Set the virtual environment in the root folder
   ```sh
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```sh
   venv\Scripts\activate 
   ```   
4. Install the dependencies
   ```sh
   pip install -r requirements.txt
   ```
6. Starting from the root, navigate to the correct folder:
   ```sh
   cd photons_tracing
   ```     
5. Run the project with GUI mode
   ```sh
   python intensity_tracing.py
   ```  
6. Or run the project with Console mode
   ```sh
   python console.py   
   ```  

## Usage Guides

Navigate to the following links to view detailed application usage guides:

- [Intensity Tracing GUI guide](./docs/v1.2/index.md)
- [Intensity Tracing Console guide ](./docs/python-flim-labs/intensity-tracing-console.md)
- [Intensity Tracing Data export guide](./docs/python-flim-labs/intensity-tracing-file-format.md)


## Contact

FLIM LABS: info@flimlabs.com

Project Link: [FLIM LABS - Intensity Tracing](https://github.com/flim-labs/intensity-tracing-py)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
