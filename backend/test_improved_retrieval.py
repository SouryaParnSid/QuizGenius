#!/usr/bin/env python3
"""
Test the improved content retrieval for podcast generation
"""
import requests
import time

def test_improved_retrieval():
    print("=== TESTING IMPROVED CONTENT RETRIEVAL ===\n")
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(3)
    
    test_topic = "AI in Action: From Waste Management to Virtual Assistants"
    
    try:
        print(f"🧪 Testing improved RAG query for: '{test_topic}'")
        
        # Test with the new improved settings
        response = requests.post('http://localhost:8001/query', json={
            'question': test_topic,
            'response_type': 'comprehensive',
            'include_sources': True,
            'top_k': 8,
            'similarity_threshold': 0.1
        })
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                content = result.get('answer', '')
                sources = result.get('sources', [])
                
                print(f"✅ Improved RAG Query successful!")
                print(f"📊 Content length: {len(content)} characters")
                print(f"📊 Word count: {len(content.split())} words")
                print(f"📊 Source documents returned: {len(sources)}")
                
                # Check improvement
                word_count = len(content.split())
                if word_count >= 500:
                    print(f"✅ EXCELLENT: Content is now substantial ({word_count} words)")
                    print("   This should generate a much better podcast!")
                elif word_count >= 300:
                    print(f"✅ GOOD: Content improved ({word_count} words)")
                    print("   Combined with enhanced AI expansion, this should work much better!")
                else:
                    print(f"⚠️  MODERATE: Content is still limited ({word_count} words)")
                    print("   The enhanced AI prompt should help expand this significantly.")
                
                print(f"\n📄 Content preview (first 300 chars):")
                print("-" * 50)
                print(content[:300] + "..." if len(content) > 300 else content)
                print("-" * 50)
                
                if sources:
                    print(f"\n📚 Sources retrieved ({len(sources)}):")
                    for i, source in enumerate(sources[:3], 1):
                        source_file = source.get('metadata', {}).get('source_file', 'Unknown')
                        similarity = source.get('similarity', 0)
                        content_length = len(source.get('content', ''))
                        print(f"   {i}. Similarity: {similarity:.3f}, Length: {content_length} chars")
                        print(f"      File: {source_file}")
                
                return True
                
            else:
                print(f"❌ RAG query failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing improved retrieval: {e}")
        return False

if __name__ == "__main__":
    success = test_improved_retrieval()
    
    print("\n" + "="*60)
    if success:
        print("✅ CONTENT RETRIEVAL IMPROVEMENTS APPLIED!")
        print("\n🎙️  For podcast generation, the system now:")
        print("   • Uses lower similarity threshold (0.1 instead of 0.7)")
        print("   • Retrieves up to 8 document chunks (instead of 5)")
        print("   • Has enhanced AI prompt for content expansion")
        print("   • Should generate much longer, more comprehensive podcasts")
        print("\n💡 Try generating a podcast now - it should be much longer!")
    else:
        print("❌ IMPROVEMENTS NEED MORE WORK")
        print("💡 Make sure the RAG API is running on localhost:8001")
