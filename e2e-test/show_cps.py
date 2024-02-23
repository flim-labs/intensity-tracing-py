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
This test aims to simulate the "Show CPS" switch input toggle
to verify that:
📌 CPS labels on charts are hidden when the input is disabled
📌 CPS labels on charts are visible when the input is enabled
📌 CPS labels number is equal to the number of active channels (charts displayed)
    🔎🔎🔎
"""

NUM_TESTS = 1000
WAITING_TIME = 400


def generate_random_interactions():
    flow = random.choice(["before_start_btn_pressed", "after_start_btn_pressed"])
    return flow


@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    window.show()
    qtbot.addWidget(window)
    yield  test_app, window



def test_show_cps_assertions(window):
    show_cps_checked = window.control_inputs[SETTINGS_SHOW_CPS].isChecked()
    cps_labels = window.cps
    enabled_channels = window.enabled_channels
    if len(cps_labels) > 0:
        if show_cps_checked:
            all_labels_visible = all(cps.isVisible() for cps in cps_labels)
            cps_and_enabled_channels_length_is_equal = len(cps_labels) == len(enabled_channels)
            assert all_labels_visible
            print_color(f"Show CPS enabled? {show_cps_checked}", Fore.WHITE)
            print_color(f"CPS labels visible? {all_labels_visible}", Fore.WHITE)
            assert cps_and_enabled_channels_length_is_equal
            print_color(f"CPS labels number = {len(cps_labels)}", Fore.WHITE)
            print_color(f"Enabled channels = {len(enabled_channels)}", Fore.WHITE)
        else: 
            all_labels_hidden = not any(cps.isVisible() for cps in cps_labels)
            assert all_labels_hidden
            print_color(f"Show CPS enabled? {show_cps_checked}", Fore.WHITE)
            print_color(f"CPS labels hidden? {all_labels_hidden}", Fore.WHITE)




def test_after_start_btn_pressed(window, qtbot):
    # Simulate 'START' button click to show realtime charts
    start_button = window.control_inputs[START_BUTTON]
    qtbot.mouseClick(start_button, Qt.LeftButton)
    qtbot.wait(300)
    # Simulate 'Show CPS' input interactions
    show_cps_switch = window.control_inputs[SETTINGS_SHOW_CPS]
    show_cps_switch_interactions_num = random.randint(1, 50)
    for interaction_num in range(show_cps_switch_interactions_num):
        qtbot.mouseClick(show_cps_switch, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
        test_show_cps_assertions(window)
    # Simulate 'RESET' button click   
    reset_button = window.control_inputs[RESET_BUTTON]
    qtbot.mouseClick(reset_button, Qt.LeftButton)


def test_before_start_btn_pressed(window, qtbot):
    # Simulate 'Show CPS' input interaction
    show_cps_switch = window.control_inputs[SETTINGS_SHOW_CPS]
    qtbot.mouseClick(show_cps_switch, Qt.LeftButton)
    qtbot.wait(WAITING_TIME)
    # Simulate 'START' button click to show realtime charts
    start_button = window.control_inputs[START_BUTTON]
    qtbot.mouseClick(start_button, Qt.LeftButton)
    test_show_cps_assertions(window)
    # Simulate 'RESET' button click   
    reset_button = window.control_inputs[RESET_BUTTON]
    qtbot.mouseClick(reset_button, Qt.LeftButton)
  

def test_show_cps(app, qtbot):
    test_app, window = app
    for idx in range(NUM_TESTS):
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)
        # Generate random interactions flow
        flow = generate_random_interactions()
        if "before_start_btn_pressed" in flow:
            test_before_start_btn_pressed(window, qtbot)
        else:
            test_after_start_btn_pressed(window, qtbot)

        print_color("Test passed successfully", Fore.GREEN)    
        test_app.quit()
