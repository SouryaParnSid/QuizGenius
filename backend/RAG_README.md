# RAG System Documentation

A comprehensive Retrieval-Augmented Generation (RAG) system built with LangChain, ChromaDB, Sentence Transformers, and Google Gemini AI.

## 🚀 Features

- **Document Processing**: Support for PDF, DOCX, TXT, and Markdown files
- **Advanced Chunking**: Multiple text splitting strategies for optimal retrieval
- **Vector Storage**: ChromaDB for efficient similarity search
- **Semantic Search**: Sentence Transformers for high-quality embeddings
- **AI Generation**: Google Gemini AI for responses, summaries, and quiz generation
- **RESTful API**: FastAPI endpoints for easy integration
- **Async Support**: Asynchronous operations for better performance
- **Comprehensive Testing**: Full test suite and examples

## 📁 Project Structure

```
backend/
├── rag/                          # Core RAG system package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── embeddings.py            # Sentence Transformers integration
│   ├── vector_store.py          # ChromaDB vector storage
│   ├── document_processor.py    # Document ingestion and chunking
│   ├── retriever.py             # Document retrieval logic
│   ├── generator.py             # Gemini AI response generation
│   └── rag_pipeline.py          # Main pipeline orchestration
├── examples/                     # Usage examples
│   └── example_usage.py         # Comprehensive examples
├── rag_api.py                   # FastAPI REST API
├── rag_setup.py                 # Setup and installation script
├── test_rag.py                  # Comprehensive test suite
├── requirements-rag.txt         # Python dependencies
├── env.example                  # Environment configuration template
└── RAG_README.md               # This documentation
```

## 🛠️ Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements-rag.txt
```

### 2. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your API keys
nano .env
```

Required environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key

### 3. Run Setup Script

```bash
python rag_setup.py --install-deps
```

This will:
- Install dependencies
- Create necessary directories
- Validate configuration
- Test basic functionality

## 🚀 Quick Start

### Using the RAG Pipeline Directly

```python
from rag import RAGPipeline

# Initialize the pipeline
pipeline = RAGPipeline()

# Ingest a document
result = pipeline.ingest_document("path/to/document.pdf")

# Query the system
answer = pipeline.query("What is the main topic of the document?")
print(answer["answer"])

# Generate a quiz
quiz = pipeline.generate_quiz("document content", num_questions=5)

# Generate a summary
summary = pipeline.summarize_documents("key topics")
```

### Using the REST API

```bash
# Start the API server
python rag_api.py
```

The API will be available at `http://localhost:8001` with interactive docs at `http://localhost:8001/docs`.

#### API Examples

```bash
# Ingest a document
curl -X POST "http://localhost:8000/ingest/file" \
  -F "file=@document.pdf" \
  -F "chunking_strategy=recursive"

# Query the system
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'

# Generate a quiz
curl -X POST "http://localhost:8000/generate/quiz" \
  -H "Content-Type: application/json" \
  -d '{"topic": "artificial intelligence", "num_questions": 5}'
```

## 📖 Core Components

### 1. Document Processor

Handles multiple file types and text chunking strategies:

```python
from rag.document_processor import DocumentProcessor
from rag.config import RAGConfig

processor = DocumentProcessor(RAGConfig.from_env())

# Process a file
documents = processor.process_file(
    "document.pdf", 
    chunking_strategy="recursive"
)

# Process text directly
documents = processor.process_text(
    "Your text content here",
    source_name="text_input"
)
```

**Supported File Types:**
- PDF (`.pdf`)
- Word Documents (`.docx`)
- Text Files (`.txt`)
- Markdown (`.md`, `.markdown`)

**Chunking Strategies:**
- `recursive`: Smart text splitting with multiple separators
- `token`: Token-based chunking
- `markdown`: Markdown-aware splitting
- `paragraph`: Paragraph-based chunks

### 2. Vector Store

ChromaDB-based vector storage with similarity search:

```python
from rag.vector_store import VectorStoreService, Document
from rag.embeddings import EmbeddingService

embedding_service = EmbeddingService(config)
vector_store = VectorStoreService(config, embedding_service)

# Add documents
documents = [Document(content="Text content", metadata={"source": "file.txt"})]
vector_store.add_documents(documents)

# Search for similar documents
results = vector_store.search("query text", n_results=5)
```

### 3. Retrieval System

Advanced retrieval with multiple search strategies:

```python
from rag.retriever import RetrieverService

retriever = RetrieverService(config, vector_store, embedding_service)

# Basic semantic search
results = retriever.retrieve("machine learning concepts")

# Hybrid search (semantic + keyword)
results = retriever.retrieve_hybrid(
    query="AI applications",
    keywords=["artificial intelligence", "machine learning"],
    semantic_weight=0.7,
    keyword_weight=0.3
)

# Filtered search
results = retriever.retrieve(
    query="Python programming",
    filter_metadata={"language": "python", "level": "beginner"}
)
```

### 4. Generation System

Google Gemini AI integration for various generation tasks:

```python
from rag.generator import GeneratorService

generator = GeneratorService(config)

# Generate response with context
response = generator.generate_response(
    query="Explain machine learning",
    context_results=retrieval_results,
    response_type="educational"
)

# Generate quiz questions
quiz = generator.generate_quiz_questions(
    context_results=retrieval_results,
    num_questions=5,
    difficulty="medium"
)

# Generate summary
summary = generator.generate_summary(
    context_results=retrieval_results,
    summary_type="comprehensive"
)
```

## 🔧 Configuration

The system is highly configurable through environment variables:

```python
from rag.config import RAGConfig

# Load from environment
config = RAGConfig.from_env()

# Or create manually
config = RAGConfig(
    gemini_api_key="your-key",
    embedding_model="all-MiniLM-L6-v2",
    chunk_size=1000,
    chunk_overlap=200,
    top_k_retrieval=5,
    similarity_threshold=0.7
)
```

### Key Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `EMBEDDING_MODEL` | Sentence Transformer model | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Text chunk size | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `TOP_K_RETRIEVAL` | Default retrieval count | 5 |
| `SIMILARITY_THRESHOLD` | Minimum similarity | 0.7 |
| `TEMPERATURE` | Generation temperature | 0.7 |

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Full test suite
python test_rag.py

# Quick tests only
python test_rag.py --quick
```

The test suite covers:
- Document ingestion (file and text)
- Vector storage and retrieval
- Response generation
- Quiz generation
- Summary generation
- System management

## 📊 API Endpoints

### Document Management

- `POST /ingest/file` - Upload and ingest a file
- `POST /ingest/text` - Ingest text content
- `POST /ingest/batch` - Batch file ingestion
- `GET /documents` - List stored documents
- `GET /documents/{id}` - Get specific document
- `DELETE /documents/{id}` - Delete document

### Querying

- `POST /query` - Query the RAG system
- `GET /search` - Search documents without generation
- `GET /documents/{id}/similar` - Find similar documents

### Generation

- `POST /generate/quiz` - Generate quiz questions
- `POST /generate/summary` - Generate document summaries

### System Management

- `GET /health` - Health check
- `GET /system/info` - System information
- `GET /config` - Current configuration
- `POST /system/export` - Export knowledge base
- `POST /system/import` - Import knowledge base

## 💡 Usage Examples

### 1. Educational Content Processing

```python
# Ingest course materials
pipeline.ingest_document("lecture_notes.pdf")
pipeline.ingest_document("textbook_chapter.pdf")

# Generate study materials
quiz = pipeline.generate_quiz("machine learning concepts", num_questions=10)
summary = pipeline.summarize_documents("key concepts from course")
```

### 2. Document Analysis

```python
# Ingest multiple reports
for report in report_files:
    pipeline.ingest_document(report)

# Analyze trends
analysis = pipeline.query(
    "What are the main trends mentioned across all reports?",
    response_type="analytical"
)
```

### 3. Knowledge Base System

```python
# Build knowledge base
for doc in knowledge_docs:
    pipeline.ingest_document(doc, custom_metadata={"category": doc.category})

# Filtered querying
answer = pipeline.query(
    "How to implement authentication?",
    filter_metadata={"category": "security"}
)
```

## 🔍 Advanced Features

### Hybrid Search

Combine semantic and keyword search for better results:

```python
results = retriever.retrieve_hybrid(
    query="machine learning algorithms",
    keywords=["supervised", "unsupervised", "neural networks"],
    semantic_weight=0.6,
    keyword_weight=0.4
)
```

### Metadata Filtering

Filter search results by metadata:

```python
# Only search Python-related content
results = retriever.retrieve(
    query="programming concepts",
    filter_metadata={"language": "python", "difficulty": "beginner"}
)
```

### Custom Response Types

Different response styles for different use cases:

```python
# Educational response
education = pipeline.query(question, response_type="educational")

# Concise summary
summary = pipeline.query(question, response_type="concise")

# Analytical deep-dive
analysis = pipeline.query(question, response_type="analytical")
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Error: Gemini API key not configured
   Solution: Set GEMINI_API_KEY in .env file
   ```

2. **ChromaDB Permission Error**
   ```
   Error: Cannot write to ChromaDB directory
   Solution: Check directory permissions for ./data/chromadb
   ```

3. **Out of Memory**
   ```
   Error: CUDA out of memory / RAM exhausted
   Solution: Reduce batch_size or chunk_size in configuration
   ```

4. **Slow Performance**
   ```
   Issue: Slow embedding generation
   Solution: Enable caching with ENABLE_CACHING=True
   ```

### Performance Optimization

1. **Enable Embedding Caching**
   ```python
   config.enable_caching = True
   ```

2. **Adjust Batch Size**
   ```python
   config.batch_size = 16  # Reduce for less memory usage
   ```

3. **Optimize Chunk Size**
   ```python
   config.chunk_size = 500    # Smaller chunks for better precision
   config.chunk_overlap = 50  # Less overlap for speed
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite to identify issues
3. Review the configuration settings
4. Check API key and environment setup

## 🔮 Future Enhancements

- [ ] Support for more file types (PowerPoint, Excel)
- [ ] Multi-modal support (images, audio)
- [ ] Advanced retrieval strategies (BM25, hybrid ranking)
- [ ] Streaming responses for long generations
- [ ] Vector database alternatives (Pinecone, Weaviate)
- [ ] Fine-tuning capabilities for embeddings
- [ ] Advanced analytics and monitoring
