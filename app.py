import os
import logging
from flask import Flask, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-me')

# Initialize SocketIO with threading async mode for better compatibility
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Setup logging
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# Import blueprints
from backend.api import api_bp
from backend.websocket import init_websocket

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

# Initialize websocket handlers
init_websocket(socketio)

# Global state for connected clients
app.connected_esp32 = None
app.servo_status = {}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'meccanoid-brain',
        'esp32_connected': app.connected_esp32 is not None,
        'version': '1.0.0'
    }), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', False))
