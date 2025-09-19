"""
RAG API

FastAPI application providing RESTful endpoints for the RAG system.
Handles document ingestion, querying, and management operations.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import tempfile
import os
from datetime import datetime

from rag import RAGPipeline, RAGConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API using LangChain, ChromaDB, and Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance
rag_pipeline: Optional[RAGPipeline] = None


# Pydantic models for request/response
class QueryRequest(BaseModel):
    """Request model for querying."""
    question: str = Field(..., description="The question to ask")
    top_k: Optional[int] = Field(5, description="Number of documents to retrieve")
    similarity_threshold: Optional[float] = Field(0.7, description="Minimum similarity threshold")
    response_type: str = Field("comprehensive", description="Type of response")
    include_sources: bool = Field(True, description="Include source citations")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class TextIngestionRequest(BaseModel):
    """Request model for text ingestion."""
    text: str = Field(..., description="Text content to ingest")
    source_name: str = Field("text_input", description="Name for the text source")
    chunking_strategy: str = Field("recursive", description="Text chunking strategy")
    custom_metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")


class QuizRequest(BaseModel):
    """Request model for quiz generation."""
    topic: str = Field(..., description="Topic for quiz questions")
    num_questions: int = Field(5, description="Number of questions to generate")
    difficulty: str = Field("medium", description="Difficulty level")
    question_types: Optional[List[str]] = Field(["multiple-choice", "true-false"], description="Types of questions")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class SummaryRequest(BaseModel):
    """Request model for summary generation."""
    query: str = Field(..., description="Topic or query to summarize")
    summary_type: str = Field("comprehensive", description="Type of summary")
    max_length: int = Field(500, description="Maximum length in words")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    embedding_model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    top_k_retrieval: Optional[int] = None
    similarity_threshold: Optional[float] = None
    temperature: Optional[float] = None


# Dependency to get RAG pipeline
def get_rag_pipeline() -> RAGPipeline:
    """Get the RAG pipeline instance."""
    global rag_pipeline
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    return rag_pipeline


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    global rag_pipeline
    try:
        logger.info("Initializing RAG system...")
        config = RAGConfig.from_env()
        rag_pipeline = RAGPipeline(config)
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        pipeline = get_rag_pipeline()
        system_info = pipeline.get_system_info()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system_info": system_info
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# Document ingestion endpoints
@app.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    chunking_strategy: str = Form("recursive"),
    custom_metadata: Optional[str] = Form(None),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Ingest a file into the RAG system."""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in pipeline.config.supported_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported types: {pipeline.config.supported_file_types}"
            )
        
        # Parse custom metadata
        metadata = None
        if custom_metadata:
            try:
                import json
                metadata = json.loads(custom_metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in custom_metadata")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Ingest the file
            result = pipeline.ingest_document(
                file_path=tmp_file_path,
                chunking_strategy=chunking_strategy,
                custom_metadata=metadata
            )
            
            # Add original filename to result
            result["original_filename"] = file.filename
            
            return result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {str(e)}")


@app.post("/ingest/text")
async def ingest_text(
    request: TextIngestionRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Ingest text content into the RAG system."""
    try:
        result = pipeline.ingest_text(
            text=request.text,
            source_name=request.source_name,
            chunking_strategy=request.chunking_strategy,
            custom_metadata=request.custom_metadata
        )
        return result
        
    except Exception as e:
        logger.error(f"Text ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Text ingestion failed: {str(e)}")


@app.post("/ingest/batch")
async def ingest_batch(
    files: List[UploadFile] = File(...),
    chunking_strategy: str = Form("recursive"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Ingest multiple files in batch."""
    try:
        temp_files = []
        
        # Save all uploaded files temporarily
        for file in files:
            if not file.filename:
                continue
                
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in pipeline.config.supported_file_types:
                continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)
        
        try:
            # Ingest all files
            result = pipeline.ingest_batch(
                file_paths=temp_files,
                chunking_strategy=chunking_strategy
            )
            
            return result
            
        finally:
            # Clean up temporary files
            for tmp_file_path in temp_files:
                try:
                    os.unlink(tmp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file: {e}")
        
    except Exception as e:
        logger.error(f"Batch ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {str(e)}")


# Query endpoints
@app.post("/query")
async def query_rag(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Query the RAG system for an answer."""
    try:
        result = pipeline.query(
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            filter_metadata=request.filter_metadata,
            response_type=request.response_type,
            include_sources=request.include_sources
        )
        return result
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/search")
async def search_documents(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results"),
    similarity_threshold: float = Query(0.7, description="Minimum similarity"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Search for documents without generating a response."""
    try:
        retrieval_results = pipeline.retriever.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "query": query,
            "results": [result.to_dict() for result in retrieval_results],
            "count": len(retrieval_results)
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Generation endpoints
@app.post("/generate/quiz")
async def generate_quiz(
    request: QuizRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Generate quiz questions based on stored documents."""
    try:
        result = pipeline.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            question_types=request.question_types,
            filter_metadata=request.filter_metadata
        )
        return result
        
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@app.post("/generate/summary")
async def generate_summary(
    request: SummaryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Generate a summary of relevant documents."""
    try:
        result = pipeline.summarize_documents(
            query=request.query,
            summary_type=request.summary_type,
            max_length=request.max_length,
            filter_metadata=request.filter_metadata
        )
        return result
        
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


# Document management endpoints
@app.get("/documents")
async def list_documents(
    limit: Optional[int] = Query(None, description="Maximum number of documents to return"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """List documents in the vector store."""
    try:
        result = pipeline.list_documents(limit=limit)
        return result
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Get a specific document by ID."""
    try:
        document = pipeline.vector_store.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document": document
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@app.get("/documents/{doc_id}/similar")
async def get_similar_documents(
    doc_id: str,
    top_k: int = Query(5, description="Number of similar documents to return"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Find documents similar to a given document."""
    try:
        result = pipeline.get_similar_documents(doc_id=doc_id, top_k=top_k)
        return result
        
    except Exception as e:
        logger.error(f"Similar documents error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar documents: {str(e)}")


@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Delete a document from the vector store."""
    try:
        result = pipeline.delete_document(doc_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.delete("/documents")
async def clear_all_documents(
    confirm: bool = Query(False, description="Confirmation required to clear all documents"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Clear all documents from the vector store."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Please set confirm=true to clear all documents"
        )
    
    try:
        result = pipeline.clear_all_documents()
        return result
        
    except Exception as e:
        logger.error(f"Clear documents error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear documents: {str(e)}")


# System management endpoints
@app.get("/system/info")
async def get_system_info(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """Get information about the RAG system."""
    try:
        result = pipeline.get_system_info()
        return result
        
    except Exception as e:
        logger.error(f"System info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")


@app.post("/system/export")
async def export_knowledge_base(
    file_path: str = Query(..., description="Path to export the knowledge base"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Export the knowledge base to a file."""
    try:
        result = pipeline.export_knowledge_base(file_path)
        return result
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/system/import")
async def import_knowledge_base(
    file_path: str = Query(..., description="Path to import the knowledge base from"),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Import a knowledge base from a file."""
    try:
        result = pipeline.import_knowledge_base(file_path)
        return result
        
    except Exception as e:
        logger.error(f"Import error: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


# Configuration endpoint
@app.get("/config")
async def get_config(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """Get current configuration."""
    return pipeline.config.to_dict()


if __name__ == "__main__":
    uvicorn.run(
        "rag_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
