APP_VERSION = "1.5"
APP_NAME = "INTENSITY TRACING"
APP_DEFAULT_WIDTH = 1460
APP_DEFAULT_HEIGHT = 800

SETTINGS_ACQUISITION_STOPPED = "acquisition_stopped"
DEFAULT_ACQUISITION_STOPPED = False

EXPORT_DATA_GUIDE_LINK = "https://flim-labs.github.io/intensity-tracing-py/python-flim-labs/intensity-tracing-file-format.html"
GUI_GUIDE_LINK = f"https://flim-labs.github.io/intensity-tracing-py/v{APP_VERSION}/#gui-usage"

SETTINGS_UPDATE_RATE = "update_rate"
DEFAULT_UPDATE_RATE = "LOW"

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

SETTINGS_DRAW_FREQUENCY = "draw_frequency"
DEFAULT_DRAW_FREQUENCY = 10

SETTINGS_FREE_RUNNING_MODE = "free_running_mode"
DEFAULT_FREE_RUNNING_MODE = True

SETTINGS_WRITE_DATA = "write_data"
DEFAULT_WRITE_DATA = True

SETTINGS_ENABLED_CHANNELS = "enabled_channels"
DEFAULT_ENABLED_CHANNELS = "[0]"

SETTINGS_SHOW_CPS = "show_cps"
DEFAULT_SHOW_CPS = False

START_BUTTON = "start_button"
STOP_BUTTON = "stop_button"
RESET_BUTTON = "reset_button"
DOWNLOAD_BUTTON = "download_button"
DOWNLOAD_MENU = "download_menu"

REALTIME_MS = 10
REALTIME_ADJUSTMENT = REALTIME_MS * 1000
REALTIME_HZ = 1000 / REALTIME_MS
REALTIME_SECS = REALTIME_MS / 1000

NS_IN_S = 1_000_000_000

EXPORTED_DATA_BYTES_UNIT = 12083.2
