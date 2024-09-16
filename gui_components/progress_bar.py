from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QApplication,
    QHBoxLayout,
)
from PyQt6.QtCore import pyqtSignal
from typing import Literal, Optional

from gui_components.gui_styles import GUIStyles


class ProgressBar(QWidget):
    
    complete = pyqtSignal() 

    def __init__(
        self,
        label_text: str = None,
        color: str = "#FFA726",
        visible: bool = True,
        enabled: bool = True,
        stylesheet: str  = None,
        layout_type: Literal["horizontal", "vertical"] = "vertical",
        spacing: int = 10,
        progress_bar_height: int  = 15,
        progress_bar_width: int  = None,
        indeterminate: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.color = color
        self.indeterminate = indeterminate

        # Initialize layout based on layout_type
        if layout_type == "horizontal":
            self.layout = QHBoxLayout()
        else:
            self.layout = QVBoxLayout()
            
        self.label_layout = QHBoxLayout()
        self.label_layout.setContentsMargins(0,0,0,0)   
        self.label_layout.setSpacing(0) 

        self.layout.setContentsMargins(0, 0, 0, 0)
       
        # Set the spacing between widgets in the layout if label_text is provided
        if label_text is not None:
            self.layout.setSpacing(spacing)

        # Create and configure the label if label_text is provided
        if label_text is not None:
            self.label = QLabel(label_text)

        # Create and configure the progress bar
        self.progress_bar = QProgressBar()
        if progress_bar_height is not None:
            self.progress_bar.setFixedHeight(progress_bar_height)
        if progress_bar_width is not None:
            self.progress_bar.setFixedWidth(progress_bar_width)

        # Add widgets to the layout
        if layout_type == "horizontal":
            self.layout.addWidget(self.progress_bar)

        if label_text is not None:
            self.label_layout.addWidget(self.label)
    
        if layout_type == "horizontal":
            if label_text is not None:
                self.layout.addLayout(self.label_layout)
        else:
            if label_text is not None:
                self.layout.addLayout(self.label_layout)
            self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)
        self.set_visible(visible)
        self.set_enabled(enabled)
        self.set_style(stylesheet)

        # Set the progress bar to indeterminate mode if specified
        if indeterminate:
            self.set_indeterminate_mode(True)

    def set_indeterminate_mode(self, state: bool) -> None:
        if state:
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
        else:
            self.progress_bar.setRange(0, 100)  # Switch back to determinate mode
        QApplication.processEvents()

    def update_progress(
        self, current_value: int, total_value: int, label_text: Optional[str] = None
    ) -> None:
        if not self.indeterminate:
            progress_value = (current_value / float(total_value)) * 100
            self.progress_bar.setValue(int(progress_value))
            if label_text:
                self.label.setText(label_text)
            
            # Emit signal if progress is complete
            if progress_value >= 100:
                self.complete.emit()            
            QApplication.processEvents()

    def clear_progress(self) -> None:
        if not self.indeterminate:
            self.progress_bar.setValue(0)
            self.label.clear()
            QApplication.processEvents()
        
    def get_value(self) -> int:
        return self.progress_bar.value()        

    def set_visible(self, visible: bool) -> None:
        self.setVisible(visible)
        QApplication.processEvents()

    def set_enabled(self, state: bool) -> None:
        self.progress_bar.setEnabled(state)
        QApplication.processEvents()

    def set_style(self, stylesheet: str) -> None:
        self.setStyleSheet(
            stylesheet
            if stylesheet is not None
            else GUIStyles.progress_bar_style(self.color)
        )