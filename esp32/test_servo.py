"""Test servo control independently"""

from config import SERVO_GPIO_MAP, SERVO_FREQ, SERVO_MIN_DUTY, SERVO_MAX_DUTY
from servo_control import ServoController
import time

def test_servo(servo_id, angle):
    """
    Test a single servo
    
    Usage:
        import test_servo
        test_servo.test_servo('A', 90)  # Move servo A to 90 degrees
    """
    print(f"Testing servo {servo_id}...")
    
    servo = ServoController(SERVO_GPIO_MAP, SERVO_FREQ, SERVO_MIN_DUTY, SERVO_MAX_DUTY)
    servo.move(servo_id, angle, speed=50)
    
    print(f"Servo {servo_id} moved to {angle}°")

def test_all_servos():
    """
    Test all servos in sequence
    """
    print("Testing all servos...")
    
    servo = ServoController(SERVO_GPIO_MAP, SERVO_FREQ, SERVO_MIN_DUTY, SERVO_MAX_DUTY)
    
    angles = [0, 90, 180, 90, 0]
    
    for servo_id in servo.servos.keys():
        print(f"\nTesting servo {servo_id}...")
        
        for angle in angles:
            print(f"  Moving to {angle}°...")
            servo.move(servo_id, angle, speed=50)
            time.sleep(0.5)
    
    servo.stop_all()
    print("\nTest complete!")

if __name__ == '__main__':
    test_all_servos()
