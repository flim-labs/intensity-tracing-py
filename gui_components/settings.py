from copy import deepcopy


APP_VERSION = "2.2"
APP_NAME = "INTENSITY TRACING"
APP_DEFAULT_WIDTH = 1460
APP_DEFAULT_HEIGHT = 800

SETTINGS_ACQUISITION_STOPPED = "acquisition_stopped"
DEFAULT_ACQUISITION_STOPPED = False

EXPORT_DATA_GUIDE_LINK = "https://flim-labs.github.io/intensity-tracing-py/python-flim-labs/intensity-tracing-file-format.html"
GUI_GUIDE_LINK = f"https://flim-labs.github.io/intensity-tracing-py/v{APP_VERSION}"

SETTINGS_CONN_CHANNEL = "conn_channel"
DEFAULT_CONN_CHANNEL = "USB"

SETTINGS_FIRMWARE = "firmware"
DEFAULT_FIRMWARE = "intensity_tracing_usb.flim"

SETTINGS_BIN_WIDTH_MICROS = "bin_width_micros"
DEFAULT_BIN_WIDTH_MICROS = 1000

SETTINGS_TIME_SPAN = "time_span"
DEFAULT_TIME_SPAN = 5

SETTINGS_ACQUISITION_TIME_MILLIS = "acquisition_time_millis"
DEFAULT_ACQUISITION_TIME_MILLIS = None

SETTINGS_FREE_RUNNING_MODE = "free_running_mode"
DEFAULT_FREE_RUNNING_MODE = True

SETTINGS_WRITE_DATA = "write_data"
DEFAULT_WRITE_DATA = True

SETTINGS_TIME_TAGGER = "time_tagger"
DEFAULT_TIME_TAGGER = False

SETTINGS_ENABLED_CHANNELS = "enabled_channels"
DEFAULT_ENABLED_CHANNELS = "[0]"

SETTINGS_SHOW_CPS = "show_cps"
DEFAULT_SHOW_CPS = False

SETTINGS_CPS_THRESHOLD = "cps_threshold"
DEFAULT_CPS_THRESHOLD = 0

SETTINGS_INTENSITY_PLOTS_TO_SHOW = "intensity_plots_to_show"
DEFAULT_INTENSITY_PLOTS_TO_SHOW = "[0]"

MAX_CHANNELS = 8

START_BUTTON = "start_button"
STOP_BUTTON = "stop_button"
RESET_BUTTON = "reset_button"
COLLAPSE_BUTTON = "collapse_button"
ACQUIRE_BUTTON = "acquire_button"
READ_BUTTON = "read_button"
EXPORT_PLOT_IMG_BUTTON = "export_plot_img_button"
BIN_METADATA_BUTTON = "bin_metadata_button"
READ_FILE_BUTTON = "read_file_button"

CHECK_CARD_BUTTON = "check_card_button"
CHECK_CARD_MESSAGE = "check_card_message"
CHECK_CARD_WIDGET = "check_card_widget"


TIME_TAGGER_PROGRESS_BAR = "time_tagger_progress_bar"
TIME_TAGGER_WIDGET = "time_tagger_widget"

MAIN_LAYOUT = "main_layout"

CHANNELS_COMPONENT = "channels_component"
CH_CORRELATIONS_POPUP = "ch_correlations_popup"
PLOTS_CONFIG_POPUP = "plots_config_popup"

INTENSITY_PLOTS_GRID = "intensity_plots_grid"
INTENSITY_ONLY_CPS_GRID = "intensity_only_cps_grid"
PLOT_GRIDS_CONTAINER = "plots_grids_container"
TOP_COLLAPSIBLE_WIDGET = "top_collapsible_widget"
INTENSITY_WIDGET_WRAPPER = "intensity_widget_wrapper"
CHANNELS_CHECKBOXES = "channels_checkboxes"

CHECKBOX_CONTROLS = "ch_controls"

REALTIME_MS = 50
REALTIME_ADJUSTMENT = REALTIME_MS * 1000
REALTIME_HZ = 1000 / REALTIME_MS
REALTIME_SECS = REALTIME_MS / 1000

NS_IN_S = 1_000_000_000

EXPORTED_DATA_BYTES_UNIT = 12083.2


READER_POPUP = "reader_popup"
READER_METADATA_POPUP = "reader_metadata_popup"
SETTINGS_ACQUIRE_READ_MODE = "acquire_read_mode"
DEFAULT_ACQUIRE_READ_MODE = "acquire"

CHANNELS_DETECTION_BUTTON = "channels_detection_button"



READER_DATA = {
    "intensity": {
        "files": {"intensity": ""},
        "plots": [],
        "metadata": {},
        "data": {},
    },
}

DEFAULT_READER_DATA = deepcopy(READER_DATA)

LOADING_OVERLAY = "loading_overlay"