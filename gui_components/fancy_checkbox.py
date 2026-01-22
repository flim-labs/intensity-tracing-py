from PyQt6.QtCore import pyqtSignal, Qt, QSize, QEvent
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QIcon, QFontMetrics
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy

SELECTED_COLOR = "#8d4ef2"
SELECTED_HOVER_COLOR = "#0053a4"
DISABLED_SELECTED_COLOR = "#2E2E2E"
UNSELECTED_COLOR = "#000000"
DISABLED_COLOR = "lightgrey"
TEXT_COLOR = "#FFFFFF"


CHECKED_COLOR = "#8d4ef2"
UNCHECKED_COLOR = "lightgrey"

SELECTED_COLOR_BUTTON = "#0078D7"



class FancyCheckbox(QWidget):
    toggled = pyqtSignal(bool) 
    labelClicked = pyqtSignal()  

    def __init__(self, text="", label_custom_part="", label_default_part="", label_clickable=False, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  
        self.layout.setSpacing(3)  # Reduced from 5px to 3px to save space  

        self.checkbox = Checkbox(self)
        
        self.label_container = QWidget(self)
        self.label_container.setObjectName("label_container")
        self.label_layout = QHBoxLayout(self.label_container)
        self.label_layout.setContentsMargins(5, 0, 0, 0)  # Reduced right margin from 5px to 0px to save space
        self.label_layout.setSpacing(0)
        
        if label_custom_part:
            # Truncate custom name to 5 characters if longer
            if len(label_custom_part) > 5:
                truncated_custom = label_custom_part[:5] + "..."
            else:
                truncated_custom = label_custom_part
            full_text = f"{truncated_custom} {label_default_part}"
        elif label_default_part:
            full_text = label_default_part
        else:
            full_text = text
        
        self.label = QLabel(full_text, self)
        self.has_custom_name = bool(label_custom_part)
        
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        # Store original parts for dynamic truncation
        self.custom_part = label_custom_part
        self.default_part = label_default_part
        
        self._apply_label_styles(label_clickable, self.has_custom_name)
        
        self.label_layout.addWidget(self.label)
        self.label_layout.addStretch()
        
        self.label_clickable = label_clickable
        self.is_hovering = False

        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if label_clickable:
            self.label_container.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_container.mousePressEvent = self._label_click_handler
            self.label_container.setToolTip("Click to rename channel")
            # Install event filter on label_container for hover effect
            self.label_container.installEventFilter(self)
            # Also set attribute to make it more responsive
            self.label_container.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        else:
            self.label_container.setCursor(Qt.CursorShape.PointingHandCursor)
            self.label_container.mousePressEvent = self.checkbox.mousePressEvent

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label_container)

        self.checkbox.toggled.connect(self.emit_toggled_signal)

    def _apply_label_styles(self, clickable, has_custom):
        """Apply CSS styles to label"""
        base_style = "color: white; font-family: 'Montserrat'; font-size: 13px;"
        
        # Apply base style to label
        self.label.setStyleSheet(base_style)
        
        # Apply base style to container (no hover in CSS to avoid double effect)
        if clickable:
            self.label_container.setStyleSheet("""
                QWidget#label_container {
                    border-radius: 3px;
                    padding: 2px;
                    background-color: transparent;
                }
            """)

    def eventFilter(self, obj, event):
        """Handle hover events for label container"""
        if obj == self.label_container and self.label_clickable:
            if event.type() == QEvent.Type.Enter:
                if not self.is_hovering:  # Only apply once
                    self.is_hovering = True
                    self.label_container.setStyleSheet("""
                        QWidget#label_container {
                            border-radius: 3px;
                            padding: 2px;
                            background-color: rgba(141, 78, 242, 0.2);
                        }
                    """)
            elif event.type() == QEvent.Type.Leave:
                if self.is_hovering:  # Only remove once
                    self.is_hovering = False
                    self.label_container.setStyleSheet("""
                        QWidget#label_container {
                            border-radius: 3px;
                            padding: 2px;
                            background-color: transparent;
                        }
                    """)
        return super().eventFilter(obj, event)
    
    def _label_click_handler(self, event):
        """Handle label click for rename functionality"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.labelClicked.emit()

    def emit_toggled_signal(self, checked):
        self.toggled.emit(checked)  

    def is_checked(self):
        return self.checkbox.is_checked()

    def set_checked(self, checked):
        self.checkbox.set_checked(checked)

    def set_text(self, text):
        """Legacy method for setting simple text"""
        self.label.setText(text)
        self.has_custom_name = False

    def set_text_parts(self, custom_part, default_part):
        """Set custom and default parts separately with dynamic truncation"""
        self.custom_part = custom_part
        self.default_part = default_part
        
        if custom_part:
            self.has_custom_name = True
        else:
            self.has_custom_name = False
        
        # Update the displayed text based on available width
        self._update_label_text()
        
        # Reapply styles
        self._apply_label_styles(self.label_clickable, self.has_custom_name)
    
    def _update_label_text(self):
        """Update label text with dynamic truncation based on available width"""
        if not self.custom_part:
            # No custom name: show full default
            self.label.setText(self.default_part if self.default_part else "")
            return
        
        # Get available width for the label
        available_width = self.label_container.width() - 20  # Account for padding and margins
        
        if available_width <= 0:
            available_width = 80  # Fallback minimum width
        
        font_metrics = QFontMetrics(self.label.font())
        
        # Always reserve space for default part (e.g., " (Ch1)")
        default_text = f" {self.default_part}"
        default_width = font_metrics.horizontalAdvance(default_text)
        
        # Available width for custom part
        available_for_custom = available_width - default_width
        
        # Calculate how much of custom text fits
        custom_text = self.custom_part
        custom_width = font_metrics.horizontalAdvance(custom_text)
        
        if custom_width > available_for_custom:
            # Need to truncate
            ellipsis = "..."
            ellipsis_width = font_metrics.horizontalAdvance(ellipsis)
            available_for_custom -= ellipsis_width
            
            # Find how many characters fit
            truncated = ""
            for i in range(len(custom_text)):
                test_text = custom_text[:i+1]
                if font_metrics.horizontalAdvance(test_text) > available_for_custom:
                    break
                truncated = test_text
            
            # Ensure at least 3 characters are shown before ellipsis
            if len(truncated) < 3 and len(custom_text) >= 3:
                truncated = custom_text[:3]
            
            custom_text = truncated + ellipsis
        
        full_text = f"{custom_text}{default_text}"
        self.label.setText(full_text)
    
    def resizeEvent(self, event):
        """Handle resize to update text truncation"""
        super().resizeEvent(event)
        if hasattr(self, 'custom_part') and self.custom_part:
            self._update_label_text()

    def setEnabled(self, enabled):
        self.checkbox.setEnabled(enabled)
        self.label.setEnabled(enabled)


class Checkbox(QWidget):
    toggled = pyqtSignal(bool) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)  
        self.checked = False
        self.enabled = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.checked:
            outer_color = QColor(CHECKED_COLOR if self.enabled else DISABLED_COLOR)
        else:
            outer_color = QColor(CHECKED_COLOR if self.enabled else DISABLED_COLOR)
        painter.setPen(QPen(outer_color, 1))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawEllipse(1, 1, 18, 18)
        if self.checked:
            inner_color = QColor(CHECKED_COLOR if self.enabled else DISABLED_COLOR)
            painter.setBrush(QBrush(inner_color))
            painter.drawEllipse(4, 4, 12, 12)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.enabled:
            self.checked = not self.checked
            self.update()  
            self.toggled.emit(self.checked)  

    def is_checked(self):
        return self.checked

    def set_checked(self, checked):
        if self.checked != checked:
            self.checked = checked
            self.update()  

    def setEnabled(self, enabled):
        if self.enabled != enabled:
            self.enabled = enabled
            self.update()  


class FancyButton(QPushButton):
    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(text, parent)
        self.selected = False  
        self.initUI(icon_path)

    def initUI(self, icon_path):
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24)) 
        self.setFlat(True)  
        self.updateStyleSheet()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_selected(self, selected):
        self.selected = selected
        self.updateStyleSheet()

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.updateStyleSheet()

    def updateStyleSheet(self):
        bg_color = SELECTED_COLOR_BUTTON if self.selected else UNSELECTED_COLOR
        color = SELECTED_COLOR_BUTTON
        if not self.isEnabled():
            bg_color = "#3c3c3c" if self.selected else "#000000"
            color = "lightgrey"
        hover_color = SELECTED_HOVER_COLOR
        pressed_color = "#003d7a"

        self.setStyleSheet(f"""
            QPushButton {{
                font-family: "Montserrat";
                font-size: 14px;
                font-weight: thin;
                border: 1px solid {color};
                border-radius: 0px;
                color: white;
                padding: 5px;
                background-color: {bg_color};
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)