
import os

from PyQt5.QtCore import QTimer,QPoint, Qt, QSize, QSettings

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))

from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QApplication,
    QCheckBox,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QMessageBox,
    QMenu,
    QAction,
)

from PyQt5.QtGui import QIcon, QPixmap, QFont
from photons_tracing.gui_styles import GUIStyles
from gui_components.logo_utilities import LogoOverlay, TitlebarIcon
from gui_components.switch_control import SwitchControl
from gui_components.select_control import SelectControl
from gui_components.input_number_control import InputNumberControl
from gui_components.gradient_text import GradientText
from gui_components.layout_utilities import draw_layout_separator
from gui_components.link_widget import LinkWidget
from gui_components.box_message import BoxMessage
from gui_components.layout_utilities import draw_layout_separator


class ControlsBar:

    @staticmethod
    def init_gui_controls_layout(controls_row, buttons_row):
        controls_layout = QVBoxLayout()
        controls_layout.addSpacing(10)
        blank_space = QWidget()
        blank_space.setMinimumHeight(1)
        blank_space.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        controls_layout.addLayout(controls_row)
        controls_layout.addWidget(draw_layout_separator())
        controls_layout.addSpacing(10)
        controls_layout.addLayout(buttons_row)
        controls_layout.addSpacing(10)

        return blank_space, controls_layout


    @staticmethod
    def create_buttons(
        show_cps_control, 
        start_btn_pressed_cb, 
        stop_btn_pressed_cb,
        reset_btn_pressed_cb,
        channels_checkboxes 
    ):    
        # ACTION BUTTONS
        buttons_row_layout = QHBoxLayout()
        buttons_row_layout.addStretch(1)
        buttons_row_layout.addLayout(show_cps_control)
        # start button
        start_button = QPushButton("START")
        start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_start_btn_style(start_button)
        start_button.clicked.connect(start_btn_pressed_cb)
        start_button.setEnabled(
            not all(not checkbox.isChecked() for checkbox in channels_checkboxes)
            )   
        buttons_row_layout.addWidget(start_button)
        # stop button
        stop_button = QPushButton("STOP")
        stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_stop_btn_style(stop_button)
        stop_button.setEnabled(False)
        stop_button.clicked.connect(stop_btn_pressed_cb)
        buttons_row_layout.addWidget(stop_button)
        # reset button 
        reset_button = QPushButton("RESET")
        reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_reset_btn_style(reset_button)
        reset_button.setEnabled(True)
        reset_button.clicked.connect(reset_btn_pressed_cb)
        buttons_row_layout.addWidget(reset_button)
        
        return buttons_row_layout, start_button, stop_button, reset_button 

    @staticmethod
    def create_channel_type_control(controls_row, value, change_cb, options):        
        # Channels type control (USB/SMA)
        _, inp = SelectControl.setup(
                "Channel type:",
                value,
                controls_row,
                options,
                change_cb,
            )
        inp.setStyleSheet(GUIStyles.set_input_select_style())    
        return inp

    @staticmethod
    def create_bin_width_control(controls_row, value, change_cb):    
        # Bin width micros control
        _, inp = InputNumberControl.setup(
                "Bin width (µs):",
                1,
                1000000,
                value,
                controls_row,
                change_cb,
            )
        inp.setStyleSheet(GUIStyles.set_input_number_style())    
        return inp

    @staticmethod
    def create_update_rate_control(controls_row, value, change_cb, options):    
        # Update rate control (LOW/HIGH)
        _, inp = SelectControl.setup(
                "Update rate:",
                value,
                controls_row,
                options,
                change_cb,
            )
        inp.setStyleSheet(GUIStyles.set_input_select_style())    
        return inp

    @staticmethod
    def create_running_mode_control(value, change_cb):    
        # Acquisition time mode switch control (Free Running/Fixed)
        running_mode_control = QVBoxLayout()
        inp = SwitchControl(
                active_color="#13B6B4", width=100, height=30, checked=value
            )
        inp.stateChanged.connect(    
            (lambda state: change_cb(state))
            )
        running_mode_control.addWidget(QLabel("Free running:"))    
        running_mode_control.addSpacing(8)
        running_mode_control.addWidget(inp)
        
        return running_mode_control, inp

    @staticmethod  
    def create_time_span_control(controls_row, value, change_cb):       
        # Time span control
        _, inp = InputNumberControl.setup(
                "Time span (s):",
                1,
                300,
                value,
                controls_row,
                change_cb,
            )
        inp.setStyleSheet(GUIStyles.set_input_number_style())    
        return inp

    @staticmethod 
    def create_acquisition_time_control(controls_row, value, change_cb, free_running):               
        # Acquisition time millis input number control 
        # # (configurable when in acquisition time fixed mode)
        _, inp = InputNumberControl.setup(
                "Acquisition time (s):",
                0,
                1800,
                int(value / 1000)
                if value is not None
                else None,
                controls_row,
                change_cb,
            )
        inp.setEnabled(    
                not free_running.isChecked()
            )
        inp.setStyleSheet(GUIStyles.set_input_number_style())    
        return inp

    @staticmethod 
    def create_show_cps_control(value, change_cb):    
        # Show CPS switch control
        show_cps_control = QHBoxLayout()
        show_cps_label = QLabel("Show CPS:")
        inp = SwitchControl(    
                active_color="#8d4ef2",
                width=70, height=30, checked=value
            )
        inp.stateChanged.connect(    
            (lambda state: change_cb(state))
            )
        show_cps_control.addWidget(show_cps_label)    
        show_cps_control.addSpacing(8)
        show_cps_control.addWidget(inp)
        show_cps_control.addSpacing(8)
        
        return show_cps_control, inp        


