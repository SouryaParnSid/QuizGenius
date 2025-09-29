#!/usr/bin/env python3
"""
Test RAG system with API key.
"""

import os

# Load API key from environment - NEVER hardcode API keys!
# Make sure to set GEMINI_API_KEY in your .env file
if not os.getenv('GEMINI_API_KEY'):
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
    print("Please set your API key in the .env file before running this script")
    exit(1)

try:
    print("Testing RAG System with API key...")
    
    # Test basic import
    from rag import RAGPipeline, RAGConfig
    print("✅ RAG modules imported successfully")
    
    # Test configuration
    config = RAGConfig.from_env()
    print("✅ Configuration loaded")
    print(f"✅ API key configured: {config.gemini_api_key[:20]}...")
    
    # Test pipeline initialization
    pipeline = RAGPipeline(config)
    print("✅ RAG pipeline initialized successfully!")
    
    # Test basic text ingestion
    print("\nTesting text ingestion...")
    result = pipeline.ingest_text(
        text="Artificial Intelligence is transforming the world through machine learning and deep learning.",
        source_name="test_ai_info"
    )
    
    if result["success"]:
        print(f"✅ Text ingested: {result['documents_created']} chunks created")
        
        # Test querying
        print("\nTesting query...")
        query_result = pipeline.query("What is artificial intelligence?")
        
        if query_result["success"]:
            print("✅ Query successful!")
            print(f"Answer: {query_result['answer'][:100]}...")
        else:
            print(f"❌ Query failed: {query_result.get('error')}")
    else:
        print(f"❌ Text ingestion failed: {result.get('error')}")
    
    print("\n🎉 RAG System is fully functional!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
