#!/usr/bin/env python3
"""
Debug the RAG content being used for podcast generation
"""
import requests
import json

def test_rag_content_for_podcast():
    print("=== DEBUGGING RAG PODCAST CONTENT ===\n")
    
    # Test a sample query to see what content RAG returns
    test_topic = "AI in Action: From Waste Management to Virtual Assistants"
    
    try:
        print(f"🧪 Testing RAG query for topic: '{test_topic}'")
        
        # Query RAG with same parameters as the frontend
        response = requests.post('http://localhost:8001/query', json={
            'question': test_topic,
            'response_type': 'comprehensive',
            'include_sources': True,
            'top_k': 8
        })
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                content = result.get('answer', '')
                sources = result.get('sources', [])
                
                print(f"✅ RAG Query successful!")
                print(f"📊 Content length: {len(content)} characters")
                print(f"📊 Word count: {len(content.split())} words")
                print(f"📊 Source documents: {len(sources)}")
                print(f"\n📄 Content preview (first 500 chars):")
                print("-" * 50)
                print(content[:500] + "..." if len(content) > 500 else content)
                print("-" * 50)
                
                # Check if content is substantial enough for podcast
                word_count = len(content.split())
                if word_count < 200:
                    print(f"\n⚠️  WARNING: Content is quite short ({word_count} words)")
                    print("   This might result in a very brief podcast script.")
                    print("   Recommendation: Upload more detailed documents or use longer documents.")
                elif word_count < 500:
                    print(f"\n⚠️  MODERATE: Content is moderate length ({word_count} words)")
                    print("   This should generate a decent podcast but may not fill the full duration.")
                else:
                    print(f"\n✅ GOOD: Content is substantial ({word_count} words)")
                    print("   This should generate a comprehensive podcast script.")
                
                print(f"\n📚 Source breakdown:")
                for i, source in enumerate(sources[:5], 1):
                    source_file = source.get('metadata', {}).get('source_file', 'Unknown')
                    similarity = source.get('similarity', 0)
                    content_length = len(source.get('content', ''))
                    print(f"   {i}. {source_file} (similarity: {similarity:.3f}, {content_length} chars)")
                
                # Test what the podcast API would receive
                print(f"\n🎙️  PODCAST GENERATION SIMULATION:")
                print(f"   Input to /api/generate-podcast:")
                print(f"   - Content length: {len(content)} characters")
                print(f"   - Duration: '5-7 minutes'")
                print(f"   - Style: 'educational'")
                print(f"   - Expected word count for 5-7 min: 900-1260 words (150-180 WPM)")
                
                if len(content.split()) >= 900:
                    print(f"   ✅ Content should be sufficient for 5-7 minute podcast")
                else:
                    print(f"   ❌ Content may be insufficient for 5-7 minute podcast")
                    print(f"   💡 The AI should expand this content, but if it's too brief, it might not work well")
                
            else:
                print(f"❌ RAG query failed: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing RAG content: {e}")

def test_document_count():
    """Check how many documents are in the RAG system"""
    try:
        response = requests.get('http://localhost:8001/documents')
        if response.status_code == 200:
            data = response.json()
            doc_count = len(data.get('documents', []))
            total_count = data.get('total_count', 0)
            
            print(f"\n📊 DOCUMENT STATUS:")
            print(f"   • Document chunks: {doc_count}")
            print(f"   • Total reported: {total_count}")
            
            if doc_count == 0:
                print(f"   ❌ No documents in RAG system!")
                print(f"   💡 This explains why podcasts are short - no content to work with!")
            elif doc_count < 10:
                print(f"   ⚠️  Very few documents - might not have enough content for long podcasts")
            else:
                print(f"   ✅ Good document count for podcast generation")
                
        else:
            print(f"❌ Error checking documents: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking document count: {e}")

if __name__ == "__main__":
    test_document_count()
    print()
    test_rag_content_for_podcast()
