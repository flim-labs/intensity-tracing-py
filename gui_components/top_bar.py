import os
from PyQt6.QtCore import Qt
from gui_components import resource_path
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, ".."))

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QSizePolicy
)
from PyQt6.QtGui import QPixmap
from gui_components.gui_styles import GUIStyles
from gui_components.switch_control import SwitchControl
from gui_components.gradient_text import GradientText
from gui_components.link_widget import LinkWidget
from gui_components.settings import *


class TopBar:
    
    @staticmethod    
    def create_header_layout(
            logo_and_title,
            export_data_widget,
    ):
        header_layout = QHBoxLayout()
        # Header row: Link to User Guide
        app_guide_link_widget = LinkWidget(
            icon_filename=resource_path.resource_path("assets/info-icon.png"), text="User Guide", link=GUI_GUIDE_LINK
        )
        app_guide_link_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addLayout(logo_and_title)
        header_layout.addStretch(1)
        header_layout.addWidget(export_data_widget)
        header_layout.addSpacing(20)
        header_layout.addWidget(app_guide_link_widget)
        return header_layout
 
 

    @staticmethod
    def create_logo_and_title(self):
        title_row = QHBoxLayout()
        pixmap = QPixmap(
            resource_path.resource_path("assets/intensity-tracing-logo-white.png")
        ).scaledToWidth(40)
        ctl = QLabel(pixmap=pixmap)
        title_row.addWidget(ctl)
        title_row.addSpacing(10)
        ctl = GradientText(self,
                           text=APP_NAME,
                           colors=[(0.5, "#23F3AB"), (1.0, "#8d4ef2")],
                           stylesheet=GUIStyles.set_main_title_style())
        ctl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.addWidget(ctl)
        title_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctl = QWidget()
        ctl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_row.addWidget(ctl)
        return title_row
    

    @staticmethod
    def create_export_data_input(value, change_cb):
        # Link to export data documentation
        info_link_widget = LinkWidget(
            icon_filename=resource_path.resource_path("assets/info-icon.png"),
            link=EXPORT_DATA_GUIDE_LINK,
        )
        info_link_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        info_link_widget.show()

        # Export data switch control
        export_data_control = QHBoxLayout()
        export_data_label = QLabel("Export data:")
        export_data_label.setStyleSheet("color: #f8f8f8;")
        inp = SwitchControl(
            active_color="#FB8C00", width=70, height=30, checked=value)
        inp.toggled.connect(change_cb)
        export_data_control.addWidget(export_data_label)
        export_data_control.addSpacing(8)
        export_data_control.addWidget(inp)

        return info_link_widget, export_data_control, inp

    @staticmethod
    def create_file_size_info_row(bin_file_size, bin_file_size_label, write_data, cb_calc_file_size):
        file_size_info_layout = QHBoxLayout()
        bin_file_size_label.setText("File size: " + str(bin_file_size))
        bin_file_size_label.setStyleSheet("QLabel { color : #FFA726; }")

        file_size_info_layout.addWidget(bin_file_size_label)
        bin_file_size_label.show() if write_data is True else bin_file_size_label.hide()
        cb_calc_file_size()

        return file_size_info_layout
  
