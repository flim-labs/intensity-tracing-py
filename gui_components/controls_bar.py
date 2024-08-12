import os
from PyQt6.QtCore import Qt
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
)
from gui_components.gui_styles import GUIStyles
from gui_components.switch_control import SwitchControl
from gui_components.select_control import SelectControl
from gui_components.input_number_control import InputNumberControl
from gui_components.layout_utilities import draw_layout_separator


class ControlsBar:
    
    @staticmethod  
    def init_gui_controls_layout(controls_row, buttons_row):
        layout_container = QVBoxLayout()
        layout_container.setSpacing(0)
        layout_container.setContentsMargins(0,0,0,0)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0,0,0,0)
        controls_layout.setSpacing(0)
        blank_space = QWidget()
        blank_space.setMinimumHeight(1)
        blank_space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        buttons_qv_box = QVBoxLayout()
        buttons_qv_box.setSpacing(0)
        buttons_qv_box.setContentsMargins(0,0,0,0)
        buttons_qv_box.addLayout(buttons_row)
        controls_layout.addWidget(controls_row)
        controls_layout.addLayout(buttons_qv_box)
        layout_container.addLayout(controls_layout)
        layout_container.addWidget(draw_layout_separator())
        return blank_space, layout_container

 

    @staticmethod
    def create_buttons(
            start_btn_pressed_cb,
            stop_btn_pressed_cb,
            reset_btn_pressed_cb,
            enabled_channels
    ):
        # ACTION BUTTONS
        buttons_row_layout = QHBoxLayout()
        buttons_row_layout.addStretch(1)
        # start button
        start_button = QPushButton("START")
        start_button.setFlat(True)
        start_button.setFixedHeight(55)
        start_button.setFixedWidth(110)
        start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_start_btn_style(start_button)
        start_button.clicked.connect(start_btn_pressed_cb)
        start_button.setEnabled(
            len(enabled_channels) > 0
        )
        buttons_row_layout.addWidget(start_button)
        # stop button
        stop_button = QPushButton("STOP")
        stop_button.setFlat(True)
        stop_button.setFixedHeight(55)
        stop_button.setFixedWidth(110)
        stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_stop_btn_style(stop_button)
        stop_button.setEnabled(False)
        stop_button.clicked.connect(stop_btn_pressed_cb)
        buttons_row_layout.addWidget(stop_button)
        # reset button 
        reset_button = QPushButton("RESET")
        reset_button.setFlat(True)
        reset_button.setFixedHeight(55)
        reset_button.setFixedWidth(110)
        reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        GUIStyles.set_reset_btn_style(reset_button)
        reset_button.setEnabled(True)
        reset_button.clicked.connect(reset_btn_pressed_cb)
        buttons_row_layout.addWidget(reset_button)
        buttons_row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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
            spacing=None
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
    def create_running_mode_control(value, change_cb):
        # Acquisition time mode switch control (Free Running/Fixed)
        running_mode_control = QVBoxLayout()
        inp = SwitchControl(
            active_color="#13B6B4", width=80, height=30, checked=value
        )
        inp.stateChanged.connect(
            (lambda state: change_cb(state))
        )
        q_label = QLabel("Free running:")
        q_label.setStyleSheet("color: #f8f8f8;")
        running_mode_control.addWidget(q_label)
        running_mode_control.addSpacing(6)
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
        show_cps_control = QVBoxLayout()
        show_cps_label = QLabel("Show CPS:")
        show_cps_label.setStyleSheet("color: #f8f8f8;")
        inp = SwitchControl(
            active_color="#8d4ef2",
            width=80, height=30, checked=value
        )
        inp.stateChanged.connect(
            (lambda state: change_cb(state))
        )
        show_cps_control.addWidget(show_cps_label)
        show_cps_control.addSpacing(6)
        show_cps_control.addWidget(inp)

        return show_cps_control, inp
