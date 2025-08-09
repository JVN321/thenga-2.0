#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Malayalam Processing Test
Test the new direct Malayalam AI processing without translation
"""

import requests
import json

def test_direct_malayalam_processing():
    """Test direct Malayalam processing with the chatbot"""
    
    print("🎯 Testing Direct Malayalam AI Processing")
    print("=" * 50)
    
    server_url = "http://localhost:5000"
    
    # Test cases
    test_messages = [
        {
            "text": "നമസ്കാരം എങ്ങനെയുണ്ട്?",
            "expected_lang": "ml",
            "description": "Malayalam greeting"
        },
        {
            "text": "LED ഓൺ ചെയ്യൂ",
            "expected_lang": "ml", 
            "description": "Malayalam command"
        },
        {
            "text": "Hello how are you?",
            "expected_lang": "en",
            "description": "English greeting"
        },
        {
            "text": "താപനില എത്രയാണ്?",
            "expected_lang": "ml",
            "description": "Malayalam question"
        }
    ]
    
    print("🧪 Testing different inputs...")
    print("-" * 30)
    
    for i, test in enumerate(test_messages, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Input: '{test['text']}'")
        
        try:
            # Send chat request
            response = requests.post(f"{server_url}/chat", 
                                   json={"message": test['text']},
                                   timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   Detected Language: {data.get('detected_language')}")
                print(f"   AI Response: '{data.get('reply')}'")
                print(f"   Direct Processing: {data.get('direct_processing', False)}")
                
                # Check if language detection is correct
                if data.get('detected_language') == test['expected_lang']:
                    print("   ✅ Language detection: CORRECT")
                else:
                    print("   ❌ Language detection: INCORRECT")
                
                # Check if response is in Malayalam for Malayalam input
                if test['expected_lang'] == 'ml':
                    reply = data.get('reply', '')
                    has_malayalam = any('\u0d00' <= char <= '\u0d7f' for char in reply)
                    if has_malayalam:
                        print("   ✅ Malayalam response: CORRECT")
                    else:
                        print("   ❌ Malayalam response: MISSING (response might be in English)")
                
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Cannot connect to server. Make sure server is running at http://localhost:5000")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Direct Malayalam Processing Benefits:")
    print("✅ No translation delays")
    print("✅ More natural Malayalam responses")
    print("✅ Faster processing")
    print("✅ Better context understanding")
    print("✅ Perfect Malayalam TTS")

def test_tts_endpoint():
    """Test TTS endpoint with Malayalam text"""
    
    print("\n🗣️ Testing Malayalam TTS...")
    print("-" * 30)
    
    server_url = "http://localhost:5000"
    
    malayalam_text = "നമസ്കാരം, ഞാൻ നിങ്ങളുടെ ESP32 സഹായിയാണ്"
    
    try:
        response = requests.post(f"{server_url}/tts",
                               json={"text": malayalam_text, "language": "ml"},
                               timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Malayalam TTS generated successfully!")
            print(f"   Audio size: {len(response.content)} bytes")
        else:
            print(f"❌ TTS failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ TTS test error: {e}")

if __name__ == "__main__":
    print("🧪 Direct Malayalam Processing System Test")
    print("=" * 60)
    
    # Test direct processing
    test_direct_malayalam_processing()
    
    # Test TTS
    test_tts_endpoint()
    
    print("\n💡 Usage Instructions:")
    print("1. Open: http://localhost:5000")
    print("2. Type in Malayalam: 'നമസ്കാരം എങ്ങനെയുണ്ട്?'")
    print("3. Expect: Direct Malayalam response from AI")
    print("4. Click 'Speak': Hear Malayalam TTS")
    print("5. Type in English: 'Hello how are you?'")
    print("6. Expect: English response from AI")
    print("\n🎉 Enjoy your bilingual ESP32 assistant!")
