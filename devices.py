"""
Flask routes for IoT device management
"""

from flask import Blueprint, jsonify, request
from src.iot_devices import device_manager, DeviceType, SmartLight, SmartThermostat, SmartFan, SmartDoorLock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/', methods=['GET'])
def get_all_devices():
    """Get all IoT devices"""
    try:
        devices = device_manager.get_devices_dict()
        return jsonify({
            'success': True,
            'devices': devices,
            'count': len(devices)
        })
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get devices: {str(e)}'
        }), 500

@devices_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device"""
    try:
        device = device_manager.get_device(device_id)
        if device:
            return jsonify({
                'success': True,
                'device': device.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Device {device_id} not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting device {device_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get device: {str(e)}'
        }), 500

@devices_bp.route('/search', methods=['GET'])
def search_devices():
    """Search devices by name or location"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'message': 'Query parameter "q" is required'
            }), 400
        
        devices = device_manager.search_devices(query)
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'count': len(devices),
            'query': query
        })
    except Exception as e:
        logger.error(f"Error searching devices: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to search devices: {str(e)}'
        }), 500

@devices_bp.route('/by-type/<device_type>', methods=['GET'])
def get_devices_by_type(device_type):
    """Get devices by type"""
    try:
        # Validate device type
        try:
            dtype = DeviceType(device_type)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid device type: {device_type}'
            }), 400
        
        devices = device_manager.find_devices_by_type(dtype)
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'count': len(devices),
            'device_type': device_type
        })
    except Exception as e:
        logger.error(f"Error getting devices by type: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get devices by type: {str(e)}'
        }), 500

@devices_bp.route('/by-location/<location>', methods=['GET'])
def get_devices_by_location(location):
    """Get devices by location"""
    try:
        devices = device_manager.find_devices_by_location(location)
        return jsonify({
            'success': True,
            'devices': [device.to_dict() for device in devices],
            'count': len(devices),
            'location': location
        })
    except Exception as e:
        logger.error(f"Error getting devices by location: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get devices by location: {str(e)}'
        }), 500

@devices_bp.route('/<device_id>/control', methods=['POST'])
def control_device(device_id):
    """Control a specific device"""
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({
                'success': False,
                'message': 'Action is required'
            }), 400
        
        action = data['action']
        kwargs = {k: v for k, v in data.items() if k != 'action'}
        
        result = device_manager.control_device(device_id, action, **kwargs)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    
    except Exception as e:
        logger.error(f"Error controlling device {device_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to control device: {str(e)}'
        }), 500

@devices_bp.route('/add', methods=['POST'])
def add_device():
    """Add a new device"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Device data is required'
            }), 400
        
        # Validate required fields
        required_fields = ['id', 'name', 'device_type', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Field "{field}" is required'
                }), 400
        
        # Validate device type
        try:
            device_type = DeviceType(data['device_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': f'Invalid device type: {data["device_type"]}'
            }), 400
        
        # Create device based on type
        device_id = data['id']
        name = data['name']
        location = data['location']
        
        if device_type == DeviceType.LIGHT:
            device = SmartLight(device_id, name, location)
        elif device_type == DeviceType.THERMOSTAT:
            device = SmartThermostat(device_id, name, location)
        elif device_type == DeviceType.FAN:
            device = SmartFan(device_id, name, location)
        elif device_type == DeviceType.DOOR_LOCK:
            device = SmartDoorLock(device_id, name, location)
        else:
            return jsonify({
                'success': False,
                'message': f'Device type {device_type.value} not yet supported for creation'
            }), 400
        
        # Add device to manager
        if device_manager.add_device(device):
            return jsonify({
                'success': True,
                'message': f'Device {name} added successfully',
                'device': device.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Device with ID {device_id} already exists'
            }), 400
    
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to add device: {str(e)}'
        }), 500

@devices_bp.route('/<device_id>', methods=['DELETE'])
def remove_device(device_id):
    """Remove a device"""
    try:
        if device_manager.remove_device(device_id):
            return jsonify({
                'success': True,
                'message': f'Device {device_id} removed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Device {device_id} not found'
            }), 404
    
    except Exception as e:
        logger.error(f"Error removing device {device_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to remove device: {str(e)}'
        }), 500

@devices_bp.route('/types', methods=['GET'])
def get_device_types():
    """Get available device types"""
    return jsonify({
        'success': True,
        'device_types': [dtype.value for dtype in DeviceType]
    })

@devices_bp.route('/stats', methods=['GET'])
def get_device_stats():
    """Get device statistics"""
    try:
        all_devices = device_manager.get_all_devices()
        
        # Count by type
        type_counts = {}
        for device in all_devices:
            device_type = device.device_type.value
            type_counts[device_type] = type_counts.get(device_type, 0) + 1
        
        # Count by status
        status_counts = {}
        for device in all_devices:
            status = device.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by location
        location_counts = {}
        for device in all_devices:
            location = device.location
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_devices': len(all_devices),
                'by_type': type_counts,
                'by_status': status_counts,
                'by_location': location_counts
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting device stats: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to get device stats: {str(e)}'
        }), 500

