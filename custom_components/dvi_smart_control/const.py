"""Constants for DVI Smart Control."""

DOMAIN = "dvi_smart_control"

CONF_URL = "url"

DEFAULT_URL = "https://smartcontrol.dvienergi.com"
DEFAULT_SCAN_INTERVAL = 60  # seconds
COMMAND_TIMEOUT = 60  # seconds - commands can take 30s+
DATA_TIMEOUT = 30  # seconds

# API endpoints
URL_LOGIN = "/"
URL_MAIN = "/main.php"
URL_PROCESS = "/includes/process.php"
URL_PUMP_INFO = "/includes/pumpinfo.php"

# POST parameters for process.php
PARAM_UPDATE_GRAPHICS = "subupdatepumpgraphics"
PARAM_UPDATE_BUTTONS = "subupdatemainbuttons"
PARAM_USER_SETTING = "subusersetting"

# User setting IDs (only those visible in the user UI)
SETTING_HEATING_SYSTEM = "1"  # 0=off, 1=on
SETTING_HEATING_TEMP_OFFSET = "2"  # 0-20
SETTING_HOT_WATER = "10"  # 0=off, 1=on
SETTING_HOT_WATER_TEMP = "11"  # 5-55
SETTING_HOT_WATER_CLOCK = "12"  # 0=clock, 1=constant on, 2=constant off
SETTING_SUPPLEMENTARY_HEATING = "15"  # 0=off, 1=auto, 2=reserve
SETTING_PUMP_ONOFF = "onoff"  # 2=on, 4=toggle

# Pump info page IDs
INFO_STATUS = "31"
INFO_ERRORS = "32"
INFO_ENERGY = "33"

# Sensor data keys (from HTML CSS classes)
KEY_OUTDOOR_TEMP = "outdoor_temperature"
KEY_TANK_TEMP = "tank_temperature"
KEY_HOT_WATER_TEMP = "hot_water_temperature"
KEY_HEATING_FLOW_TEMP = "heating_flow_temperature"
KEY_HEATING_RETURN_TEMP = "heating_return_temperature"
KEY_ROOM_TEMP = "room_temperature"

# Status keys
KEY_COMPRESSOR_HOURS = "compressor_hours"
KEY_HOT_WATER_HOURS = "hot_water_hours"
KEY_SUPPLEMENTARY_HEAT_HOURS = "supplementary_heat_hours"
KEY_INSTALLATION_DATE = "installation_date"
KEY_MANUFACTURING_NUMBER = "manufacturing_number"
KEY_SOFTWARE_VERSION = "software_version"

# Energy keys
KEY_ENERGY_CONSUMED_KWH = "energy_consumed_kwh"
KEY_ENERGY_CONSUMED_KW = "energy_consumed_kw"
KEY_ENERGY_DELIVERED_KWH = "energy_delivered_kwh"
KEY_ENERGY_DELIVERED_KW = "energy_delivered_kw"
KEY_FLOW_RATE = "flow_rate"

# Error keys
KEY_CURRENT_ERRORS = "current_errors"

# State keys (derived from GIF image names and button HTML)
KEY_PUMP_POWER = "pump_power"
KEY_COMPRESSOR_RUNNING = "compressor_running"
KEY_FAN_RUNNING = "fan_running"

# Setting state keys (current values from pumpchoice dialogs)
KEY_HEATING_SYSTEM_STATE = "heating_system_state"
KEY_HOT_WATER_STATE = "hot_water_state"
KEY_HOT_WATER_TEMP_SETPOINT = "hot_water_temp_setpoint"
KEY_HEATING_TEMP_OFFSET_VALUE = "heating_temp_offset_value"
KEY_SUPPLEMENTARY_HEATING_STATE = "supplementary_heating_state"
KEY_HOT_WATER_CLOCK_STATE = "hot_water_clock_state"

KEY_LAST_UPDATE = "last_update"
