import pytest
import os
import sys
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
This test verifies the functionality of 'DOWNLOAD' button:
📌 If the "Export Data" switch is disabled, the download button should be disabled.

📌 If the "Export Data" switch is enabled, and the start button is active and the stop button wasn't clicked (First GUI run) the download button should be disabled
📌 If the "Export Data" switch is enabled, and the start button is active and the stop button was clicked (data acquisition process completed) the download button should be active

📌 If the "Export Data" switch is enabled, and the data acquisition mode is active the download button should be disabled
📌 If the reset button is clicked the download button should be disabled
    🔎🔎🔎
"""

NUM_TESTS = 20000
WAITING_TIME=100

def generate_random_parameters():
    write_data = random.choice([True, False])

    return (
        write_data
    )


@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = PhotonsTracingWindow()
    window.show()
    qtbot.addWidget(window)
    yield  test_app, window
 

def simulate_parameter_changes(window,test_params):
    (write_data)=test_params
    # Test parameters
    window.settings.setValue(SETTINGS_WRITE_DATA, write_data)


def export_data_disabled(window):
    download_button_enabled=window.control_inputs[DOWNLOAD_BUTTON].isEnabled()
    assert  download_button_enabled is False
    print_color("Test passed successfully", Fore.GREEN)
    


def export_data_enabled(window, qtbot):

    # GET CONTROLS
    start_button=window.control_inputs[START_BUTTON]
    stop_button=window.control_inputs[STOP_BUTTON]
    download_button=window.control_inputs[DOWNLOAD_BUTTON]
    
    
    assert download_button.isEnabled() is False
    print_color("Test passed successfully", Fore.GREEN)

    # START THE DATA ACQUISITION PROCESS
    qtbot.mouseClick(start_button, Qt.LeftButton)
    qtbot.wait(WAITING_TIME)

    assert download_button.isEnabled() is False
    print_color("Test passed successfully", Fore.GREEN)

    # STOP THE DATA ACQUISITION PROCESS    
    qtbot.mouseClick(stop_button, Qt.LeftButton)
    qtbot.wait(WAITING_TIME)
    assert download_button.isEnabled() is True
    print_color("Test passed successfully", Fore.GREEN)

    # OPEN THE CONTEXT MENU AND RESET THE GUI SETTINGS
    test_context_menu(window,qtbot)




# OPEN THE CONTEXT MENU AND RESET THE GUI SETTINGS
def test_context_menu(window, qtbot):
    context_menu=window.control_inputs[DOWNLOAD_MENU]
    for action in context_menu.actions():
         assert action.isEnabled()
    test_reset_button(window,qtbot)

#CLICK THE RESET BUTTON AND RESET THE GUI SETTINGS  
def test_reset_button(window, qtbot):
    download_button=window.control_inputs[DOWNLOAD_BUTTON]
    reset_button=window.control_inputs[RESET_BUTTON]
    qtbot.mouseClick(reset_button, Qt.LeftButton)
    qtbot.wait(WAITING_TIME)
    assert download_button.isEnabled() is False
    print_color("Test passed successfully", Fore.GREEN)




# DOWNLOAD BUTTON FEATURE COMPLETE PROCESS
def test_download_button_feature(app, qtbot):
    test_app, window=app

    for idx in range(NUM_TESTS):
        print_color(f"\nRunning test {idx + 1}...", Fore.CYAN)


        # GENERATE RANDOM PARAMS    
        test_params=generate_random_parameters()
        
        #SET RANDOM PARAMS
        simulate_parameter_changes(window,test_params)
        
        
        
        # TOGGLE THE EXPORT DATA SWITCH
        export_data_switch = window.control_inputs[SETTINGS_WRITE_DATA]
        qtbot.mouseClick(export_data_switch, Qt.LeftButton)
        qtbot.wait(WAITING_TIME)
        export_data_switch_checked=export_data_switch.isChecked()
 
        print_color(f"Export data switch enabled? {export_data_switch_checked}", Fore.WHITE)

        if not export_data_switch_checked:
            export_data_disabled(window)
        else:
            export_data_enabled(window, qtbot)    
         
          
    test_app.quit()        