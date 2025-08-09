#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Test Script
Test if Malayalam to English and back translation is working
"""

from googletrans import Translator
import sys

def test_translation():
    """Test translation functionality"""
    
    # Initialize translator
    translator = Translator()
    
    print("🔄 Testing Translation Functionality...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("നമസ്കാരം എങ്ങനെയുണ്ട്?", "ml", "en"),
        ("LED ഓൺ ചെയ്യൂ", "ml", "en"),
        ("താപനില എത്രയാണ്?", "ml", "en"),
        ("ESP32 ന്റെ അവസ്ഥ പരിശോധിക്കൂ", "ml", "en"),
    ]
    
    print("📝 Malayalam to English Translation:")
    for text, src, dest in test_cases:
        try:
            result = translator.translate(text, src=src, dest=dest)
            print(f"✅ '{text}' -> '{result.text}'")
        except Exception as e:
            print(f"❌ Translation failed for '{text}': {e}")
    
    print("\n📝 English to Malayalam Translation:")
    english_texts = [
        "Hello, how are you?",
        "Turn on the LED",
        "What is the temperature?",
        "Check ESP32 status"
    ]
    
    for text in english_texts:
        try:
            result = translator.translate(text, src='en', dest='ml')
            print(f"✅ '{text}' -> '{result.text}'")
        except Exception as e:
            print(f"❌ Translation failed for '{text}': {e}")
    
    print("\n🔄 Round-trip Translation Test:")
    malayalam_original = "നമസ്കാരം എങ്ങനെയുണ്ട്?"
    
    try:
        # Malayalam to English
        to_english = translator.translate(malayalam_original, src='ml', dest='en')
        print(f"Original Malayalam: '{malayalam_original}'")
        print(f"Translated to English: '{to_english.text}'")
        
        # English back to Malayalam
        back_to_malayalam = translator.translate(to_english.text, src='en', dest='ml')
        print(f"Back to Malayalam: '{back_to_malayalam.text}'")
        
        print("✅ Round-trip translation completed!")
        
    except Exception as e:
        print(f"❌ Round-trip translation failed: {e}")

def test_auto_detection():
    """Test automatic language detection"""
    
    print("\n🔍 Testing Language Auto-Detection...")
    print("=" * 50)
    
    translator = Translator()
    
    test_texts = [
        "Hello how are you?",
        "നമസ്കാരം എങ്ങനെയുണ്ട്?",
        "LED ഓൺ ചെയ്യൂ",
        "Turn on the LED"
    ]
    
    for text in test_texts:
        try:
            detection = translator.detect(text)
            print(f"'{text}' -> Detected: {detection.lang} (confidence: {detection.confidence:.2f})")
        except Exception as e:
            print(f"❌ Detection failed for '{text}': {e}")

if __name__ == "__main__":
    print("🧪 Google Translate Integration Test")
    print("=" * 60)
    
    try:
        # Test basic translation
        test_translation()
        
        # Test auto-detection
        test_auto_detection()
        
        print("\n" + "=" * 60)
        print("🎉 Translation system ready!")
        print("\n💡 How it works:")
        print("1. Malayalam input is detected automatically")
        print("2. Malayalam is translated to English for AI processing")
        print("3. AI responds in English (better understanding)")
        print("4. English response is translated back to Malayalam")
        print("5. User sees Malayalam response with TTS support")
        
    except ImportError:
        print("❌ Error: googletrans library not found")
        print("Run: pip install googletrans==4.0.0rc1")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
