import pytest
import os
import re
import sys
import json
import math
import random
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from colorama import Fore

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(project_root)

subdirectory_path = os.path.join(project_root, "photons_tracing")
sys.path.append(subdirectory_path)

from photons_tracing.gui import PhotonsTracingWindow
from photons_tracing.settings import *
from photons_tracing.format_utilities import FormatUtils
from utils import print_color


""" 🔎🔎🔎
This test aims to simulate the export data (write bin file) correct functionality
to verify that:
📌 if write_data is enabled, the data bin file is written at 'C:\\Users\\USERPROFILE\\.flim-labs\data'
📌 if write_data is disabled, no bin file is written at 'C:\\Users\\USERPROFILE\\.flim-labs\data'
⚠️ WARNING! For testing purposes, bin files saved in 'C:\\Users\\USERPROFILE\\.flim-labs\data' 
are being preemptively deleted. If you wish to keep them, it is recommended to temporarily 
move them to another folder. 
    🔎🔎🔎
"""

NUM_TESTS = 100
WAITING_TIME = 200


def generate_random_interactions():
    rand_enabled_channels = random.sample(range(8),random.randint(1, 8))
    return rand_enabled_channels


@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    window.show()
    qtbot.addWidget(window)
    yield  test_app, window


def clean_exported_data_files():
    data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        for file_name in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print_color(f"Error during data bin file elimination {e}", Fore.RED)


def check_bin_file_existence():
    data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        for file_name in os.listdir(data_folder):
            if file_name.startswith("intensity-tracing") and os.path.isfile(os.path.join(data_folder, file_name)):
                return True
        return False
    else:
        return False


def test_write_data(app, qtbot):
    test_app, window = app
    for idx in range(NUM_TESTS):
        qtbot.wait(WAITING_TIME)
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)
        
        # Clean bin data folder
        clean_exported_data_files()
        qtbot.wait(WAITING_TIME)
        
        # Generate random channels checkboxes interactions
        rand_enabled_channels = generate_random_interactions()
        
        if len(window.enabled_channels) == 0:        
            continue
        
        # Simulate write data switch clicking (random interactions num)
        write_data_switch = window.control_inputs[SETTINGS_WRITE_DATA]
        write_data_switch_interactions_num = random.randint(1, 5)
        for interaction_num in range(write_data_switch_interactions_num):
            qtbot.mouseClick(write_data_switch, Qt.LeftButton)
        print_color(f"Write data enabled?: {window.write_data}", Fore.WHITE)    
            
        # Simulate channels checkboxes clicking    
        channels_checkboxes = window.channels_checkboxes
        for index in rand_enabled_channels:
            qtbot.mouseClick(channels_checkboxes[index], Qt.LeftButton)
        print_color(f"Enabled channels: {window.enabled_channels}", Fore.WHITE)
        qtbot.wait(WAITING_TIME)

        # Simulate START button click
        start_button = window.control_inputs[START_BUTTON]
        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(1000)
        
        # Simulate STOP button click
        stop_button = window.control_inputs[STOP_BUTTON]
        qtbot.mouseClick(stop_button, Qt.LeftButton)
        qtbot.wait(1000)
        
        # Check bin file existence
        exported_file_existence = check_bin_file_existence()

        qtbot.wait(2000)

        if window.write_data:
            assert exported_file_existence
        else:
           assert exported_file_existence is False

        print_color(f"Write data enabled? {window.write_data}", Fore.WHITE)
        print_color(f"Bin file exported? {exported_file_existence}", Fore.WHITE)        

  
        test_app.quit()
