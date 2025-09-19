"""
Retrieval Service

Service for retrieving relevant documents from the vector store
based on query similarity and filtering.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from .config import RAGConfig
from .vector_store import VectorStoreService
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    content: str
    metadata: Dict[str, Any]
    similarity: float
    doc_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "similarity": self.similarity,
            "doc_id": self.doc_id
        }


class RetrieverService:
    """Service for retrieving relevant documents."""
    
    def __init__(
        self,
        config: RAGConfig,
        vector_store: VectorStoreService,
        embedding_service: EmbeddingService
    ):
        """Initialize the retriever service."""
        self.config = config
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents for a query."""
        top_k = top_k or self.config.top_k_retrieval
        similarity_threshold = similarity_threshold or self.config.similarity_threshold
        
        logger.info(f"Retrieving documents for query (top_k={top_k}, threshold={similarity_threshold})")
        
        try:
            # Search in vector store
            search_results = self.vector_store.search(
                query=query,
                n_results=top_k * 2 if rerank else top_k,  # Get more for reranking
                filter_metadata=filter_metadata
            )
            
            # Convert to RetrievalResult objects
            results = []
            for result in search_results:
                # Don't apply threshold here - vector store already filtered
                # The FAISS fallback already applies an appropriate threshold
                retrieval_result = RetrievalResult(
                    content=result["content"],
                    metadata=result["metadata"],
                    similarity=result["similarity"],
                    doc_id=result["id"]
                )
                results.append(retrieval_result)
            
            # Rerank if requested
            if rerank and len(results) > top_k:
                results = self._rerank_results(query, results)[:top_k]
            
            logger.info(f"Retrieved {len(results)} relevant documents")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def retrieve_by_keywords(
        self,
        keywords: List[str],
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve documents based on keywords."""
        # Combine keywords into a query
        query = " ".join(keywords)
        return self.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filter_metadata=filter_metadata
        )
    
    def retrieve_similar_to_document(
        self,
        doc_id: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        exclude_self: bool = True
    ) -> List[RetrievalResult]:
        """Retrieve documents similar to a given document."""
        # Get the reference document
        ref_doc = self.vector_store.get_document(doc_id)
        if not ref_doc:
            logger.error(f"Reference document {doc_id} not found")
            return []
        
        # Use the document content as query
        results = self.retrieve(
            query=ref_doc["content"],
            top_k=(top_k or self.config.top_k_retrieval) + (1 if exclude_self else 0),
            similarity_threshold=similarity_threshold
        )
        
        # Exclude the reference document itself if requested
        if exclude_self:
            results = [r for r in results if r.doc_id != doc_id]
        
        return results[:top_k or self.config.top_k_retrieval]
    
    def retrieve_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """Retrieve documents by metadata filtering only."""
        try:
            documents = self.vector_store.list_documents(
                filter_metadata=metadata_filter,
                limit=top_k
            )
            
            results = []
            for doc in documents:
                result = RetrievalResult(
                    content=doc["content"],
                    metadata=doc["metadata"],
                    similarity=1.0,  # No similarity calculation for metadata-only search
                    doc_id=doc["id"]
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents by metadata: {e}")
            return []
    
    def retrieve_hybrid(
        self,
        query: str,
        keywords: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[RetrievalResult]:
        """Hybrid retrieval combining semantic and keyword search."""
        top_k = top_k or self.config.top_k_retrieval
        
        # Semantic search
        semantic_results = self.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            filter_metadata=metadata_filter,
            rerank=False
        )
        
        # Keyword search (if keywords provided)
        keyword_results = []
        if keywords:
            keyword_results = self.retrieve_by_keywords(
                keywords=keywords,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                filter_metadata=metadata_filter
            )
        
        # Combine and rerank
        combined_results = self._combine_hybrid_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight
        )
        
        return combined_results[:top_k]
    
    def _rerank_results(self, query: str, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Rerank results based on additional criteria."""
        try:
            # Generate query embedding for comparison
            query_embedding = self.embedding_service.encode_text(query)
            
            # Calculate additional scores
            for result in results:
                # Content length score (prefer medium-length content)
                content_length = len(result.content)
                optimal_length = 500  # Optimal chunk length
                length_score = 1.0 - abs(content_length - optimal_length) / optimal_length
                length_score = max(0.1, min(1.0, length_score))
                
                # Freshness score (if timestamp available)
                freshness_score = 1.0
                if "processed_at" in result.metadata:
                    # This could be enhanced with actual date parsing
                    freshness_score = 0.8  # Default slightly lower score for older content
                
                # Metadata relevance score
                metadata_score = self._calculate_metadata_relevance(query, result.metadata)
                
                # Combined score
                combined_score = (
                    result.similarity * 0.6 +
                    length_score * 0.2 +
                    freshness_score * 0.1 +
                    metadata_score * 0.1
                )
                
                # Update similarity with combined score
                result.similarity = combined_score
            
            # Sort by updated similarity
            results.sort(key=lambda x: x.similarity, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to rerank results: {e}")
            return results
    
    def _combine_hybrid_results(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        semantic_weight: float,
        keyword_weight: float
    ) -> List[RetrievalResult]:
        """Combine semantic and keyword search results."""
        # Create a mapping of doc_id to results
        result_map: Dict[str, RetrievalResult] = {}
        
        # Add semantic results
        for result in semantic_results:
            result_copy = RetrievalResult(
                content=result.content,
                metadata=result.metadata,
                similarity=result.similarity * semantic_weight,
                doc_id=result.doc_id
            )
            result_map[result.doc_id] = result_copy
        
        # Add keyword results
        for result in keyword_results:
            if result.doc_id in result_map:
                # Combine scores
                result_map[result.doc_id].similarity += result.similarity * keyword_weight
            else:
                # New result from keyword search
                result_copy = RetrievalResult(
                    content=result.content,
                    metadata=result.metadata,
                    similarity=result.similarity * keyword_weight,
                    doc_id=result.doc_id
                )
                result_map[result.doc_id] = result_copy
        
        # Convert back to list and sort
        combined_results = list(result_map.values())
        combined_results.sort(key=lambda x: x.similarity, reverse=True)
        
        return combined_results
    
    def _calculate_metadata_relevance(self, query: str, metadata: Dict[str, Any]) -> float:
        """Calculate relevance score based on metadata."""
        score = 0.0
        query_lower = query.lower()
        
        # Check file name relevance
        if "file_name" in metadata:
            file_name = str(metadata["file_name"]).lower()
            if any(word in file_name for word in query_lower.split()):
                score += 0.3
        
        # Check source relevance
        if "source" in metadata:
            source = str(metadata["source"]).lower()
            if any(word in source for word in query_lower.split()):
                score += 0.2
        
        # Check file type preference (prefer text documents)
        if "file_type" in metadata:
            file_type = str(metadata["file_type"]).lower()
            if file_type in [".txt", ".md", ".markdown"]:
                score += 0.1
        
        # Prefer earlier chunks (usually contain more important info)
        if "chunk_index" in metadata:
            chunk_index = metadata.get("chunk_index", 0)
            total_chunks = metadata.get("total_chunks", 1)
            if total_chunks > 1:
                position_score = 1.0 - (chunk_index / total_chunks)
                score += position_score * 0.2
        
        return min(score, 1.0)
    
    def get_retrieval_stats(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> Dict[str, Any]:
        """Get statistics about retrieval results."""
        if not results:
            return {
                "total_results": 0,
                "avg_similarity": 0.0,
                "max_similarity": 0.0,
                "min_similarity": 0.0,
                "total_content_length": 0,
                "avg_content_length": 0.0,
                "unique_sources": 0
            }
        
        similarities = [r.similarity for r in results]
        content_lengths = [len(r.content) for r in results]
        sources = set()
        
        for result in results:
            if "source_file" in result.metadata:
                sources.add(result.metadata["source_file"])
            elif "source" in result.metadata:
                sources.add(result.metadata["source"])
        
        return {
            "query": query,
            "total_results": len(results),
            "avg_similarity": sum(similarities) / len(similarities),
            "max_similarity": max(similarities),
            "min_similarity": min(similarities),
            "total_content_length": sum(content_lengths),
            "avg_content_length": sum(content_lengths) / len(content_lengths),
            "unique_sources": len(sources),
            "similarity_distribution": {
                "above_0.8": len([s for s in similarities if s >= 0.8]),
                "above_0.6": len([s for s in similarities if s >= 0.6]),
                "above_0.4": len([s for s in similarities if s >= 0.4]),
                "below_0.4": len([s for s in similarities if s < 0.4])
            }
        }
    
    def explain_retrieval(
        self,
        query: str,
        result: RetrievalResult
    ) -> Dict[str, Any]:
        """Explain why a specific document was retrieved."""
        explanation = {
            "query": query,
            "doc_id": result.doc_id,
            "similarity": result.similarity,
            "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content,
            "factors": {}
        }
        
        # Analyze similarity factors
        try:
            query_embedding = self.embedding_service.encode_text(query)
            content_embedding = self.embedding_service.encode_text(result.content)
            base_similarity = self.embedding_service.get_similarity(query_embedding, content_embedding)
            
            explanation["factors"]["semantic_similarity"] = base_similarity
            explanation["factors"]["metadata_bonus"] = result.similarity - base_similarity
            
        except Exception as e:
            logger.warning(f"Could not calculate similarity factors: {e}")
        
        # Metadata factors
        explanation["factors"]["metadata_relevance"] = self._calculate_metadata_relevance(query, result.metadata)
        
        # Content factors
        explanation["factors"]["content_length"] = len(result.content)
        explanation["factors"]["chunk_position"] = result.metadata.get("chunk_index", "unknown")
        
        return explanation
