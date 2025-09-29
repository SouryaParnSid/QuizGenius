#!/usr/bin/env python3
"""
Startup script for RAG API with embedded API key.
"""

import os
import uvicorn

# Load API key from environment - NEVER hardcode API keys!
# Make sure to set GEMINI_API_KEY in your .env file
if not os.getenv('GEMINI_API_KEY'):
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables")
    print("Please set your API key in the .env file before running this script")
    exit(1)

print("🚀 Starting RAG API Server...")
print("📡 Server URL: http://localhost:8001")
print("📖 API Docs: http://localhost:8001/docs")
print("❤️ Health Check: http://localhost:8001/health")
print("=" * 50)

if __name__ == "__main__":
    # Import the app from rag_api module
    from rag_api import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
