"""
Embedding Service

Service for generating embeddings using Sentence Transformers.
Handles text vectorization for semantic search.
"""

import logging
import numpy as np
from typing import List, Optional, Union
from sentence_transformers import SentenceTransformer
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import pickle
from pathlib import Path

from .config import RAGConfig

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using Sentence Transformers."""
    
    def __init__(self, config: RAGConfig):
        """Initialize the embedding service."""
        self.config = config
        self.model: Optional[SentenceTransformer] = None
        self.cache_dir = Path("./data/embedding_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def _load_model(self) -> SentenceTransformer:
        """Load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            try:
                self.model = SentenceTransformer(self.config.embedding_model)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self.model
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(f"{self.config.embedding_model}:{text}".encode()).hexdigest()
    
    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding if available."""
        if not self.config.enable_caching:
            return None
        
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    embedding = pickle.load(f)
                logger.debug(f"Retrieved cached embedding for text hash: {cache_key[:8]}")
                return embedding
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {e}")
        
        return None
    
    def _cache_embedding(self, text: str, embedding: np.ndarray) -> None:
        """Cache embedding for future use."""
        if not self.config.enable_caching:
            return
        
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(embedding, f)
            logger.debug(f"Cached embedding for text hash: {cache_key[:8]}")
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        # Check cache first
        cached_embedding = self._get_cached_embedding(text)
        if cached_embedding is not None:
            return cached_embedding
        
        # Generate new embedding
        model = self._load_model()
        embedding = model.encode(text, convert_to_numpy=True)
        
        # Cache the result
        self._cache_embedding(text, embedding)
        
        return embedding
    
    def encode_texts(self, texts: List[str], batch_size: Optional[int] = None) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        batch_size = batch_size or self.config.batch_size
        embeddings = []
        
        # Check cache for all texts first
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cached_embedding = self._get_cached_embedding(text)
            if cached_embedding is not None:
                embeddings.append(cached_embedding)
            else:
                embeddings.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            model = self._load_model()
            logger.info(f"Generating embeddings for {len(uncached_texts)} uncached texts")
            
            # Process in batches
            for i in range(0, len(uncached_texts), batch_size):
                batch_texts = uncached_texts[i:i + batch_size]
                batch_embeddings = model.encode(batch_texts, convert_to_numpy=True)
                
                # Update embeddings list and cache results
                for j, embedding in enumerate(batch_embeddings):
                    original_index = uncached_indices[i + j]
                    embeddings[original_index] = embedding
                    self._cache_embedding(batch_texts[j], embedding)
        
        return embeddings
    
    async def encode_text_async(self, text: str) -> np.ndarray:
        """Generate embedding for a single text asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.encode_text, text)
    
    async def encode_texts_async(self, texts: List[str], batch_size: Optional[int] = None) -> List[np.ndarray]:
        """Generate embeddings for multiple texts asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.encode_texts, texts, batch_size)
    
    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def get_similarities(self, query_embedding: np.ndarray, embeddings: List[np.ndarray]) -> List[float]:
        """Calculate similarities between query embedding and list of embeddings."""
        similarities = []
        for embedding in embeddings:
            similarity = self.get_similarity(query_embedding, embedding)
            similarities.append(similarity)
        return similarities
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()
    
    def validate_embedding(self, embedding: np.ndarray) -> bool:
        """Validate that embedding has correct dimensions."""
        expected_dim = self.get_dimension()
        return embedding.shape == (expected_dim,)
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        model = self._load_model()
        return {
            "model_name": self.config.embedding_model,
            "max_seq_length": getattr(model, "max_seq_length", "Unknown"),
            "embedding_dimension": self.get_dimension(),
            "pooling_mode": str(getattr(model._modules.get("1", None), "pooling_mode", "Unknown")),
        }
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Embedding cache cleared")
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)
