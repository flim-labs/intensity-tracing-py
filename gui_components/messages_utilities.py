class MessagesUtilities:
    @staticmethod
    def error_handler(error_msg, custom_content=""):
        if "NotDownloadable" in error_msg:
            return (
                "Error Resolving Firmware",
                "Unable to download the selected firmware",
            )
        elif "ErrorSavingConfiguration" in error_msg:
            return ("Error Saving Configuration", custom_content)

        elif "ErrorSavingScriptFile" in error_msg:
            return ("Error Saving Files", f"An error occurred while saving script and data file: {custom_content}")
        else:
            return ("Error", error_msg)

    @staticmethod
    def info_handler(info_msg, custom_content=""):
        if "SavedConfiguration" in info_msg:
            return ("Configuration successfully saved", custom_content)
        elif "SavedScriptFile" in info_msg:
            return ("Files successfully saved", "Script and data files have been saved successfully")
        else:
            return (None, None)

    @staticmethod
    def invalid_inputs_handler(
            bin_width_micros,
            time_span,
            acquisition_time_millis,
            acquisition_time_mode_switch,
            enabled_channels,
            selected_conn_channel,
    ):
        def empty_input_error():
            return (
                "Empty input number values",
                "Active input number fields with value '0' are not allowed",
            )

        def no_acquisition_time_error():
            return (
                "Empty input number values",
                "A value for 'Acquisition time (s)' should be provided when 'Free running acquisition time' is deactivated",
            )

        def no_enabled_channels_error():
            return (
                "0 channels enabled",
                "You must activate at least one channel to start photons tracing",
            )

        def no_conn_channel_error():
            return (
                "No connection channel selected",
                "You must choose between 'USB' and 'SMA' connection channels before starting photons tracing",
            )
      

        if bin_width_micros == 0 or time_span == 0 or acquisition_time_millis == 0:
            return empty_input_error()

        elif (
                not acquisition_time_mode_switch.isChecked() and not acquisition_time_millis
        ):
            return no_acquisition_time_error()

        elif len(enabled_channels) == 0:
            return no_enabled_channels_error()

        elif not selected_conn_channel:
            return no_conn_channel_error()

        else:
            return MessagesUtilities.range_check(
                bin_width_micros, time_span, acquisition_time_millis
            )

    @staticmethod
    def range_check(bin_width_micros, time_span, acquisition_time_millis):
        bin_width_range = (1, 1000000)
        time_span_range = (1, 300)
        acquisition_time_range = (0.5 * 1000, 1800 * 1000)

        if (
                (
                        bin_width_micros is not None
                        and not (bin_width_range[0] <= bin_width_micros <= bin_width_range[1])
                )
                or (
                time_span is not None
                and not (time_span_range[0] <= time_span <= time_span_range[1])
        )
                or (
                acquisition_time_millis is not None
                and not (
                acquisition_time_range[0]
                <= acquisition_time_millis
                <= acquisition_time_range[1]
        )
        )
        ):
            return (
                "Values out of range",
                "Bin width (µs) value should be between 1 and 1000000. Time span (s) value should be between 1 and 300. Acquisition time (s) should be between 0.5 and 1800.",
            )
        else:
            return (None, None)
