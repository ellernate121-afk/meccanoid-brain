from flask import Blueprint, request, jsonify, current_app
import logging
import requests
from datetime import datetime
import os

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Local bridge URL (your Linux box running local_bridge.py)
BRIDGE_URL = os.getenv('BRIDGE_URL', 'http://localhost:5001')

def send_to_bridge(command):
    """Send command to local bridge and get response"""
    try:
        response = requests.post(
            f'{BRIDGE_URL}',
            json=command,
            timeout=5
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect to bridge at {BRIDGE_URL}")
        return {'error': 'Bridge unavailable'}
    except Exception as e:
        logger.error(f"Error communicating with bridge: {str(e)}")
        return {'error': str(e)}

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status and bridge connection state"""
    try:
        bridge_status = requests.get(f'{BRIDGE_URL}/status', timeout=2).json()
    except:
        bridge_status = {'error': 'Bridge unavailable'}
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'bridge_status': bridge_status,
        'server_status': 'online'
    }), 200

@api_bp.route('/servo/move', methods=['POST'])
def move_servo():
    """Move a servo to a specific angle
    
    Expected JSON:
    {
        "servo_id": "A",
        "angle": 90,
        "speed": 50  (optional, 0-100)
    }
    """
    data = request.get_json()
    
    # Validation
    servo_id = data.get('servo_id')
    angle = data.get('angle')
    speed = data.get('speed', 50)
    
    if not servo_id or angle is None:
        return jsonify({'error': 'Missing servo_id or angle'}), 400
    
    if not (0 <= angle <= 180):
        return jsonify({'error': 'Angle must be between 0 and 180'}), 400
    
    if not (0 <= speed <= 100):
        return jsonify({'error': 'Speed must be between 0 and 100'}), 400
    
    # Send command to ESP32 via local bridge
    command = {
        'type': 'servo_move',
        'servo': servo_id,
        'angle': angle,
        'speed': speed
    }
    
    response = send_to_bridge(command)
    logger.info(f"Servo move command: {command} -> Response: {response}")
    
    if 'error' in response:
        return jsonify(response), 503
    
    return jsonify({
        'status': 'sent',
        'command': command,
        'response': response
    }), 200

@api_bp.route('/command', methods=['POST'])
def send_command():
    """Send a generic command to ESP32
    
    Expected JSON:
    {
        "command": "move_arm_left",
        "params": {...}
    }
    """
    data = request.get_json()
    command_name = data.get('command')
    params = data.get('params', {})
    
    if not command_name:
        return jsonify({'error': 'Missing command name'}), 400
    
    command = {
        'type': 'custom_command',
        'command': command_name,
        'params': params
    }
    
    response = send_to_bridge(command)
    logger.info(f"Custom command: {command_name} -> Response: {response}")
    
    if 'error' in response:
        return jsonify(response), 503
    
    return jsonify({
        'status': 'sent',
        'command': command_name,
        'response': response
    }), 200

@api_bp.route('/healthz', methods=['GET'])
def healthz():
    """Kubernetes/health check endpoint"""
    return jsonify({'status': 'ok'}), 200
