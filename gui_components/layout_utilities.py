import os

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
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
    plot_grids_container = QHBoxLayout()
    plot_grids_container.setSpacing(0)
    plot_grids_container.setAlignment(Qt.AlignmentFlag.AlignLeft)
    intensity_widget = create_intensity_layout(self)
    plot_grids_container.addWidget(intensity_widget)
    main_layout.addLayout(plot_grids_container)
    main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.layouts[MAIN_LAYOUT] = main_layout
    self.layouts[PLOT_GRIDS_CONTAINER] = plot_grids_container
    widget.setLayout(main_layout)
    scroll_area.setWidget(widget)
    self.setCentralWidget(scroll_area)

    return main_layout, plot_grids_container



def create_intensity_layout(app):    
    intensity_widget = QWidget()
    intensity_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    app.widgets[INTENSITY_WIDGET_WRAPPER] = intensity_widget
    intensity_h_box = QHBoxLayout()
    intensity_plots_grid = QGridLayout()
    only_cps_grid = QGridLayout()
    intensity_h_box.addLayout(intensity_plots_grid)
    intensity_h_box.addLayout(only_cps_grid)
    intensity_widget.setLayout(intensity_h_box)
    app.layouts[INTENSITY_PLOTS_GRID] = intensity_plots_grid
    app.layouts[INTENSITY_ONLY_CPS_GRID] = only_cps_grid
    return intensity_widget