"""
Rename Channel Modal Dialog
Allows users to set custom names for channels.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from gui_components.channel_name_utils import validate_channel_name


class RenameChannelModal(QDialog):
    """
    Modal dialog for renaming a channel.
    Emits a signal with the new name when saved.
    """
    
    channelRenamed = pyqtSignal(int, str)  # Emits (channel_id, new_name)
    
    def __init__(self, channel_id, current_name="", parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.current_name = current_name
        
        self.setWindowTitle("Rename Channel")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #f8f8f8;
            }
            QLabel {
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 13px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                color: #f8f8f8;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-family: "Montserrat";
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #773344;
            }
            QPushButton {
                background-color: #8d4ef2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-family: "Montserrat";
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9d5eff;
            }
            QPushButton:pressed {
                background-color: #7d3ed2;
            }
            QPushButton#cancelButton {
                background-color: #444;
            }
            QPushButton#cancelButton:hover {
                background-color: #555;
            }
            QPushButton#cancelButton:pressed {
                background-color: #333;
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel(f"Enter custom name for Channel {self.channel_id + 1}")
        title_font = QFont("Montserrat", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description label
        desc_label = QLabel("Leave empty to use default channel name.")
        desc_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(desc_label)
        
        # Input field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter channel name...")
        self.name_input.setText(self.current_name)
        self.name_input.setMaxLength(50)
        self.name_input.selectAll()
        layout.addWidget(self.name_input)
        
        # Error label (initially hidden)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6b6b; font-size: 11px;")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        
        save_button = QPushButton("Save")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.clicked.connect(self._on_save)
        save_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Focus on input field
        self.name_input.setFocus()
        
        # Connect Enter key to save
        self.name_input.returnPressed.connect(self._on_save)
    
    def _on_save(self):
        """Handle save button click"""
        new_name = self.name_input.text().strip()
        
        # Validate if not empty
        if new_name and not validate_channel_name(new_name):
            self.error_label.setText("Invalid name. Maximum 50 characters allowed.")
            self.error_label.show()
            return
        
        # Emit signal with new name (empty string if cleared)
        self.channelRenamed.emit(self.channel_id, new_name)
        self.accept()
    
    @staticmethod
    def show_rename_dialog(channel_id, current_name="", parent=None):
        """
        Static method to show the rename dialog.
        Returns the new name if saved, None if cancelled.
        """
        dialog = RenameChannelModal(channel_id, current_name, parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.name_input.text().strip()
        return None

