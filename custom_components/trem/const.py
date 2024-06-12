"""Constants for Taiwan Real-time Earthquake Monitoring integration."""

from datetime import timedelta
from typing import Final

DOMAIN = "trem"

ATTR_ID: Final = "serial"
ATTR_AUTHOR: Final = "provider"
ATTR_LNG: Final = "longitude"
ATTR_LAT: Final = "latitude"
ATTR_DEPTH: Final = "depth"
ATTR_MAG: Final = "magnitude"
ATTR_LOC: Final = "location"
ATTR_TIME: Final = "time_of_occurrence"
ATTR_INT: Final = "intensity"
ATTR_EST: Final = "estimate"
ATTR_EQDATA: Final = "earthquake_data"

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

DEFAULT_FRIENDLY_NAME = "Taiwan Real-time Earthquake Monitoring"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=5)

ATTRIBUTION = "Powered by ExpTech Studio"
DEFAULT_ICON = "mdi:earth"

HA_USER_AGENT = (
    "TREM custom integration for Home Assistant (https://github.com/j1a-t13n/ha-trem)"
)

LOGIN_URLS = "https://api.exptech.com.tw/api/v3/et/login"

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
CONF_NODE: Final = "node"
CONF_KEEP_ALIVE: Final = "keep_alive"
