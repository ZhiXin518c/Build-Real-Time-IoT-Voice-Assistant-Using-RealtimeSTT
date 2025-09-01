"""
Voice Assistant Module using RealtimeSTT
Handles speech-to-text, natural language understanding, and command processing
"""

import threading
import time
import json
import logging
from typing import Dict, List, Callable, Optional
from RealtimeSTT import AudioToTextRecorder
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAssistant:
    """
    Real-time voice assistant using RealtimeSTT for speech recognition
    """
    
    def __init__(self, wake_words: str = "jarvis", model: str = "base"):
        """
        Initialize the voice assistant
        
        Args:
            wake_words: Comma-separated list of wake words
            model: Whisper model size (tiny, base, small, medium, large)
        """
        self.wake_words = wake_words
        self.model = model
        self.is_listening = False
        self.is_active = False
        self.recorder = None
        self.command_callbacks = {}
        self.status_callback = None
        self.transcription_callback = None
        
        # Command patterns for IoT devices
        self.command_patterns = {
            'turn_on': [
                r'turn on (?:the )?(.+)',
                r'switch on (?:the )?(.+)',
                r'activate (?:the )?(.+)',
                r'start (?:the )?(.+)'
            ],
            'turn_off': [
                r'turn off (?:the )?(.+)',
                r'switch off (?:the )?(.+)',
                r'deactivate (?:the )?(.+)',
                r'stop (?:the )?(.+)',
                r'shut down (?:the )?(.+)'
            ],
            'set_brightness': [
                r'set (?:the )?(.+) brightness to (\d+)',
                r'dim (?:the )?(.+) to (\d+)',
                r'brighten (?:the )?(.+) to (\d+)'
            ],
            'set_temperature': [
                r'set (?:the )?(.+) to (\d+) degrees?',
                r'change (?:the )?(.+) temperature to (\d+)',
                r'adjust (?:the )?(.+) to (\d+) degrees?'
            ],
            'get_status': [
                r'what is the status of (?:the )?(.+)',
                r'check (?:the )?(.+) status',
                r'how is (?:the )?(.+)',
                r'status of (?:the )?(.+)'
            ],
            'list_devices': [
                r'list (?:all )?devices',
                r'show (?:all )?devices',
                r'what devices (?:do (?:we|I) have|are available)',
                r'available devices'
            ]
        }
        
        self._setup_recorder()
    
    def _setup_recorder(self):
        """Setup the RealtimeSTT recorder with callbacks"""
        try:
            self.recorder = AudioToTextRecorder(
                wake_words=self.wake_words,
                model=self.model,
                on_recording_start=self._on_recording_start,
                on_recording_stop=self._on_recording_stop,
                on_transcription_start=self._on_transcription_start,
                on_realtime_transcription_update=self._on_realtime_transcription_update,
                on_realtime_transcription_stabilized=self._on_realtime_transcription_stabilized
            )
            logger.info(f"Voice assistant initialized with wake words: {self.wake_words}")
        except Exception as e:
            logger.error(f"Failed to initialize recorder: {e}")
            raise
    
    def _on_recording_start(self):
        """Callback when recording starts"""
        self.is_listening = True
        logger.info("Recording started")
        if self.status_callback:
            self.status_callback("recording", "Recording started")
    
    def _on_recording_stop(self):
        """Callback when recording stops"""
        self.is_listening = False
        logger.info("Recording stopped")
        if self.status_callback:
            self.status_callback("idle", "Recording stopped")
    
    def _on_transcription_start(self):
        """Callback when transcription starts"""
        logger.info("Transcription started")
        if self.status_callback:
            self.status_callback("transcribing", "Processing speech...")
    
    def _on_realtime_transcription_update(self, text):
        """Callback for real-time transcription updates"""
        if self.transcription_callback:
            self.transcription_callback(text, False)  # False = not final
    
    def _on_realtime_transcription_stabilized(self, text):
        """Callback when transcription is stabilized (final)"""
        logger.info(f"Final transcription: {text}")
        if self.transcription_callback:
            self.transcription_callback(text, True)  # True = final
        
        # Process the command
        self._process_command(text)
    
    def _process_command(self, text: str):
        """
        Process the transcribed text and extract commands
        
        Args:
            text: The transcribed text to process
        """
        if not text or not text.strip():
            return
        
        text = text.lower().strip()
        logger.info(f"Processing command: {text}")
        
        # Try to match command patterns
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    self._execute_command(command_type, match.groups(), text)
                    return
        
        # If no pattern matched, treat as unknown command
        self._execute_command('unknown', (text,), text)
    
    def _execute_command(self, command_type: str, params: tuple, original_text: str):
        """
        Execute a recognized command
        
        Args:
            command_type: Type of command (turn_on, turn_off, etc.)
            params: Extracted parameters from the command
            original_text: Original transcribed text
        """
        command_data = {
            'type': command_type,
            'params': params,
            'original_text': original_text,
            'timestamp': time.time()
        }
        
        logger.info(f"Executing command: {command_data}")
        
        # Call registered callback for this command type
        if command_type in self.command_callbacks:
            try:
                self.command_callbacks[command_type](command_data)
            except Exception as e:
                logger.error(f"Error executing command callback: {e}")
        
        # Call general command callback if registered
        if 'all' in self.command_callbacks:
            try:
                self.command_callbacks['all'](command_data)
            except Exception as e:
                logger.error(f"Error executing general command callback: {e}")
    
    def register_command_callback(self, command_type: str, callback: Callable):
        """
        Register a callback for a specific command type
        
        Args:
            command_type: Type of command or 'all' for all commands
            callback: Function to call when command is recognized
        """
        self.command_callbacks[command_type] = callback
        logger.info(f"Registered callback for command type: {command_type}")
    
    def register_status_callback(self, callback: Callable):
        """
        Register a callback for status updates
        
        Args:
            callback: Function to call with status updates (status, message)
        """
        self.status_callback = callback
        logger.info("Registered status callback")
    
    def register_transcription_callback(self, callback: Callable):
        """
        Register a callback for transcription updates
        
        Args:
            callback: Function to call with transcription updates (text, is_final)
        """
        self.transcription_callback = callback
        logger.info("Registered transcription callback")
    
    def start(self):
        """Start the voice assistant"""
        if self.is_active:
            logger.warning("Voice assistant is already active")
            return
        
        try:
            self.is_active = True
            logger.info("Starting voice assistant...")
            
            # Start listening in a separate thread
            def listen_loop():
                while self.is_active:
                    try:
                        if self.recorder:
                            self.recorder.text()  # This will block until speech is detected
                    except Exception as e:
                        logger.error(f"Error in listen loop: {e}")
                        time.sleep(1)  # Brief pause before retrying
            
            self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
            self.listen_thread.start()
            
            if self.status_callback:
                self.status_callback("active", f"Voice assistant started. Say '{self.wake_words}' to activate.")
            
            logger.info("Voice assistant started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start voice assistant: {e}")
            self.is_active = False
            raise
    
    def stop(self):
        """Stop the voice assistant"""
        if not self.is_active:
            logger.warning("Voice assistant is not active")
            return
        
        try:
            self.is_active = False
            logger.info("Stopping voice assistant...")
            
            if self.recorder:
                self.recorder.shutdown()
            
            if self.status_callback:
                self.status_callback("stopped", "Voice assistant stopped")
            
            logger.info("Voice assistant stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping voice assistant: {e}")
    
    def get_status(self) -> Dict:
        """
        Get current status of the voice assistant
        
        Returns:
            Dictionary with status information
        """
        return {
            'is_active': self.is_active,
            'is_listening': self.is_listening,
            'wake_words': self.wake_words,
            'model': self.model,
            'available_commands': list(self.command_patterns.keys())
        }
    
    def add_command_pattern(self, command_type: str, pattern: str):
        """
        Add a new command pattern
        
        Args:
            command_type: Type of command
            pattern: Regular expression pattern
        """
        if command_type not in self.command_patterns:
            self.command_patterns[command_type] = []
        
        self.command_patterns[command_type].append(pattern)
        logger.info(f"Added pattern for {command_type}: {pattern}")
    
    def remove_command_pattern(self, command_type: str, pattern: str):
        """
        Remove a command pattern
        
        Args:
            command_type: Type of command
            pattern: Regular expression pattern to remove
        """
        if command_type in self.command_patterns:
            if pattern in self.command_patterns[command_type]:
                self.command_patterns[command_type].remove(pattern)
                logger.info(f"Removed pattern for {command_type}: {pattern}")

