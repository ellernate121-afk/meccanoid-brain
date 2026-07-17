"""Servo command handling and validation"""

class ServoCommand:
    """Represents a servo movement command"""
    
    VALID_SERVOS = ['A', 'B', 'C', 'D', 'E', 'F']
    MIN_ANGLE = 0
    MAX_ANGLE = 180
    
    def __init__(self, servo_id, angle, speed=50):
        self.servo_id = servo_id
        self.angle = angle
        self.speed = speed
        self._validate()
    
    def _validate(self):
        """Validate command parameters"""
        if self.servo_id not in self.VALID_SERVOS:
            raise ValueError(f"Invalid servo ID: {self.servo_id}")
        
        if not (self.MIN_ANGLE <= self.angle <= self.MAX_ANGLE):
            raise ValueError(f"Angle {self.angle} out of range [{self.MIN_ANGLE}, {self.MAX_ANGLE}]")
        
        if not (0 <= self.speed <= 100):
            raise ValueError(f"Speed {self.speed} out of range [0, 100]")
    
    def to_dict(self):
        """Convert to dictionary for transmission"""
        return {
            'type': 'servo_move',
            'servo': self.servo_id,
            'angle': self.angle,
            'speed': self.speed
        }
    
    def __repr__(self):
        return f"ServoCommand(servo={self.servo_id}, angle={self.angle}, speed={self.speed})"
