#!/usr/bin/env python3
"""
Quick Fix Script for RAG Dependencies

Addresses the specific SQLite and PyTorch/Transformers compatibility issues.
"""

import subprocess
import sys
import os
import platform


def run_command(cmd):
    """Run a command safely."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("Success")
            return True
        else:
            print(f"Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Quick fix for dependency issues."""
    print("Quick Fix for RAG Dependencies")
    print("=" * 40)
    
    # Step 1: Install compatible PyTorch first
    print("\n1. Installing compatible PyTorch...")
    if run_command("pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu"):
        print("PyTorch installed successfully")
    
    # Step 2: Install compatible transformers
    print("\n2. Installing compatible Transformers...")
    run_command("pip install transformers==4.35.2")
    
    # Step 3: Install sentence-transformers
    print("\n3. Installing Sentence Transformers...")
    run_command("pip install sentence-transformers==2.2.2")
    
    # Step 4: Install SQLite fix for Windows
    if platform.system() == "Windows":
        print("\n4. Installing SQLite fix for Windows...")
        run_command("pip install pysqlite3-binary")
    
    # Step 5: Try ChromaDB, fallback to FAISS
    print("\n5. Installing vector database...")
    if not run_command("pip install chromadb==0.4.22"):
        print("ChromaDB failed, installing FAISS as fallback...")
        run_command("pip install faiss-cpu")
    
    # Step 6: Install other essential dependencies
    print("\n6. Installing other dependencies...")
    essential_deps = [
        "langchain==0.1.20",
        "langchain-google-genai==1.0.10", 
        "google-generativeai==0.3.2",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-dotenv==1.0.0",
        "pypdf==3.17.4",
        "python-docx==1.1.0",
        "numpy==1.24.4"
    ]
    
    for dep in essential_deps:
        run_command(f"pip install {dep}")
    
    print("\n" + "=" * 40)
    print("Quick fix completed!")
    print("\nNext steps:")
    print("1. Copy env.example to .env: cp env.example .env")
    print("2. Edit .env and add your GEMINI_API_KEY")
    print("3. Test with: python -c \"from rag import RAGPipeline; print('Success!')\"")


if __name__ == "__main__":
    main()
