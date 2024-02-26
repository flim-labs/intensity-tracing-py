from PyQt5.QtWidgets import QMessageBox

class BoxMessage:
    @staticmethod
    def setup(title, msg, icon, style):
        message_box = QMessageBox()
        message_box.setIcon(icon)
        message_box.setText(msg)
        message_box.setWindowTitle(title)
        message_box.setStyleSheet(style)
        message_box.show()
        return message_box

    @staticmethod    
    def close(message_box):
        message_box.accept()    