import sys
import os
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QDesktopServices

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))

class LinkWidget(QWidget):
    def __init__(self, icon_filename=None, text=None, parent=None, icon_dimensions=25, icon_hover_dimensions=28, link='https://github.com/flim-labs/flim-labs.github.io/blob/main/products/intensity-tracing/index.md#exported-data-visualization'):
        super(LinkWidget, self).__init__(parent)

        self.link_label = QLabel()
        self.link = link 

        if icon_filename:
            icon_path = os.path.join(project_root, 'assets', icon_filename)
            self.original_icon_pixmap = QPixmap(icon_path).scaled(icon_dimensions, icon_dimensions, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.link_label.setPixmap(self.original_icon_pixmap)

        if text:
            self.link_label.setText(text)

        self.link_label.setAlignment(Qt.AlignCenter)
        self.link_label.mousePressEvent = self.open_link


        layout = QVBoxLayout()
        layout.addWidget(self.link_label)
        self.setLayout(layout)


    def open_link(self, event):
        QDesktopServices.openUrl(QUrl(self.link))