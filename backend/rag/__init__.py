"""
RAG System Package

Retrieval-Augmented Generation system using LangChain, ChromaDB, 
Sentence Transformers, and Google Gemini API.
"""

# Apply compatibility fixes first
try:
    from .compatibility import check_dependencies
    check_dependencies()
except Exception as e:
    print(f"Warning: Compatibility check failed: {e}")

from .config import RAGConfig
from .embeddings import EmbeddingService
from .vector_store import VectorStoreService
from .document_processor import DocumentProcessor
from .retriever import RetrieverService
from .generator import GeneratorService
from .rag_pipeline import RAGPipeline

__version__ = "1.0.0"

__all__ = [
    "RAGConfig",
    "EmbeddingService", 
    "VectorStoreService",
    "DocumentProcessor",
    "RetrieverService",
    "GeneratorService",
    "RAGPipeline"
]
