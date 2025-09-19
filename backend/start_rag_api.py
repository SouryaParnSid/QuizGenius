#!/usr/bin/env python3
"""
Startup script for RAG API with embedded API key.
"""

import os
import uvicorn

# Set the API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyD6qe2a7hPLHzXqXsx_i9zEy45hOyTRdog'

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
