
import os
import re
import json
import flim_labs
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QHBoxLayout, QMessageBox, QGridLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import QPropertyAnimation, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
from gui_components.data_export_controls import DataExportActions
from gui_components.intensity_tracing_controller import IntensityTracing, IntensityTracingOnlyCPS, IntensityTracingPlot
from gui_components.logo_utilities import TitlebarIcon
from gui_components.resource_path import resource_path
from gui_components.gui_styles import GUIStyles
from gui_components.controls_bar import ControlsBar
from gui_components.messages_utilities import MessagesUtilities
from  gui_components.box_message import BoxMessage
from gui_components.settings import *
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_path))

class CollapseButton(QWidget):
    def __init__(self, collapsible_widget, parent=None):
        super().__init__(parent)
        self.collapsible_widget = collapsible_widget
        self.collapsed = True
        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon(resource_path("assets/arrow-up-dark-grey.png")))
        self.toggle_button.setFixedSize(30, 30) 
        self.toggle_button.setStyleSheet(GUIStyles.toggle_collapse_button())
        self.toggle_button.clicked.connect(self.toggle_collapsible)
        self.toggle_button.move(self.toggle_button.x(), self.toggle_button.y() -100)
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.toggle_button)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        self.animation = QPropertyAnimation(self.collapsible_widget, b"maximumHeight")
        self.animation.setDuration(300)

    def toggle_collapsible(self):
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.collapsible_widget.sizeHint().height())
            self.toggle_button.setIcon(QIcon(resource_path("assets/arrow-up-dark-grey.png")))
        else:
            self.animation.setStartValue(self.collapsible_widget.sizeHint().height())
            self.animation.setEndValue(0)
            self.toggle_button.setIcon(QIcon(resource_path("assets/arrow-down-dark-grey.png")))
        self.animation.start()
       
       
       


class ActionButtons(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        
        layout = self.create_buttons()
        self.setLayout(layout)

    def create_buttons(self):        
        buttons_row_layout, start_button, stop_button, reset_button = ControlsBar.create_buttons(
            self.start_button_pressed,
            self.stop_button_pressed,
            self.reset_button_pressed,
            self.app.enabled_channels
        )
        self.app.control_inputs[START_BUTTON] = start_button
        self.app.control_inputs[STOP_BUTTON] = stop_button
        self.app.control_inputs[RESET_BUTTON] = reset_button
        return buttons_row_layout 

    def start_button_pressed(self):
        open_popup = len(self.app.intensity_plots_to_show) == 0
        if open_popup: 
            popup = PlotsConfigPopup(self.app, start_acquisition=True)
            popup.show()
        else: 
            ButtonsActionsController.start_button_pressed(self.app)       

    def stop_button_pressed(self):
        ButtonsActionsController.stop_button_pressed(self.app)

    def reset_button_pressed(self):
        ButtonsActionsController.reset_button_pressed(self.app)  
        
        
        
class ButtonsActionsController:
    @staticmethod
    def start_button_pressed(app):
        ButtonsActionsController.clear_intensity_grid_widgets(app) 
        app.acquisition_stopped = False
        app.warning_box = None
        app.settings.setValue(SETTINGS_ACQUISITION_STOPPED, False)
        app.control_inputs[DOWNLOAD_BUTTON].setEnabled(app.write_data and app.acquisition_stopped)
        #DataExportActions.set_download_button_icon(app)
        warn_title, warn_msg = MessagesUtilities.invalid_inputs_handler(
            app.bin_width_micros,
            app.time_span,
            app.acquisition_time_millis,
            app.control_inputs[SETTINGS_FREE_RUNNING_MODE],
            app.enabled_channels,
            app.selected_conn_channel,
        )
        if warn_title and warn_msg:
            message_box = BoxMessage.setup(
                warn_title, warn_msg, QMessageBox.Warning, GUIStyles.set_msg_box_style(), app.test_mode
            )
            app.warning_box = message_box
            return
        app.control_inputs[START_BUTTON].setEnabled(False)
        app.control_inputs[STOP_BUTTON].setEnabled(True)   
        app.intensity_charts.clear()
        app.cps_charts_widgets.clear()
        app.cps_ch.clear()
        for chart in app.intensity_charts:
            chart.setVisible(False)
        app.intensity_lines.clear()        
        app.intensity_charts_wrappers.clear()
        QApplication.processEvents()         
        ButtonsActionsController.intensity_tracing_start(app)
        IntensityTracing.start_photons_tracing(app)


    @staticmethod
    def intensity_tracing_start(app):
        only_cps_widgets = [item for item in app.enabled_channels if item not in app.intensity_plots_to_show]
        only_cps_widgets.sort()
        for i, channel in enumerate(app.intensity_plots_to_show):
            if i < len(app.intensity_charts):
                app.intensity_charts[i].show()
            else:
                IntensityTracingPlot.create_chart_widget(app, i, channel)
        if len(only_cps_widgets) > 0:        
            for index, channel in enumerate(only_cps_widgets):
                IntensityTracingOnlyCPS.create_only_cps_widget(app, index, channel)



    @staticmethod
    def stop_button_pressed(app):
        app.acquisition_stopped = True
        app.last_cps_update_time.invalidate() 
        app.cps_counts = [0]* 8
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        app.control_inputs[DOWNLOAD_BUTTON].setEnabled(app.write_data and app.acquisition_stopped)
        DataExportActions.set_download_button_icon(app)
        QApplication.processEvents()
        flim_labs.request_stop()
        app.pull_from_queue_timer.stop() 
    
   
    @staticmethod
    def reset_button_pressed(app):
        flim_labs.request_stop()
        app.pull_from_queue_timer.stop() 
        app.last_cps_update_time.invalidate() 
        app.blank_space.show()
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        app.control_inputs[DOWNLOAD_BUTTON].setEnabled(app.write_data and app.acquisition_stopped)
        DataExportActions.set_download_button_icon(app)
        for chart in app.intensity_charts:
            chart.setParent(None)
            chart.deleteLater()
        for wrapper in app.intensity_charts_wrappers:
            wrapper.setParent(None)
            wrapper.deleteLater()  
        app.intensity_lines.clear()         
        app.intensity_charts.clear()
        app.cps_charts_widgets.clear()
        app.cps_ch.clear()
        app.cps_counts = [0]* 8
        app.intensity_charts_wrappers.clear()
        ButtonsActionsController.clear_intensity_grid_widgets(app)  
        QApplication.processEvents()    
 

    @staticmethod
    def clear_intensity_grid_widgets(app):
        for i in reversed(range(app.layouts[INTENSITY_ONLY_CPS_GRID].count())):
            widget = app.layouts[INTENSITY_ONLY_CPS_GRID].itemAt(i).widget()
            if widget is not None:
                app.layouts[INTENSITY_ONLY_CPS_GRID].removeWidget(widget)
                widget.deleteLater()
        for i in reversed(range(app.layouts[INTENSITY_PLOTS_GRID].count())):  
            widget = app.layouts[INTENSITY_PLOTS_GRID].itemAt(i).widget()
            if widget is not None:
                app.layouts[INTENSITY_PLOTS_GRID].removeWidget(widget)
                widget.deleteLater()
             

 
class PlotsConfigPopup(QWidget): 
    def __init__(self, window, start_acquisition = False):
        super().__init__()
        self.app = window
        self.setWindowTitle("Intensity Tracing - Plots config")
        TitlebarIcon.setup(self)
        GUIStyles.customize_theme(self, bg= QColor(20, 20, 20))
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        desc = QLabel("To avoid cluttering the interface, only a maximum of 4 intensity tracing charts will be displayed. However, all charts can be reconstructed by exporting the acquired data. Please select the intensity tracing charts you would like to be shown.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addSpacing(20)
        desc.setStyleSheet("font-size: 16px;")
        intensity_prompt = QLabel("INTENSITY TRACING PLOTS (MAX 4):")
        intensity_prompt.setObjectName("prompt_text")
        self.intensity_ch_grid = QGridLayout()
        self.intensity_checkboxes = []
        self.intensity_checkboxes_wrappers = []
        layout.addWidget(intensity_prompt)
        
        if len(self.app.enabled_channels) == 0:
            layout.addLayout(self.set_data_empty_row("No channels enabled."))
        else:
            self.init_intensity_grid()
            layout.addLayout(self.intensity_ch_grid) 
        layout.addSpacing(20)       
        
        self.start_btn = QPushButton("START")
        self.start_btn.setEnabled(len(self.app.intensity_plots_to_show) > 0)
        GUIStyles.set_reset_btn_style(self.start_btn)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_acquisition)  
        
        layout.addSpacing(20)
        row_btn = QHBoxLayout()
        row_btn.addStretch(1)
        row_btn.addWidget(self.start_btn)
        layout.addLayout(row_btn)
              
        self.setLayout(layout)
        self.setStyleSheet(GUIStyles.plots_config_popup_style())
        self.app.widgets[PLOTS_CONFIG_POPUP] = self


    def init_intensity_grid(self):
        self.app.enabled_channels.sort()
        for ch in self.app.enabled_channels:
            checkbox = self.set_checkboxes(f"Channel {ch + 1}")
            isChecked = ch in self.app.intensity_plots_to_show
            checkbox.setChecked(isChecked)
            if len(self.app.intensity_plots_to_show) >=4 and ch not in self.app.intensity_plots_to_show:
                checkbox.setEnabled(False)
        self.update_layout(self.intensity_checkboxes_wrappers, self.intensity_ch_grid)        


    def set_checkboxes(self, text):
        checkbox_wrapper = QWidget()
        checkbox_wrapper.setObjectName(f"tau_checkbox_wrapper")
        row = QHBoxLayout()
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet(GUIStyles.set_simple_checkbox_style(color = "#23F3AB"))
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.toggled.connect(lambda state, checkbox=checkbox: self.on_ch_intensity_toggled(state, checkbox) )
        row.addWidget(checkbox)
        checkbox_wrapper.setLayout(row)
        checkbox_wrapper.setStyleSheet(GUIStyles.checkbox_wrapper_style())
        self.intensity_checkboxes_wrappers.append(checkbox_wrapper)
        self.intensity_checkboxes.append(checkbox)
        return checkbox  

    def set_data_empty_row(self, text):    
        row = QHBoxLayout()
        remove_icon_label = QLabel()
        remove_icon_label.setPixmap(QPixmap(resource_path("assets/close-icon-red.png")).scaledToWidth(15))
        label = QLabel(text)
        label.setStyleSheet("color: #c90404;")
        row.addWidget(remove_icon_label)
        row.addWidget(label)
        row.addStretch(1)
        return row

    def update_layout(self, widgets, grid):       
        screen_width = self.width()
        if screen_width < 500:
            num_columns = 4 
        elif 500 <= screen_width <= 1200:
            num_columns = 6 
        elif 1201 <= screen_width <= 1450:
            num_columns = 8 
        else:
            num_columns = 12 
        for i, widget in enumerate(widgets):
            row, col = divmod(i, num_columns)
            grid.addWidget(widget, row, col)
            

    def on_ch_intensity_toggled(self, state, checkbox):
        label_text = checkbox.text() 
        ch_num_index = self.extract_channel_from_label(label_text) 
        if state:
            if ch_num_index not in self.app.intensity_plots_to_show:
                self.app.intensity_plots_to_show.append(ch_num_index)
        else:
            if ch_num_index in self.app.intensity_plots_to_show:
                self.app.intensity_plots_to_show.remove(ch_num_index) 
        self.app.intensity_plots_to_show.sort()        
        self.app.settings.setValue(SETTINGS_INTENSITY_PLOTS_TO_SHOW, json.dumps(self.app.intensity_plots_to_show)) 
        if len(self.app.intensity_plots_to_show) >= 4:
            for checkbox in self.intensity_checkboxes:
                if checkbox.text() != label_text and not checkbox.isChecked():
                    checkbox.setEnabled(False)
        else:
            for checkbox in self.intensity_checkboxes:
                checkbox.setEnabled(True)
        if hasattr(self, 'start_btn'):        
            start_btn_enabled = len(self.app.intensity_plots_to_show) > 0
            self.start_btn.setEnabled(start_btn_enabled)


                           
    def start_acquisition(self):
        self.close()
        ButtonsActionsController.start_button_pressed(self.app)
       

    def extract_channel_from_label(self,text):
        ch = re.search(r'\d+', text).group()  
        ch_num = int(ch) 
        ch_num_index = ch_num - 1 
        return ch_num_index

    
 