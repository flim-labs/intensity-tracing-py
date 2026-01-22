
from functools import partial
import os
import re
import json
import flim_labs
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QCheckBox, QHBoxLayout, QMessageBox, QGridLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import QPropertyAnimation, Qt, QTimer, QSize, QThreadPool
from PyQt6.QtGui import QIcon, QPixmap, QColor
from gui_components.data_export_controls import ExportData
from gui_components.intensity_tracing_controller import IntensityTracing, IntensityTracingOnlyCPS, IntensityTracingPlot
from gui_components.logo_utilities import TitlebarIcon
from gui_components.read_data import BuildIntensityPlotTask, BuildIntensityPlotWorkerSignals, ReadData, ReadDataControls, ReaderMetadataPopup, ReaderPopup
from gui_components.resource_path import resource_path
from gui_components.gui_styles import GUIStyles
from gui_components.controls_bar import ControlsBar
from gui_components.messages_utilities import MessagesUtilities
from  gui_components.box_message import BoxMessage
from gui_components.settings import *
from gui_components.time_tagger import TimeTaggerController
from gui_components.channel_name_utils import get_channel_name
from load_data import plot_intensity_data
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
        
        
class TimeTaggerWidget(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        write_data = self.app.write_data
        time_tagger_container = QWidget()
        time_tagger_container.setObjectName("container")
        time_tagger_container.setStyleSheet(GUIStyles.time_tagger_style())
        time_tagger_container.setFixedHeight(48)
        time_tagger_container.setContentsMargins(0, 0, 0, 0)
        time_tagget_layout = QHBoxLayout()
        time_tagget_layout.setSpacing(0)
        # time tagger icon
        pixmap = QPixmap(resource_path("assets/time-tagger-icon.png")).scaledToWidth(25)
        icon = QLabel(pixmap=pixmap)
        # time tagger checkbox
        time_tagger_checkbox = QCheckBox("TIME TAGGER")
        time_tagger_checkbox.setChecked(self.app.time_tagger)
        time_tagger_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        time_tagger_checkbox.toggled.connect(
            lambda checked: self.on_time_tagger_state_changed(
                checked
            )
        )        
        time_tagget_layout.addWidget(time_tagger_checkbox)
        time_tagget_layout.addWidget(icon)
        time_tagger_container.setLayout(time_tagget_layout)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(time_tagger_container)
        self.app.widgets[TIME_TAGGER_WIDGET] = self
        self.setLayout(main_layout)
        self.setVisible(write_data)
        
    def on_time_tagger_state_changed(self, checked):
        self.app.time_tagger = checked        
        
        
        
class ExportPlotImageButton(QWidget):
    def __init__(self, app, show = True, parent=None):
        super().__init__(parent)
        self.app = app
        self.show = show
        self.data = None
        self.export_img_button = self.create_button()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.export_img_button)
        self.setLayout(layout)
        
    def create_button(self):
        export_img_button = QPushButton()
        export_img_button.setIcon(
            QIcon(resource_path("assets/save-img-icon.png"))
        )
        export_img_button.setIconSize(QSize(30, 30))
        export_img_button.setStyleSheet("background-color: #1e90ff; padding: 0 14px;")
        export_img_button.setFixedHeight(55)
        export_img_button.setCursor(Qt.CursorShape.PointingHandCursor)
        export_img_button.clicked.connect(self.on_export_plot_image)
        button_visible = ReadDataControls.read_bin_metadata_enabled(self.app) and self.show
        export_img_button.setVisible(button_visible)
        self.app.control_inputs[EXPORT_PLOT_IMG_BUTTON] = export_img_button
        return export_img_button
    
    
    def on_export_plot_image(self):
        self.app.loading_overlay.set_loading_text("Processing data...")
        self.app.loading_overlay.toggle_overlay()
        channels_lines, times, metadata = ReadData.prepare_intensity_data_for_export_img(self.app)
        signals = BuildIntensityPlotWorkerSignals()
        signals.success.connect(self.on_intensity_plot_built)
        task = BuildIntensityPlotTask(channels_lines, times, metadata, False, signals)
        QThreadPool.globalInstance().start(task)
   
    def on_intensity_plot_built(self, plot):
        self.app.loading_overlay.toggle_overlay()
        ReadData.save_plot_image(self.app, plot)
  


class ActionButtons(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.app = window
        
        layout = self.create_buttons()
        self.setLayout(layout)

    def create_buttons(self):        
        buttons_row_layout, start_button, stop_button, reset_button, read_bin_data_button, bin_metadata_button = ControlsBar.create_buttons(
            self.start_button_pressed,
            self.stop_button_pressed,
            self.reset_button_pressed,
            self.plot_read_data_button_pressed,
            self.read_bin_metadata_button_pressed,
            self.app.enabled_channels,
            self.app
        )
        self.app.control_inputs[START_BUTTON] = start_button
        self.app.control_inputs[STOP_BUTTON] = stop_button
        self.app.control_inputs[RESET_BUTTON] = reset_button
        bin_metadata_btn_visible = ReadDataControls.read_bin_metadata_enabled(self.app)
        bin_metadata_button.setVisible(bin_metadata_btn_visible)
        read_bin_data_button.setVisible(self.app.acquire_read_mode == "read")
        self.app.control_inputs[READ_FILE_BUTTON] = read_bin_data_button
        self.app.control_inputs[BIN_METADATA_BUTTON] = bin_metadata_button
        return buttons_row_layout 

    def start_button_pressed(self):
        open_popup = len(self.app.enabled_channels) > 4 and self.app.plots_to_show_popup_already_shown == False
        if open_popup: 
            self.app.plots_to_show_popup_already_shown = True
            popup = PlotsConfigPopup(self.app, start_acquisition=True)
            popup.show()
        else: 
            ButtonsActionsController.start_button_pressed(self.app)       

    def stop_button_pressed(self):
        ButtonsActionsController.stop_button_pressed(self.app)

    def reset_button_pressed(self):
        ButtonsActionsController.reset_button_pressed(self.app)  
        
    def plot_read_data_button_pressed(self):
        popup = ReaderPopup(self.app)
        popup.show()   
    
    def read_bin_metadata_button_pressed(self):
        popup = ReaderMetadataPopup(self.app)
        popup.show()
    
        
class ButtonsActionsController:
    @staticmethod
    def start_button_pressed(app):
        ButtonsActionsController.clear_intensity_grid_widgets(app) 
        app.acquisition_stopped = False
        app.warning_box = None
        app.settings.setValue(SETTINGS_ACQUISITION_STOPPED, False)
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
                warn_title, warn_msg, QMessageBox.Icon.Warning, GUIStyles.set_msg_box_style(), app.test_mode
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
    def intensity_tracing_start(app, read_data=False):
        if not read_data:
            only_cps_widgets = [item for item in app.enabled_channels if item not in app.intensity_plots_to_show]
            only_cps_widgets.sort()
            for ch in app.enabled_channels:
                app.cps_counts[ch] = {
                    "last_time_ns": 0,
                    "last_count": 0,
                    "current_count": 0,
                }    
            if len(only_cps_widgets) > 0:        
                for index, channel in enumerate(only_cps_widgets):
                    IntensityTracingOnlyCPS.create_only_cps_widget(app, index, channel)                    
        for i, channel in enumerate(app.intensity_plots_to_show):
            if i < len(app.intensity_charts):
                app.intensity_charts[i].show()
            else:
                IntensityTracingPlot.create_chart_widget(app, i, channel, read_data)




    @staticmethod
    def stop_button_pressed(app, app_close = False):
        app.acquisition_stopped = True
        app.cps_counts.clear()   
        for _, widget in app.acquisition_time_countdown_widgets.items():
            if widget and isinstance(widget, QWidget):
                widget.setVisible(False)        
        def clear_cps_and_countdown_widgets():
            for _, animation in app.cps_widgets_animation.items():
                if animation:
                    animation.stop()
        QTimer.singleShot(400, clear_cps_and_countdown_widgets)
        app.cps_widgets_animation.clear()   
        app.acquisition_time_countdown_widgets.clear()      
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        QApplication.processEvents()
        flim_labs.request_stop()
        app.pull_from_queue_timer.stop() 
        if app.write_data:
                QTimer.singleShot(
                    300,
                    partial(ExportData.save_intensity_data, app),
                )
    
   
    @staticmethod
    def reset_button_pressed(app):
        flim_labs.request_stop()
        app.pull_from_queue_timer.stop() 
        app.blank_space.show()      
        app.control_inputs[START_BUTTON].setEnabled(len(app.enabled_channels) > 0)
        app.control_inputs[STOP_BUTTON].setEnabled(False)
        ButtonsActionsController.clear_plots(app) 
        
        
    @staticmethod
    def clear_plots(app):
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
        app.cps_counts.clear()  
        app.cps_widgets_animation.clear()     
        app.acquisition_time_countdown_widgets.clear()         
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
        desc.setStyleSheet("font-size: 14px; color: #cecece")
        intensity_prompt = QLabel("INTENSITY TRACING PLOTS (MAX 4):")
        intensity_prompt.setObjectName("prompt_text")
        intensity_prompt.setStyleSheet("font-size: 18px; color: white")
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
        self.start_btn.setFixedHeight(40)
        self.start_btn.setFixedWidth(100)
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
            channel_names = getattr(self.app, 'channel_names', {})
            # Get channel name and truncate custom name to 15 characters (more space in modal)
            custom_name = channel_names.get(str(ch), None)
            if custom_name:
                if len(custom_name) > 15:
                    truncated_name = custom_name[:15] + "..."
                else:
                    truncated_name = custom_name
                channel_label = f"{truncated_name} (Ch{ch + 1})"
            else:
                channel_label = f"Channel {ch + 1}"
            
            checkbox = self.set_checkboxes(channel_label)
            isChecked = ch in self.app.intensity_plots_to_show
            checkbox.setChecked(isChecked)
            if len(self.app.intensity_plots_to_show) >=4 and ch not in self.app.intensity_plots_to_show:
                checkbox.setEnabled(False)
        self.update_layout(self.intensity_checkboxes_wrappers, self.intensity_ch_grid)        


    def set_checkboxes(self, text):
        checkbox_wrapper = QWidget()
        checkbox_wrapper.setObjectName("simple_checkbox_wrapper")
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
    
    
    
    
class ReadAcquireModeButton(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        layout = QVBoxLayout()
        buttons_row = self.create_buttons()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(buttons_row)
        self.setLayout(layout)

    def create_buttons(self):
        buttons_row_layout = QHBoxLayout()
        buttons_row_layout.setSpacing(0)
        # Acquire button
        acquire_button = QPushButton("ACQUIRE")
        acquire_button.setCursor(Qt.CursorShape.PointingHandCursor)
        acquire_button.setCheckable(True)
        acquire_button.setObjectName("acquire_btn")  # Set objectName
        acquire_button.setChecked(self.app.acquire_read_mode == "acquire")
        acquire_button.clicked.connect(self.on_acquire_btn_pressed)
        buttons_row_layout.addWidget(acquire_button)
        # Read button
        read_button = QPushButton("READ")
        read_button.setCheckable(True)
        read_button.setCursor(Qt.CursorShape.PointingHandCursor)
        read_button.setObjectName("read_btn")  # Set objectName
        read_button.setChecked(self.app.acquire_read_mode != "acquire")
        read_button.clicked.connect(self.on_read_btn_pressed)
        buttons_row_layout.addWidget(read_button)
        self.app.control_inputs[ACQUIRE_BUTTON] = acquire_button
        self.app.control_inputs[READ_BUTTON] = read_button
        self.apply_base_styles()
        self.set_buttons_styles()
        return buttons_row_layout

    def apply_base_styles(self):
        base_style = GUIStyles.acquire_read_btn_style()
        self.app.control_inputs[ACQUIRE_BUTTON].setStyleSheet(base_style)
        self.app.control_inputs[READ_BUTTON].setStyleSheet(base_style)

    def set_buttons_styles(self):
        def get_buttons_style(color_acquire, color_read, bg_acquire, bg_read):
            return f"""
            QPushButton {{
                font-family: "Montserrat";
                letter-spacing: 0.1em;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: bold;
                min-width: 60px;
            }}
            QPushButton#acquire_btn {{
                border-top-left-radius: 3px;
                border-bottom-left-radius: 3px;
                color: {color_acquire};
                background-color: {bg_acquire};
            }}
            QPushButton#read_btn {{
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                color: {color_read};
                background-color: {bg_read};
            }}
        """
        read_mode = self.app.acquire_read_mode == 'read'
        if read_mode:
            style = get_buttons_style(color_acquire="#8c8b8b", color_read="white", bg_acquire="#cecece", bg_read="#8d4ef2")
        else:
            style = get_buttons_style(color_acquire="white", color_read="#8c8b8b", bg_acquire="#8d4ef2", bg_read="#cecece")
        self.app.control_inputs[ACQUIRE_BUTTON].setStyleSheet(style)
        self.app.control_inputs[READ_BUTTON].setStyleSheet(style)

    def on_acquire_btn_pressed(self, checked):
        ButtonsActionsController.clear_plots(self.app)
        self.app.control_inputs[ACQUIRE_BUTTON].setChecked(checked)
        self.app.control_inputs[READ_BUTTON].setChecked(not checked)
        self.app.acquire_read_mode = 'acquire' if checked else 'read'
        self.app.settings.setValue(SETTINGS_ACQUIRE_READ_MODE, self.app.acquire_read_mode)
        self.set_buttons_styles()
        self.app.reader_data = deepcopy(DEFAULT_READER_DATA)
        ReadDataControls.handle_widgets_visibility(self.app, self.app.acquire_read_mode == 'read')

    def on_read_btn_pressed(self, checked):
        ButtonsActionsController.clear_plots(self.app)
        self.app.control_inputs[ACQUIRE_BUTTON].setChecked(not checked)
        self.app.control_inputs[READ_BUTTON].setChecked(checked)
        self.app.acquire_read_mode = 'read' if checked else 'acquire'
        self.app.settings.setValue(SETTINGS_ACQUIRE_READ_MODE, self.app.acquire_read_mode)
        self.set_buttons_styles()
        ReadDataControls.handle_widgets_visibility(self.app, self.app.acquire_read_mode == 'read')

    
 
