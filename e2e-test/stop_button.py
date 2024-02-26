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
This test aims to simulate the "STOP" button correct functionality
to verify that:
📌 STOP button is disabled right after click
📌 START button is enabled after STOP button click
📌 Channels checkboxes clicks are enabled after STOP button activation
📌 acquisition_stopped variabled is set to True after STOP button activation
    🔎🔎🔎
"""

NUM_TESTS = 20000
WAITING_TIME = 600


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



def test_stop_button(app, qtbot):
    test_app, window = app
    for idx in range(NUM_TESTS):
        qtbot.wait(WAITING_TIME)
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)

        # Generate random channels checkboxes interactions
        rand_enabled_channels = generate_random_interactions()
        # Simulate channels checkboxes clicking
        channels_checkboxes = window.channels_checkboxes
        for index in rand_enabled_channels:
            qtbot.mouseClick(channels_checkboxes[index], Qt.LeftButton)
        print_color(f"Enabled channels: {window.enabled_channels}", Fore.WHITE)
        qtbot.wait(WAITING_TIME)      


        # Simulate "START" button click
        start_button = window.control_inputs[START_BUTTON]
        qtbot.mouseClick(start_button, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
        
        # Simulate "STOP" button click
        stop_button = window.control_inputs[STOP_BUTTON]
        qtbot.mouseClick(stop_button, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
        
        acquisition_stopped = window.acquisition_stopped
        assert acquisition_stopped 
        print_color(f"Acquisition stopped = {acquisition_stopped}", Fore.WHITE)


        stop_button = window.control_inputs[STOP_BUTTON]
        stop_button_enabled = stop_button.isEnabled()
        assert stop_button_enabled is False
        print_color(f"Stop button enabled = {stop_button_enabled}", Fore.WHITE)
        
        some_checkboxes_checked = not all(not checkbox.isChecked() for checkbox in channels_checkboxes)
        print_color(f"Some channels chexboxes checked? = {some_checkboxes_checked}", Fore.WHITE)
        start_button_enabled = start_button.isEnabled()
        if some_checkboxes_checked:
            assert start_button_enabled
        else:
            assert start_button_enabled is False
        print_color(f"Start button enabled = {start_button_enabled}", Fore.WHITE)

        all_checkboxes_enabled = all(checkbox.isEnabled() for checkbox in channels_checkboxes)
        assert all_checkboxes_enabled
        print_color(f"All channels checkboxes enabled = {all_checkboxes_enabled}", Fore.WHITE)
       

        print_color("Test passed successfully", Fore.GREEN)    
        test_app.quit()
