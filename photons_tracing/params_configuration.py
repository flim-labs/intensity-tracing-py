import json
import os
from PyQt5.QtWidgets import QMessageBox
from gui_components.box_message import BoxMessage
from gui_styles import GUIStyles
from messages_utilities import MessagesUtilities


class ParamsConfigHandler:
    CONFIG_PATH = os.path.join(
        os.path.expanduser("~"), ".flim-labs", "config", "intensity_tracing_config.json"
    )

    def __init__(
        self,
        selected_update_rate="LOW",
        selected_conn_channel="USB",
        selected_firmware="intensity_tracing_usb.flim",
        bin_width_micros=1000,
        time_span=5,
        acquisition_time_millis=None,
        draw_frequency=10,
        free_running_acquisition_time=True,
        write_data=True,
        enabled_channels=[0],
        show_cps=False
    ):
        self.config = {
            "selected_update_rate": selected_update_rate,
            "selected_conn_channel": selected_conn_channel,
            "selected_firmware": selected_firmware,
            "bin_width_micros": bin_width_micros,
            "time_span": time_span,
            "acquisition_time_millis": acquisition_time_millis,
            "draw_frequency": draw_frequency,
            "free_running_acquisition_time": free_running_acquisition_time,
            "write_data": write_data,
            "enabled_channels": enabled_channels,
            "show_cps": show_cps,
        }

    def save(self):
        try:
            directory_path = os.path.dirname(self.CONFIG_PATH)
            os.makedirs(directory_path, exist_ok=True)

            with open(self.CONFIG_PATH, "w") as file:
                json.dump(self.config, file, indent=2)

            print(f"Parameters configuration saved to {self.CONFIG_PATH}")
            BoxMessage.setup(
                *MessagesUtilities.info_handler(
                    "SavedConfiguration",
                    f"Parameters configuration saved to {self.CONFIG_PATH}",
                ),
                QMessageBox.Information,
                GUIStyles.set_msg_box_style(),
            )

        except Exception as e:
            print(f"Error saving parameters configuration: {e}")
            BoxMessage.setup(
                *MessagesUtilities.error_handler(
                    "ErrorSavingConfiguration",
                    f"Error saving parameters configuration to {self.CONFIG_PATH}: {str(e)}",
                ),
                QMessageBox.Critical,
                GUIStyles.set_msg_box_style(),
            )

    def load(self):
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r") as file:
                    return json.load(file)
            except Exception as e:
                print(f"Error loading parameters configuration: {e}")

        print(
            f"No parameters configuration found at {self.CONFIG_PATH}. Returning default configuration."
        )
        return self.config
