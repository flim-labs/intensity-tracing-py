import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import  QLabel, QHBoxLayout, QWidget
from PyQt5.QtGui import QDesktopServices

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))


class LinkWidget(QWidget):
    def __init__(self, icon_filename=None, text=None, parent=None, icon_dimensions=25, icon_hover_dimensions=28, link='https://flim-labs.github.io/intensity-tracing-py/v1.3/#gui-usage'):
        super(LinkWidget, self).__init__(parent)

        layout = QHBoxLayout()

        if text:
            text_label = QLabel(text)
            layout.addWidget(text_label)

        layout.addSpacing(10)

        self.link_label = QLabel()
        self.link = link

        if icon_filename:
            icon_path = os.path.join(project_root, 'assets', icon_filename)
            original_icon_pixmap = QPixmap(icon_path).scaled(icon_dimensions, icon_dimensions, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.link_label.setPixmap(original_icon_pixmap)

        layout.addWidget(self.link_label)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        if text:
            text_label.mousePressEvent = self.open_link
        self.link_label.mousePressEvent = self.open_link

    def open_link(self, event):
        QDesktopServices.openUrl(QUrl(self.link))