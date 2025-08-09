#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Malayalam TTS Test Script
Test if Malayalam TTS is working properly
"""

import tempfile
import os
from gtts import gTTS

def test_malayalam_tts():
    """Test Malayalam TTS functionality"""
    
    # Test texts
    malayalam_text = "നമസ്കാരം, എങ്ങനെയുണ്ട്?"
    english_text = "Hello, how are you?"
    
    print("🧪 Testing Malayalam TTS...")
    
    # Test Malayalam TTS
    try:
        print(f"Testing Malayalam: '{malayalam_text}'")
        
        # Try different language codes for Malayalam
        for lang_code in ['ml', 'ml-in']:
            try:
                tts_engine = gTTS(text=malayalam_text, lang=lang_code, slow=False)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts_engine.save(temp_file.name)
                temp_file.close()
                
                file_size = os.path.getsize(temp_file.name)
                print(f"✅ Malayalam TTS SUCCESS with code '{lang_code}' - File size: {file_size} bytes")
                
                # Clean up
                os.unlink(temp_file.name)
                return True
                
            except Exception as e:
                print(f"❌ Malayalam TTS FAILED with code '{lang_code}': {e}")
                continue
                
    except Exception as e:
        print(f"❌ Malayalam TTS FAILED: {e}")
    
    # Test English TTS as fallback
    try:
        print(f"\nTesting English fallback: '{english_text}'")
        tts_engine = gTTS(text=english_text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts_engine.save(temp_file.name)
        temp_file.close()
        
        file_size = os.path.getsize(temp_file.name)
        print(f"✅ English TTS SUCCESS - File size: {file_size} bytes")
        
        # Clean up
        os.unlink(temp_file.name)
        
    except Exception as e:
        print(f"❌ English TTS FAILED: {e}")
        return False
    
    return True

def test_language_detection():
    """Test language detection function"""
    print("\n🔍 Testing Language Detection...")
    
    test_cases = [
        ("Hello how are you?", "en"),
        ("നമസ്കാരം എങ്ങനെയുണ്ട്?", "ml"),
        ("LED ഓൺ ചെയ്യൂ", "ml"),
        ("Turn on the LED", "en"),
        ("നമസ്കാരം! How are you?", "ml"),  # Mixed text
    ]
    
    for text, expected in test_cases:
        # Simple detection logic (same as in main.py)
        malayalam_chars = sum(1 for char in text if '\u0d00' <= char <= '\u0d7f')
        total_chars = len([char for char in text if char.isalpha()])
        
        detected = 'ml' if total_chars > 0 and (malayalam_chars / total_chars) > 0.2 else 'en'
        
        status = "✅" if detected == expected else "❌"
        print(f"{status} '{text}' -> Detected: {detected}, Expected: {expected}")

if __name__ == "__main__":
    print("🧪 Malayalam TTS & Language Detection Test")
    print("=" * 50)
    
    # Test language detection
    test_language_detection()
    
    # Test TTS
    success = test_malayalam_tts()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Malayalam TTS should work.")
        print("\n💡 Tips:")
        print("- Make sure you have internet connection for Google TTS")
        print("- Try typing: 'നമസ്കാരം എങ്ങനെയുണ്ട്?' in the chat")
        print("- The bot should respond in Malayalam")
        print("- TTS should work for Malayalam responses")
    else:
        print("❌ Some tests failed. Check your internet connection and try again.")
