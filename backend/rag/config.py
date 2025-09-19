"""
RAG System Configuration

Centralized configuration for the RAG system including models,
vector store settings, and API configurations.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RAGConfig:
    """Configuration class for RAG system."""
    
    # API Keys
    gemini_api_key: Optional[str] = None
    
    # Model configurations
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer model
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Vector store configuration
    vector_store_type: str = "chromadb"  # chromadb or faiss
    chromadb_persist_directory: str = "./data/chromadb"
    collection_name: str = "documents"
    
    # Document processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens_per_chunk: int = 512
    
    # Retrieval configuration
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.1  # Lower threshold for better retrieval with limited content
    
    # Generation configuration
    max_context_length: int = 4000
    temperature: float = 0.7
    max_output_tokens: int = 1000
    
    # File handling
    supported_file_types: tuple = (".pdf", ".txt", ".docx", ".md")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    upload_directory: str = "./data/uploads"
    
    # System settings
    batch_size: int = 32
    enable_caching: bool = True
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create configuration from environment variables."""
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            vector_store_type=os.getenv("VECTOR_STORE_TYPE", "chromadb"),
            chromadb_persist_directory=os.getenv(
                "CHROMADB_PERSIST_DIRECTORY", "./data/chromadb"
            ),
            collection_name=os.getenv("COLLECTION_NAME", "documents"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            max_tokens_per_chunk=int(os.getenv("MAX_TOKENS_PER_CHUNK", "512")),
            top_k_retrieval=int(os.getenv("TOP_K_RETRIEVAL", "5")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7")),
            max_context_length=int(os.getenv("MAX_CONTEXT_LENGTH", "4000")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            max_output_tokens=int(os.getenv("MAX_OUTPUT_TOKENS", "1000")),
            upload_directory=os.getenv("UPLOAD_DIRECTORY", "./data/uploads"),
            batch_size=int(os.getenv("BATCH_SIZE", "32")),
            enable_caching=os.getenv("ENABLE_CACHING", "True").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        if self.top_k_retrieval <= 0:
            raise ValueError("top_k_retrieval must be positive")
        
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        
        return True
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = [
            self.chromadb_persist_directory,
            self.upload_directory,
            "./data/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "embedding_model": self.embedding_model,
            "gemini_model": self.gemini_model,
            "vector_store_type": self.vector_store_type,
            "chromadb_persist_directory": self.chromadb_persist_directory,
            "collection_name": self.collection_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_tokens_per_chunk": self.max_tokens_per_chunk,
            "top_k_retrieval": self.top_k_retrieval,
            "similarity_threshold": self.similarity_threshold,
            "max_context_length": self.max_context_length,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "supported_file_types": self.supported_file_types,
            "max_file_size": self.max_file_size,
            "upload_directory": self.upload_directory,
            "batch_size": self.batch_size,
            "enable_caching": self.enable_caching,
            "log_level": self.log_level,
        }


# Global configuration instance
config = RAGConfig.from_env()
