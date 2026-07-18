"""Main entry point for ESP32 meccanoid controller"""

import time
import json
from machine import UART
from config import *
from servo_control import ServoController

def serial_listen(uart, servo_ctrl):
    """Listen for commands over serial (USB)"""
    print("Listening for commands over serial...")
    
    while True:
        try:
            # Check if data is available
            if uart.any():
                data = uart.readline()
                if data:
                    try:
                        msg_str = data.decode('utf-8').strip()
                        command = json.loads(msg_str)
                        print(f"Received command: {command}")
                        
                        # Process the command
                        if command.get('type') == 'servo_move':
                            servo_id = command.get('servo')
                            angle = command.get('angle')
                            speed = command.get('speed', 50)
                            
                            success = servo_ctrl.move(servo_id, angle, speed)
                            
                            # Send response back
                            response = {
                                'status': 'success' if success else 'error',
                                'servo': servo_id,
                                'angle': angle
                            }
                            uart.write(json.dumps(response) + '\n')
                        
                        else:
                            error_response = {
                                'status': 'error',
                                'message': f'Unknown command type: {command.get("type")}'
                            }
                            uart.write(json.dumps(error_response) + '\n')
                    
                    except json.JSONDecodeError:
                        error_response = {'status': 'error', 'message': 'Invalid JSON'}
                        uart.write(json.dumps(error_response) + '\n')
                    except Exception as e:
                        error_response = {'status': 'error', 'message': str(e)}
                        uart.write(json.dumps(error_response) + '\n')
            
            time.sleep(0.1)
        
        except Exception as e:
            print(f"Error in serial listen: {e}")
            time.sleep(1)

def main():
    """Main loop"""
    print("\n" + "="*50)
    print("Meccanoid Brain - ESP32 Controller (Serial Mode)")
    print("="*50 + "\n")
    
    # Initialize UART for USB serial communication
    uart = UART(0, 115200)
    print(f"Serial listening at 115200 baud")
    
    # Initialize servo controller
    print("Initializing servo controller...")
    servo_ctrl = ServoController(SERVO_GPIO_MAP, SERVO_FREQ, SERVO_MIN_DUTY, SERVO_MAX_DUTY)
    print("Ready!")
    
    # Listen for commands
    serial_listen(uart, servo_ctrl)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
