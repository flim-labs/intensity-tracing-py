from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QStyleFactory, QWidget, QLabel

class GUIStyles:
    @staticmethod
    def set_default_theme(theme):
        QApplication.setStyle(QStyleFactory.create(theme))
        
    @staticmethod        
    def customize_theme(window, bg = QColor(28, 28, 28, 128), fg = QColor(255, 255, 255)):
        palette = QPalette()
        background_color = bg
        palette.setColor(QPalette.ColorRole.Window, background_color)
        palette.setColor(QPalette.ColorRole.WindowText, fg)
        window.setPalette(palette)  
        window.setStyleSheet(
            """
        QLabel {
            color: #f8f8f8;
            font-family: "Montserrat";
        }
        """
        )  

    @staticmethod
    def set_fonts(font_name="Montserrat", font_size=10):
        general_font = QFont("Montserrat", 10)
        QApplication.setFont(general_font)

    @staticmethod
    def set_fonts_deep(root):
        if root is None:
            return
        for child in root.findChildren(QWidget):
            if child.objectName() == "font":
                child.setFont(QFont("Montserrat", 14, QFont.Weight.Thin))
            if child.metaObject().className() == "QPushButton":
                child.setFont(QFont("Montserrat", 14, QFont.Weight.Thin))
            GUIStyles.set_fonts_deep(child)
        for child in root.findChildren(QLabel):
            child.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))
            GUIStyles.set_fonts_deep(child)
            

    @staticmethod
    def set_main_title_style():
        return """
            QLabel{
                color: #23F3AB;
                font-family: "Montserrat";
                font-size: 40px;
                font-weight: 100;
                font-style: italic;
            }
        """

    @staticmethod
    def button_style(color_base, color_border, color_hover, color_pressed):
        return f"""
            QPushButton {{
                background-color: {color_base};
                border: 1px solid {color_border};
                font-family: "Montserrat";
                color: white;
                letter-spacing: 0.1em;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}

        
            QPushButton:hover {{
                background-color: {color_hover};
                border: 2px solid {color_hover};
            }}

            QPushButton:focus {{
                background-color: {color_pressed};
                border: 2px solid {color_pressed};
            }}

            QPushButton:pressed {{
                background-color: {color_pressed};
                border: 2px solid {color_pressed};
            }}
            
            QPushButton:disabled {{
                background-color: #cecece;
                border: 2px solid #cecece;
                color: #8c8b8b;
            }}
        """

    @staticmethod
    def _set_button_style(button, color_dict):
        color_base, color_border, color_hover, color_pressed = (
            color_dict["base"],
            color_dict["border"],
            color_dict["hover"],
            color_dict["pressed"],
        )
        button.setStyleSheet(
            GUIStyles.button_style(
                color_base, color_border, color_hover, color_pressed
            )
        )

    @staticmethod
    def set_start_btn_style(button):
        color_dict = {
            "base": "#13B6B4",
            "border": "#13B6B4",
            "hover": "#1EC99F",
            "pressed": "#1AAE88",
        }
        GUIStyles._set_button_style(button, color_dict)

    @staticmethod
    def set_stop_btn_style(button):
        color_dict = {
            "base": "#FFA726",
            "border": "#FFA726",
            "hover": "#FB8C00",
            "pressed": "#E65100",
        }
        GUIStyles._set_button_style(button, color_dict)

    @staticmethod
    def set_reset_btn_style(button):
        color_dict = {
            "base": "#8d4ef2",
            "border": "#8d4ef2",
            "hover": "#a179ff",
            "pressed": "#6b3da5",
        }
        GUIStyles._set_button_style(button, color_dict)

    @staticmethod
    def set_config_btn_style(button):
        color_dict = {
            "base": "black",
            "border": "#FFA726",
            "hover": "#FB8C00",
            "pressed": "#E65100",
        }
        GUIStyles._set_button_style(button, color_dict)

    @staticmethod
    def set_checkbox_style():
        return """
            QCheckBox {
                spacing: 5px;
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 14px;
                letter-spacing: 0.1em;
                border: 1px solid #252525;
                border-radius: 5px;
                padding: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;  
            }

            QCheckBox::indicator:unchecked {
                background-color: #6b6a6a;
            }

            QCheckBox::indicator:checked {
                background-color: #8d4ef2;
            }
        """

    @staticmethod
    def set_input_number_style():
        return """
            QDoubleSpinBox, QSpinBox {
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 14px;
                padding: 8px;
                min-width: 100px;
                border: 1px solid #3b3b3b;
                border-radius: 5px;
                background-color: transparent;
            }
            QDoubleSpinBox:disabled, QSpinBox:disabled {
            color: #404040;  
            border-color: #404040;
            }        
        """

    @staticmethod
    def set_input_select_style():
        return """
            QComboBox {
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 14px;
                padding: 8px;
                min-width: 100px;
                border: 1px solid #3b3b3b;
                border-radius: 5px;
                background-color: transparent;
            }
            QSpinBox:disabled {
                color: #404040;  
                border-color: #404040;
            } 
            QComboBox:on { 
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }

           QComboBox QAbstractItemView {
            font-family: "Montserrat";
            border: 1px solid #3b3b3b;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
            background-color: #181818;
            color: #f8f8f8;
            selection-background-color: #8d4ef2;
            }   
        """
        
    @staticmethod    
    def set_input_text_style():
        return """
        QLineEdit  {
                color: #13B6B4;
                font-family: "Montserrat";
                font-size: 14px;
                padding: 8px;
                min-width: 60px;
                border: 1px solid #13B6B4;
                border-radius: 5px;
                background-color: transparent;
            }
            QLineEdit:disabled, QLineEdit:disabled {
            color: #404040;  
            border-color: #3c3c3c;
            }        
        """           

    @staticmethod
    def set_msg_box_style():
        return """
            QMessageBox {
                background-color: #080808;   
            }
            QMessageBox QLabel {
                color: #f8f8f8;
                font-family: "Montserrat";
                font-weight: 300;
                font-size: 16px;
            }
            QMessageBox QIcon {
                width: 20px;
            }  
            QMessageBox QPushButton {
                background-color: #181818;
                color: white;
                width: 150px;
                padding: 12px;
                font-size: 14px;
                font-family: "Montserrat";
            }   
                 
        """

    @staticmethod
    def set_cps_label_style():
        return """
            QLabel{
                color: white;
                font-weight: 700;
                font-family: "Montserrat";
                font-size: 22px;
            }
        """

    @staticmethod
    def set_context_menu_style(base, selected, pressed):
        return f"""

        QWidget {{
            background-color: #181818;  
        }}
        
        QMenu {{

            margin: 0;   
            padding: 5px;
            border-radius: 20px;
            background: #181818;       
        }}

        QMenu::item {{
            background-color: {base}; 
            color: white; 
            height: 20px;
            width: 60px;
            margin: 5px 0px 5px 0px;
            border-radius: 4px;   
            font-family: "Montserrat";
            font-size: 12px;
            font-weight: bold;
            padding:10px 13px 10px 10px;
            min-width:120px
        }}

        QMenu::item:selected {{
            background-color: {selected};  
         }}
        QMenu::item:pressed {{
            background-color: {pressed};  
         }}

        """
    @staticmethod         
    def toggle_collapse_button():
        return """
            QPushButton{
                background-color: transparent;
                border-radius: 15px;
                qproperty-iconSize: 15px;
                border: 1px solid #808080;
            } 
        """   
        
    @staticmethod           
    def channels_btn_style(base, hover, pressed, text="white"):
        return f"""
            QPushButton, QPushButton:released {{
                font-family: "Montserrat";
                letter-spacing: 0.1em;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                background-color: {base};
                border: 2px solid {base};
                color: {text};
            }}
            
            QPushButton:hover {{
                background-color: {hover};
                border: 2px solid {hover};
            }}

            QPushButton:focus {{
                background-color: {base};
                border: 2px solid {base};
            }}

            QPushButton:pressed {{
                background-color: {base};
                border: 2px solid {base};
            }}

            QPushButton:disabled {{
                background-color: #cecece;
                border: 2px solid #cecece;
                color: #8c8b8b;
            }}
        """
        
    @staticmethod   
    def plots_config_popup_style():
        return """
            QWidget {
                background-color: #141414;
                color: #6e6b6b;
                font-family: Montserrat;
                font-size: 14px;
            }
            QLabel#prompt_text {
                color: white;
                font-size: 18px;
            } 
        """
        
    @staticmethod        
    def set_simple_checkbox_style(color):
        return f"""
            QCheckBox {{
                spacing: 5px;
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 14px;
                letter-spacing: 0.1em;
                border-radius: 5px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border-radius: 7px;  
            }}

            QCheckBox::indicator:unchecked {{
                background-color: #6b6a6a;
            }}

            QCheckBox::indicator:checked {{
                background-color: {color};
            }}
        """  
        
    @staticmethod            
    def checkbox_wrapper_style():
        return """
            QWidget#ch_checkbox_wrapper, QWidget#simple_checkbox_wrapper {
                border: 1px solid #3b3b3b;
                background-color: transparent;
                padding: 0;
            } 
            QWidget#simple_checkbox_wrapper {
                border-radius: 5px;
            } 
            QWidget{
                color: #f8f8f8;
                font-family: "Montserrat";
                font-size: 12px;
                padding: 0;
            }        
        """ 
        
    @staticmethod  
    def set_cps_label_style():
        return """
            QLabel{
                font-weight: 700;
                font-family: "Montserrat";
                font-size: 40px;
                color: #a877f7;
            }
        """ 
    
    @staticmethod       
    def only_cps_widget():
        return """
            QWidget#container{
                padding: 12px;
                border: 1px solid #3b3b3b;
                margin-right: 8px;
                margin-left: 8px;
            }
            QLabel#cps{
                font-weight: 700;
                font-family: "Montserrat";
                font-size: 34px;
                color: #FB8C00;
            }
            QLabel#ch{
                font-size: 24px;
                color: #cecece;
                margin-left: 8px;
            }
        """        
        
    @staticmethod   
    def acquire_read_btn_style():
        return f"""
            QPushButton {{
                font-family: "Montserrat";
                letter-spacing: 0.1em;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: bold;;
                min-width: 60px;
            }}
            QPushButton#acquire_btn{{ 
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;   
            }}
            QPushButton#read_btn{{  
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                
            }}
        """ 
        
    @staticmethod
    def acquisition_time_countdown_style():
        return """
            QLabel {
                color: #13B6B4;
                font-size: 16px;
                padding: 0 8px;
            }
        """                               
         
