#!/usr/bin/env python3
"""
Test script to debug RAG file upload issue
"""
import requests
import os

def test_upload():
    # Create a simple test text file
    test_content = """
    This is a test document for the RAG system.
    
    Utility computing is a service provisioning model in which a service provider 
    makes computing resources and infrastructure management available to the customer 
    as needed, and charges them for specific usage rather than a flat rate.
    
    Key characteristics:
    1. On-demand availability
    2. Pay-per-use pricing
    3. Scalable resources
    4. Managed infrastructure
    
    This model is similar to traditional utilities like electricity or water.
    """
    
    # Write test file
    test_file_path = "test_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("Created test file:", test_file_path)
    
    # Test upload to RAG API
    url = "http://localhost:8001/ingest/file"
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            data = {
                "chunking_strategy": "recursive",
                "custom_metadata": '{"source": "test_upload", "topic": "utility_computing"}'
            }
            
            print(f"Uploading to: {url}")
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Upload successful!")
            else:
                print("❌ Upload failed!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print("Cleaned up test file")

    # Check documents count after upload
    try:
        response = requests.get("http://localhost:8001/documents")
        print(f"Documents endpoint response: {response.text}")
    except Exception as e:
        print(f"Error checking documents: {e}")

if __name__ == "__main__":
    test_upload()
