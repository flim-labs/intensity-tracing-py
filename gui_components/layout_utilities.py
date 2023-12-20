from PyQt5.QtWidgets import QWidget, QFrame, QSizePolicy, QVBoxLayout


def draw_layout_separator(line_width=1, color="#282828", vertical_space=10):
    spacer_widget = QWidget()
    spacer_widget.setFixedSize(1, vertical_space)

    direction = QFrame.HLine
    separator = QFrame()
    separator.setFrameShape(direction)
    separator.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
    separator.setLineWidth(line_width)
    separator.setStyleSheet(f"QFrame{{color: {color};}}")
    
    layout = QVBoxLayout()
    layout.addWidget(spacer_widget)
    layout.addWidget(separator)

    container_widget = QWidget()
    container_widget.setLayout(layout)

    return container_widget