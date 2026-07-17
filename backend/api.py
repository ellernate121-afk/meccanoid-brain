from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status and ESP32 connection state"""
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'esp32_connected': current_app.connected_esp32 is not None,
        'servos': current_app.servo_status,
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
    if not current_app.connected_esp32:
        return jsonify({'error': 'ESP32 not connected'}), 503
    
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
    
    # Send command to ESP32 via websocket
    try:
        command = {
            'type': 'servo_move',
            'servo': servo_id,
            'angle': angle,
            'speed': speed
        }
        
        # Import socketio from app context
        from app import socketio
        socketio.emit('command', command, to=current_app.connected_esp32)
        
        logger.info(f"Sent servo move command: {command}")
        
        return jsonify({
            'status': 'sent',
            'command': command
        }), 202
    
    except Exception as e:
        logger.error(f"Error sending command: {str(e)}")
        return jsonify({'error': 'Failed to send command'}), 500

@api_bp.route('/command', methods=['POST'])
def send_command():
    """Send a generic command to ESP32
    
    Expected JSON:
    {
        "command": "move_arm_left",
        "params": {...}
    }
    """
    if not current_app.connected_esp32:
        return jsonify({'error': 'ESP32 not connected'}), 503
    
    data = request.get_json()
    command_name = data.get('command')
    params = data.get('params', {})
    
    if not command_name:
        return jsonify({'error': 'Missing command name'}), 400
    
    try:
        command = {
            'type': 'custom_command',
            'command': command_name,
            'params': params
        }
        
        from app import socketio
        socketio.emit('command', command, to=current_app.connected_esp32)
        
        logger.info(f"Sent custom command: {command_name}")
        
        return jsonify({
            'status': 'sent',
            'command': command_name
        }), 202
    
    except Exception as e:
        logger.error(f"Error sending command: {str(e)}")
        return jsonify({'error': 'Failed to send command'}), 500

@api_bp.route('/healthz', methods=['GET'])
def healthz():
    """Kubernetes/health check endpoint"""
    return jsonify({'status': 'ok'}), 200
