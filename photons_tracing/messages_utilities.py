class MessagesUtilities:
    @staticmethod
    def error_handler(error_msg):
        if "NotDownloadable" in error_msg:
            return ("Error Resolving Firmware", "Unable to download the selected firmware")
        else:
            return ("Error", error_msg)    

    @staticmethod
    def invalid_inputs_handler(bin_width_micros, keep_points, acquisition_time_millis, acquisition_time_mode_switch, enabled_channels, selected_conn_channel, selected_update_rate):
        if bin_width_micros == 0 or keep_points == 0 or acquisition_time_millis == 0:
            return ("Empty input number values", "Active input number fields with value '0' are not allowed")

        elif acquisition_time_mode_switch.isChecked() and not keep_points:
            return ("Empty input number values", "A value for 'Max points' should be provided when 'Free running acquisition time' is active")
           
        elif not acquisition_time_mode_switch.isChecked() and not acquisition_time_millis:
            return ("Empty input number values", "A value for 'Acquisition time (ms)' should be provided when 'Free running acquisition time' is deactivated")

        elif len(enabled_channels) == 0:
            return ("0 channels enabled", "You must activate at least one channel to start photons tracing")
         
        elif not selected_conn_channel:
            return ("No connection channel selected", "You must choose between 'USB' and 'SMA' connection channels before starting photons tracing")
                  
        elif not selected_update_rate:
            return ("No update rate selected", "You must choose between 'LOW' and 'HIGH' update rate before starting photons tracing")

        else:
            return (None, None)

