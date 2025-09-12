#!/usr/bin/env python3
"""
Simple test script for gTTS functionality.
"""

def test_gtts():
    try:
        from gtts import gTTS
        import tempfile
        import os
        
        print("🎙️ Testing gTTS...")
        
        # Test text
        text = "Hello! This is a test of Google Text to Speech for the QuizGenius podcast generator."
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', tld='com', slow=False)
            
            # Save to file
            tts.save(output_path)
            
            # Check if file was created
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print("✅ gTTS test successful!")
                print(f"Audio file created: {os.path.getsize(output_path)} bytes")
                return True
            else:
                print("❌ gTTS test failed - no audio file created")
                return False
                
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
        
    except ImportError:
        print("❌ gTTS not installed. Run: pip install gtts")
        return False
    except Exception as e:
        print(f"❌ gTTS test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_gtts()
    exit(0 if success else 1)

