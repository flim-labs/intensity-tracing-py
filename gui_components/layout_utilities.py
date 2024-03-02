import os

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QFrame,
    QSizePolicy
)

from gui_components.settings import *
from gui_components.logo_utilities import LogoOverlay, TitlebarIcon
from gui_components.gui_styles import GUIStyles


def draw_layout_separator(line_width=1, color="#282828", vertical_space=10):
    spacer_widget = QWidget()
    spacer_widget.setFixedSize(1, vertical_space)

    direction = QFrame.HLine
    separator = QFrame()
    separator.setFrameShape(direction)
    separator.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
    separator.setLineWidth(line_width)
    separator.setStyleSheet(f"QFrame{{color: {color};}}")

    layout = QVBoxLayout()
    layout.addWidget(spacer_widget)
    layout.addWidget(separator)

    container_widget = QWidget()
    container_widget.setLayout(layout)

    return container_widget


def create_logo_overlay(self):
    # Logo overlay
    logo_overlay = LogoOverlay(self)
    logo_overlay.show()
    logo_overlay.update_visibility(self)
    logo_overlay.update_position(logo_overlay)
    logo_overlay.lower()
    return logo_overlay


def init_ui(self, top_utilities_layout):
    # Titlebar logo icon
    TitlebarIcon.setup(self)

    self.setWindowTitle("FlimLabs - INTENSITY TRACING v" + APP_VERSION)
    GUIStyles.customize_theme(self)
    GUIStyles.set_fonts()
    self.resize(APP_DEFAULT_WIDTH, APP_DEFAULT_HEIGHT)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    widget = QWidget()
    main_layout = QVBoxLayout()

    main_layout.addLayout(top_utilities_layout)

    # Charts grid
    charts_grid = QGridLayout()
    main_layout.addLayout(charts_grid)

    widget.setLayout(main_layout)
    scroll_area.setWidget(widget)
    self.setCentralWidget(scroll_area)
    logo_overlay = create_logo_overlay(self)

    return main_layout, logo_overlay, charts_grid
