#!/usr/bin/env python3
"""
Debug retrieval issues in detail
"""
import requests
import json

def debug_retrieval():
    print("=== DEBUGGING RAG RETRIEVAL ===\n")
    
    # 1. Check documents
    print("1. Checking documents in store...")
    try:
        response = requests.get("http://localhost:8001/documents")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Documents API accessible")
            print(f"✓ Total documents: {result.get('total_count', 0)}")
            print(f"✓ Returned documents: {result.get('count', 0)}")
            
            docs = result.get('documents', [])
            if docs:
                print(f"✓ First document preview: {docs[0]['content'][:100]}...")
            else:
                print("✗ No documents returned!")
                return
        else:
            print(f"✗ Documents API failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ Documents API error: {e}")
        return
    
    # 2. Test direct search
    print(f"\n2. Testing direct search...")
    try:
        search_url = "http://localhost:8001/search"
        params = {
            "query": "utility computing",
            "top_k": 5,
            "similarity_threshold": 0.1  # Low threshold
        }
        
        response = requests.get(search_url, params=params)
        print(f"Search status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Search successful: {result.get('success', False)}")
            results = result.get('results', [])
            print(f"✓ Search results count: {len(results)}")
            
            if results:
                for i, res in enumerate(results[:2]):
                    print(f"  Result {i+1}:")
                    print(f"    - Similarity: {res.get('similarity', 'N/A')}")
                    print(f"    - Content: {res.get('content', '')[:80]}...")
            else:
                print("✗ No search results returned!")
        else:
            print(f"✗ Search failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Search error: {e}")
    
    # 3. Test RAG query
    print(f"\n3. Testing RAG query...")
    try:
        query_url = "http://localhost:8001/query"
        query_data = {
            "question": "What is utility computing?",
            "top_k": 5,
            "similarity_threshold": 0.1,
            "response_type": "comprehensive",
            "include_sources": True
        }
        
        response = requests.post(query_url, json=query_data)
        print(f"Query status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Query successful: {result.get('success', False)}")
            print(f"✓ Answer length: {len(result.get('answer', ''))}")
            sources = result.get('sources', [])
            print(f"✓ Sources count: {len(sources)}")
        else:
            print(f"✗ Query failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Query error: {e}")
    
    # 4. Test quiz generation with detailed info
    print(f"\n4. Testing quiz generation...")
    try:
        quiz_url = "http://localhost:8001/generate/quiz"
        quiz_data = {
            "topic": "utility computing",
            "num_questions": 3,
            "difficulty": "medium",
            "question_types": ["multiple_choice"]
        }
        
        response = requests.post(quiz_url, json=quiz_data)
        print(f"Quiz status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Quiz API accessible")
            print(f"✓ Quiz successful: {result.get('success', False)}")
            
            if result.get('success'):
                quiz = result.get('quiz', {})
                questions = quiz.get('questions', [])
                print(f"✓ Questions generated: {len(questions)}")
            else:
                print(f"✗ Quiz error: {result.get('error', 'Unknown error')}")
        else:
            print(f"✗ Quiz API failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Quiz error: {e}")

if __name__ == "__main__":
    debug_retrieval()
