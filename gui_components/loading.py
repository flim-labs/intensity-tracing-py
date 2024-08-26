from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import  QMovie
from PyQt6.QtCore import Qt, QSize

from gui_components.gui_styles import GUIStyles
from gui_components.resource_path import resource_path

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = parent 
        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint) 
        loading_widget = self.create_loading_row()
        overlay_layout = QVBoxLayout(self)
        overlay_layout.addWidget(loading_widget)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.setLayout(overlay_layout)
        self.hide()

    def create_loading_row(self):
        loading_widget = QWidget()
        loading_widget.setObjectName("loading_widget")
        loading_widget.setStyleSheet(GUIStyles.set_loading_widget_style())
        loading_row = QHBoxLayout()
        loading_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_row.addSpacing(20)
        self.loading_text = QLabel("Processing data...")
        self.loading_text.setStyleSheet(
            "font-family: Montserrat; font-size: 30px; font-weight: bold; color: #50b3d7"
        )
        loading_gif = QMovie(resource_path("assets/loading.gif"))
        self.gif_label = QLabel()
        self.gif_label.setMovie(loading_gif)
        loading_gif.setScaledSize(QSize(50, 50))
        loading_gif.start()
        loading_row.addWidget(self.loading_text)
        loading_row.addSpacing(5)
        loading_row.addWidget(self.gif_label)
        loading_widget.setLayout(loading_row)
        return loading_widget     
    
    def set_loading_text(self, text):
        self.loading_text.setText(text)   

    def toggle_overlay(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_() 

    def resize_overlay(self, rect):
        self.setGeometry(self.app.rect())
        self.raise_()  