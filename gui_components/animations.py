from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, QAbstractAnimation


class VibrantAnimation:
    def __init__(self, widget, start_color="", stop_color="", bg_color="", margin_top=""):
        self.widget = widget
        self.start_color = start_color
        self.stop_color = stop_color
        self.bg_color = bg_color
        self.margin_top = margin_top
        self.animation = QPropertyAnimation(widget, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.animation.setLoopCount(-1)
        self.original_pos = widget.pos()  
        
    def start(self, amplitude=10, duration=50):
        if self.animation.state() == QAbstractAnimation.State.Running:
            return
        self.original_pos = self.widget.pos()
        self.widget.setStyleSheet(        
                    f"QLabel {{ color : {self.start_color}; font-size: 42px; font-weight: bold; background-color: {self.bg_color};}}"
                )         
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.original_pos)
        self.animation.setKeyValueAt(0.5, QPoint(self.original_pos.x() + amplitude, self.original_pos.y()))
        self.animation.setEndValue(self.original_pos)
        self.animation.start()

    def stop(self):
        if self.animation.state() == QAbstractAnimation.State.Running:
            self.widget.setStyleSheet(        
                        f"QLabel {{ color : {self.stop_color}; font-size: 42px; font-weight: bold; background-color: {self.bg_color};}}"
                    )              
            self.animation.stop()
            self.widget.move(self.original_pos)
        