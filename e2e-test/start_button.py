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
This test aims to simulate the "START" button correct functionality
to verify that:
📌 START button is disabled right after click
📌 STOP button is enabled after START button click
📌 DOWNLOAD button is enabled only if write_data and acquisition_stopped are set to True
📌 Channels checkboxes clicks are disabled after START button activation
📌 acquisition_stopped variabled is set to False after START button activation
📌 lenght of visible charts is equal to the length of enabled_channels after START button click
    🔎🔎🔎
"""

NUM_TESTS = 20000
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


# Preset long acquisitions to avoid too early 'stop button' deactivation
def prepopulate_inputs(window, qtbot):
    # Enable "free running acquisition mode" switch
    free_mode_switch = window.control_inputs[SETTINGS_FREE_RUNNING_MODE]
    free_mode_switch.setChecked(True)
    # Simulate acquisition_time number input typing
    acquisition_time_input = window.control_inputs[SETTINGS_ACQUISITION_TIME_MILLIS]
    acquisition_time_input.clear()
    acquisition_time_input.setValue(1800)
    # Simulate time_span number input typing
    time_span_input = window.control_inputs[SETTINGS_TIME_SPAN]
    time_span_input.clear()
    time_span_input.setValue(1)
    # Simulate bin_width number input typing
    bin_width_input = window.control_inputs[SETTINGS_BIN_WIDTH_MICROS]
    bin_width_input.clear()
    bin_width_input.setValue(1000000)
  

def test_start_button(app, qtbot):
    test_app, window = app
    for idx in range(NUM_TESTS):
        qtbot.wait(WAITING_TIME)
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)
        
        # Simulate "RESET" button click
        reset_button = window.control_inputs[RESET_BUTTON]
        qtbot.mouseClick(reset_button, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)

        # Generate random channels checkboxes interactions
        rand_enabled_channels = generate_random_interactions()
        # Simulate channels checkboxes clicking
        channels_checkboxes = window.channels_checkboxes
        for index in rand_enabled_channels:
            qtbot.mouseClick(channels_checkboxes[index], Qt.LeftButton)
        print_color(f"Enabled channels: {window.enabled_channels}", Fore.WHITE)
        qtbot.wait(WAITING_TIME)

        if len(window.enabled_channels) == 0:        
            continue

        prepopulate_inputs(window, qtbot)
        
        # Simulate write data switch clicking (random interactions num)
        write_data_switch = window.control_inputs[SETTINGS_WRITE_DATA]
        write_data_switch_interactions_num = random.randint(1, 5)
        for interaction_num in range(write_data_switch_interactions_num):
            qtbot.mouseClick(write_data_switch, Qt.LeftButton)
            qtbot.wait(WAITING_TIME)
        print_color(f"Write data enabled? {write_data_switch.isEnabled()}", Fore.WHITE)    
      

        # Simulate "START" button click
        start_button = window.control_inputs[START_BUTTON]
        qtbot.mouseClick(start_button, Qt.LeftButton)
        acquisition_stopped = window.acquisition_stopped

        
        print_color(f"Acquisition stopped? {acquisition_stopped}", Fore.WHITE)

        start_button_enabled = start_button.isEnabled()
        assert start_button_enabled is False
        print_color(f"Start button enabled? {start_button_enabled}", Fore.WHITE)

        stop_button = window.control_inputs[STOP_BUTTON]
        stop_button_enabled = stop_button.isEnabled()
        assert stop_button_enabled
        print_color(f"Stop button enabled? {stop_button_enabled}", Fore.WHITE)

        all_checkboxes_disabled = all(checkbox.isEnabled() is False for checkbox in channels_checkboxes)
        assert all_checkboxes_disabled
        print_color(f"All channels checkboxes disabled? {all_checkboxes_disabled}", Fore.WHITE)
       
        enabled_channels = window.enabled_channels
        visible_charts = [chart for chart in window.charts if chart.isVisible()]

        assert len(enabled_channels) == len(visible_charts)
        print_color(f"Active channels = {len(enabled_channels)}", Fore.WHITE)
        print_color(f"Visibile charts = {len(visible_charts)}", Fore.WHITE)
        
        write_data_enabled = window.write_data
        download_button_enabled = window.control_inputs[DOWNLOAD_BUTTON].isEnabled()
        if write_data_enabled and acquisition_stopped:
            assert download_button_enabled
        else:
            assert download_button_enabled is False
        print_color(f"Download button enabled? {download_button_enabled}", Fore.WHITE)


        print_color("Test passed successfully", Fore.GREEN)    
        test_app.quit()
