# Configuration file for ESP32 Chatbot
# Copy this file to config.py and update with your actual values

# Gemini API Configuration
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# Server Configuration
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# ESP32 Configuration
ESP32_COMMANDS = {
    "turn_on_led": "LED turned on successfully.",
    "turn_off_led": "LED turned off successfully.", 
    "get_status": "ESP32 status: Online and ready.",
    "read_sensors": "Temperature: 25°C, Humidity: 60%",
    "reset": "ESP32 reset command sent.",
    "sleep": "ESP32 entering sleep mode."
}

# Text-to-Speech Configuration
TTS_LANGUAGE = "en"
TTS_SLOW = False
