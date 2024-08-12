import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QPainter
from PyQt6.QtWidgets import QWidget

from gui_components.resource_path import resource_path

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))




class LogoOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.imagePath = "assets/flimlabs-logo.png"  
        self.pixmap = QPixmap(self.imagePath).scaledToWidth(100)
        self.opacity = 0.3
        self.adjustSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)  # Set the painter opacity for translucent drawing
        x = self.width() - self.pixmap.width() - 10  # 10 pixels padding from the right edge
        y = self.height() - self.pixmap.height() - 20  # 20 pixels padding from the bottom edge
        painter.drawPixmap(x, y, self.pixmap)


class TitlebarIcon():
    @staticmethod
    def setup(window):
        window.setWindowIcon(QIcon(resource_path('assets/intensity-tracing-logo.png')))
