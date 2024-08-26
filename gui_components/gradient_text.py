from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QPen, QTextOption
from PyQt6.QtWidgets import QLabel


class GradientText(QLabel):
    def __init__(self, parent=None, text="", colors: list[(float, str)] = None, stylesheet=""):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet(stylesheet)
        self.colors = colors if colors else [(0.0, "red"), (1.0, "blue")]
        self.draw_shadow = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        self.draw_shadow = True
        self.update()

    def mouseReleaseEvent(self, event):
        self.draw_shadow = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setWindow(0, 0, self.width() + 6, self.height() + 3)

        if self.draw_shadow:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("white"), 0))
            painter.drawText(QRectF(3, -2, self.width(), self.height()), self.text(),
                             QTextOption(Qt.AlignmentFlag.AlignLeft))

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        for position, color in self.colors:
            gradient.setColorAt(position, QColor(color))
        painter.setPen(QPen(gradient, 0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawText(QRectF(0, 0, self.width(), self.height()), self.text(),
                         QTextOption(Qt.AlignmentFlag.AlignLeft))
