#!/usr/bin/env python3
"""
Setup script to verify Edge TTS installation for podcast generation.
Run this script to test if the TTS system is working correctly.
"""

import sys
import subprocess

def check_gtts():
    """Check if gTTS is installed and working."""
    try:
        from gtts import gTTS
        print("✅ gTTS is installed")
        return True
    except ImportError:
        print("❌ gTTS is not installed")
        print("Install it with: pip install gtts")
        return False

def test_tts_generation():
    """Test basic TTS generation."""
    try:
        from gtts import gTTS
        import tempfile
        import os
        
        text = "This is a test of the Google Text to Speech system for podcast generation."
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', tld='com', slow=False)
            
            # Save to file
            tts.save(output_path)
            
            # Check if file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print("✅ TTS generation test successful")
                print(f"Audio file created: {os.path.getsize(output_path)} bytes")
                return True
            else:
                print("❌ TTS generation failed - no audio file created")
                return False
        finally:
            # Clean up test file
            if os.path.exists(output_path):
                os.unlink(output_path)
        
    except Exception as e:
        print(f"❌ TTS generation test failed: {e}")
        return False

def main():
    """Main setup verification function."""
    print("🎙️ Setting up gTTS for Podcast Generation...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check gTTS installation
    if not check_gtts():
        return False
    
    # Test TTS generation
    if not test_tts_generation():
        return False
    
    print("=" * 50)
    print("🎉 gTTS setup complete! The podcast generator is ready to use.")
    print("\nAvailable voice accents include:")
    print("- US English (professional)")
    print("- UK English (casual)")
    print("- Australian English (academic)")
    print("- Canadian English (friendly)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
