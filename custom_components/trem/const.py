"""Constants for Taiwan Real-time Earthquake Monitoring integration."""

from datetime import timedelta

# Initialize
DEFAULT_NAME = "TREM"
DEFAULT_ICON = "mdi:chart-timeline-variant"
DOMAIN = "trem"
PLATFORMS = ["image", "sensor"]

# Proj
CLIENT_NAME = "TREM-HA"
PROJECT_URL = "https://github.com/J1A-T13N/ha-trem/"
ISSUE_URL = f"{PROJECT_URL}issues"

# Version
MIN_HA_MAJ_VER = 2024
MIN_HA_MIN_VER = 3
__min_ha_version__ = f"{MIN_HA_MAJ_VER}.{MIN_HA_MIN_VER}.0"
__version__ = "1.0.3"

# General sensor attributes
ATTRIBUTION = "Powered by ExpTech Studio"
ATTR_FILENAME = "filename"
ATTR_ID = "serial"
ATTR_AUTHOR = "provider"
ATTR_LNG = "longitude"
ATTR_LAT = "latitude"
ATTR_DEPTH = "depth"
ATTR_MAG = "magnitude"
ATTR_LOC = "location"
ATTR_TIME = "time_of_occurrence"
ATTR_INT = "intensity"
ATTR_EST = "estimate"
ATTR_NODE = "API_Node"
ATTR_EQDATA = "earthquake_data"
ATTR_LIST = [
    ATTR_ID,
    ATTR_AUTHOR,
    ATTR_LNG,
    ATTR_LAT,
    ATTR_DEPTH,
    ATTR_MAG,
    ATTR_LOC,
    ATTR_TIME,
    ATTR_INT,
    ATTR_EST,
]
MANUFACTURER = "ExptechTW"

# Configuration
CONF_DRAW_MAP = "draw_map"
CONF_NODE = "node"
CONF_PASS = "pass"
CONF_PRESERVE_DATA = "preserve_data"

# Coordinator
TREM_COORDINATOR = "trem_coordinator"
TREM_NAME = "trem_name"
UPDATE_LISTENER = "update_listener"
HTTPS_API_COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=5)
WEBSOCKET_COORDINATOR_UPDATE_INTERVAL = timedelta(seconds=1)

# REST
HA_USER_AGENT = (
    "TREM custom integration for Home Assistant (https://github.com/j1a-t13n/ha-trem)"
)
LOGIN_URLS = "https://api-1.exptech.dev/api/v3/et/login"
BASE_URLS = {
    "tainan_cache_limit": "https://api-1.exptech.com.tw",
    "tainan_cache": "https://api-1.exptech.dev",
    "taipe_cache_limit": "https://api-2.exptech.com.tw",
    "taipe_cache": "https://api-2.exptech.dev",
    "taipei_limit": "https://lb-1.exptech.com.tw",
    "taipei": "https://lb-1.exptech.dev",
    "pingtung_limit": "https://lb-2.exptech.com.tw",
    "pingtung": "https://lb-2.exptech.dev",
    "taipei_2": "https://lb-3.exptech.com.tw",
    "pingtung_2": "https://lb-4.exptech.com.tw",
}
REQUEST_TIMEOUT = 10  # seconds

# Websocket
BASE_WS = {
    "taipeiWS": "wss://lb-1.exptech.dev/websocket",
    "pingtungWS": "wss://lb-2.exptech.dev/websocket",
    "taipeiWS_2": "wss://lb-3.exptech.dev/websocket",
    "pingtungWS_2": "wss://lb-4.exptech.dev/websocket",
}
DEFAULT_MAX_MSG_SIZE = 16 * 1024 * 1024

# Message

WS_MSG_TOO_BIG = (
    f"Please consider increasing message size with `{DEFAULT_MAX_MSG_SIZE}`."
)
STARTUP = f"""
-------------------------------------------------------------------
{CLIENT_NAME}
Version: {__version__}
This is a custom component
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
