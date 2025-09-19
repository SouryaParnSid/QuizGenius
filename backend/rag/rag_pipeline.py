"""
RAG Pipeline

Main pipeline that orchestrates the entire RAG workflow:
document processing, storage, retrieval, and generation.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import asyncio

from .config import RAGConfig
from .embeddings import EmbeddingService
from .vector_store import VectorStoreService, Document
from .document_processor import DocumentProcessor
from .retriever import RetrieverService, RetrievalResult
from .generator import GeneratorService, GenerationResult

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main RAG pipeline orchestrating all components."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize the RAG pipeline."""
        self.config = config or RAGConfig.from_env()
        self.config.validate()
        self.config.ensure_directories()
        
        # Initialize services
        self.embedding_service = EmbeddingService(self.config)
        self.vector_store = VectorStoreService(self.config, self.embedding_service)
        self.document_processor = DocumentProcessor(self.config)
        self.retriever = RetrieverService(self.config, self.vector_store, self.embedding_service)
        self.generator = GeneratorService(self.config)
        
        logger.info("RAG Pipeline initialized successfully")
    
    def ingest_document(
        self,
        file_path: str,
        chunking_strategy: str = "recursive",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest a single document into the RAG system."""
        try:
            logger.info(f"Ingesting document: {file_path}")
            
            # Validate file
            is_valid, error_msg = self.document_processor.validate_file(file_path)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "file_path": file_path
                }
            
            # Process document
            documents = self.document_processor.process_file(
                file_path=file_path,
                chunking_strategy=chunking_strategy,
                custom_metadata=custom_metadata
            )
            
            if not documents:
                return {
                    "success": False,
                    "error": "No documents generated from file",
                    "file_path": file_path
                }
            
            # Store in vector database
            doc_ids = self.vector_store.add_documents(documents)
            
            result = {
                "success": True,
                "file_path": file_path,
                "documents_created": len(documents),
                "document_ids": doc_ids,
                "chunking_strategy": chunking_strategy,
                "metadata": {
                    "file_name": Path(file_path).name,
                    "file_type": Path(file_path).suffix,
                    "total_chunks": len(documents),
                    "avg_chunk_size": sum(len(doc.content) for doc in documents) / len(documents)
                }
            }
            
            logger.info(f"Successfully ingested {file_path}: {len(documents)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def ingest_text(
        self,
        text: str,
        source_name: str = "text_input",
        chunking_strategy: str = "recursive",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest raw text into the RAG system."""
        try:
            logger.info(f"Ingesting text: {source_name}")
            
            # Process text
            documents = self.document_processor.process_text(
                text=text,
                source_name=source_name,
                chunking_strategy=chunking_strategy,
                custom_metadata=custom_metadata
            )
            
            if not documents:
                return {
                    "success": False,
                    "error": "No documents generated from text",
                    "source_name": source_name
                }
            
            # Store in vector database
            doc_ids = self.vector_store.add_documents(documents)
            
            result = {
                "success": True,
                "source_name": source_name,
                "documents_created": len(documents),
                "document_ids": doc_ids,
                "chunking_strategy": chunking_strategy,
                "metadata": {
                    "text_length": len(text),
                    "total_chunks": len(documents),
                    "avg_chunk_size": sum(len(doc.content) for doc in documents) / len(documents)
                }
            }
            
            logger.info(f"Successfully ingested text '{source_name}': {len(documents)} chunks created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to ingest text '{source_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "source_name": source_name
            }
    
    def ingest_batch(
        self,
        file_paths: List[str],
        chunking_strategy: str = "recursive",
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ingest multiple documents in batch."""
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch ingestion of {len(file_paths)} files")
        
        for file_path in file_paths:
            result = self.ingest_document(
                file_path=file_path,
                chunking_strategy=chunking_strategy,
                custom_metadata=custom_metadata
            )
            
            results.append(result)
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        summary = {
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results,
            "total_documents": sum(r.get("documents_created", 0) for r in results if r["success"])
        }
        
        logger.info(f"Batch ingestion completed: {successful} successful, {failed} failed")
        return summary
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
        response_type: str = "comprehensive",
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """Query the RAG system for an answer."""
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            # Retrieve relevant documents
            retrieval_results = self.retriever.retrieve(
                query=question,
                top_k=top_k,
                similarity_threshold=similarity_threshold,
                filter_metadata=filter_metadata
            )
            
            if not retrieval_results:
                return {
                    "success": False,
                    "error": "No relevant documents found",
                    "query": question,
                    "retrieved_documents": 0
                }
            
            # Generate response
            generation_result = self.generator.generate_response(
                query=question,
                context_results=retrieval_results,
                response_type=response_type,
                include_sources=include_sources
            )
            
            # Prepare response
            response = {
                "success": True,
                "query": question,
                "answer": generation_result.response,
                "retrieved_documents": len(retrieval_results),
                "context_used": generation_result.context_used,
                "metadata": generation_result.metadata,
                "retrieval_stats": self.retriever.get_retrieval_stats(question, retrieval_results)
            }
            
            logger.info(f"Query processed successfully: {len(retrieval_results)} docs retrieved")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": question
            }
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate quiz questions based on stored documents."""
        try:
            logger.info(f"Generating quiz on topic: {topic}")
            
            # Retrieve relevant documents
            retrieval_results = self.retriever.retrieve(
                query=topic,
                top_k=self.config.top_k_retrieval * 2,  # Get more context for quiz generation
                filter_metadata=filter_metadata
            )
            
            if not retrieval_results:
                return {
                    "success": False,
                    "error": "No relevant documents found for quiz generation",
                    "topic": topic
                }
            
            # Generate quiz
            generation_result = self.generator.generate_quiz_questions(
                context_results=retrieval_results,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types
            )
            
            response = {
                "success": True,
                "topic": topic,
                "quiz": generation_result.response,
                "context_used": generation_result.context_used,
                "metadata": generation_result.metadata
            }
            
            logger.info(f"Quiz generated successfully for topic: {topic}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate quiz: {e}")
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    def summarize_documents(
        self,
        query: str,
        summary_type: str = "comprehensive",
        max_length: int = 500,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a summary of relevant documents."""
        try:
            logger.info(f"Generating summary for: {query}")
            
            # Retrieve relevant documents
            retrieval_results = self.retriever.retrieve(
                query=query,
                top_k=self.config.top_k_retrieval * 2,  # Get more context for summary
                filter_metadata=filter_metadata
            )
            
            if not retrieval_results:
                return {
                    "success": False,
                    "error": "No relevant documents found for summarization",
                    "query": query
                }
            
            # Generate summary
            generation_result = self.generator.generate_summary(
                context_results=retrieval_results,
                summary_type=summary_type,
                max_length=max_length
            )
            
            response = {
                "success": True,
                "query": query,
                "summary": generation_result.response,
                "context_used": generation_result.context_used,
                "metadata": generation_result.metadata
            }
            
            logger.info(f"Summary generated successfully for: {query}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def get_similar_documents(
        self,
        doc_id: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """Find documents similar to a given document."""
        try:
            similar_docs = self.retriever.retrieve_similar_to_document(
                doc_id=doc_id,
                top_k=top_k or self.config.top_k_retrieval
            )
            
            return {
                "success": True,
                "reference_doc_id": doc_id,
                "similar_documents": [doc.to_dict() for doc in similar_docs],
                "count": len(similar_docs)
            }
            
        except Exception as e:
            logger.error(f"Failed to find similar documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "reference_doc_id": doc_id
            }
    
    def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """List documents in the vector store."""
        try:
            documents = self.vector_store.list_documents(
                filter_metadata=filter_metadata,
                limit=limit
            )
            
            return {
                "success": True,
                "documents": documents,
                "count": len(documents),
                "total_count": self.vector_store.count_documents()
            }
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from the vector store."""
        try:
            success = self.vector_store.delete_document(doc_id)
            
            return {
                "success": success,
                "doc_id": doc_id,
                "message": "Document deleted successfully" if success else "Failed to delete document"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return {
                "success": False,
                "error": str(e),
                "doc_id": doc_id
            }
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """Clear all documents from the vector store."""
        try:
            success = self.vector_store.clear_collection()
            
            return {
                "success": success,
                "message": "All documents cleared successfully" if success else "Failed to clear documents"
            }
            
        except Exception as e:
            logger.error(f"Failed to clear documents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the RAG system."""
        try:
            collection_info = self.vector_store.get_collection_info()
            embedding_info = self.embedding_service.get_model_info()
            
            return {
                "system_status": "healthy",
                "configuration": self.config.to_dict(),
                "vector_store": collection_info,
                "embedding_model": embedding_info,
                "supported_file_types": self.document_processor.get_supported_types()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {
                "system_status": "error",
                "error": str(e)
            }
    
    def export_knowledge_base(self, file_path: str) -> Dict[str, Any]:
        """Export the knowledge base to a file."""
        try:
            success = self.vector_store.export_collection(file_path)
            
            return {
                "success": success,
                "export_path": file_path,
                "message": "Knowledge base exported successfully" if success else "Failed to export knowledge base"
            }
            
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {e}")
            return {
                "success": False,
                "error": str(e),
                "export_path": file_path
            }
    
    def import_knowledge_base(self, file_path: str) -> Dict[str, Any]:
        """Import a knowledge base from a file."""
        try:
            success = self.vector_store.import_collection(file_path)
            
            return {
                "success": success,
                "import_path": file_path,
                "message": "Knowledge base imported successfully" if success else "Failed to import knowledge base"
            }
            
        except Exception as e:
            logger.error(f"Failed to import knowledge base: {e}")
            return {
                "success": False,
                "error": str(e),
                "import_path": file_path
            }
    
    async def query_async(self, question: str, **kwargs) -> Dict[str, Any]:
        """Async version of query method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, question, **kwargs)
    
    async def ingest_document_async(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Async version of ingest_document method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.ingest_document, file_path, **kwargs)
