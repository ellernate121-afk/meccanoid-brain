# ESP32 Servo Controller

MicroPython code for ESP32 to control servos via websocket connection to the Render backend.

## Hardware Setup

### Components
- ESP32 Development Board
- Servos (connected to breadboard)
- Jumper wires
- USB cable (for `/dev/ttyUSB0` connection)

### Servo Connections

Connect servos to GPIO pins:
- **Servo A**: GPIO 12 (PWM)
- **Servo B**: GPIO 13 (PWM)
- **Servo C**: GPIO 14 (PWM)
- **Servo D**: GPIO 15 (PWM)
- **Servo E**: GPIO 4 (PWM)
- **Servo F**: GPIO 2 (PWM)

Each servo needs:
- 5V power (from breadboard PSU)
- GND (common ground)
- Signal wire (GPIO pin above)

## Software Setup

### 1. Flash MicroPython

Download MicroPython for ESP32:
```bash
wget https://micropython.org/download/esp32/
```

Flash to ESP32:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-YYYYMMDD-VXXX.bin
```

### 2. Configure WiFi

Edit `config.py`:
```python
WIFI_SSID = 'your-wifi-name'
WIFI_PASSWORD = 'your-wifi-password'
SERVER_URL = 'https://your-render-app.onrender.com'
DEVICE_ID = 'esp32-meccanoid-1'
```

### 3. Upload Code

Using `ampy` (Adafruit MicroPython Tool):

```bash
pip install adafruit-ampy

# Upload files
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put servo_control.py
ampy --port /dev/ttyUSB0 put servo_client.py
ampy --port /dev/ttyUSB0 put main.py
```

Or using WebREPL:
1. Connect to ESP32 via USB
2. Open WebREPL: http://micropython.org/webrepl/
3. Upload files via browser interface

### 4. Monitor Serial Output

```bash
screen /dev/ttyUSB0 115200
```

Or with `picocom`:
```bash
picocom /dev/ttyUSB0 -b 115200
```

## File Structure

```
esp32/
├── config.py           # WiFi & server configuration
├── main.py             # Entry point
├── servo_control.py    # PWM servo control library
├── servo_client.py     # Websocket client
└── test_servo.py       # Standalone servo test
```

## Testing

### Test Individual Servo

Upload and run `test_servo.py`:
```python
import test_servo
test_servo.test_servo('A', 90)  # Move servo A to 90 degrees
```

### Test Websocket Connection

1. Ensure backend is running (locally or on Render)
2. Check ESP32 serial output for connection messages
3. Call `/api/status` endpoint to verify ESP32 is connected

## Troubleshooting

### ESP32 won't boot
- Check USB cable connection
- Try different USB port
- Verify MicroPython firmware is installed: `screen /dev/ttyUSB0 115200` should show REPL prompt

### WiFi connection fails
- Check SSID and password in `config.py`
- Verify WiFi router is 2.4GHz (ESP32 doesn't support 5GHz)
- Check signal strength

### Servos don't respond
- Test servos independently with `test_servo.py`
- Check GPIO pin numbers match hardware wiring
- Verify power supply voltage (5V typical)
- Check servo PWM signal (oscilloscope or logic analyzer)

### Websocket connection hangs
- Verify server URL is correct in `config.py`
- Check firewall/port forwarding if using local server
- Look for timeout errors in serial output
- Increase `CONNECT_TIMEOUT` in `servo_client.py` if needed
