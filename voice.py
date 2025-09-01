"""
Flask routes for voice assistant API
"""

from flask import Blueprint, jsonify, request
from src.voice_assistant import VoiceAssistant
from src.iot_devices import device_manager
import logging
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

voice_bp = Blueprint('voice', __name__)

# Global voice assistant instance
voice_assistant = None
assistant_lock = threading.Lock()

# Store recent events for the web interface
recent_events = []
max_events = 100

def add_event(event_type: str, message: str, data: dict = None):
    """Add an event to the recent events list"""
    global recent_events
    event = {
        'type': event_type,
        'message': message,
        'timestamp': time.time(),
        'data': data or {}
    }
    recent_events.append(event)
    
    # Keep only the most recent events
    if len(recent_events) > max_events:
        recent_events = recent_events[-max_events:]
    
    logger.info(f"Event added: {event_type} - {message}")

def status_callback(status: str, message: str):
    """Callback for voice assistant status updates"""
    add_event('status', message, {'status': status})

def transcription_callback(text: str, is_final: bool):
    """Callback for transcription updates"""
    event_type = 'transcription_final' if is_final else 'transcription_partial'
    add_event(event_type, text, {'is_final': is_final})

def command_callback(command_data: dict):
    """Callback for processed commands"""
    # Process the command with IoT device manager
    result = device_manager.process_voice_command(command_data)
    
    # Add event with result
    add_event('command', f"Command: {command_data['type']}", {
        **command_data,
        'result': result
    })

@voice_bp.route('/start', methods=['POST'])
def start_assistant():
    """Start the voice assistant"""
    global voice_assistant
    
    try:
        with assistant_lock:
            if voice_assistant and voice_assistant.is_active:
                return jsonify({
                    'success': False,
                    'message': 'Voice assistant is already running'
                }), 400
            
            # Get configuration from request
            data = request.get_json() or {}
            wake_words = data.get('wake_words', 'jarvis')
            model = data.get('model', 'base')
            
            # Create and configure voice assistant
            voice_assistant = VoiceAssistant(wake_words=wake_words, model=model)
            
            # Register callbacks
            voice_assistant.register_status_callback(status_callback)
            voice_assistant.register_transcription_callback(transcription_callback)
            voice_assistant.register_command_callback('all', command_callback)
            
            # Start the assistant
            voice_assistant.start()
            
            add_event('system', 'Voice assistant started', {
                'wake_words': wake_words,
                'model': model
            })
            
            return jsonify({
                'success': True,
                'message': 'Voice assistant started successfully',
                'status': voice_assistant.get_status()
            })
    
    except Exception as e:
        logger.error(f"Error starting voice assistant: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to start voice assistant: {str(e)}'
        }), 500

@voice_bp.route('/stop', methods=['POST'])
def stop_assistant():
    """Stop the voice assistant"""
    global voice_assistant
    
    try:
        with assistant_lock:
            if not voice_assistant or not voice_assistant.is_active:
                return jsonify({
                    'success': False,
                    'message': 'Voice assistant is not running'
                }), 400
            
            voice_assistant.stop()
            voice_assistant = None
            
            add_event('system', 'Voice assistant stopped')
            
            return jsonify({
                'success': True,
                'message': 'Voice assistant stopped successfully'
            })
    
    except Exception as e:
        logger.error(f"Error stopping voice assistant: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to stop voice assistant: {str(e)}'
        }), 500

@voice_bp.route('/status', methods=['GET'])
def get_status():
    """Get voice assistant status"""
    global voice_assistant
    
    try:
        with assistant_lock:
            if voice_assistant:
                status = voice_assistant.get_status()
            else:
                status = {
                    'is_active': False,
                    'is_listening': False,
                    'wake_words': None,
                    'model': None,
                    'available_commands': []
                }
            
            return jsonify({
                'success': True,
                'status': status
            })
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get status: {str(e)}'
        }), 500

@voice_bp.route('/events', methods=['GET'])
def get_events():
    """Get recent events"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        event_type = request.args.get('type')
        
        # Filter events
        filtered_events = recent_events
        if event_type:
            filtered_events = [e for e in recent_events if e['type'] == event_type]
        
        # Limit results
        if limit > 0:
            filtered_events = filtered_events[-limit:]
        
        return jsonify({
            'success': True,
            'events': filtered_events,
            'total_events': len(recent_events)
        })
    
    except Exception as e:
        logger.error(f"Error getting events: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get events: {str(e)}'
        }), 500

@voice_bp.route('/events/clear', methods=['POST'])
def clear_events():
    """Clear all events"""
    global recent_events
    
    try:
        recent_events = []
        return jsonify({
            'success': True,
            'message': 'Events cleared successfully'
        })
    
    except Exception as e:
        logger.error(f"Error clearing events: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to clear events: {str(e)}'
        }), 500

@voice_bp.route('/config', methods=['GET'])
def get_config():
    """Get voice assistant configuration options"""
    return jsonify({
        'success': True,
        'config': {
            'available_models': ['tiny', 'base', 'small', 'medium', 'large'],
            'available_wake_words': [
                'alexa', 'americano', 'blueberry', 'bumblebee', 'computer',
                'grapefruits', 'grasshopper', 'hey google', 'hey siri', 'jarvis',
                'ok google', 'picovoice', 'porcupine', 'terminator'
            ],
            'default_wake_words': 'jarvis',
            'default_model': 'base'
        }
    })

@voice_bp.route('/test', methods=['POST'])
def test_command():
    """Test command processing without voice input"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'message': 'Text is required'
            }), 400
        
        text = data['text']
        
        # Process the command if assistant is running
        if voice_assistant and voice_assistant.is_active:
            voice_assistant._process_command(text)
            return jsonify({
                'success': True,
                'message': f'Command processed: {text}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Voice assistant is not running'
            }), 400
    
    except Exception as e:
        logger.error(f"Error testing command: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to test command: {str(e)}'
        }), 500

