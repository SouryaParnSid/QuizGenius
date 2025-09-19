"""
Vector Store Service

Service for managing document vectors using ChromaDB.
Handles document storage, retrieval, and similarity search.
"""

import logging
import uuid
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json
from datetime import datetime

# Try ChromaDB import, but don't fail if it's not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    CHROMADB_AVAILABLE = False
    print(f"ChromaDB not available: {e}")

from .config import RAGConfig
from .embeddings import EmbeddingService

# Fallback imports
try:
    from .vector_store_fallback import FAISSVectorStore, Document as FallbackDocument
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

logger = logging.getLogger(__name__)


class Document:
    """Document class for storing text chunks with metadata."""
    
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


class VectorStoreService:
    """Service for managing document vectors using ChromaDB."""
    
    def __init__(self, config: RAGConfig, embedding_service: EmbeddingService):
        """Initialize the vector store service."""
        self.config = config
        self.embedding_service = embedding_service
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self._use_fallback = False
        self._fallback_store = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client and collection."""
        # First check if ChromaDB is available
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, using FAISS fallback")
            if FALLBACK_AVAILABLE:
                self._use_fallback = True
                self._fallback_store = FAISSVectorStore(self.config, self.embedding_service)
                logger.info("Successfully initialized FAISS fallback")
                return
            else:
                raise RuntimeError("Neither ChromaDB nor FAISS available")
        
        try:
            # Create persist directory if it doesn't exist
            persist_dir = Path(self.config.chromadb_persist_directory)
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            settings = Settings(
                persist_directory=str(persist_dir),
                anonymized_telemetry=False
            )
            self.client = chromadb.Client(settings)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.collection_name
                )
                logger.info(f"Loaded existing collection: {self.config.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.config.collection_name,
                    metadata={"description": "RAG document collection"}
                )
                logger.info(f"Created new collection: {self.config.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            # Try fallback to FAISS if available
            if FALLBACK_AVAILABLE:
                logger.info("Attempting to use FAISS fallback...")
                try:
                    self._use_fallback = True
                    self._fallback_store = FAISSVectorStore(self.config, self.embedding_service)
                    logger.info("Successfully initialized FAISS fallback")
                    return
                except Exception as fallback_error:
                    logger.error(f"FAISS fallback also failed: {fallback_error}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        if not documents:
            return []
        
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.add_documents(documents)
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            # Generate embeddings for all documents
            texts = [doc.content for doc in documents]
            embeddings = self.embedding_service.encode_texts(texts)
            
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully added {len(documents)} documents")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def add_document(self, document: Document) -> str:
        """Add a single document to the vector store."""
        return self.add_documents([document])[0]
    
    def search(
        self,
        query: str,
        n_results: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        n_results = n_results or self.config.top_k_retrieval
        
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.search(query, n_results, filter_metadata)
        
        logger.info(f"Searching for top {n_results} similar documents")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.encode_text(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                doc_id = results["ids"][0][i]
                content = results["documents"][0][i]
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                # Filter by similarity threshold
                if similarity >= self.config.similarity_threshold:
                    formatted_results.append({
                        "id": doc_id,
                        "content": content,
                        "metadata": metadata,
                        "similarity": similarity,
                        "distance": distance
                    })
            
            logger.info(f"Found {len(formatted_results)} documents above similarity threshold")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if results["ids"]:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            return None
    
    def update_document(self, doc_id: str, document: Document) -> bool:
        """Update an existing document."""
        try:
            # Generate new embedding
            embedding = self.embedding_service.encode_text(document.content)
            
            # Update in ChromaDB
            self.collection.update(
                ids=[doc_id],
                documents=[document.content],
                embeddings=[embedding.tolist()],
                metadatas=[document.metadata]
            )
            
            logger.info(f"Updated document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.delete_document(doc_id)
        
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def delete_documents(self, doc_ids: List[str]) -> int:
        """Delete multiple documents by IDs."""
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            deleted_count = 0
            for doc_id in doc_ids:
                if self._fallback_store.delete_document(doc_id):
                    deleted_count += 1
            return deleted_count
        
        try:
            self.collection.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents")
            return len(doc_ids)
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return 0
    
    def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List documents with optional filtering."""
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.list_documents(filter_metadata, limit)
        
        try:
            results = self.collection.get(
                where=filter_metadata,
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            documents = []
            for i in range(len(results["ids"])):
                documents.append({
                    "id": results["ids"][i],
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    def count_documents(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """Count documents in the collection."""
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.count_documents(filter_metadata)
        
        try:
            if filter_metadata:
                results = self.collection.get(where=filter_metadata, limit=1)
                # ChromaDB doesn't have a direct count with filter, so we estimate
                # This is a simplified approach
                all_results = self.collection.get(where=filter_metadata)
                return len(all_results["ids"])
            else:
                return self.collection.count()
                
        except Exception as e:
            logger.error(f"Failed to count documents: {e}")
            return 0
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        # Use fallback if ChromaDB failed
        if self._use_fallback and self._fallback_store:
            return self._fallback_store.clear_collection()
        
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs["ids"]:
                self.collection.delete(ids=all_docs["ids"])
            
            logger.info("Cleared all documents from collection")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            count = self.collection.count()
            return {
                "name": self.config.collection_name,
                "document_count": count,
                "embedding_dimension": self.embedding_service.get_dimension(),
                "persist_directory": self.config.chromadb_persist_directory
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def export_collection(self, file_path: str) -> bool:
        """Export collection to a JSON file."""
        try:
            documents = self.list_documents()
            
            export_data = {
                "collection_name": self.config.collection_name,
                "export_date": datetime.now().isoformat(),
                "document_count": len(documents),
                "documents": documents
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported collection to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export collection: {e}")
            return False
    
    def import_collection(self, file_path: str) -> bool:
        """Import collection from a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            documents = []
            for doc_data in import_data["documents"]:
                document = Document(
                    content=doc_data["content"],
                    metadata=doc_data["metadata"],
                    doc_id=doc_data["id"]
                )
                documents.append(document)
            
            self.add_documents(documents)
            logger.info(f"Imported {len(documents)} documents from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import collection: {e}")
            return False
