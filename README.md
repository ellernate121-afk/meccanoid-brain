# Meccanoid Brain 🤖

Custom brain for Meccanoid G15KS using ESP32 + Python backend with LLM integration via base44.

## Architecture

```
base44 LLM
    |
    v
Render.com (Flask API + Websocket Server)
    |
    v
ESP32 (Websocket Client + Servo Control)
    |
    v
Servos on Breadboard
```

## Components

### Backend (Render)
- Flask REST API for command ingestion
- Websocket server for ESP32 communication
- Servo command parsing & routing
- Connection management

### ESP32 (Local Device)
- MicroPython websocket client
- PWM servo control
- Auto-reconnect logic
- `/dev/ttyUSB0` serial bridge

## Quick Start

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (see `.env.example`):
```bash
cp .env.example .env
export FLASK_ENV=development
```

3. Run locally:
```bash
python app.py
```

4. Deploy to Render:
- Push to GitHub
- Connect Render to this repo
- Set `WEB_CONCURRENCY=1` (websocket compatibility)
- Deploy!

### ESP32 Setup

1. Flash MicroPython to ESP32 (see `esp32/README.md`)
2. Configure WiFi in `esp32/config.py`
3. Upload `esp32/main.py` and `esp32/servo_client.py`
4. Power on—should auto-connect to websocket server

## API Endpoints

### REST API

**POST /api/servo/move**
```json
{
  "servo_id": "A",
  "angle": 90,
  "speed": 50
}
```

**POST /api/command**
```json
{
  "command": "move_arm_left",
  "params": {}
}
```

**GET /api/status**
Returns connection status and connected servos.

### Websocket

ESP32 connects to `/ws` endpoint. Messages are JSON:

**Server → ESP32:**
```json
{"type": "servo_move", "servo": "A", "angle": 90}
```

**ESP32 → Server:**
```json
{"type": "status", "servos": ["A", "B", "C"], "connected": true}
```

## Integration with base44 LLM

Your base44 LLM should call the REST API:

```python
import requests

response = requests.post(
    'https://your-render-app.onrender.com/api/command',
    json={
        'command': 'move_servo',
        'params': {'servo_id': 'A', 'angle': 45}
    }
)
```

## File Structure

```
meccanoid-brain/
├── app.py                 # Flask app entry point
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── Procfile               # Render deployment
├── .env.example           # Environment template
├── backend/
│   ├── __init__.py
│   ├── api.py            # REST API routes
│   ├── websocket.py      # Websocket server logic
│   ├── servo.py          # Servo command handling
│   └── utils.py          # Helper functions
├── esp32/
│   ├── README.md         # ESP32 setup guide
│   ├── config.py         # WiFi & server config
│   ├── main.py           # Entry point
│   ├── servo_client.py   # Websocket client
│   └── servo_control.py  # PWM servo control
└── docs/
    ├── API.md            # Full API documentation
    └── PROTOCOL.md       # Websocket protocol
```

## Troubleshooting

### ESP32 won't connect to websocket
- Check WiFi credentials in `esp32/config.py`
- Verify Render app URL is correct
- Check ESP32 serial output: `screen /dev/ttyUSB0 115200`

### Servos not responding
- Verify servo pins in `esp32/config.py` match breadboard wiring
- Test servo PWM directly with `esp32/test_servo.py`
- Check power supply voltage (typical servos need 5V)

### Render websocket timeout
- Set `WEB_CONCURRENCY=1` in Render environment
- Use `python-socketio` for better websocket stability

## Development

Want to add features? Check out:
- `DEVELOPMENT.md` for local testing setup
- `PROTOCOL.md` for adding new command types
- Issues/discussions for feature ideas

## License

MIT

## Contributors

- **ellernate121-afk** (you!) + partner
