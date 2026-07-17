"""
Local Serial Bridge for ESP32
Runs on your Linux box, communicates with ESP32 via /dev/ttyUSB0
and provides REST API for Render backend to send commands
"""

import serial
import json
import logging
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import urllib.parse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Global serial connection
esp32_serial = None
last_command_response = None


class SerialBridge:
    """Manages communication with ESP32 via serial"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False
    
    def connect(self):
        """Connect to ESP32 via serial"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            logger.info(f"Connected to ESP32 on {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            self.connected = False
            return False
    
    def send_command(self, command):
        """Send command to ESP32 and wait for response"""
        if not self.connected:
            return {'error': 'Not connected to ESP32'}
        
        try:
            # Send command as JSON
            cmd_str = json.dumps(command) + '\n'
            self.serial.write(cmd_str.encode())
            logger.info(f"Sent to ESP32: {command}")
            
            # Wait for response
            response_str = self.serial.readline().decode('utf-8').strip()
            
            if response_str:
                response = json.loads(response_str)
                logger.info(f"Response from ESP32: {response}")
                return response
            else:
                return {'error': 'No response from ESP32'}
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ESP32 response: {e}")
            return {'error': 'Invalid JSON response from ESP32'}
        except Exception as e:
            logger.error(f"Error communicating with ESP32: {e}")
            return {'error': str(e)}
    
    def disconnect(self):
        """Disconnect from ESP32"""
        if self.serial:
            self.serial.close()
        self.connected = False
        logger.info("Disconnected from ESP32")


class CommandHandler(BaseHTTPRequestHandler):
    """HTTP request handler for receiving commands from Render"""
    
    def do_POST(self):
        """Handle POST requests with servo commands"""
        global esp32_serial, last_command_response
        
        # Parse request
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            command = json.loads(body)
            logger.info(f"Received command from Render: {command}")
            
            # Send to ESP32
            response = esp32_serial.send_command(command)
            last_command_response = response
            
            # Send response back to Render
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode())
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_GET(self):
        """Handle GET requests for status"""
        global esp32_serial
        
        if self.path == '/status':
            status = {
                'bridge_connected': True,
                'esp32_connected': esp32_serial.connected,
                'port': esp32_serial.port,
                'last_response': last_command_response
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass


def run_http_server(host='localhost', port=5001):
    """Run HTTP server for receiving commands"""
    server = HTTPServer((host, port), CommandHandler)
    logger.info(f"HTTP server listening on {host}:{port}")
    server.serve_forever()


def main():
    """Main entry point"""
    # Configuration
    SERIAL_PORT = '/dev/ttyUSB0'
    SERIAL_BAUDRATE = 115200
    HTTP_HOST = 'localhost'
    HTTP_PORT = 5001
    
    global esp32_serial
    
    # Initialize serial bridge
    esp32_serial = SerialBridge(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE)
    
    # Try to connect to ESP32
    max_retries = 3
    for attempt in range(max_retries):
        if esp32_serial.connect():
            break
        if attempt < max_retries - 1:
            logger.warning(f"Retry {attempt + 1}/{max_retries - 1} in 2 seconds...")
            time.sleep(2)
    
    if not esp32_serial.connected:
        logger.error("Failed to connect to ESP32. Exiting.")
        return
    
    # Start HTTP server in a separate thread
    server_thread = Thread(target=run_http_server, args=(HTTP_HOST, HTTP_PORT), daemon=True)
    server_thread.start()
    
    logger.info("Local bridge is ready!")
    logger.info(f"Send commands to http://{HTTP_HOST}:{HTTP_PORT}")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        esp32_serial.disconnect()


if __name__ == '__main__':
    main()
