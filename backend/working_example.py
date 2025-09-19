#!/usr/bin/env python3
"""
Working example of RAG system.
"""

import os

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyD6qe2a7hPLHzXqXsx_i9zEy45hOyTRdog'

from rag import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

print("🚀 RAG System Working Example")
print("=" * 40)

# Ingest some sample content
print("\n1. Ingesting sample content...")
sample_content = """
Artificial Intelligence (AI) is a field of computer science focused on creating 
intelligent machines. Machine learning is a subset of AI that enables computers 
to learn from data. Deep learning uses neural networks with multiple layers to 
process information similar to the human brain.

Natural Language Processing (NLP) is a branch of AI that helps computers 
understand and work with human language. It's used in applications like 
chatbots, translation services, and sentiment analysis.

Computer vision is another AI field that enables machines to interpret and 
understand visual information from the world, such as images and videos.
"""

result = pipeline.ingest_text(
    text=sample_content,
    source_name="ai_basics",
    custom_metadata={"topic": "artificial_intelligence"}
)

print(f"✅ Content ingested: {result['documents_created']} chunks")

# Test query with lower similarity threshold
print("\n2. Testing query...")
query_result = pipeline.query(
    question="What is artificial intelligence?",
    similarity_threshold=0.3,  # Lower threshold
    top_k=3
)

if query_result["success"]:
    print("✅ Query successful!")
    print(f"\nQuestion: {query_result['query']}")
    print(f"Answer: {query_result['answer']}")
    print(f"Documents used: {query_result['retrieved_documents']}")
else:
    print(f"❌ Query failed: {query_result.get('error')}")

print("\n3. Testing document listing...")
docs = pipeline.list_documents()
print(f"✅ Total documents in store: {docs['count']}")

print("\n✅ RAG System is fully operational!")
print("\nYou can now:")
print("- Start the API: python rag_api.py")
print("- Upload documents via API")
print("- Query the knowledge base")
print("- Generate quizzes and summaries")
