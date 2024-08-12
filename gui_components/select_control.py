from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QComboBox


class SelectControl:
    @staticmethod
    def setup(label, selectedValue, container, options, event_callback, spacing=20, control_layout="vertical"):
        q_label = QLabel(label)
        q_label.setStyleSheet("color: #f8f8f8;")
        control = QVBoxLayout() if control_layout == 'vertical' else QHBoxLayout()
        input = QComboBox()
        for value in options:
            input.addItem(value)
        input.setCurrentText(selectedValue)
        input.currentIndexChanged.connect(event_callback)
        control.addWidget(q_label)
        control.addWidget(input)
        container.addLayout(control)
        if spacing:
            container.addSpacing(spacing)
        return control, input
