#!/usr/bin/env python3
"""
RAG System Usage Examples

This script demonstrates how to use the RAG system for various tasks
including document ingestion, querying, and content generation.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import rag module
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag import RAGPipeline, RAGConfig


def example_basic_usage():
    """Example: Basic RAG system usage."""
    print("=== Basic RAG Usage Example ===")
    
    # Initialize RAG pipeline
    config = RAGConfig.from_env()
    pipeline = RAGPipeline(config)
    
    # Ingest some text
    text_content = """
    Artificial Intelligence (AI) is transforming the world as we know it. 
    Machine learning, a subset of AI, enables computers to learn and improve 
    from experience without being explicitly programmed. Deep learning, 
    using neural networks with multiple layers, has revolutionized fields 
    like computer vision and natural language processing.
    
    The applications of AI are vast: from autonomous vehicles and medical 
    diagnosis to recommendation systems and language translation. As AI 
    continues to evolve, it promises to bring both opportunities and 
    challenges to society.
    """
    
    # Ingest the text
    print("Ingesting text content...")
    result = pipeline.ingest_text(
        text=text_content,
        source_name="AI_overview",
        custom_metadata={"topic": "artificial_intelligence", "example": True}
    )
    
    if result["success"]:
        print(f"✓ Text ingested successfully: {result['documents_created']} chunks created")
    else:
        print(f"✗ Text ingestion failed: {result['error']}")
        return
    
    # Query the system
    print("\nQuerying the system...")
    question = "What is machine learning and how does it relate to AI?"
    
    answer_result = pipeline.query(
        question=question,
        response_type="educational",
        include_sources=True
    )
    
    if answer_result["success"]:
        print(f"Question: {question}")
        print(f"Answer: {answer_result['answer']}")
        print(f"Documents used: {answer_result['retrieved_documents']}")
    else:
        print(f"✗ Query failed: {answer_result['error']}")


def example_file_ingestion():
    """Example: File ingestion and processing."""
    print("\n=== File Ingestion Example ===")
    
    # Initialize RAG pipeline
    pipeline = RAGPipeline()
    
    # Create a sample document
    sample_doc = """
    # Python Programming Guide
    
    ## Introduction
    Python is a high-level, interpreted programming language known for its 
    simplicity and readability. It supports multiple programming paradigms 
    including procedural, object-oriented, and functional programming.
    
    ## Key Features
    - Easy to learn and use
    - Large standard library
    - Cross-platform compatibility
    - Strong community support
    - Extensive third-party packages
    
    ## Applications
    Python is widely used in:
    - Web development (Django, Flask)
    - Data science and analytics
    - Machine learning and AI
    - Automation and scripting
    - Scientific computing
    
    ## Getting Started
    To start programming in Python:
    1. Install Python from python.org
    2. Set up a development environment
    3. Learn basic syntax and concepts
    4. Practice with small projects
    5. Explore libraries and frameworks
    """
    
    # Save to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_doc)
        temp_file_path = f.name
    
    try:
        # Ingest the file
        print("Ingesting Python guide document...")
        result = pipeline.ingest_document(
            file_path=temp_file_path,
            chunking_strategy="markdown",
            custom_metadata={"language": "python", "type": "tutorial"}
        )
        
        if result["success"]:
            print(f"✓ Document ingested: {result['documents_created']} chunks")
            
            # Query about Python
            questions = [
                "What are the key features of Python?",
                "How can I get started with Python programming?",
                "What are the main applications of Python?"
            ]
            
            for question in questions:
                print(f"\nQ: {question}")
                answer = pipeline.query(question, response_type="concise")
                if answer["success"]:
                    print(f"A: {answer['answer'][:200]}...")
                else:
                    print(f"Failed to answer: {answer['error']}")
        
        else:
            print(f"✗ Document ingestion failed: {result['error']}")
    
    finally:
        # Clean up
        os.unlink(temp_file_path)


def example_quiz_generation():
    """Example: Quiz generation from ingested content."""
    print("\n=== Quiz Generation Example ===")
    
    pipeline = RAGPipeline()
    
    # Ingest educational content
    content = """
    Data Science Fundamentals
    
    Data science is an interdisciplinary field that combines statistics, 
    computer science, and domain expertise to extract insights from data.
    
    The typical data science workflow includes:
    1. Problem Definition: Clearly defining the business problem
    2. Data Collection: Gathering relevant data from various sources
    3. Data Cleaning: Preprocessing and cleaning the raw data
    4. Exploratory Data Analysis (EDA): Understanding data patterns
    5. Feature Engineering: Creating meaningful features for modeling
    6. Model Building: Developing predictive or descriptive models
    7. Model Evaluation: Assessing model performance and validity
    8. Deployment: Implementing the model in production
    9. Monitoring: Tracking model performance over time
    
    Key skills for data scientists include:
    - Programming (Python, R, SQL)
    - Statistics and mathematics
    - Machine learning algorithms
    - Data visualization
    - Business acumen
    - Communication skills
    """
    
    # Ingest content
    print("Ingesting data science content...")
    ingest_result = pipeline.ingest_text(
        text=content,
        source_name="data_science_fundamentals",
        custom_metadata={"subject": "data_science", "level": "beginner"}
    )
    
    if ingest_result["success"]:
        print(f"✓ Content ingested: {ingest_result['documents_created']} chunks")
        
        # Generate quiz
        print("\nGenerating quiz questions...")
        quiz_result = pipeline.generate_quiz(
            topic="data science workflow and skills",
            num_questions=3,
            difficulty="medium",
            question_types=["multiple-choice", "true-false"]
        )
        
        if quiz_result["success"]:
            print("✓ Quiz generated successfully!")
            try:
                import json
                quiz_data = json.loads(quiz_result["quiz"])
                
                print("\nGenerated Quiz Questions:")
                for i, question in enumerate(quiz_data.get("questions", []), 1):
                    print(f"\n{i}. {question.get('question')}")
                    if question.get('type') == 'multiple-choice':
                        for j, option in enumerate(question.get('options', [])):
                            print(f"   {chr(65+j)}. {option}")
                    print(f"   Answer: {question.get('correct_answer')}")
                    
            except json.JSONDecodeError:
                print("Quiz generated but could not parse JSON format")
        else:
            print(f"✗ Quiz generation failed: {quiz_result['error']}")
    else:
        print(f"✗ Content ingestion failed: {ingest_result['error']}")


def example_summary_generation():
    """Example: Summary generation from multiple documents."""
    print("\n=== Summary Generation Example ===")
    
    pipeline = RAGPipeline()
    
    # Ingest multiple related documents
    documents = [
        {
            "name": "machine_learning_basics",
            "content": """
            Machine Learning is a subset of artificial intelligence that enables 
            computers to learn and make decisions from data without being explicitly 
            programmed. There are three main types of machine learning:
            
            1. Supervised Learning: Uses labeled data to train models
            2. Unsupervised Learning: Finds patterns in unlabeled data
            3. Reinforcement Learning: Learns through interaction with environment
            
            Common algorithms include linear regression, decision trees, neural 
            networks, and support vector machines.
            """
        },
        {
            "name": "deep_learning_intro",
            "content": """
            Deep Learning is a specialized area of machine learning that uses 
            neural networks with multiple layers (deep neural networks). These 
            networks can automatically learn hierarchical representations of data.
            
            Key architectures include:
            - Feedforward Neural Networks
            - Convolutional Neural Networks (CNNs) for image processing
            - Recurrent Neural Networks (RNNs) for sequential data
            - Transformers for natural language processing
            
            Deep learning has achieved remarkable success in computer vision, 
            natural language processing, and game playing.
            """
        },
        {
            "name": "nlp_overview",
            "content": """
            Natural Language Processing (NLP) is a branch of AI that focuses on 
            the interaction between computers and human language. It combines 
            computational linguistics with machine learning and deep learning.
            
            Key NLP tasks include:
            - Text classification and sentiment analysis
            - Named entity recognition
            - Machine translation
            - Question answering
            - Text summarization
            - Language generation
            
            Modern NLP relies heavily on transformer models like BERT and GPT.
            """
        }
    ]
    
    # Ingest all documents
    print("Ingesting AI/ML documents...")
    for doc in documents:
        result = pipeline.ingest_text(
            text=doc["content"],
            source_name=doc["name"],
            custom_metadata={"domain": "AI_ML", "type": "educational"}
        )
        
        if result["success"]:
            print(f"✓ Ingested {doc['name']}: {result['documents_created']} chunks")
        else:
            print(f"✗ Failed to ingest {doc['name']}: {result['error']}")
    
    # Generate summary
    print("\nGenerating comprehensive summary...")
    summary_result = pipeline.summarize_documents(
        query="machine learning, deep learning, and natural language processing",
        summary_type="comprehensive",
        max_length=400
    )
    
    if summary_result["success"]:
        print("✓ Summary generated successfully!")
        print(f"\nSummary:\n{summary_result['summary']}")
        print(f"\nDocuments used: {len(summary_result['context_used'])}")
    else:
        print(f"✗ Summary generation failed: {summary_result['error']}")


def example_hybrid_search():
    """Example: Hybrid search with metadata filtering."""
    print("\n=== Hybrid Search Example ===")
    
    pipeline = RAGPipeline()
    
    # Ingest documents with different metadata
    docs_with_metadata = [
        {
            "text": "Python is excellent for beginners due to its simple syntax.",
            "metadata": {"language": "python", "level": "beginner", "topic": "syntax"}
        },
        {
            "text": "Advanced Python features include decorators, generators, and metaclasses.",
            "metadata": {"language": "python", "level": "advanced", "topic": "features"}
        },
        {
            "text": "JavaScript is the language of the web, used for both frontend and backend.",
            "metadata": {"language": "javascript", "level": "intermediate", "topic": "web"}
        },
        {
            "text": "React is a popular JavaScript library for building user interfaces.",
            "metadata": {"language": "javascript", "level": "intermediate", "topic": "frontend"}
        }
    ]
    
    # Ingest documents
    print("Ingesting programming documents with metadata...")
    for i, doc in enumerate(docs_with_metadata):
        result = pipeline.ingest_text(
            text=doc["text"],
            source_name=f"programming_doc_{i+1}",
            custom_metadata=doc["metadata"]
        )
        
        if result["success"]:
            print(f"✓ Ingested document {i+1}")
    
    # Perform filtered search
    print("\nSearching for Python beginner content...")
    results = pipeline.retriever.retrieve(
        query="Python programming for beginners",
        filter_metadata={"language": "python", "level": "beginner"}
    )
    
    print(f"Found {len(results)} Python beginner documents:")
    for result in results:
        print(f"- {result.content} (similarity: {result.similarity:.3f})")
    
    # Search with different filter
    print("\nSearching for JavaScript content...")
    js_results = pipeline.retriever.retrieve(
        query="web development",
        filter_metadata={"language": "javascript"}
    )
    
    print(f"Found {len(js_results)} JavaScript documents:")
    for result in js_results:
        print(f"- {result.content} (similarity: {result.similarity:.3f})")


async def example_async_operations():
    """Example: Async operations for better performance."""
    print("\n=== Async Operations Example ===")
    
    pipeline = RAGPipeline()
    
    # Async text ingestion
    print("Running async text ingestion...")
    text = "Async programming allows for concurrent execution of tasks."
    
    ingest_task = pipeline.ingest_text(
        text=text,
        source_name="async_example"
    )
    
    # Simulate multiple async queries
    questions = [
        "What is async programming?",
        "How does concurrent execution work?",
        "What are the benefits of async operations?"
    ]
    
    print("Running multiple async queries...")
    query_tasks = []
    for question in questions:
        # Note: The async methods need to be implemented in the pipeline
        # This is a conceptual example
        print(f"Would query: {question}")
    
    print("✓ Async operations completed (conceptual example)")


def example_system_management():
    """Example: System management and maintenance."""
    print("\n=== System Management Example ===")
    
    pipeline = RAGPipeline()
    
    # Get system information
    print("Getting system information...")
    system_info = pipeline.get_system_info()
    
    if system_info.get("system_status") == "healthy":
        print("✓ System is healthy")
        print(f"Documents in store: {system_info.get('vector_store', {}).get('document_count', 0)}")
        print(f"Embedding model: {system_info.get('embedding_model', {}).get('model_name', 'unknown')}")
    else:
        print("⚠ System status unknown")
    
    # List documents
    print("\nListing documents...")
    doc_list = pipeline.list_documents(limit=5)
    
    if doc_list["success"]:
        print(f"Total documents: {doc_list['count']}")
        for doc in doc_list["documents"][:3]:  # Show first 3
            print(f"- {doc['id']}: {doc['content'][:50]}...")
    
    # Get similar documents (if any exist)
    if doc_list["documents"]:
        sample_doc_id = doc_list["documents"][0]["id"]
        print(f"\nFinding documents similar to: {sample_doc_id}")
        
        similar_docs = pipeline.get_similar_documents(sample_doc_id, top_k=2)
        if similar_docs["success"]:
            print(f"Found {len(similar_docs['similar_documents'])} similar documents")


def main():
    """Run all examples."""
    print("RAG System Usage Examples")
    print("=" * 50)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("File Ingestion", example_file_ingestion),
        ("Quiz Generation", example_quiz_generation),
        ("Summary Generation", example_summary_generation),
        ("Hybrid Search", example_hybrid_search),
        ("System Management", example_system_management),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ {name} example failed: {e}")
        
        print("\n" + "-" * 50)
    
    print("\nAll examples completed!")
    print("\nNote: Make sure to set your GEMINI_API_KEY in the .env file")
    print("for the generation examples to work properly.")


if __name__ == "__main__":
    main()
