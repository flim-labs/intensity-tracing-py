import pytest
import os
import sys
import json
import random
from PyQt5.QtWidgets import QApplication
from colorama import Fore

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(project_root)

subdirectory_path = os.path.join(project_root, "photons_tracing")
sys.path.append(subdirectory_path)

from photons_tracing.gui import PhotonsTracingWindow
from photons_tracing.settings import *
from utils import print_color


""" 🔎🔎🔎
This test aims to simulate the persistence of GUI parameter configurations after the application is closed and reopened. 
The application automatically saves updates to configurations in a settings.ini file when parameter values change.
Random parameters are generated on each test
    🔎🔎🔎
"""

NUM_TESTS = 10000

def generate_random_parameters():
    enabled_channels = random.sample(range(8),random.randint(0, 8))
    selected_connection = random.choice(["SMA", "USB"])
    bin_width = random.randint(1, 1000000)
    update_rate = random.choice(["HIGH", "LOW"])
    free_running_mode = random.choice([False, True])
    time_span = random.randint(1, 300)
    acquisition_time = random.randint(0, 1800000)
    show_cps = random.choice([True, False])
    write_data = random.choice([True, False])

    return (
        enabled_channels,
        selected_connection,
        bin_width,
        update_rate,
        free_running_mode,
        time_span,
        acquisition_time,
        show_cps,
        write_data
    )

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    # window.show()
    qtbot.addWidget(window)
    yield  test_app, window
 
def simulate_parameter_changes(window, qtbot, test_params):
    (
        enabled_channels,
        selected_connection,
        bin_width,
        update_rate,
        free_running_mode,
        time_span,
        acquisition_time,
        show_cps,
        write_data
    ) = test_params

    # Test parameters
    window.settings.setValue(SETTINGS_ENABLED_CHANNELS, json.dumps(enabled_channels))
    window.settings.setValue(SETTINGS_CONN_CHANNEL, selected_connection)
    window.settings.setValue(SETTINGS_BIN_WIDTH_MICROS, bin_width)
    window.settings.setValue(SETTINGS_UPDATE_RATE, update_rate)
    window.settings.setValue(SETTINGS_FREE_RUNNING_MODE, free_running_mode)
    window.settings.setValue(SETTINGS_TIME_SPAN, time_span)
    window.settings.setValue(SETTINGS_ACQUISITION_TIME_MILLIS, acquisition_time)
    window.settings.setValue(SETTINGS_SHOW_CPS, show_cps)
    window.settings.setValue(SETTINGS_WRITE_DATA, write_data)

def test_parameter_changes_persistence(app, qtbot):
    test_app, window = app

    for idx in range(NUM_TESTS):
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)
        test_params = generate_random_parameters()

        # Parameters change simulation
        simulate_parameter_changes(window, qtbot, test_params)

        # Close App
        window.close()

        # Reopen App
        window = PhotonsTracingWindow()
        # window.show()

        # Verify parameters configuration persistence
        assert len(window.enabled_channels) == len(test_params[0]) and set(window.enabled_channels) == set(test_params[0])
        print_color(f"{window.enabled_channels} == {test_params[0]}", Fore.WHITE)
        
        assert window.selected_conn_channel == test_params[1]
        print_color(f"{window.selected_conn_channel} == {test_params[1]}", Fore.WHITE)

        assert window.bin_width_micros == test_params[2]
        print_color(f"{window.bin_width_micros} == {test_params[2]}", Fore.WHITE)

        assert window.selected_update_rate == test_params[3]
        print_color(f"{window.selected_update_rate} == {test_params[3]}", Fore.WHITE)

        assert window.free_running_acquisition_time == test_params[4]
        print_color(f"{window.free_running_acquisition_time} == {test_params[4]}", Fore.WHITE)

        assert window.time_span == test_params[5]
        print_color(f"{window.time_span} == {test_params[5]}", Fore.WHITE)

        assert window.acquisition_time_millis == test_params[6]
        print_color(f"{window.acquisition_time_millis} == {test_params[6]}", Fore.WHITE)

        assert window.show_cps == test_params[7]
        print_color(f"{window.show_cps} == {test_params[7]}", Fore.WHITE)

        assert window.write_data == test_params[8]
        print_color(f"{window.write_data} == {test_params[8]}", Fore.WHITE)
    

        print_color("Test passed successfully", Fore.GREEN)

    test_app.quit()    
