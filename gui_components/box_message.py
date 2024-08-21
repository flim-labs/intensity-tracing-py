from PyQt6.QtWidgets import QMessageBox


class BoxMessage:
    @staticmethod
    def setup(title, msg, icon, style, test_mode=False):
        message_box = QMessageBox()
        message_box.setIcon(icon)
        message_box.setText(msg)
        message_box.setWindowTitle(title)
        message_box.setStyleSheet(style)
        if test_mode:
            message_box.show()
        else:
            message_box.exec()
        return message_box

    @staticmethod
    def close(message_box):
        message_box.accept()
