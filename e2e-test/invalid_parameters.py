import pytest
import os
import re
import sys
import json
import math
import random
from PyQt5.QtWidgets import QApplication, QMessageBox
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
from gui_components.box_message import BoxMessage
from utils import print_color


""" 🔎🔎🔎
This test aims to simulate invalid parameters settings
to verify that:
📌 a warning box message should appear to avoid starting acquisition process
    🔎🔎🔎
"""

NUM_TESTS = 1000
WAITING_TIME = 400


def generate_random_parameters():
    rand_enabled_channels = random.sample(range(8),random.randint(0, 8))
    rand_selected_connection = random.choice(["SMA", "USB", None])
    rand_bin_width = random.choice([0, 1000, 9000000])
    rand_update_rate = random.choice(["HIGH", "LOW", None])
    rand_free_running_mode = random.choice([False, True])
    rand_time_span = random.choice([0, 200, 600]) 
    rand_acquisition_time = random.choice([0, 1800, 2000]) 

    return rand_enabled_channels, rand_selected_connection, rand_bin_width, rand_update_rate, rand_free_running_mode, rand_time_span, rand_acquisition_time



# Prepopulate inputs with random values
def prepopulate_inputs(
    window, 
    qtbot,
    rand_enabled_channels, 
    rand_selected_connection, 
    rand_bin_width, 
    rand_update_rate,
    rand_free_running_mode, 
    rand_time_span, 
    rand_acquisition_time
    ):

    free_mode_switch = window.control_inputs[SETTINGS_FREE_RUNNING_MODE]
    free_mode_switch.setChecked(rand_free_running_mode)

    acquisition_time_input = window.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS]
    acquisition_time_input.clear()
    acquisition_time_input.setValue(rand_acquisition_time)

    time_span_input = window.control_inputs[SETTINGS_TIME_SPAN]
    time_span_input.clear()
    time_span_input.setValue(rand_time_span)

    bin_width_input = window.control_inputs[SETTINGS_BIN_WIDTH_MICROS]
    bin_width_input.clear()
    bin_width_input.setValue(rand_bin_width)

    selected_conn_channel = window.control_inputs[SETTINGS_CONN_CHANNEL]
    selected_conn_channel.setCurrentText(rand_selected_connection)
    
    selected_update_rate = window.control_inputs[SETTINGS_UPDATE_RATE]
    selected_update_rate.setCurrentText(rand_update_rate)
    
    channels_checkboxes = window.channels_checkboxes
    for index in rand_enabled_channels:
        qtbot.mouseClick(channels_checkboxes[index], Qt.LeftButton)

    return free_mode_switch    




@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    window.show()
    qtbot.addWidget(window)
    yield  test_app, window


def test_invalid_parameters_warning(app, qtbot):
    test_app, window = app
    for idx in range(NUM_TESTS):
        qtbot.wait(WAITING_TIME)
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)

        window.test_mode = True
                
        # Simulate "RESET" button click
        reset_button = window.control_inputs[RESET_BUTTON]
        qtbot.mouseClick(reset_button, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)

        # Generate random parameters
        rand_enabled_channels, rand_selected_connection, rand_bin_width, rand_update_rate, rand_free_running_mode, rand_time_span, rand_acquisition_time = generate_random_parameters()
        
        bin_width_range = (1, 1000000)
        time_span_range = (1, 300)
        acquisition_time_range = (0.5 * 1000, 1800 * 1000)


        free_mode_switch = prepopulate_inputs(
            window, 
            qtbot,
            rand_enabled_channels, 
            rand_selected_connection, 
            rand_bin_width, 
            rand_update_rate,
            rand_free_running_mode, 
            rand_time_span, 
            rand_acquisition_time
        )
    

        # Simulate "START" button click
        start_button = window.control_inputs[START_BUTTON]
        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(2000)


        print_color(f"Enabled channels: {window.enabled_channels}", Fore.WHITE)
        print_color(f"Bin width micros: {window.bin_width_micros}", Fore.WHITE)
        print_color(f"Free acquisition mode: {free_mode_switch.isChecked()}", Fore.WHITE)
        print_color(f"Acquisition time millis: {window.acquisition_time_millis}", Fore.WHITE)
        print_color(f"Selected connection channel: {window.selected_conn_channel}", Fore.WHITE)
        print_color(f"Selected update rate: {window.selected_update_rate}", Fore.WHITE)
        

        if ((window.bin_width_micros == 0 or 
        window.time_span == 0) or 
        (not free_mode_switch.isChecked() and  window.acquisition_time_millis == 0) or
        (len(window.enabled_channels) == 0) or
        (not window.selected_conn_channel) or
        (not window.selected_update_rate) or
        (window.bin_width_micros is not None and not (bin_width_range[0] <= window.bin_width_micros <= bin_width_range[1])) or
        (window.time_span is not None and not (time_span_range[0] <= window.time_span <= time_span_range[1])) or
        (window.acquisition_time_millis is not None and not (acquisition_time_range[0] <= window.acquisition_time_millis <= acquisition_time_range[1])) 
        ):
   
            assert window.warning_box is not None and window.warning_box.icon() == QMessageBox.Warning
            print_color(f"Invalid input warning box apperead?: {window.warning_box is not None}", Fore.WHITE)
            BoxMessage.close(window.warning_box)

        else: 
            assert window.warning_box is None 
            print_color(f"Invalid input warning box apperead?: {window.warning_box is not None}", Fore.WHITE)

        print_color("Test passed successfully", Fore.GREEN)     

    test_app.quit()    
