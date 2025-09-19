#!/usr/bin/env python3
"""
Test the similarity search fix
"""
import requests
import time

def test_similarity_search():
    print("Testing similarity search...")
    
    # First, upload a test document
    print("1. Uploading test document...")
    test_content = """
    This document contains information about utility computing and cloud services.
    
    Utility computing is a service model where computing resources are provided 
    on-demand and billed based on usage, similar to traditional utilities like 
    electricity or water. This approach allows organizations to scale their 
    computing needs dynamically.
    
    Key benefits include:
    - Cost efficiency through pay-per-use pricing
    - Scalability to handle varying workloads
    - Reduced infrastructure management overhead
    - Access to enterprise-grade resources without large capital investments
    """
    
    # Write test file
    with open("test_doc.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # Upload to RAG API
    url = "http://localhost:8001/ingest/file"
    try:
        with open("test_doc.txt", "rb") as f:
            files = {"file": ("test_doc.txt", f, "text/plain")}
            data = {"chunking_strategy": "recursive"}
            
            response = requests.post(url, files=files, data=data)
            print(f"Upload status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Documents created: {result.get('documents_created', 0)}")
            else:
                print(f"Upload failed: {response.text}")
                return
    except Exception as e:
        print(f"Upload error: {e}")
        return
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test quiz generation
    print("\n2. Testing quiz generation...")
    try:
        quiz_url = "http://localhost:8001/generate/quiz"
        quiz_data = {
            "topic": "utility computing",
            "num_questions": 3,
            "difficulty": "medium"
        }
        
        response = requests.post(quiz_url, json=quiz_data)
        print(f"Quiz generation status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Quiz generated successfully: {result.get('success', False)}")
            questions = result.get('quiz', {}).get('questions', [])
            print(f"Number of questions: {len(questions)}")
            
            if questions:
                print("\nFirst question:")
                print(f"Q: {questions[0].get('question', 'N/A')}")
                print(f"Options: {questions[0].get('options', [])}")
            else:
                print("No questions generated!")
        else:
            print(f"Quiz generation failed: {response.text}")
            
    except Exception as e:
        print(f"Quiz generation error: {e}")
    
    # Cleanup
    import os
    if os.path.exists("test_doc.txt"):
        os.remove("test_doc.txt")

if __name__ == "__main__":
    test_similarity_search()
