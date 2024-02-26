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
This test aims to simulate the "RESET" button correct functionality
to verify that:
📌 blank_space layout is visible right after click
📌 DOWNLOAD button is disabled
📌 START button is enabled after RESET button click (only if at least one channel is active)
📌 STOP button is disabled
📌 Channels checkboxes clicks are enabled after RESET button activation
📌 charts list is cleared after RESET button activation
📌 charts connectors list is cleared after RESET button activation
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



def test_reset_button(app, qtbot):
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
        
        # Simulate "RESET" button click
        reset_button = window.control_inputs[RESET_BUTTON]
        qtbot.mouseClick(reset_button, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)

        blank_space_layout = window.blank_space
        blank_space_visibile = blank_space_layout.isVisible()
        assert blank_space_visibile
        print_color(f"Blank space layout visible? {blank_space_visibile}", Fore.WHITE)

        download_button = window.control_inputs[DOWNLOAD_BUTTON]
        download_button_enabled = download_button.isEnabled()
        assert download_button_enabled is False
        print_color(f"Download button enabled? {download_button_enabled}", Fore.WHITE)

        stop_button = window.control_inputs[STOP_BUTTON]
        stop_button_enabled = stop_button.isEnabled()
        assert stop_button_enabled is False
        print_color(f"Stop button enabled? {stop_button_enabled}", Fore.WHITE)
        
        some_checkboxes_checked = not all(not checkbox.isChecked() for checkbox in channels_checkboxes)
        print_color(f"Some channels chexboxes checked? = {some_checkboxes_checked}", Fore.WHITE)
        start_button_enabled = start_button.isEnabled()
        if some_checkboxes_checked:
            assert start_button_enabled
        else:
            assert start_button_enabled is False
        print_color(f"Start button enabled? {start_button_enabled}", Fore.WHITE)

        charts_length = len(window.charts)
        assert charts_length == 0
        print_color(f"Is charts list empty? {charts_length == 0}", Fore.WHITE)

        charts_connectors_length = len(window.connectors)
        assert charts_connectors_length == 0
        print_color(f"Is charts connectors list empty? {charts_length == 0}", Fore.WHITE)

        all_checkboxes_enabled = all(checkbox.isEnabled() for checkbox in channels_checkboxes)
        assert all_checkboxes_enabled
        print_color(f"All channels checkboxes enabled = {all_checkboxes_enabled}", Fore.WHITE)
       

        print_color("Test passed successfully", Fore.GREEN)    
        test_app.quit()
