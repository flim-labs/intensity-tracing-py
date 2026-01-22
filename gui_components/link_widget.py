import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))


class LinkWidget(QWidget):
    def __init__(self, icon_filename=None, text=None, parent=None, icon_dimensions=30, icon_hover_dimensions=36,
                 link='https://flim-labs.github.io/intensity-tracing-py/v2.3/#gui-usage'):
        super(LinkWidget, self).__init__(parent)

        layout = QHBoxLayout()

        if text:
            text_label = QLabel(text)
            text_label.setStyleSheet("color: #f8f8f8;")
            layout.addWidget(text_label)
            layout.addSpacing(10)
        self.link_label = QLabel()
        self.link = link
        if icon_filename:
            original_icon_pixmap = QPixmap(icon_filename).scaled(icon_dimensions, icon_dimensions, 
                                                                Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation)
            self.link_label.setPixmap(original_icon_pixmap)

        layout.addWidget(self.link_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        if text:
            text_label.mousePressEvent = self.open_link
        self.link_label.mousePressEvent = self.open_link

    def open_link(self, event):
        QDesktopServices.openUrl(QUrl(self.link))
