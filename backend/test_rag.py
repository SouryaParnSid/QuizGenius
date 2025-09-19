#!/usr/bin/env python3
"""
RAG System Test Script

Comprehensive testing script for the RAG system components.
Tests document ingestion, retrieval, and generation functionality.
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
import asyncio
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag import RAGPipeline, RAGConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGTester:
    """Comprehensive RAG system tester."""
    
    def __init__(self):
        """Initialize the tester."""
        self.config = None
        self.pipeline = None
        self.test_results = {}
        
    def setup(self):
        """Setup the RAG system for testing."""
        try:
            logger.info("Setting up RAG system for testing...")
            
            # Load configuration
            self.config = RAGConfig.from_env()
            
            # Initialize pipeline
            self.pipeline = RAGPipeline(self.config)
            
            logger.info("RAG system setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def create_test_documents(self):
        """Create test documents for ingestion."""
        test_docs = []
        
        # Create test text files
        texts = [
            {
                "name": "artificial_intelligence.txt",
                "content": """
                Artificial Intelligence (AI) is a branch of computer science that aims to create 
                intelligent machines that work and react like humans. Some of the activities 
                computers with artificial intelligence are designed for include speech recognition, 
                learning, planning, and problem solving.
                
                Machine learning is a subset of AI that provides systems the ability to automatically 
                learn and improve from experience without being explicitly programmed. Deep learning 
                is a subset of machine learning that uses neural networks with many layers.
                
                Natural Language Processing (NLP) is a branch of AI that helps computers understand, 
                interpret and manipulate human language. It bridges the gap between human communication 
                and computer understanding.
                """
            },
            {
                "name": "python_programming.txt", 
                "content": """
                Python is a high-level, interpreted programming language with dynamic semantics. 
                Its high-level built-in data structures, combined with dynamic typing and dynamic 
                binding, make it very attractive for Rapid Application Development.
                
                Python's simple, easy-to-learn syntax emphasizes readability and therefore reduces 
                the cost of program maintenance. Python supports modules and packages, which 
                encourages program modularity and code reuse.
                
                Key features of Python include:
                - Easy to learn and use
                - Interpreted language
                - Object-oriented programming support
                - Large standard library
                - Cross-platform compatibility
                """
            },
            {
                "name": "data_science.txt",
                "content": """
                Data Science is an interdisciplinary field that uses scientific methods, processes, 
                algorithms and systems to extract knowledge and insights from structured and 
                unstructured data.
                
                The data science process typically involves:
                1. Data collection and acquisition
                2. Data cleaning and preprocessing
                3. Exploratory data analysis
                4. Model building and machine learning
                5. Model evaluation and validation
                6. Deployment and monitoring
                
                Common tools used in data science include Python, R, SQL, Jupyter notebooks, 
                pandas, numpy, scikit-learn, and various visualization libraries.
                """
            }
        ]
        
        # Create temporary files
        for doc in texts:
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.txt', 
                delete=False,
                encoding='utf-8'
            )
            temp_file.write(doc["content"])
            temp_file.close()
            
            test_docs.append({
                "name": doc["name"],
                "path": temp_file.name,
                "content": doc["content"]
            })
        
        return test_docs
    
    def test_document_ingestion(self, test_docs):
        """Test document ingestion functionality."""
        logger.info("Testing document ingestion...")
        
        try:
            results = []
            
            for doc in test_docs:
                result = self.pipeline.ingest_document(
                    file_path=doc["path"],
                    chunking_strategy="recursive",
                    custom_metadata={"test_document": True, "original_name": doc["name"]}
                )
                
                results.append({
                    "document": doc["name"],
                    "success": result["success"],
                    "chunks_created": result.get("documents_created", 0),
                    "error": result.get("error")
                })
                
                if result["success"]:
                    logger.info(f"✓ Ingested {doc['name']}: {result['documents_created']} chunks")
                else:
                    logger.error(f"✗ Failed to ingest {doc['name']}: {result.get('error')}")
            
            self.test_results["document_ingestion"] = {
                "total_documents": len(test_docs),
                "successful": sum(1 for r in results if r["success"]),
                "failed": sum(1 for r in results if not r["success"]),
                "details": results
            }
            
            return len([r for r in results if r["success"]]) > 0
            
        except Exception as e:
            logger.error(f"Document ingestion test failed: {e}")
            self.test_results["document_ingestion"] = {"error": str(e)}
            return False
    
    def test_text_ingestion(self):
        """Test text ingestion functionality."""
        logger.info("Testing text ingestion...")
        
        try:
            test_text = """
            Vector databases are specialized databases designed to store and query vector embeddings. 
            They are essential for similarity search, recommendation systems, and retrieval-augmented 
            generation (RAG) applications. Popular vector databases include ChromaDB, Pinecone, 
            Weaviate, and Qdrant.
            """
            
            result = self.pipeline.ingest_text(
                text=test_text,
                source_name="vector_databases_info",
                custom_metadata={"test_text": True, "topic": "vector_databases"}
            )
            
            self.test_results["text_ingestion"] = {
                "success": result["success"],
                "chunks_created": result.get("documents_created", 0),
                "error": result.get("error")
            }
            
            if result["success"]:
                logger.info(f"✓ Text ingestion successful: {result['documents_created']} chunks")
                return True
            else:
                logger.error(f"✗ Text ingestion failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Text ingestion test failed: {e}")
            self.test_results["text_ingestion"] = {"error": str(e)}
            return False
    
    def test_retrieval(self):
        """Test document retrieval functionality."""
        logger.info("Testing document retrieval...")
        
        test_queries = [
            "What is artificial intelligence?",
            "Python programming features",
            "Data science process steps",
            "Machine learning and deep learning",
            "Vector databases"
        ]
        
        try:
            results = []
            
            for query in test_queries:
                retrieval_results = self.pipeline.retriever.retrieve(
                    query=query,
                    top_k=3,
                    similarity_threshold=0.5
                )
                
                result = {
                    "query": query,
                    "documents_found": len(retrieval_results),
                    "avg_similarity": sum(r.similarity for r in retrieval_results) / len(retrieval_results) if retrieval_results else 0,
                    "top_similarity": max(r.similarity for r in retrieval_results) if retrieval_results else 0
                }
                
                results.append(result)
                logger.info(f"Query: '{query}' -> {len(retrieval_results)} documents (top similarity: {result['top_similarity']:.3f})")
            
            self.test_results["retrieval"] = {
                "total_queries": len(test_queries),
                "successful_queries": sum(1 for r in results if r["documents_found"] > 0),
                "avg_documents_per_query": sum(r["documents_found"] for r in results) / len(results),
                "details": results
            }
            
            return sum(r["documents_found"] for r in results) > 0
            
        except Exception as e:
            logger.error(f"Retrieval test failed: {e}")
            self.test_results["retrieval"] = {"error": str(e)}
            return False
    
    def test_generation(self):
        """Test response generation functionality."""
        logger.info("Testing response generation...")
        
        test_queries = [
            {
                "question": "What is artificial intelligence and how does it relate to machine learning?",
                "response_type": "comprehensive"
            },
            {
                "question": "List the main features of Python programming language",
                "response_type": "concise"
            },
            {
                "question": "Explain the data science process",
                "response_type": "educational"
            }
        ]
        
        try:
            results = []
            
            for test_query in test_queries:
                result = self.pipeline.query(
                    question=test_query["question"],
                    response_type=test_query["response_type"],
                    top_k=3
                )
                
                query_result = {
                    "question": test_query["question"],
                    "success": result["success"],
                    "response_length": len(result.get("answer", "")) if result["success"] else 0,
                    "documents_used": result.get("retrieved_documents", 0),
                    "error": result.get("error")
                }
                
                results.append(query_result)
                
                if result["success"]:
                    logger.info(f"✓ Generated response for: '{test_query['question'][:50]}...' ({query_result['response_length']} chars)")
                else:
                    logger.error(f"✗ Failed to generate response: {result.get('error')}")
            
            self.test_results["generation"] = {
                "total_queries": len(test_queries),
                "successful": sum(1 for r in results if r["success"]),
                "failed": sum(1 for r in results if not r["success"]),
                "avg_response_length": sum(r["response_length"] for r in results if r["success"]) / max(1, sum(1 for r in results if r["success"])),
                "details": results
            }
            
            return sum(1 for r in results if r["success"]) > 0
            
        except Exception as e:
            logger.error(f"Generation test failed: {e}")
            self.test_results["generation"] = {"error": str(e)}
            return False
    
    def test_quiz_generation(self):
        """Test quiz generation functionality."""
        logger.info("Testing quiz generation...")
        
        try:
            result = self.pipeline.generate_quiz(
                topic="artificial intelligence and machine learning",
                num_questions=3,
                difficulty="medium"
            )
            
            self.test_results["quiz_generation"] = {
                "success": result["success"],
                "topic": result.get("topic"),
                "error": result.get("error")
            }
            
            if result["success"]:
                logger.info("✓ Quiz generation successful")
                # Try to parse the quiz JSON
                try:
                    quiz_data = json.loads(result["quiz"])
                    self.test_results["quiz_generation"]["questions_generated"] = len(quiz_data.get("questions", []))
                except:
                    self.test_results["quiz_generation"]["questions_generated"] = "unknown"
                return True
            else:
                logger.error(f"✗ Quiz generation failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Quiz generation test failed: {e}")
            self.test_results["quiz_generation"] = {"error": str(e)}
            return False
    
    def test_summary_generation(self):
        """Test summary generation functionality."""
        logger.info("Testing summary generation...")
        
        try:
            result = self.pipeline.summarize_documents(
                query="artificial intelligence, machine learning, and programming",
                summary_type="comprehensive",
                max_length=300
            )
            
            self.test_results["summary_generation"] = {
                "success": result["success"],
                "summary_length": len(result.get("summary", "")) if result["success"] else 0,
                "error": result.get("error")
            }
            
            if result["success"]:
                logger.info(f"✓ Summary generation successful ({self.test_results['summary_generation']['summary_length']} chars)")
                return True
            else:
                logger.error(f"✗ Summary generation failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Summary generation test failed: {e}")
            self.test_results["summary_generation"] = {"error": str(e)}
            return False
    
    def test_system_management(self):
        """Test system management functionality."""
        logger.info("Testing system management...")
        
        try:
            # Test system info
            system_info = self.pipeline.get_system_info()
            
            # Test document listing
            doc_list = self.pipeline.list_documents()
            
            self.test_results["system_management"] = {
                "system_info_available": "system_status" in system_info,
                "document_count": doc_list.get("count", 0),
                "collection_info": system_info.get("vector_store", {})
            }
            
            logger.info(f"✓ System management test successful ({doc_list.get('count', 0)} documents in store)")
            return True
            
        except Exception as e:
            logger.error(f"System management test failed: {e}")
            self.test_results["system_management"] = {"error": str(e)}
            return False
    
    def cleanup_test_files(self, test_docs):
        """Clean up temporary test files."""
        logger.info("Cleaning up test files...")
        
        for doc in test_docs:
            try:
                os.unlink(doc["path"])
            except Exception as e:
                logger.warning(f"Failed to delete {doc['path']}: {e}")
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info("Generating test report...")
        
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "config": self.config.to_dict() if self.config else {}
            },
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": 0,
                "failed": 0
            }
        }
        
        # Calculate summary
        for test_name, test_result in self.test_results.items():
            if isinstance(test_result, dict):
                if test_result.get("success", False) or (test_result.get("error") is None and "error" not in test_result):
                    report["summary"]["passed"] += 1
                else:
                    report["summary"]["failed"] += 1
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("RAG SYSTEM TEST SUMMARY")
        print("="*50)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['passed']/report['summary']['total_tests']*100:.1f}%")
        print("="*50)
        
        return report
    
    def run_all_tests(self):
        """Run all RAG system tests."""
        logger.info("Starting comprehensive RAG system tests...")
        
        # Setup
        if not self.setup():
            logger.error("Setup failed, aborting tests")
            return False
        
        # Create test documents
        test_docs = self.create_test_documents()
        
        try:
            # Run tests
            tests = [
                ("Document Ingestion", lambda: self.test_document_ingestion(test_docs)),
                ("Text Ingestion", self.test_text_ingestion),
                ("Retrieval", self.test_retrieval),
                ("Generation", self.test_generation),
                ("Quiz Generation", self.test_quiz_generation),
                ("Summary Generation", self.test_summary_generation),
                ("System Management", self.test_system_management)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\n--- Running {test_name} Test ---")
                success = test_func()
                status = "PASSED" if success else "FAILED"
                logger.info(f"{test_name} Test: {status}")
            
            # Generate report
            self.generate_test_report()
            
        finally:
            # Cleanup
            self.cleanup_test_files(test_docs)
        
        logger.info("All tests completed!")
        return True


def main():
    """Main test function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            logger.info("Running quick tests (ingestion and retrieval only)")
            tester = RAGTester()
            if tester.setup():
                test_docs = tester.create_test_documents()
                try:
                    tester.test_document_ingestion(test_docs)
                    tester.test_retrieval()
                    tester.generate_test_report()
                finally:
                    tester.cleanup_test_files(test_docs)
            return
    
    # Run comprehensive tests
    tester = RAGTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
