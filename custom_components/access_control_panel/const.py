"""Constants for the Access Control Panel integration."""

DOMAIN = "access_control_panel"

DEFAULT_NAME = "Access Control Panel"
DEFAULT_SCAN_INTERVAL = 10

ENDPOINT_STATUS = "/api/status"
ENDPOINT_LOG = "/api/log"
ENDPOINT_ALARM_ARM = "/api/alarm/arm"
ENDPOINT_ALARM_DISARM = "/api/alarm/disarm"
ENDPOINT_ALARM_TRIGGER = "/api/alarm/trigger"
ENDPOINT_ALARM_CLEAR = "/api/alarm/clear"
ENDPOINT_KEYPAD = "/api/keypad"
ENDPOINT_USERS = "/api/users"
ENDPOINT_LOCKS = "/api/locks"
ENDPOINT_LOCK = "/api/lock"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_PORT = 80

SERVICE_SEND_CODE = "send_code"
SERVICE_ADD_USER = "add_user"
SERVICE_REMOVE_USER = "remove_user"
SERVICE_UPDATE_USER = "update_user"
SERVICE_GRANT_DIVISION = "grant_division"
SERVICE_REVOKE_DIVISION = "revoke_division"
SERVICE_CONTROL_LOCK = "control_lock"
