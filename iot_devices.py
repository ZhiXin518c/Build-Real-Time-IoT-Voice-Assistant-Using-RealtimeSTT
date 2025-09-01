"""
IoT Device Simulation Module
Simulates various IoT devices that can be controlled by voice commands
"""

import json
import time
import threading
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Types of IoT devices"""
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    FAN = "fan"
    DOOR_LOCK = "door_lock"
    SECURITY_CAMERA = "security_camera"
    SMART_PLUG = "smart_plug"
    SPEAKER = "speaker"
    TV = "tv"

class DeviceStatus(Enum):
    """Device status states"""
    ON = "on"
    OFF = "off"
    UNKNOWN = "unknown"
    ERROR = "error"

@dataclass
class IoTDevice:
    """Base IoT device class"""
    id: str
    name: str
    device_type: DeviceType
    location: str
    status: DeviceStatus = DeviceStatus.OFF
    properties: Dict[str, Any] = None
    last_updated: float = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.last_updated is None:
            self.last_updated = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        data = asdict(self)
        data['device_type'] = self.device_type.value
        data['status'] = self.status.value
        return data
    
    def update_property(self, key: str, value: Any):
        """Update a device property"""
        self.properties[key] = value
        self.last_updated = time.time()
        logger.info(f"Device {self.name} property {key} updated to {value}")
    
    def turn_on(self) -> bool:
        """Turn the device on"""
        self.status = DeviceStatus.ON
        self.last_updated = time.time()
        logger.info(f"Device {self.name} turned on")
        return True
    
    def turn_off(self) -> bool:
        """Turn the device off"""
        self.status = DeviceStatus.OFF
        self.last_updated = time.time()
        logger.info(f"Device {self.name} turned off")
        return True

class SmartLight(IoTDevice):
    """Smart light device"""
    
    def __init__(self, id: str, name: str, location: str):
        super().__init__(id, name, DeviceType.LIGHT, location)
        self.properties = {
            'brightness': 100,
            'color': '#FFFFFF',
            'color_temperature': 3000
        }
    
    def set_brightness(self, brightness: int) -> bool:
        """Set light brightness (0-100)"""
        if 0 <= brightness <= 100:
            self.update_property('brightness', brightness)
            if brightness == 0:
                self.status = DeviceStatus.OFF
            else:
                self.status = DeviceStatus.ON
            return True
        return False
    
    def set_color(self, color: str) -> bool:
        """Set light color (hex format)"""
        if color.startswith('#') and len(color) == 7:
            self.update_property('color', color)
            return True
        return False

class SmartThermostat(IoTDevice):
    """Smart thermostat device"""
    
    def __init__(self, id: str, name: str, location: str):
        super().__init__(id, name, DeviceType.THERMOSTAT, location)
        self.properties = {
            'target_temperature': 22,
            'current_temperature': 20,
            'mode': 'auto',  # auto, heat, cool, off
            'humidity': 45
        }
    
    def set_temperature(self, temperature: int) -> bool:
        """Set target temperature"""
        if 10 <= temperature <= 35:
            self.update_property('target_temperature', temperature)
            self.status = DeviceStatus.ON
            return True
        return False
    
    def set_mode(self, mode: str) -> bool:
        """Set thermostat mode"""
        valid_modes = ['auto', 'heat', 'cool', 'off']
        if mode.lower() in valid_modes:
            self.update_property('mode', mode.lower())
            self.status = DeviceStatus.ON if mode != 'off' else DeviceStatus.OFF
            return True
        return False

class SmartFan(IoTDevice):
    """Smart fan device"""
    
    def __init__(self, id: str, name: str, location: str):
        super().__init__(id, name, DeviceType.FAN, location)
        self.properties = {
            'speed': 0,  # 0-5
            'oscillating': False,
            'timer': 0  # minutes
        }
    
    def set_speed(self, speed: int) -> bool:
        """Set fan speed (0-5)"""
        if 0 <= speed <= 5:
            self.update_property('speed', speed)
            if speed == 0:
                self.status = DeviceStatus.OFF
            else:
                self.status = DeviceStatus.ON
            return True
        return False
    
    def set_oscillating(self, oscillating: bool) -> bool:
        """Set oscillating mode"""
        self.update_property('oscillating', oscillating)
        return True

class SmartDoorLock(IoTDevice):
    """Smart door lock device"""
    
    def __init__(self, id: str, name: str, location: str):
        super().__init__(id, name, DeviceType.DOOR_LOCK, location)
        self.properties = {
            'locked': True,
            'battery_level': 85,
            'last_access': None
        }
    
    def lock(self) -> bool:
        """Lock the door"""
        self.update_property('locked', True)
        self.update_property('last_access', time.time())
        self.status = DeviceStatus.ON
        return True
    
    def unlock(self) -> bool:
        """Unlock the door"""
        self.update_property('locked', False)
        self.update_property('last_access', time.time())
        self.status = DeviceStatus.ON
        return True

class IoTDeviceManager:
    """Manages all IoT devices"""
    
    def __init__(self):
        self.devices: Dict[str, IoTDevice] = {}
        self.device_lock = threading.Lock()
        self._initialize_default_devices()
    
    def _initialize_default_devices(self):
        """Initialize some default devices for demonstration"""
        default_devices = [
            SmartLight("light_1", "Living Room Light", "living_room"),
            SmartLight("light_2", "Bedroom Light", "bedroom"),
            SmartLight("light_3", "Kitchen Light", "kitchen"),
            SmartThermostat("thermostat_1", "Main Thermostat", "living_room"),
            SmartFan("fan_1", "Bedroom Fan", "bedroom"),
            SmartFan("fan_2", "Living Room Fan", "living_room"),
            SmartDoorLock("lock_1", "Front Door", "entrance"),
            SmartDoorLock("lock_2", "Back Door", "back_yard"),
        ]
        
        for device in default_devices:
            self.devices[device.id] = device
        
        logger.info(f"Initialized {len(default_devices)} default IoT devices")
    
    def add_device(self, device: IoTDevice) -> bool:
        """Add a new device"""
        with self.device_lock:
            if device.id in self.devices:
                logger.warning(f"Device {device.id} already exists")
                return False
            
            self.devices[device.id] = device
            logger.info(f"Added device: {device.name} ({device.id})")
            return True
    
    def remove_device(self, device_id: str) -> bool:
        """Remove a device"""
        with self.device_lock:
            if device_id in self.devices:
                device = self.devices.pop(device_id)
                logger.info(f"Removed device: {device.name} ({device_id})")
                return True
            return False
    
    def get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Get a device by ID"""
        return self.devices.get(device_id)
    
    def get_device_by_name(self, name: str) -> Optional[IoTDevice]:
        """Get a device by name (case-insensitive)"""
        name_lower = name.lower()
        for device in self.devices.values():
            if device.name.lower() == name_lower:
                return device
        return None
    
    def find_devices_by_location(self, location: str) -> List[IoTDevice]:
        """Find devices by location"""
        location_lower = location.lower()
        return [device for device in self.devices.values() 
                if device.location.lower() == location_lower]
    
    def find_devices_by_type(self, device_type: DeviceType) -> List[IoTDevice]:
        """Find devices by type"""
        return [device for device in self.devices.values() 
                if device.device_type == device_type]
    
    def search_devices(self, query: str) -> List[IoTDevice]:
        """Search devices by name or location"""
        query_lower = query.lower()
        results = []
        
        for device in self.devices.values():
            if (query_lower in device.name.lower() or 
                query_lower in device.location.lower()):
                results.append(device)
        
        return results
    
    def get_all_devices(self) -> List[IoTDevice]:
        """Get all devices"""
        return list(self.devices.values())
    
    def get_devices_dict(self) -> Dict[str, Dict[str, Any]]:
        """Get all devices as dictionary"""
        return {device_id: device.to_dict() 
                for device_id, device in self.devices.items()}
    
    def control_device(self, device_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """Control a device with the specified action"""
        device = self.get_device(device_id)
        if not device:
            return {
                'success': False,
                'message': f'Device {device_id} not found'
            }
        
        try:
            if action == 'turn_on':
                success = device.turn_on()
            elif action == 'turn_off':
                success = device.turn_off()
            elif action == 'set_brightness' and isinstance(device, SmartLight):
                brightness = kwargs.get('brightness', 100)
                success = device.set_brightness(brightness)
            elif action == 'set_temperature' and isinstance(device, SmartThermostat):
                temperature = kwargs.get('temperature', 22)
                success = device.set_temperature(temperature)
            elif action == 'set_speed' and isinstance(device, SmartFan):
                speed = kwargs.get('speed', 1)
                success = device.set_speed(speed)
            elif action == 'lock' and isinstance(device, SmartDoorLock):
                success = device.lock()
            elif action == 'unlock' and isinstance(device, SmartDoorLock):
                success = device.unlock()
            else:
                return {
                    'success': False,
                    'message': f'Action {action} not supported for device {device.name}'
                }
            
            if success:
                return {
                    'success': True,
                    'message': f'Successfully executed {action} on {device.name}',
                    'device': device.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to execute {action} on {device.name}'
                }
        
        except Exception as e:
            logger.error(f"Error controlling device {device_id}: {e}")
            return {
                'success': False,
                'message': f'Error controlling device: {str(e)}'
            }
    
    def process_voice_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a voice command and control appropriate devices"""
        command_type = command_data.get('type')
        params = command_data.get('params', ())
        original_text = command_data.get('original_text', '')
        
        logger.info(f"Processing voice command: {command_type} with params: {params}")
        
        try:
            if command_type == 'turn_on':
                if params:
                    device_name = params[0].strip()
                    device = self.get_device_by_name(device_name)
                    if device:
                        return self.control_device(device.id, 'turn_on')
                    else:
                        # Try searching for partial matches
                        matches = self.search_devices(device_name)
                        if matches:
                            device = matches[0]  # Use first match
                            return self.control_device(device.id, 'turn_on')
                        else:
                            return {
                                'success': False,
                                'message': f'Device "{device_name}" not found'
                            }
            
            elif command_type == 'turn_off':
                if params:
                    device_name = params[0].strip()
                    device = self.get_device_by_name(device_name)
                    if device:
                        return self.control_device(device.id, 'turn_off')
                    else:
                        matches = self.search_devices(device_name)
                        if matches:
                            device = matches[0]
                            return self.control_device(device.id, 'turn_off')
                        else:
                            return {
                                'success': False,
                                'message': f'Device "{device_name}" not found'
                            }
            
            elif command_type == 'set_brightness':
                if len(params) >= 2:
                    device_name = params[0].strip()
                    brightness = int(params[1])
                    device = self.get_device_by_name(device_name)
                    if device and isinstance(device, SmartLight):
                        return self.control_device(device.id, 'set_brightness', brightness=brightness)
                    else:
                        return {
                            'success': False,
                            'message': f'Light "{device_name}" not found'
                        }
            
            elif command_type == 'set_temperature':
                if len(params) >= 2:
                    device_name = params[0].strip()
                    temperature = int(params[1])
                    device = self.get_device_by_name(device_name)
                    if device and isinstance(device, SmartThermostat):
                        return self.control_device(device.id, 'set_temperature', temperature=temperature)
                    else:
                        return {
                            'success': False,
                            'message': f'Thermostat "{device_name}" not found'
                        }
            
            elif command_type == 'get_status':
                if params:
                    device_name = params[0].strip()
                    device = self.get_device_by_name(device_name)
                    if device:
                        return {
                            'success': True,
                            'message': f'{device.name} is {device.status.value}',
                            'device': device.to_dict()
                        }
                    else:
                        return {
                            'success': False,
                            'message': f'Device "{device_name}" not found'
                        }
            
            elif command_type == 'list_devices':
                devices = self.get_all_devices()
                device_list = [f"{device.name} ({device.device_type.value})" for device in devices]
                return {
                    'success': True,
                    'message': f'Available devices: {", ".join(device_list)}',
                    'devices': [device.to_dict() for device in devices]
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown command type: {command_type}'
                }
        
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {
                'success': False,
                'message': f'Error processing command: {str(e)}'
            }

# Global device manager instance
device_manager = IoTDeviceManager()

