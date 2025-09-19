#!/usr/bin/env python3
"""
RAG System Setup Script

Sets up the RAG system with necessary directories, configurations,
and validates the installation.
"""

import os
import sys
import logging
from pathlib import Path
import subprocess
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'langchain',
        'chromadb',
        'sentence_transformers',
        'fastapi',
        'uvicorn',
        'google.generativeai',
        'pypdf',
        'python-docx',
        'numpy',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                importlib.import_module('google.generativeai')
            elif package == 'python-docx':
                importlib.import_module('docx')
            else:
                importlib.import_module(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install missing packages with: pip install -r requirements-rag.txt")
        return False
    
    logger.info("All required dependencies are installed")
    return True


def create_directories():
    """Create necessary directories for the RAG system."""
    directories = [
        "data",
        "data/chromadb",
        "data/uploads", 
        "data/logs",
        "data/embedding_cache",
        "data/exports"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")
    
    return True


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        logger.info("✓ .env file already exists")
        return True
    
    if env_example.exists():
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        logger.info("✓ Created .env file from env.example")
        logger.warning("⚠ Please edit .env file and add your API keys")
        return True
    else:
        logger.warning("⚠ env.example not found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        return True


def validate_config():
    """Validate the configuration."""
    try:
        from rag.config import RAGConfig
        
        # Try to load config
        config = RAGConfig.from_env()
        
        # Check API key
        if not config.gemini_api_key or config.gemini_api_key == "your_gemini_api_key_here":
            logger.warning("⚠ GEMINI_API_KEY not set or using placeholder value")
            logger.info("Please set your Gemini API key in the .env file")
            return False
        
        # Validate config
        config.validate()
        logger.info("✓ Configuration is valid")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def test_rag_system():
    """Test basic RAG system functionality."""
    try:
        logger.info("Testing RAG system components...")
        
        # Test embedding service
        from rag.embeddings import EmbeddingService
        from rag.config import RAGConfig
        
        config = RAGConfig.from_env()
        embedding_service = EmbeddingService(config)
        
        # Test embedding generation
        test_text = "This is a test sentence."
        embedding = embedding_service.encode_text(test_text)
        
        if embedding is not None and len(embedding) > 0:
            logger.info("✓ Embedding service working")
        else:
            logger.error("✗ Embedding service failed")
            return False
        
        # Test vector store initialization
        from rag.vector_store import VectorStoreService
        vector_store = VectorStoreService(config, embedding_service)
        
        info = vector_store.get_collection_info()
        if info:
            logger.info("✓ Vector store working")
        else:
            logger.error("✗ Vector store failed")
            return False
        
        logger.info("✓ RAG system test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"RAG system test failed: {e}")
        return False


def install_dependencies():
    """Install dependencies using pip."""
    try:
        logger.info("Installing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements-rag.txt"
        ])
        logger.info("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("=== RAG System Setup ===")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    # Check if dependencies should be installed
    if "--install-deps" in sys.argv:
        if not install_dependencies():
            sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        logger.info("Run with --install-deps to install missing dependencies")
        sys.exit(1)
    
    # Validate configuration
    if not validate_config():
        logger.warning("Configuration validation failed - please check your .env file")
        # Don't exit here as user might want to configure manually
    
    # Test RAG system (only if config is valid)
    try:
        if test_rag_system():
            logger.info("🎉 RAG system setup completed successfully!")
            logger.info("You can now start the API server with: python rag_api.py")
        else:
            logger.warning("RAG system test failed - please check your configuration")
    except:
        logger.warning("Could not test RAG system - please ensure configuration is complete")
    
    logger.info("=== Setup Complete ===")


if __name__ == "__main__":
    main()
