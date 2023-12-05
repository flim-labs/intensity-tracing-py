import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path, '..'))

class LogoOverlay(QWidget):
    def __init__(self, parent=None):
        super(LogoOverlay, self).__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
   
        logo_path = os.path.join(project_root, 'assets', 'flimlabs-logo.png')
    
        self.logo_label = QLabel(self, pixmap=QPixmap(logo_path).scaledToWidth(100))
        layout = QVBoxLayout(self)
        layout.addWidget(self.logo_label)
        self.setLayout(layout)
        self.adjustSize()

    def update_position(self, window):
        self.move(window.width() - self.width() - 10, window.height() - self.height() - 30)

    def update_visibility(self, window):
        self.setVisible(500 <= window.height() <= 2000)



class TitlebarIcon():  
    @staticmethod
    def setup(window):
        icon_path = os.path.join(project_root, 'assets', 'flimlabs-icon.png')
        window.setWindowIcon(QIcon(icon_path))

          