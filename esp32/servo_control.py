"""Servo control library for ESP32"""

from machine import PWM, Pin
import time

class ServoController:
    """Control multiple servos via PWM"""
    
    def __init__(self, gpio_map, freq=50, min_duty=26, max_duty=128):
        """
        Initialize servo controller
        
        Args:
            gpio_map: dict mapping servo IDs to GPIO pins
            freq: PWM frequency (Hz), default 50Hz for standard servos
            min_duty: minimum duty cycle (0-1023), corresponds to 0 degrees
            max_duty: maximum duty cycle (0-1023), corresponds to 180 degrees
        """
        self.gpio_map = gpio_map
        self.freq = freq
        self.min_duty = min_duty
        self.max_duty = max_duty
        
        # Initialize PWM pins
        self.servos = {}
        self.current_angles = {}
        
        for servo_id, gpio_pin in gpio_map.items():
            try:
                pin = Pin(gpio_pin, Pin.OUT)
                pwm = PWM(pin, freq=freq)
                self.servos[servo_id] = pwm
                self.current_angles[servo_id] = 90  # Default to middle
                print(f"Servo {servo_id} initialized on GPIO {gpio_pin}")
            except Exception as e:
                print(f"Error initializing servo {servo_id}: {e}")
    
    def angle_to_duty(self, angle):
        """
        Convert angle (0-180) to PWM duty cycle
        
        Args:
            angle: angle in degrees (0-180)
        
        Returns:
            duty cycle (0-1023)
        """
        # Clamp angle to valid range
        angle = max(0, min(180, angle))
        
        # Linear interpolation from angle to duty cycle
        duty = self.min_duty + (angle / 180.0) * (self.max_duty - self.min_duty)
        return int(duty)
    
    def move(self, servo_id, angle, speed=50):
        """
        Move servo to specified angle
        
        Args:
            servo_id: servo identifier (e.g., 'A', 'B')
            angle: target angle in degrees (0-180)
            speed: movement speed (0-100), where 100 is instantaneous
        
        Returns:
            True if successful, False otherwise
        """
        if servo_id not in self.servos:
            print(f"Error: Unknown servo {servo_id}")
            return False
        
        if not (0 <= angle <= 180):
            print(f"Error: Angle {angle} out of range [0, 180]")
            return False
        
        try:
            pwm = self.servos[servo_id]
            current_angle = self.current_angles[servo_id]
            
            # Calculate movement parameters
            angle_diff = abs(angle - current_angle)
            if angle_diff == 0:
                return True  # Already at target angle
            
            # Convert speed (0-100) to movement steps
            # Higher speed = fewer intermediate steps
            if speed >= 100:
                steps = 1
            else:
                steps = max(1, int(angle_diff * (1.0 - speed / 100.0)))
            
            step_size = angle_diff / steps if steps > 0 else 0
            direction = 1 if angle > current_angle else -1
            
            # Move servo gradually
            for i in range(steps + 1):
                current = current_angle + direction * step_size * i
                duty = self.angle_to_duty(current)
                pwm.duty(duty)
                time.sleep(0.02)  # 20ms between steps for smooth motion
            
            # Ensure we're at exact target
            duty = self.angle_to_duty(angle)
            pwm.duty(duty)
            self.current_angles[servo_id] = angle
            
            print(f"Servo {servo_id} moved to {angle}°")
            return True
        
        except Exception as e:
            print(f"Error moving servo {servo_id}: {e}")
            return False
    
    def stop(self, servo_id):
        """
        Stop servo (release it)
        
        Args:
            servo_id: servo identifier
        """
        if servo_id in self.servos:
            self.servos[servo_id].duty(0)
            print(f"Servo {servo_id} stopped")
    
    def stop_all(self):
        """Stop all servos"""
        for servo_id in self.servos:
            self.stop(servo_id)
    
    def get_status(self):
        """
        Get status of all servos
        
        Returns:
            dict with servo angles
        """
        return dict(self.current_angles)
