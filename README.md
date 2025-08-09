
<img width="3188" height="1202" alt="frame (3)" src="https://github.com/user-attachments/assets/517ad8e9-ad22-457d-9538-a9e62d137cd7" />


# Thenga - AI-Powered Coconut Robot 🥥🤖

## Basic Details

### Team Name: Thenga Team

### Team Members

• Team Lead: John Varghese Nettady - Muthoot Institute of Technology and Science
• Member 2: Sam Sunny - Muthoot Institute of Technology and Science

### Project Description

Thenga is a self-aware coconut robot powered by AI that can interact through voice in Malayalam/English, detect motion using ESP32 sensors, coconut-themed personality.

### The Problem (that doesn't exist)

Ever wondered what it would be like if coconuts could talk back and control your IoT devices? What if your ESP32 project needed a sassy, self-aware coconut companion that speaks Malayalam and has attitude?

### The Solution (that nobody asked for)

Meet Thenga an AI-powered coconut robot that combines Flask web server, Google Gemini AI, multilingual text-to-speech, ESP32 hardware integration, and motion detection. It speaks Malayalam, detects when it's picked up, controls motors, and has a personality that knows it's a coconut!

## Technical Details

### Technologies/Components Used

For Software:
• **Languages**: Python, C++, HTML, JavaScript
• **Frameworks**: Flask, Arduino Framework
• **Libraries**:

- Flask, requests, gTTS, edge-tts
- pygame, asyncio, dotenv
- ArduinoJson, WiFi, HTTPClient
  • **APIs**: Google Gemini AI, Google Translate
  • **Tools**: VS Code, Arduino IDE, Git

For Hardware:
• **Main Components**:

- ESP32 Development Board
- MPU6050 Gyroscope/Accelerometer Sensor
- L298N Motor Driver Module
- DC Motor
- LEDs for status indication
  • **Specifications**:
- ESP32: WiFi enabled, 240MHz dual-core
- MPU6050: 6-axis motion detection
- Motor Driver: L298N dual H-bridge
  • **Tools Required**: Breadboard, Jumper wires, Power supply

### Implementation

For Software:

# Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/thenga.git
cd thenga

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp inside_thenga/config_example.py inside_thenga/config.py
# Add your Gemini API key to .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

# Run

```bash
# Start the Flask server
cd inside_thenga
python main.py

# The server will be available at http://localhost:5000
# ESP32 should connect to this server automatically
```

### Project Documentation

For Software:

# Screenshots (Add at least 3)

![Web Interface](screenshots/web_interface.png)
*Main chat interface where users can interact with Thenga in Malayalam/English*

![ESP32 Serial Monitor](screenshots/esp32_serial.png)
*ESP32 serial monitor showing motion detection and server communication*

![Audio Notification System](screenshots/audio_system.png)
*Audio notification system with Malayalam TTS responses*

# Diagrams

![System Architecture](diagrams/architecture.png)
*Complete system workflow showing Flask server, ESP32 communication, AI processing, and audio output*

For Hardware:

# Schematic & Circuit

![ESP32 Circuit](circuit/esp32_circuit.png)
*ESP32 connections with MPU6050 sensor, L298N motor driver, and LED indicators*

![MPU6050 Wiring](circuit/mpu6050_wiring.png)
*Detailed wiring diagram for MPU6050 gyroscope sensor with I2C connections*

# Build Photos

![Components Layout](photos/components.jpg)
*All components: ESP32, MPU6050, L298N motor driver, DC motor, LEDs, breadboard, jumper wires*

![Assembly Process](photos/build_process.jpg)
*Step-by-step assembly showing sensor mounting, motor connections, and breadboard wiring*

![Final Build](photos/final_build.jpg)
*Completed Thenga robot with ESP32 brain, motion sensors, and motor control system*

### Project Demo

# Video

[Thenga Demo Video](https://youtu.be/your_demo_video)
*Complete demonstration showing voice interaction, motion detection, motor control, and multilingual responses*

# Additional Demos

## Key Features Demonstrated:

- **Multilingual Chat**: Voice interaction in Malayalam, Manglish, and English
- **Motion Detection**: ESP32 detects when picked up using MPU6050 sensor
- **Motor Control**: Automatic motor activation after device placement
- **Audio Notifications**: Malayalam TTS responses with neural voices
- **AI Personality**: Self-aware coconut robot with witty responses
- **Real-time Communication**: ESP32 ↔ Flask server JSON communication

## API Endpoints:

- `POST /chat` - Chat with Thenga AI
- `POST /tts` - Text-to-speech conversion
- `POST /esp32/pickup` - Handle device pickup events
- `POST /esp32/placement` - Handle device placement events
- `POST /esp32/gyro` - Gyroscope threshold detection
- `GET /audio/list` - List available audio files

## Technical Highlights:

- **Language Detection**: Automatic detection of Malayalam, Manglish, English
- **Translation Workflow**: Input → English → Gemini AI → Malayalam → TTS
- **Edge TTS**: High-quality neural voice synthesis
- **Motion Algorithms**: Gyroscope-based pickup/placement detection
- **Hardware Integration**: ESP32 + sensors + motor control

## Team Contributions

Sam Sunny: ESP32 firmware, hardware setup, sensor integration, motor control logic
• John Varghese Nettady: Frontend development, audio system, TTS implementation, testing and debugging

---

## Additional Links

- **Live Demo**: [http://localhost:5000](http://localhost:5000)
- **Hardware Guide**: [ESP32 Setup Documentation](docs/hardware_setup.md)
- **API Documentation**: [API Reference](docs/api_reference.md)
- **Voice Samples**: [Audio Examples](audio_files/)

---

**Made with ❤️ and lots of coconut enthusiasm at TinkerHub Useless Projects**

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--25-25?link=https%3A%2F%2Fwww.tinkerhub.org%2Fevents%2FQ2Q1TQKX6Q%2FUseless%2520Projects)
