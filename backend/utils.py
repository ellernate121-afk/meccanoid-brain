"""Utility functions"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_command(command):
    """Log a command with timestamp"""
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"[{timestamp}] Command: {command}")

def parse_angle(angle_str):
    """Parse angle from string, handling various formats"""
    try:
        angle = int(angle_str)
        if 0 <= angle <= 180:
            return angle
        else:
            raise ValueError(f"Angle {angle} out of range")
    except ValueError:
        raise ValueError(f"Invalid angle: {angle_str}")
