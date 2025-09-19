"""
FAISS-based Vector Store Fallback

Alternative vector store implementation using FAISS when ChromaDB fails.
Provides similar functionality with better cross-platform compatibility.
"""

import logging
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .config import RAGConfig
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class Document:
    """Document class for FAISS vector store."""
    
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ):
        self.id = doc_id or str(uuid.uuid4())
        self.content = content
        self.metadata = metadata or {}
        self.metadata["created_at"] = datetime.now().isoformat()
        self.metadata["content_length"] = len(content)


class FAISSVectorStore:
    """FAISS-based vector store as fallback for ChromaDB."""
    
    def __init__(self, config: RAGConfig, embedding_service: EmbeddingService):
        """Initialize FAISS vector store."""
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        self.config = config
        self.embedding_service = embedding_service
        
        # FAISS index
        self.index = None
        self.documents = {}  # doc_id -> Document
        self.id_to_index = {}  # doc_id -> index position
        self.index_to_id = {}  # index position -> doc_id
        
        # Persistence
        self.persist_dir = Path(config.chromadb_persist_directory.replace("chromadb", "faiss"))
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self._load_index()
    
    def _load_index(self):
        """Load existing index from disk."""
        index_file = self.persist_dir / "faiss.index"
        metadata_file = self.persist_dir / "metadata.pkl"
        
        if index_file.exists() and metadata_file.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.id_to_index = data['id_to_index']
                    self.index_to_id = data['index_to_id']
                
                logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            except Exception as e:
                logger.warning(f"Failed to load existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        dimension = self.embedding_service.get_dimension()
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        self.documents = {}
        self.id_to_index = {}
        self.index_to_id = {}
        logger.info(f"Created new FAISS index with dimension {dimension}")
    
    def _save_index(self):
        """Save index and metadata to disk."""
        try:
            # Save FAISS index
            index_file = self.persist_dir / "faiss.index"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = self.persist_dir / "metadata.pkl"
            data = {
                'documents': self.documents,
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id
            }
            with open(metadata_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug("Saved FAISS index and metadata")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        if not documents:
            return []
        
        logger.info(f"Adding {len(documents)} documents to FAISS store")
        
        try:
            # Generate embeddings
            texts = [doc.content for doc in documents]
            embeddings = self.embedding_service.encode_texts(texts)
            
            # Normalize embeddings for cosine similarity
            embeddings_array = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings_array)
            
            # Add to index
            start_index = self.index.ntotal
            self.index.add(embeddings_array)
            
            # Update mappings
            doc_ids = []
            for i, doc in enumerate(documents):
                index_pos = start_index + i
                self.documents[doc.id] = doc
                self.id_to_index[doc.id] = index_pos
                self.index_to_id[index_pos] = doc.id
                doc_ids.append(doc.id)
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Successfully added {len(documents)} documents")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        n_results = n_results or self.config.top_k_retrieval
        
        if self.index.ntotal == 0:
            return []
        
        logger.info(f"Searching for top {n_results} similar documents")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode_text(query)
            query_embedding = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query_embedding)
            
            # Search
            search_k = min(n_results * 2, self.index.ntotal)
            scores, indices = self.index.search(query_embedding, search_k)
            logger.info(f"FAISS search returned {len(scores[0])} results, max score: {max(scores[0]) if len(scores[0]) > 0 else 'N/A'}")
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                doc_id = self.index_to_id.get(idx)
                if not doc_id or doc_id not in self.documents:
                    continue
                
                document = self.documents[doc_id]
                similarity = float(score)  # FAISS returns inner product
                
                # Apply metadata filter
                if filter_metadata:
                    if not all(
                        document.metadata.get(k) == v 
                        for k, v in filter_metadata.items()
                    ):
                        continue
                
                # Apply similarity threshold (use a lower threshold for FAISS inner product)
                # FAISS inner product scores are different from cosine similarity
                effective_threshold = min(0.1, self.config.similarity_threshold)  # Much lower threshold for FAISS
                logger.debug(f"Document {doc_id} similarity: {similarity}, threshold: {effective_threshold}")
                
                if similarity >= effective_threshold:
                    results.append({
                        "id": doc_id,
                        "content": document.content,
                        "metadata": document.metadata,
                        "similarity": similarity,
                        "distance": 1 - similarity
                    })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:n_results]
            
            logger.info(f"Found {len(results)} documents above similarity threshold")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        if doc_id in self.documents:
            doc = self.documents[doc_id]
            return {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata
            }
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id not in self.documents:
            return False
        
        try:
            # Remove from mappings
            if doc_id in self.id_to_index:
                index_pos = self.id_to_index[doc_id]
                del self.id_to_index[doc_id]
                del self.index_to_id[index_pos]
            
            del self.documents[doc_id]
            
            # Note: FAISS doesn't support individual deletion
            # We'd need to rebuild the index to truly remove it
            # For now, just remove from our mappings
            
            self._save_index()
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List documents with optional filtering."""
        documents = []
        
        for doc_id, doc in self.documents.items():
            # Apply metadata filter
            if filter_metadata:
                if not all(
                    doc.metadata.get(k) == v 
                    for k, v in filter_metadata.items()
                ):
                    continue
            
            documents.append({
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata
            })
            
            if limit and len(documents) >= limit:
                break
        
        return documents
    
    def count_documents(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in the collection."""
        if not filter_metadata:
            return len(self.documents)
        
        count = 0
        for doc in self.documents.values():
            if all(
                doc.metadata.get(k) == v 
                for k, v in filter_metadata.items()
            ):
                count += 1
        
        return count
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self._create_new_index()
            self._save_index()
            logger.info("Cleared all documents from FAISS store")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        return {
            "name": "faiss_collection",
            "document_count": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_service.get_dimension(),
            "persist_directory": str(self.persist_dir)
        }
