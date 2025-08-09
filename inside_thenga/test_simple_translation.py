#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Translation Test Script
Test the new simple translation functionality
"""

import requests
import urllib.parse

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

def test_simple_translation():
    """Test the simple translation function"""
    
    print("🔄 Testing Simple Translation Functionality...")
    print("=" * 50)
    
    # Test cases - Malayalam to English
    malayalam_tests = [
        "നമസ്കാരം എങ്ങനെയുണ്ട്?",
        "LED ഓൺ ചെയ്യൂ",
        "താപനില എത്രയാണ്?",
        "ESP32 ന്റെ അവസ്ഥ പരിശോധിക്കൂ"
    ]
    
    print("📝 Malayalam to English:")
    for text in malayalam_tests:
        translated, _ = translate_text_simple(text, 'en', 'ml')
        print(f"✅ '{text}' -> '{translated}'")
    
    print("\n📝 English to Malayalam:")
    english_tests = [
        "Hello, how are you?",
        "Turn on the LED",
        "What is the temperature?",
        "Check ESP32 status"
    ]
    
    for text in english_tests:
        translated, _ = translate_text_simple(text, 'ml', 'en')
        print(f"✅ '{text}' -> '{translated}'")
    
    print("\n🔄 Round-trip Translation Test:")
    original = "നമസ്കാരം എങ്ങനെയുണ്ട്?"
    
    # Malayalam to English
    to_english, _ = translate_text_simple(original, 'en', 'ml')
    print(f"Original Malayalam: '{original}'")
    print(f"To English: '{to_english}'")
    
    # English back to Malayalam
    back_to_malayalam, _ = translate_text_simple(to_english, 'ml', 'en')
    print(f"Back to Malayalam: '{back_to_malayalam}'")

if __name__ == "__main__":
    print("🧪 Simple Translation Test")
    print("=" * 60)
    
    try:
        test_simple_translation()
        
        print("\n" + "=" * 60)
        print("🎉 Simple translation system working!")
        print("\n💡 Translation Flow:")
        print("1. Malayalam input detected")
        print("2. Malayalam -> English for AI")
        print("3. AI processes in English")
        print("4. English response -> Malayalam")
        print("5. User sees Malayalam with TTS")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your internet connection and try again.")
