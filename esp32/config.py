"""ESP32 Configuration"""

# WiFi Configuration
WIFI_SSID = 'YOUR_WIFI_SSID'
WIFI_PASSWORD = 'YOUR_WIFI_PASSWORD'

# Server Configuration
SERVER_URL = 'http://localhost:5000'  # Change to Render URL in production
DEVICE_ID = 'esp32-meccanoid-1'
DEVICE_TYPE = 'esp32'

# Connection Configuration
CONNECT_TIMEOUT = 10  # seconds
RECONNECT_INTERVAL = 5  # seconds
HEARTBEAT_INTERVAL = 30  # seconds

# Servo Configuration
SERVO_GPIO_MAP = {
    'A': 12,
    'B': 13,
    'C': 14,
    'D': 15,
    'E': 4,
    'F': 2
}

# Servo PWM Configuration
SERVO_FREQ = 50  # Hz (standard servo frequency)
SERVO_MIN_DUTY = 26  # ~0.5ms pulse at 50Hz
SERVO_MAX_DUTY = 128  # ~2.5ms pulse at 50Hz

# Logging
DEBUG = True
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
