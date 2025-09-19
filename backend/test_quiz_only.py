#!/usr/bin/env python3
"""
Test only quiz generation with existing documents
"""
import requests
import json

def test_quiz():
    print("Testing quiz generation with existing documents...")
    
    try:
        quiz_url = "http://localhost:8001/generate/quiz"
        quiz_data = {
            "topic": "utility computing",
            "num_questions": 2,
            "difficulty": "easy",
            "question_types": ["multiple_choice"]
        }
        
        print(f"Sending request to: {quiz_url}")
        print(f"Request data: {json.dumps(quiz_data, indent=2)}")
        
        response = requests.post(quiz_url, json=quiz_data)
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                quiz = result.get('quiz', {})
                if isinstance(quiz, str):
                    quiz = json.loads(quiz)
                
                questions = quiz.get('questions', [])
                print(f"Questions generated: {len(questions)}")
                
                for i, q in enumerate(questions, 1):
                    print(f"\nQuestion {i}:")
                    print(f"  Q: {q.get('question', 'N/A')}")
                    print(f"  Type: {q.get('type', 'N/A')}")
                    print(f"  Options: {q.get('options', [])}")
                    print(f"  Correct Answer: {q.get('correct_answer', 'N/A')}")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Full response: {json.dumps(result, indent=2)}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_quiz()
