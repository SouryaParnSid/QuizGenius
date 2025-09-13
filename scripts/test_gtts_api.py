#!/usr/bin/env python3
"""
Test script to verify the gTTS API route is working correctly.
This script tests the same Python code that the API route uses.
"""

import os
import sys
import tempfile
import shutil

def test_gtts_api_simulation():
    """Simulate the exact process used by the API route."""
    try:
        from gtts import gTTS
    except ImportError as e:
        print(f"❌ gTTS not installed - {e}")
        return False

    try:
        # Test parameters (similar to what API would send)
        text = """Welcome to our AI-generated podcast! Today we'll be exploring the fascinating world of artificial intelligence and machine learning. This is a comprehensive test of our text-to-speech system to ensure high-quality audio generation for our podcast platform."""
        lang = "en"
        tld = "com"
        
        # Create test output directory
        test_dir = os.path.join(os.getcwd(), "test_audio")
        os.makedirs(test_dir, exist_ok=True)
        output_path = os.path.join(test_dir, "test_podcast.mp3")
        
        print(f"🎙️ Testing gTTS API simulation...")
        print(f"Text length: {len(text)} characters")
        print(f"Language: {lang}, TLD: {tld}")
        print(f"Output: {output_path}")
        
        # Validate inputs (same as API)
        if not text or len(text.strip()) == 0:
            print("❌ Empty text provided")
            return False
        
        # Create gTTS object with error handling (same as API)
        try:
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        except Exception as e:
            print(f"❌ Failed to create gTTS object - {e}")
            return False
        
        # Use temporary file first to avoid partial writes (same as API)
        temp_file = None
        try:
            # Create temporary file in same directory as output
            temp_fd, temp_file = tempfile.mkstemp(suffix='.mp3', dir=test_dir)
            os.close(temp_fd)  # Close file descriptor, keep filename
            
            # Save to temporary file
            print("📝 Saving audio...")
            tts.save(temp_file)
            
            # Check if temp file was created successfully
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                print("❌ Temporary file not created or empty")
                return False
            
            # Move temp file to final location
            shutil.move(temp_file, output_path)
            
            # Final verification
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                print(f"✅ API simulation successful! Generated {file_size} bytes")
                
                # Clean up test file
                os.unlink(output_path)
                os.rmdir(test_dir)
                return True
            else:
                print("❌ Final file not created or empty")
                return False
                
        except Exception as e:
            print(f"❌ Audio generation failed - {e}")
            # Clean up temp file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_connectivity():
    """Test if gTTS can connect to Google's servers."""
    try:
        from gtts import gTTS
        import tempfile
        
        print("🌐 Testing network connectivity...")
        
        # Simple network test
        tts = gTTS(text="Network test", lang='en', tld='com', slow=False)
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as tmp_file:
            tts.save(tmp_file.name)
            
            if os.path.getsize(tmp_file.name) > 0:
                print("✅ Network connectivity OK")
                return True
            else:
                print("❌ Network test failed - no data received")
                return False
        
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GTTS API ROUTE TEST")
    print("=" * 50)
    
    # Test 1: Network connectivity
    network_ok = test_network_connectivity()
    print()
    
    # Test 2: API simulation
    api_ok = test_gtts_api_simulation()
    print()
    
    # Summary
    print("=" * 50)
    print("TEST RESULTS:")
    print(f"Network Connectivity: {'✅ PASS' if network_ok else '❌ FAIL'}")
    print(f"API Simulation: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if network_ok and api_ok:
        print("🎉 All tests passed! gTTS should work in the API route.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check your network connection and gTTS installation.")
        sys.exit(1)
