from functools import partial
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
import flim_labs

from gui_components.gui_styles import GUIStyles
from gui_components.resource_path import resource_path
from gui_components.settings import CHECK_CARD_BUTTON, CHECK_CARD_MESSAGE, CHECK_CARD_WIDGET


current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path))


class CheckCard(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        widget_container = QWidget()
        widget_container.setContentsMargins(0,0,0,0)
        layout_container = QVBoxLayout()
        layout_container.setContentsMargins(0,0,0,0)
        layout_container.setSpacing(0)
        # Check button
        self.check_button = QPushButton(" CHECK DEVICE")
        self.check_button.setIcon(QIcon(resource_path("assets/card-icon.png")))
        self.check_button.setFixedHeight(40)
        self.check_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_button.clicked.connect(partial(CheckCard.check_card_connection, self.app))
        GUIStyles.set_reset_btn_style(self.check_button)
        self.app.widgets[CHECK_CARD_BUTTON] = self.check_button
        # Check message
        self.check_message = QLabel("")
        self.check_message.setStyleSheet(GUIStyles.check_card_message(color="#285da6"))
        self.check_message.setFixedHeight(36)
        self.app.widgets[CHECK_CARD_MESSAGE] = self.check_message
        
        self.layout.addWidget(self.check_button)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.check_message)
        self.check_message.hide()
     
        layout_container.addLayout(self.layout)
        widget_container.setLayout(layout_container)
        self.setLayout(layout_container)
        self.app.widgets[CHECK_CARD_WIDGET] = self

    @staticmethod
    def update_check_message(app, message, error):
        if CHECK_CARD_MESSAGE in app.widgets:
            app.widgets[CHECK_CARD_MESSAGE].setText(
                message if error else f"Card ID: {message}"
            )
            app.widgets[CHECK_CARD_MESSAGE].setStyleSheet(
                GUIStyles.check_card_message(
                    color="#8d4ef2" if not error else "#f72828"
                )
            )
            if not (app.widgets[CHECK_CARD_MESSAGE].isVisible()):
                app.widgets[CHECK_CARD_MESSAGE].setVisible(True)

    @staticmethod
    def check_card_connection(app):
        try:
            card_serial_number = flim_labs.check_card()
            CheckCard.update_check_message(app, str(card_serial_number), error=False)
        except Exception as e:
            if str(e) == "CardNotFound":
                CheckCard.update_check_message(app, "Card Not Found", error=True)
            else:
                CheckCard.update_check_message(app, str(e), error=True)
