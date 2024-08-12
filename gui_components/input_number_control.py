from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QSpinBox


class InputNumberControl:
    @staticmethod
    def setup(
            label,
            min,
            max,
            value,
            row,
            event_callback,
            spacing=20,
            control_layout="vertical",
    ):
        q_label = QLabel(label)
        q_label.setStyleSheet("color: #f8f8f8;")
        control = QVBoxLayout() if control_layout == "vertical" else QHBoxLayout()
        input = QSpinBox()
        input.setRange(min, max)
        if value:
            input.setValue(value)
        input.valueChanged.connect(event_callback)
        control.addWidget(q_label)
        control.addWidget(input)
        row.addLayout(control)
        if spacing:
            row.addSpacing(20)
        return control, input
