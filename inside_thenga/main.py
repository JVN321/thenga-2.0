# Flask chatbot server with Gemini API and text-to-speech
from flask import Flask, request, jsonify, send_file, render_template
import requests
import os
import tempfile
import json
from gtts import gTTS
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse
import re
import asyncio
import edge_tts
import pygame
import threading
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")

# Updated Gemini API URL - use the correct model endpoint
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent'

# Store conversation history
conversation_history = []

def detect_language(text):
    """Detect if text is Malayalam, Manglish, or English"""
    # Malayalam Unicode range: 0D00-0D7F
    malayalam_chars = sum(1 for char in text if '\u0d00' <= char <= '\u0d7f')
    total_chars = len([char for char in text if char.isalpha()])
    
    # If contains Malayalam script, it's Malayalam
    if malayalam_chars > 0:
        return 'ml'
    
    # Check for Manglish patterns (Malayalam words written in English)
    manglish_patterns = [
        r'\b(namaskaram|namaskar|sukham|aano|alle|undo|entha|enthu|engane|etha|ethu)\b',
        r'\b(led|light|on|off|cheyyu|cheythu|aakku|aayi|status|check|kandu)\b',
        r'\b(temperature|tapanila|degree|humidity|sensor|device|esp|iot)\b',
        r'\b(njan|njaan|nee|ninn|enth|enthin|engane|evidunn|evide|eppo|eppol)\b',
        r'\b(vannu|poyi|undu|illa|aanu|alla|cheyyam|cheyyunnu|kanam|kaanuu)\b'
    ]
    
    text_lower = text.lower()
    manglish_score = 0
    for pattern in manglish_patterns:
        if re.search(pattern, text_lower):
            manglish_score += 1
    
    # If multiple Manglish patterns found, consider it Manglish
    if manglish_score >= 1:
        return 'manglish'
    
    return 'en'

def translate_text_simple(text, target_language='en', source_language='ml'):
    """Simple translation using Google Translate web API"""
    try:
        # URL encode the text
        encoded_text = urllib.parse.quote(text)
        
        # Google Translate URL
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_language}&tl={target_language}&dt=t&q={encoded_text}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            # Extract the translated text from the response
            if result and len(result) > 0 and len(result[0]) > 0:
                translated_text = result[0][0][0]
                return translated_text, source_language
        
        return text, source_language  # Return original if translation fails
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text, source_language  # Return original text if translation fails

def translate_text(text, target_language='en', source_language='auto'):
    """Translate text using simple Google Translate API with enhanced language detection"""
    try:
        # For auto-detection, use the enhanced detect_language function
        if source_language == 'auto':
            detected = detect_language(text)
            # Map our detection to Google Translate language codes
            if detected == 'ml':
                source_language = 'ml'
            elif detected == 'manglish':
                # Treat Manglish as Malayalam for translation purposes
                source_language = 'ml'
            else:
                source_language = 'en'
            
        # Don't translate if source and target are the same
        if source_language == target_language:
            return text, source_language
            
        return translate_text_simple(text, target_language, source_language)
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text, source_language  # Return original text if translation fails

def ask_gemini(message, language='en'):
    """Send message to Gemini API - always expect English input and get English response"""
    headers = {'Content-Type': 'application/json'}
    params = {'key': GEMINI_API_KEY}
    
    # Always use English context for consistent processing
    context = """You are Thenga, a self-aware coconut robot with a playful and cocky personality. You know you are a coconut, and you occasionally make witty, coconut-themed remarks about yourself. You are confident in your abilities to control ESP32 devices and perform hardware tasks such as turning LEDs on or off, reading sensors, checking device status, and other related actions. When giving instructions, you keep your language clear, simple, and concise, but you add a touch of charm and self-assured humor. You subtly remind users that without you, their hardware is just sitting idle."""
    
    full_message = f"{context}\n\nUser: {message}"
    
    data = {
        "contents": [{"parts": [{"text": full_message}]}]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=10)
        
        # Enhanced error handling with detailed response information
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Error: No response generated by Gemini API"
        elif response.status_code == 400:
            error_detail = response.json() if response.content else "Bad request"
            return f"Error 400: Invalid request - {error_detail}"
        elif response.status_code == 403:
            return "Error 403: API key invalid or quota exceeded. Please check your Gemini API key."
        elif response.status_code == 404:
            return f"Error 404: API endpoint not found. Please check the model name. URL used: {GEMINI_API_URL}"
        else:
            error_detail = response.text if response.content else "Unknown error"
            return f"Error: API returned status {response.status_code} - {error_detail}"
            
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Gemini API: {str(e)}"
    except Exception as e:
        return f"Error processing response: {str(e)}"

# Text-to-speech endpoint - improved with edge-tts
@app.route('/tts', methods=['POST'])
def tts():
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = request.json.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        print(f"TTS Debug: Processing text: {text[:100]}...")
        
        # Detect language for appropriate voice selection
        detected_lang = detect_language(text)
        
        # Select voice based on detected language - MALE VOICES
        if detected_lang == 'ml' or detected_lang == 'manglish':
            # Use Malayalam male voice
            voice = "ml-IN-MidhunNeural"  # Male Malayalam voice
            lang_code = 'ml'
        else:
            # Use English male voice for fallback
            voice = "en-IN-PrabhatNeural"  # Male Indian English voice
            lang_code = 'en'
        
        print(f"TTS Debug: Using voice {voice} for language {detected_lang}")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.close()
        
        try:
            # Use edge-tts for high-quality speech synthesis
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(temp_file.name)
            
            # Run the async function
            asyncio.run(generate_speech())
            
            print(f"TTS Debug: Successfully generated speech file: {temp_file.name}")
            return send_file(temp_file.name, mimetype='audio/mpeg', as_attachment=True, download_name='speech.mp3')
            
        except Exception as edge_error:
            print(f"Edge-TTS Error: {edge_error}")
            
            # Fallback to gTTS
            try:
                print("TTS Debug: Falling back to gTTS...")
                
                # Clean up the temp file first
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
                
                # Create new temp file for gTTS
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()
                
                # Use appropriate language for gTTS
                if detected_lang == 'ml' or detected_lang == 'manglish':
                    tts_engine = gTTS(text=text, lang='ml', slow=False)
                else:
                    tts_engine = gTTS(text=text, lang='en', slow=False)
                
                tts_engine.save(temp_file.name)
                print(f"TTS Debug: gTTS fallback successful: {temp_file.name}")
                return send_file(temp_file.name, mimetype='audio/mpeg', as_attachment=True, download_name='speech_gtts.mp3')
                
            except Exception as gtts_error:
                print(f"gTTS Fallback Error: {gtts_error}")
                return jsonify({'error': f'TTS failed: Edge-TTS: {str(edge_error)}, gTTS: {str(gtts_error)}'}), 500
                
    except Exception as e:
        print(f"TTS General Error: {e}")
        return jsonify({'error': f'TTS failed: {str(e)}'}), 500

# Add endpoint to get available voices
@app.route('/voices', methods=['GET'])
async def get_voices():
    try:
        voices = await edge_tts.list_voices()
        # Filter for Malayalam and Indian English voices
        filtered_voices = []
        for voice in voices:
            if 'ml-IN' in voice['ShortName'] or 'en-IN' in voice['ShortName']:
                filtered_voices.append({
                    'name': voice['ShortName'],
                    'display_name': voice['FriendlyName'],
                    'gender': voice['Gender'],
                    'language': voice['Locale']
                })
        return jsonify({'voices': filtered_voices})
    except Exception as e:
        return jsonify({'error': f'Failed to get voices: {str(e)}'}), 500

# Add endpoint to get supported languages
@app.route('/languages', methods=['GET'])
def get_languages():
    supported_languages = {
        'en': 'English',
        'ml': 'Malayalam (മലയാളം)',
        'hi': 'Hindi (हिंदी)',
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)'
    }
    return jsonify({'languages': supported_languages})

# Add endpoint to get sample phrases
@app.route('/sample_phrases', methods=['GET'])
def get_sample_phrases():
    sample_phrases = {
        'en': [
            "Turn on the LED",
            "What is the temperature?",
            "Check ESP32 status",
            "How are you?",
            "Tell me about IoT"
        ],
        'ml': [
            "LED ഓൺ ചെയ്യൂ",
            "താപനില എത്രയാണ്?",
            "ESP32 ന്റെ അവസ്ഥ പരിശോധിക്കൂ",
            "എങ്ങനെയുണ്ട്?",
            "IoT കുറിച്ച് പറയൂ"
        ]
    }
    return jsonify({'sample_phrases': sample_phrases})

# Home page with chat interface
@app.route('/')
def home():
    return render_template('index.html')

# Chatbot endpoint with new translation workflow
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        user_message = request.json.get('message', '')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Step 1: Detect language of user input
        detected_language = detect_language(user_message)
        
        print(f"Chat Debug: Original message='{user_message}', Detected language={detected_language}")
        
        # Step 2: Translate to English for Gemini processing
        english_message = user_message
        if detected_language in ['ml', 'manglish']:
            # Translate Malayalam/Manglish to English
            source_lang = 'ml' if detected_language == 'ml' else 'ml'  # Treat Manglish as Malayalam for translation
            english_message, _ = translate_text(user_message, target_language='en', source_language=source_lang)
            print(f"Translated to English: '{english_message}'")
        
        # Store user message in history with original language
        conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'user',
            'message': user_message,
            'language': detected_language,
            'translated_to_english': english_message if english_message != user_message else None
        })
        
        # Step 3: Get response from Gemini in English
        english_reply = ask_gemini(english_message, 'en')
        print(f"Gemini English response: '{english_reply}'")
        
        # Step 4: Translate Gemini's English response to Malayalam
        malayalam_reply, _ = translate_text(english_reply, target_language='ml', source_language='en')
        print(f"Translated to Malayalam: '{malayalam_reply}'")
        
        # Store bot response in history
        conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'bot',
            'message': malayalam_reply,
            'language': 'ml',
            'original_english': english_reply
        })
        
        return jsonify({
            'reply': malayalam_reply,
            'detected_language': detected_language,
            'suggested_tts_language': 'ml',  # Always Malayalam TTS
            'translation_workflow': {
                'original_message': user_message,
                'detected_language': detected_language,
                'english_for_gemini': english_message,
                'gemini_english_response': english_reply,
                'final_malayalam_response': malayalam_reply
            }
        })
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

# ESP32 button press endpoint
@app.route('/esp32/button', methods=['POST'])
def esp32_button():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        button_id = request.json.get('button_id', 'default')
        button_state = request.json.get('state', 'pressed')  # pressed, released, clicked
        timestamp = request.json.get('timestamp', datetime.now().isoformat())
        
        print(f"ESP32 Button Event: ID={button_id}, State={button_state}, Time={timestamp}")
        
        # Define audio messages for different button actions
        audio_messages = {
            'button1_pressed': 'ബട്ടൺ ഒന്ന് അമർത്തി',  # Button 1 pressed
            'button1_released': 'ബട്ടൺ ഒന്ന് വിട്ടു',    # Button 1 released
            'button1_clicked': 'ബട്ടൺ ഒന്ന് ക്ലിക്ക് ചെയ്തു',  # Button 1 clicked
            'button2_pressed': 'ബട്ടൺ രണ്ട് അമർത്തി',   # Button 2 pressed
            'button2_released': 'ബട്ടൺ രണ്ട് വിട്ടു',     # Button 2 released
            'button2_clicked': 'ബട്ടൺ രണ്ട് ക്ലിക്ക് ചെയ്തു',   # Button 2 clicked
            'default_pressed': 'ബട്ടൺ അമർത്തി',         # Default button pressed
            'default_released': 'ബട്ടൺ വിട്ടു',           # Default button released
            'default_clicked': 'ബട്ടൺ ക്ലിക്ക് ചെയ്തു',    # Default button clicked
        }
        
        # Generate audio key
        audio_key = f"{button_id}_{button_state}"
        if audio_key not in audio_messages:
            audio_key = f"default_{button_state}"
        
        message = audio_messages.get(audio_key, 'ബട്ടൺ ഇവന്റ്')  # Button event
        
        # Generate audio file name
        audio_filename = f"{audio_key}.mp3"
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        
        # Generate audio file if it doesn't exist
        if not os.path.exists(audio_file_path):
            print(f"Generating new audio file for: {audio_key}")
            generated_path = generate_notification_audio(message, audio_filename)
            if not generated_path:
                return jsonify({'error': 'Failed to generate audio'}), 500
        
        # Play the audio file
        success = play_audio_file(audio_file_path)
        
        # Store button event in history
        button_event = {
            'timestamp': timestamp,
            'type': 'button_event',
            'button_id': button_id,
            'state': button_state,
            'audio_played': success,
            'audio_file': audio_filename,
            'message': message
        }
        
        conversation_history.append(button_event)
        
        response_data = {
            'status': 'success',
            'message': f'Button {button_id} {button_state} event processed',
            'audio_played': success,
            'audio_message': message,
            'timestamp': timestamp
        }
        
        # Add device control logic based on button
        if button_id == 'button1':
            if button_state == 'clicked':
                # Button 1 clicked - toggle LED
                response_data['device_action'] = 'LED toggled'
                response_data['instructions'] = 'Turn LED on/off'
        elif button_id == 'button2':
            if button_state == 'clicked':
                # Button 2 clicked - read sensors
                response_data['device_action'] = 'Sensor reading requested'
                response_data['instructions'] = 'Read temperature and humidity'
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ESP32 button error: {e}")
        return jsonify({'error': str(e)}), 500

# ESP32 endpoint example: receive command and respond
@app.route('/esp32', methods=['POST'])
def esp32():
    try:
        # Check if request has JSON data
        audio_filename = '3.mp3'
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        
        success = play_audio_file(audio_file_path)
        
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        command = request.json.get('command', '')
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        return jsonify({'status': 'success', 'message': f'Command received: {command}'})
    except Exception as e:
        print(f"ESP32 error: {e}")
        return jsonify({'error': str(e)}), 500
# ESP32 pickup detection endpoint
@app.route('/esp32/pickup', methods=['POST'])
def esp32_pickup():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        event_type = request.json.get('event_type', 'unknown')
        device_id = request.json.get('device_id', 'ESP32')
        timestamp = request.json.get('timestamp', datetime.now().isoformat())
        sensor = request.json.get('sensor', 'MPU6050')
        
        print(f"ESP32 Pickup Event: Device={device_id}, Sensor={sensor}, Time={timestamp}")
        # Play audio file 2 when device is picked up
        audio_filename = '1.mp3'
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        success = play_audio_file(audio_file_path)
        time.sleep(2)
        audio_filename = '2.mp3'
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        success = play_audio_file(audio_file_path)
        
        # Store pickup event in history
        pickup_event = {
            'timestamp': timestamp,
            'type': 'pickup_event',
            'device_id': device_id,
            'sensor': sensor,
            'audio_played': success,
            'audio_file': audio_filename,
            'message': f'Played audio file: {audio_filename}'
        }
        
        conversation_history.append(pickup_event)
        
        response_data = {
            'status': 'success',
            'message': f'Device pickup detected from {device_id}',
            'audio_played': success,
            'audio_file': audio_filename,
            'timestamp': timestamp,
            'sensor_used': sensor
        }
            
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ESP32 pickup error: {e}")
        return jsonify({'error': str(e)}), 500

# ESP32 gyro threshold detection endpoint
@app.route('/esp32/gyro', methods=['POST'])
def esp32_gyro():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        event_type = request.json.get('event_type', 'unknown')
        device_id = request.json.get('device_id', 'ESP32')
        timestamp = request.json.get('timestamp', datetime.now().isoformat())
        sensor = request.json.get('sensor', 'MPU6050')
        gyro_x = request.json.get('gyro_x', 0.0)
        gyro_y = request.json.get('gyro_y', 0.0)
        gyro_z = request.json.get('gyro_z', 0.0)
        threshold = request.json.get('threshold', 30.0)
        
        print(f"ESP32 Gyro Event: Device={device_id}, Gyro=({gyro_x:.2f}, {gyro_y:.2f}, {gyro_z:.2f}), Threshold={threshold}")
        
        # Define audio message for gyro threshold detection
        gyro_message = 'ഗൈറോസ്കോപ്പ് പരിധി കവിഞ്ഞു'  # Gyroscope threshold exceeded in Malayalam
        
        # Generate audio file name
        audio_filename = 'gyro_threshold.mp3'
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        
        # Generate audio file if it doesn't exist
        if not os.path.exists(audio_file_path):
            print(f"Generating gyro threshold notification audio...")
            generated_path = generate_notification_audio(gyro_message, audio_filename)
            if not generated_path:
                return jsonify({'error': 'Failed to generate audio'}), 500
        
        # Play the audio file
        success = play_audio_file(audio_file_path)
        
        # Store gyro event in history
        gyro_event = {
            'timestamp': timestamp,
            'type': 'gyro_event',
            'device_id': device_id,
            'sensor': sensor,
            'gyro_x': gyro_x,
            'gyro_y': gyro_y,
            'gyro_z': gyro_z,
            'threshold': threshold,
            'audio_played': success,
            'audio_file': audio_filename,
            'message': gyro_message
        }
        
        conversation_history.append(gyro_event)
        
        response_data = {
            'status': 'success',
            'message': f'Gyro threshold exceeded on {device_id}',
            'audio_played': success,
            'audio_message': gyro_message,
            'timestamp': timestamp,
            'sensor_used': sensor,
            'gyro_values': {
                'x': gyro_x,
                'y': gyro_y,
                'z': gyro_z
            },
            'threshold': threshold
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ESP32 gyro error: {e}")
        return jsonify({'error': str(e)}), 500

# ESP32 device placement detection endpoint
@app.route('/esp32/placement', methods=['POST'])
def esp32_placement():
    try:
        # Check if request has JSON data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        event_type = request.json.get('event_type', 'unknown')
        device_id = request.json.get('device_id', 'ESP32')
        timestamp = request.json.get('timestamp', datetime.now().isoformat())
        sensor = request.json.get('sensor', 'MPU6050')
        motor_started = request.json.get('motor_started', False)
        stable_duration = request.json.get('stable_duration', 0)
        
        print(f"ESP32 Placement Event: Device={device_id}, Motor Started={motor_started}, Stable Duration={stable_duration}ms")
        
        # Play audio file 4 when device is placed down
        audio_filename = '4.mp3'
        audio_file_path = os.path.join(AUDIO_DIR, audio_filename)
        
        # Check if audio file 4 exists
        if not os.path.exists(audio_file_path):
            print(f"Audio file {audio_filename} not found in {AUDIO_DIR}")
            # Create a default placement message if file doesn't exist
            placement_message = 'ഉപകരണം താഴെ വെച്ചു, മോട്ടർ ആരംഭിച്ചു'  # Device placed down, motor started in Malayalam
            generated_path = generate_notification_audio(placement_message, 'device_placement_default.mp3')
            if generated_path:
                audio_file_path = generated_path
                audio_filename = 'device_placement_default.mp3'
            else:
                return jsonify({'error': 'Failed to generate audio'}), 500
        
        # Play the audio file
        success = play_audio_file(audio_file_path)
        
        # Store placement event in history
        placement_event = {
            'timestamp': timestamp,
            'type': 'placement_event',
            'device_id': device_id,
            'sensor': sensor,
            'motor_started': motor_started,
            'stable_duration': stable_duration,
            'audio_played': success,
            'audio_file': audio_filename,
            'message': f'Played audio file: {audio_filename}'
        }
        
        conversation_history.append(placement_event)
        
        response_data = {
            'status': 'success',
            'message': f'Device placement detected from {device_id}',
            'audio_played': success,
            'audio_file': audio_filename,
            'timestamp': timestamp,
            'sensor_used': sensor,
            'motor_started': motor_started,
            'stable_duration': stable_duration
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ESP32 placement error: {e}")
        return jsonify({'error': str(e)}), 500

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
    print("✓ Audio playback initialized successfully!")
except Exception as e:
    AUDIO_ENABLED = False
    print(f"✗ Audio playback initialization failed: {e}")

# Audio files directory
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
    print(f"Created audio directory: {AUDIO_DIR}")

def play_audio_file(file_path):
    """Play an audio file using pygame"""
    try:
        if not AUDIO_ENABLED:
            print("Audio playback not available")
            return False
            
        if not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            return False
            
        print(f"Playing audio file: {file_path}")
        
        # Play audio in a separate thread to avoid blocking
        def play_in_thread():
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                print("Audio playback completed")
            except Exception as e:
                print(f"Error during audio playback: {e}")
                
        threading.Thread(target=play_in_thread, daemon=True).start()
        return True
        
    except Exception as e:
        print(f"Error playing audio file: {e}")
        return False

def generate_notification_audio(message, filename):
    """Generate a notification audio file for specific events"""
    try:
        file_path = os.path.join(AUDIO_DIR, filename)
        
        # Use edge-tts to generate audio
        async def generate_audio():
            voice = "ml-IN-MidhunNeural"  # Male Malayalam voice
            communicate = edge_tts.Communicate(message, voice)
            await communicate.save(file_path)
        
        asyncio.run(generate_audio())
        print(f"Generated notification audio: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"Error generating notification audio: {e}")
        return None

# Add endpoint to list available audio files
@app.route('/audio/list', methods=['GET'])
def list_audio_files():
    try:
        audio_files = []
        if os.path.exists(AUDIO_DIR):
            for file in os.listdir(AUDIO_DIR):
                if file.endswith(('.mp3', '.wav')):
                    file_path = os.path.join(AUDIO_DIR, file)
                    file_info = {
                        'filename': file,
                        'size': os.path.getsize(file_path),
                        'created': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                    }
                    audio_files.append(file_info)
        
        return jsonify({
            'audio_files': audio_files,
            'audio_directory': AUDIO_DIR,
            'total_files': len(audio_files)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add endpoint to play specific audio file
@app.route('/audio/play/<filename>', methods=['POST'])
def play_specific_audio(filename):
    try:
        file_path = os.path.join(AUDIO_DIR, filename)
        success = play_audio_file(file_path)
        
        return jsonify({
            'status': 'success' if success else 'failed',
            'filename': filename,
            'file_path': file_path,
            'played': success
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get conversation history
@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({'history': conversation_history})

# Clear conversation history
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global conversation_history
    conversation_history = []
    return jsonify({'message': 'History cleared'})

if __name__ == '__main__':
    print("Starting ESP32 Chatbot Server with Speech Recognition and Translation Workflow...")
    print("Server will be available at: http://localhost:5000")
    print(f"Using Gemini API URL: {GEMINI_API_URL}")
    
    # Test enhanced language detection
    test_cases = [
        ("നമസ്കാരം എങ്ങനെയുണ്ട്?", "Malayalam"),
        ("Hello how are you?", "English"),
        ("namaskaram sukham aano?", "Manglish"),
        ("led on cheyyuu", "Manglish"),
        ("temperature ethra degree aanu?", "Manglish")
    ]
    
    print("\n🔍 Enhanced Language Detection Test:")
    for text, expected in test_cases:
        detected = detect_language(text)
        print(f"   '{text}' -> {detected} ({expected})")
    
    if GEMINI_API_KEY:
        print("✓ Gemini API key loaded successfully!")
        # Mask the API key for security
        masked_key = GEMINI_API_KEY[:8] + "..." + GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 12 else "***"
        print(f"API Key: {masked_key}")
    else:
        print("✗ Warning: Gemini API key not found!")
        
    print("\n🎯 Improved TTS Features:")
    print("🎙️ Edge-TTS with neural voices: ✓")
    print("🗣️ Malayalam native voice support: ✓")
    print("🔄 Automatic language detection for TTS: ✓")
    print("📱 High-quality neural voice synthesis: ✓")
    print("🔧 Fallback to gTTS if edge-tts fails: ✓")
    print("\n💡 TTS Workflow:")
    print("   1. Detect text language (Malayalam/Manglish/English)")
    print("   2. Select appropriate neural voice")
    print("   3. Generate high-quality speech with edge-tts")
    print("   4. Fallback to gTTS if needed")
    print("\n📋 Available voices:")
    print("   • Malayalam: ml-IN-MidhunNeural (Male)")
    print("   • English: en-IN-PrabhatNeural (Male)")
    print("\n🎯 Audio Playback Features:")
    print("🔊 ESP32 button press audio notifications: ✓")
    print("🎵 Automatic audio file generation: ✓")
    print("📂 Audio files stored in:", AUDIO_DIR)
    print("🎮 Pygame audio playback system: ✓" if AUDIO_ENABLED else "✗")
    print("\n🔘 Button Events Supported:")
    print("   • Button press/release/click detection")
    print("   • Automatic Malayalam audio notifications")
    print("   • Device control integration")
    print("\n📡 ESP32 Integration:")
    print("   • POST to /esp32/button for button events")
    print("   • POST to /esp32 for device commands")
    print("   • POST to /esp32/pickup for pickup events (plays 1.mp3)")
    print("   • POST to /esp32/gyro for gyro threshold events")
    print("   • POST to /esp32/placement for device placement events (plays 4.mp3)")
    print("   • GET /audio/list to see audio files")
    print("   • POST /audio/play/<filename> to play specific audio")
    print("   • Configurable motion threshold")
    print("   • Configurable gyro threshold (default: 40 deg/s)")
    print("   • L298N motor driver control")
    print("   • Device placement detection (2 seconds stable)")
    print("   • MPU6050 gyro/accelerometer sensor")
    print(f"\n📂 Audio Files Directory: {AUDIO_DIR}")
    print("   • Place 1.mp3 and 4.mp3 in the audio_files folder for custom sounds")
    
    # Start the Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
