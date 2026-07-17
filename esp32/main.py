"""Main entry point for ESP32 meccanoid controller"""

import time
import network
from config import *
from servo_control import ServoController
from servo_client import WebsocketClient

def connect_wifi():
    """Connect to WiFi"""
    print(f"Connecting to WiFi: {WIFI_SSID}...")
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(0.5)
            timeout -= 1
        
        print()
    
    if wlan.isconnected():
        print(f"WiFi connected!")
        print(f"IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("WiFi connection failed!")
        return False

def main():
    """Main loop"""
    print("\n" + "="*50)
    print("Meccanoid Brain - ESP32 Controller")
    print("="*50 + "\n")
    
    # Connect to WiFi
    if not connect_wifi():
        print("Failed to connect to WiFi. Restarting...")
        time.sleep(5)
        return
    
    # Initialize servo controller
    print("Initializing servo controller...")
    servo_ctrl = ServoController(SERVO_GPIO_MAP, SERVO_FREQ, SERVO_MIN_DUTY, SERVO_MAX_DUTY)
    
    # Initialize websocket client
    print(f"Initializing websocket client...")
    ws_client = WebsocketClient(SERVER_URL, DEVICE_ID, servo_ctrl, DEBUG)
    
    # Connect to server
    connected = False
    reconnect_count = 0
    
    while True:
        # Try to connect if not already connected
        if not ws_client.connected:
            reconnect_count += 1
            print(f"\nConnection attempt {reconnect_count}...")
            
            if ws_client.connect(CONNECT_TIMEOUT):
                connected = True
                reconnect_count = 0
                last_status_time = time.time()
            else:
                print(f"Reconnecting in {RECONNECT_INTERVAL} seconds...")
                time.sleep(RECONNECT_INTERVAL)
                continue
        
        # Main loop: check for commands and send periodic status
        try:
            # Check for incoming commands
            command = ws_client.receive(timeout=0.5)
            if command:
                print(f"Received command: {command}")
                ws_client.process_command(command)
            
            # Send status periodically
            current_time = time.time()
            if current_time - last_status_time >= HEARTBEAT_INTERVAL:
                ws_client.send_status()
                last_status_time = current_time
            
            time.sleep(0.1)  # Small delay to prevent busy-waiting
        
        except Exception as e:
            print(f"Error in main loop: {e}")
            ws_client.disconnect()
            connected = False
            time.sleep(RECONNECT_INTERVAL)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
