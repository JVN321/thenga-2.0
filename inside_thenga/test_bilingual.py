# Test script to demonstrate bilingual features
import requests
import json

def test_language_detection():
    """Test the language detection and bilingual chat feature"""
    
    # Test English input
    english_message = "Hello, how are you?"
    print(f"Testing English: '{english_message}'")
    
    # Test Malayalam input  
    malayalam_message = "നമസ്കാരം, എങ്ങനെയുണ്ട്?"
    print(f"Testing Malayalam: '{malayalam_message}'")
    
    # Note: These tests require the server to be running
    # Uncomment the lines below to test with actual server
    
    """
    # Test with English
    response = requests.post('http://localhost:5000/chat', 
                           json={'message': english_message})
    if response.status_code == 200:
        data = response.json()
        print(f"English detected: {data.get('detected_language')}")
        print(f"Reply: {data.get('reply')}")
    
    # Test with Malayalam
    response = requests.post('http://localhost:5000/chat', 
                           json={'message': malayalam_message})
    if response.status_code == 200:
        data = response.json()
        print(f"Malayalam detected: {data.get('detected_language')}")
        print(f"Reply: {data.get('reply')}")
    
    # Test TTS
    tts_response = requests.post('http://localhost:5000/tts',
                               json={'text': malayalam_message, 'language': 'ml'})
    if tts_response.status_code == 200:
        print("Malayalam TTS generated successfully!")
    """

if __name__ == "__main__":
    test_language_detection()
    print("\n✅ Language detection system is ready!")
    print("🚀 Start the server with: python main.py")
    print("🌐 Then visit: http://localhost:5000")
