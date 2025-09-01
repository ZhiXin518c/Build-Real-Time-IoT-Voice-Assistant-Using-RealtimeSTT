# Real-Time Voice Assistant for IoT Devices

A sophisticated voice-controlled assistant system built with RealtimeSTT for managing IoT devices through natural language commands.

## 🎯 Features

- **Real-time Speech Recognition**: Powered by RealtimeSTT and OpenAI Whisper
- **Natural Language Processing**: Understands conversational commands
- **IoT Device Control**: Unified interface for diverse smart home devices
- **Wake Word Detection**: Always-on listening with customizable wake words
- **Web Interface**: Comprehensive dashboard for monitoring and control
- **Real-time Updates**: Live transcription and device status updates
- **RESTful API**: Complete API for third-party integrations

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Microphone and speakers
- Ubuntu 20.04+ (or compatible Linux distribution)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice_assistant
   ```

2. **Install system dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential python3-dev python3-pip
   sudo apt-get install -y portaudio19-dev python3-pyaudio
   ```

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Access the web interface**
   Open your browser and navigate to `http://localhost:5000`

## 🎮 Usage

### Voice Commands

The system supports natural language commands for controlling IoT devices:

- **Device Control**: "Turn on the living room light"
- **Brightness Control**: "Set bedroom light brightness to 50"
- **Temperature Control**: "Set thermostat to 22 degrees"
- **Multiple Devices**: "Turn off all lights"
- **Status Queries**: "List all devices"

### Wake Words

Choose from multiple wake words:
- Jarvis
- Alexa
- Hey Google
- Computer
- OK Google

### Web Interface

The web dashboard provides:
- Voice assistant control and configuration
- Real-time transcription display
- IoT device management and control
- Activity log and system monitoring
- Device addition and configuration

## 🏗️ Architecture

### Core Components

- **Voice Assistant Engine**: RealtimeSTT integration and speech processing
- **NLP Module**: Command parsing and intent recognition
- **Device Manager**: IoT device abstraction and control
- **Web Framework**: Flask-based API and interface
- **Real-time Communication**: WebSocket-based updates

### Technology Stack

- **Backend**: Python, Flask, RealtimeSTT, OpenAI Whisper
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Database**: SQLite
- **Audio**: PyAudio, PortAudio
- **Communication**: HTTP/HTTPS, WebSocket

## 📡 API Reference

### Voice Control

- `POST /api/voice/start` - Start voice assistant
- `POST /api/voice/stop` - Stop voice assistant
- `GET /api/voice/status` - Get assistant status
- `POST /api/voice/test` - Test command processing
- `GET /api/voice/events` - Get recent events

### Device Management

- `GET /api/devices/` - List all devices
- `POST /api/devices/add` - Add new device
- `DELETE /api/devices/{id}` - Remove device
- `POST /api/devices/{id}/control` - Control device
- `GET /api/devices/{id}/status` - Get device status

## 🔧 Configuration

### Speech Recognition

Configure speech recognition parameters:
- **Model Size**: Choose between tiny, base, small, medium, large
- **Wake Words**: Select preferred activation phrase
- **Audio Settings**: Microphone selection and audio quality

### Device Integration

Add IoT devices with:
- Device ID and name
- Device type (light, thermostat, fan, door_lock)
- Location information
- Communication parameters

## 🛡️ Security

- HTTPS encryption for all communications
- CORS protection for API endpoints
- Input validation and sanitization
- Session-based authentication
- Rate limiting for API access

## 📊 Monitoring

The system provides comprehensive monitoring:
- Real-time transcription display
- Device status tracking
- Command execution logging
- System performance metrics
- Error tracking and reporting

## 🔍 Troubleshooting

### Common Issues

1. **Audio Input Problems**
   - Check microphone permissions
   - Verify audio device selection
   - Test microphone with other applications

2. **Speech Recognition Issues**
   - Ensure clear audio input
   - Check background noise levels
   - Try different Whisper model sizes

3. **Device Control Problems**
   - Verify device configuration
   - Check network connectivity
   - Review device communication logs

### Debug Mode

Enable debug mode for detailed logging:
```bash
export FLASK_DEBUG=1
python src/main.py
```

## 🚀 Deployment

### Development
```bash
python src/main.py
```

### Production
For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) for real-time speech recognition
- [OpenAI Whisper](https://openai.com/research/whisper) for speech-to-text models
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Picovoice Porcupine](https://picovoice.ai/platform/porcupine/) for wake word detection

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `voice_assistant_documentation.md`
- Review the troubleshooting section above

---

