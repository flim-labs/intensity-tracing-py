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
This test verifies the functionality of displaying the exported data file size:
📌 If the "Export Data" switch is disabled, the file size helper should not be visible.
📌 If the "Export Data" switch is enabled, I expect to see it displayed (top-right, next to the switch).
📌 The file size format is rounded to 2 decimal places and contains the correct metric 
    for human readability purposes (B, KB, MB, GB, TB)
📌 If I change the values of bin width, acquisition time, free running acquisition time, and active channels, 
    I should see real-time updates on the helper.
📌 If Free running acquisition time is active, the size value is undefined (as is the acquisition time), 
    and I should see "XXXMB" displayed.
    🔎🔎🔎
"""

NUM_TESTS = 100
WAITING_TIME = 100
FILE_SIZE_LABEL_WITH_FREE_RUNNING_DISABLED = "File size: XXXMB"

def generate_random_parameters():
    rand_enabled_channels = random.sample(range(8),random.randint(0, 8))
    rand_bin_width = random.randint(1, 1000000)
    rand_acquisition_time = random.randint(1, 1800)
    return rand_enabled_channels, rand_bin_width, rand_acquisition_time, 
   

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    window.show()
    qtbot.addWidget(window)
    yield  test_app, window
 

def test_with_export_data_disabled(window, qtbot):
    file_size_label = window.bin_file_size_label
    print_color(f"File size label visible? {file_size_label.isVisible()}", Fore.WHITE)

    assert file_size_label.isVisible() is False
    print_color("Test passed successfully", Fore.GREEN)


def test_with_export_data_enabled(
    window, 
    qtbot, 
    rand_enabled_channels, 
    rand_bin_width, 
    rand_acquisition_time,
    ):

    # Simulate 'Free running mode' switch interaction
    free_running_mode_switch = window.control_inputs[SETTINGS_FREE_RUNNING_MODE]
    qtbot.mouseClick(free_running_mode_switch, Qt.LeftButton)
    qtbot.wait(WAITING_TIME)
    free_running_mode_checked = free_running_mode_switch.isChecked()

    print_color(f"Free running mode enabled? {free_running_mode_checked}", Fore.WHITE)

    if free_running_mode_checked:
        test_with_free_running_mode_enabled(window, qtbot)
    else:
        test_with_free_running_mode_disabled(window, qtbot, rand_bin_width, rand_acquisition_time, rand_enabled_channels)



def bin_width_interaction(window, qtbot, rand_bin_width):
    # Simulate bin_width number input typing
    bin_width_input = window.control_inputs[SETTINGS_BIN_WIDTH_MICROS]
    bin_width_input.clear()
    bin_width_input.setValue(rand_bin_width)
    qtbot.wait(WAITING_TIME)
    print_color(f"Bin width set to {bin_width_input.value()}", Fore.WHITE)
    print(window.bin_width_micros)


def acquisition_time_interaction(window, qtbot, rand_acquisition_time):
    # Simulate acquisition_time number input typing
    acquisition_time_input = window.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS]
    acquisition_time_input.clear()
    acquisition_time_input.setValue(rand_acquisition_time)
    qtbot.wait(WAITING_TIME)
    print_color(f"Acquisition time set to {acquisition_time_input.value()}", Fore.WHITE)
    print(window.acquisition_time_millis)

def channels_interaction(window, qtbot, rand_enabled_channels):
    # Simulate channels checkboxes clicking
    channels_checkboxes = window.channels_checkboxes
    
    for index in rand_enabled_channels:
        qtbot.mouseClick(channels_checkboxes[index], Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
    print_color(f"Enabled channels: {window.enabled_channels}", Fore.WHITE)    


def check_correct_file_size_format(
    window,
    qtbot,
):
    file_size_MB = int((window.acquisition_time_millis / 1000) * len(window.enabled_channels) * (window.bin_width_micros / 1000))
    file_size_bytes = file_size_MB * 1024 * 1024
    file_size_label = window.bin_file_size_label.text()
    file_size_label_num_slice = re.search(r'\d+\.\d+', file_size_label)
    file_size_num_value = float(file_size_label_num_slice.group())
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0

    while file_size_bytes >= 1024 and unit_index < len(units) - 1:
        file_size_bytes /= 1024.0
        unit_index += 1

    expected_metric = units[unit_index]

    print_color(file_size_label, Fore.WHITE)
    # Check if file size value has exactly 2 decimal positions
    assert re.match(r'\d+\.\d{0,2}$', str(file_size_num_value)), f"formatted_calc does not contain exactly two decimals: {file_size_label}"
    print_color(f"Does File size formatted calc contain exactly 2 decimals?: {bool(re.match(r'\d+\.\d{0,2}$', str(file_size_num_value)))}", Fore.WHITE)
    # Check correct file size metric (for human readability)
    assert expected_metric in file_size_label, f"Expected metric {expected_metric} not found in file_size_label: {file_size_label}"
    print_color(f"'{file_size_label}' label contains expected metric {expected_metric}", Fore.WHITE)


def test_with_free_running_mode_disabled(
    window, 
    qtbot, 
    rand_bin_width, 
    rand_acquisition_time,
    rand_enabled_channels,
    ):
    
    bin_width_interaction(window, qtbot, rand_bin_width)
    channels_interaction(window, qtbot, rand_enabled_channels)
    acquisition_time_interaction(window, qtbot, rand_acquisition_time)

    check_correct_file_size_format(window, qtbot)    


def test_with_free_running_mode_enabled(window, qtbot):
    file_size_label = window.bin_file_size_label
    assert file_size_label.text() == FILE_SIZE_LABEL_WITH_FREE_RUNNING_DISABLED
    print_color(f"File size label == {file_size_label.text()}", Fore.WHITE)


def test_file_size_feature(app, qtbot):
    test_app, window = app

    for idx in range(NUM_TESTS):
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)
        rand_enabled_channels, rand_bin_width, rand_acquisition_time = generate_random_parameters()

        # Simulate 'Export Data' switch interaction
        export_data_switch = window.control_inputs[SETTINGS_WRITE_DATA]
        qtbot.mouseClick(export_data_switch, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
        export_data_switch_checked = export_data_switch.isChecked()

        print_color(f"Export data switch enabled? {export_data_switch_checked}", Fore.WHITE)

        if not export_data_switch_checked:
            test_with_export_data_disabled(window, qtbot)
        else:
            test_with_export_data_enabled(window, qtbot, rand_enabled_channels, rand_bin_width, rand_acquisition_time)
           
    test_app.quit()
        


    

        
