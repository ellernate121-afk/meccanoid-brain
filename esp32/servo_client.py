"""Websocket client for ESP32 to communicate with backend"""

import socket
import json
import time
from machine import reset

class WebsocketClient:
    """Simple websocket client for ESP32"""
    
    def __init__(self, server_url, device_id, servo_controller, debug=True):
        """
        Initialize websocket client
        
        Args:
            server_url: server URL (e.g., 'http://example.com:5000')
            device_id: device identifier
            servo_controller: ServoController instance
            debug: enable debug logging
        """
        self.server_url = server_url.replace('http://', '').replace('https://', '')
        self.device_id = device_id
        self.servo_controller = servo_controller
        self.debug = debug
        self.socket = None
        self.connected = False
        self.msg_id = 0
    
    def log(self, msg):
        """Debug logging"""
        if self.debug:
            print(f"[WS] {msg}")
    
    def connect(self, timeout=10):
        """
        Connect to websocket server
        
        Args:
            timeout: connection timeout in seconds
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.log(f"Connecting to {self.server_url}...")
            
            # Parse server URL
            if ':' in self.server_url:
                host, port = self.server_url.split(':')
                port = int(port)
            else:
                host = self.server_url
                port = 80
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            
            # Connect
            self.socket.connect((host, port))
            self.connected = True
            self.log(f"Connected to {host}:{port}")
            
            # Send identification
            self._send_identify()
            
            return True
        
        except Exception as e:
            self.log(f"Connection failed: {e}")
            self.connected = False
            return False
    
    def _send_identify(self):
        """
        Send device identification to server
        """
        identify_msg = {
            'device_type': 'esp32',
            'device_id': self.device_id,
            'servos': self.servo_controller.get_status()
        }
        
        self.log(f"Sending identify: {identify_msg}")
        self._send_json(identify_msg)
    
    def _send_json(self, data):
        """
        Send JSON message to server
        
        Args:
            data: dict to send as JSON
        """
        try:
            json_str = json.dumps(data)
            self.socket.send(json_str.encode() + b'\n')
            self.log(f"Sent: {json_str}")
        except Exception as e:
            self.log(f"Send error: {e}")
            self.connected = False
    
    def process_command(self, command):
        """
        Process command from server
        
        Args:
            command: dict with command data
        """
        cmd_type = command.get('type')
        
        if cmd_type == 'servo_move':
            servo_id = command.get('servo')
            angle = command.get('angle')
            speed = command.get('speed', 50)
            
            self.log(f"Moving servo {servo_id} to {angle}° (speed={speed})")
            success = self.servo_controller.move(servo_id, angle, speed)
            
            # Send feedback
            feedback = {
                'type': 'servo_feedback',
                'servo_id': servo_id,
                'angle': angle,
                'status': 'success' if success else 'error'
            }
            self._send_json(feedback)
        
        elif cmd_type == 'custom_command':
            custom_cmd = command.get('command')
            params = command.get('params', {})
            self.log(f"Received custom command: {custom_cmd} with params {params}")
            # Handle custom commands as needed
        
        else:
            self.log(f"Unknown command type: {cmd_type}")
    
    def send_status(self):
        """
        Send current status to server
        """
        status = {
            'type': 'status',
            'device_id': self.device_id,
            'servos': self.servo_controller.get_status()
        }
        self._send_json(status)
    
    def disconnect(self):
        """
        Disconnect from server
        """
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        self.log("Disconnected")
    
    def receive(self, timeout=1):
        """
        Receive message from server (non-blocking)
        
        Args:
            timeout: receive timeout in seconds
        
        Returns:
            dict if message received, None otherwise
        """
        try:
            self.socket.settimeout(timeout)
            data = self.socket.recv(1024)
            
            if data:
                msg_str = data.decode('utf-8').strip()
                if msg_str:
                    msg = json.loads(msg_str)
                    return msg
            else:
                self.connected = False
        
        except socket.timeout:
            pass
        except Exception as e:
            self.log(f"Receive error: {e}")
            self.connected = False
        
        return None
