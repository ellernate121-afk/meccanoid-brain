import logging
from flask import current_app
from flask_socketio import emit, disconnect
from datetime import datetime

logger = logging.getLogger(__name__)

def init_websocket(socketio):
    """Initialize websocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle ESP32 connection"""
        from flask import request
        client_id = request.sid
        logger.info(f"Client connected: {client_id}")
        emit('response', {'data': 'Connected to websocket server'})
    
    @socketio.on('identify')
    def handle_identify(data):
        """Handle ESP32 identification"""
        device_type = data.get('device_type')
        device_id = data.get('device_id')
        
        if device_type == 'esp32':
            from flask import request
            current_app.connected_esp32 = request.sid
            current_app.servo_status = data.get('servos', {})
            
            logger.info(f"ESP32 identified: {device_id}")
            logger.info(f"Servo status: {current_app.servo_status}")
            
            emit('response', {'data': 'Identified as ESP32'})
        else:
            emit('response', {'error': 'Unknown device type'})
    
    @socketio.on('status')
    def handle_status(data):
        """Handle ESP32 status updates"""
        current_app.servo_status = data.get('servos', {})
        logger.debug(f"Servo status update: {current_app.servo_status}")
    
    @socketio.on('servo_feedback')
    def handle_servo_feedback(data):
        """Handle servo feedback from ESP32"""
        servo_id = data.get('servo_id')
        angle = data.get('angle')
        status = data.get('status')
        
        logger.info(f"Servo {servo_id} feedback: angle={angle}, status={status}")
        current_app.servo_status[servo_id] = {
            'angle': angle,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @socketio.on('error')
    def handle_error(data):
        """Handle errors from ESP32"""
        error_msg = data.get('message')
        error_code = data.get('code')
        logger.error(f"ESP32 error (code {error_code}): {error_msg}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        from flask import request
        client_id = request.sid
        
        if current_app.connected_esp32 == client_id:
            current_app.connected_esp32 = None
            logger.warning("ESP32 disconnected")
        
        logger.info(f"Client disconnected: {client_id}")
