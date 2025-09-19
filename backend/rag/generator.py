"""
Generator Service

Service for generating responses using Google Gemini API
with retrieved context from the RAG system.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import google.generativeai as genai
from dataclasses import dataclass
import json
import time

from .config import RAGConfig
from .retriever import RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result from text generation."""
    response: str
    context_used: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "response": self.response,
            "context_used": self.context_used,
            "metadata": self.metadata
        }


class GeneratorService:
    """Service for generating responses with retrieved context."""
    
    def __init__(self, config: RAGConfig):
        """Initialize the generator service."""
        self.config = config
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini model."""
        try:
            if not self.config.gemini_api_key:
                raise ValueError("Gemini API key not provided")
            
            genai.configure(api_key=self.config.gemini_api_key)
            self.model = genai.GenerativeModel(self.config.gemini_model)
            logger.info(f"Initialized Gemini model: {self.config.gemini_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def generate_response(
        self,
        query: str,
        context_results: List[RetrievalResult],
        response_type: str = "comprehensive",
        custom_prompt: Optional[str] = None,
        include_sources: bool = True
    ) -> GenerationResult:
        """Generate a response using retrieved context."""
        try:
            # Prepare context
            context_text = self._prepare_context(context_results)
            
            # Create prompt
            if custom_prompt:
                prompt = self._create_custom_prompt(query, context_text, custom_prompt)
            else:
                prompt = self._create_system_prompt(query, context_text, response_type)
            
            # Generate response
            start_time = time.time()
            response = self.model.generate_content(prompt)
            generation_time = time.time() - start_time
            
            # Extract response text
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Prepare context metadata
            context_metadata = []
            for result in context_results:
                context_metadata.append({
                    "doc_id": result.doc_id,
                    "similarity": result.similarity,
                    "source": result.metadata.get("source_file", result.metadata.get("source", "unknown")),
                    "chunk_index": result.metadata.get("chunk_index", 0),
                    "content_preview": result.content[:100] + "..." if len(result.content) > 100 else result.content
                })
            
            # Add source citations if requested
            if include_sources and context_results:
                response_text = self._add_source_citations(response_text, context_results)
            
            # Create result
            result = GenerationResult(
                response=response_text,
                context_used=context_metadata,
                metadata={
                    "query": query,
                    "response_type": response_type,
                    "context_count": len(context_results),
                    "generation_time": generation_time,
                    "model_used": self.config.gemini_model,
                    "prompt_length": len(prompt),
                    "response_length": len(response_text),
                    "include_sources": include_sources
                }
            )
            
            logger.info(f"Generated response ({len(response_text)} chars) using {len(context_results)} context documents")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def generate_quiz_questions(
        self,
        context_results: List[RetrievalResult],
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None
    ) -> GenerationResult:
        """Generate quiz questions from retrieved context."""
        if question_types is None:
            question_types = ["multiple-choice", "true-false"]
        
        context_text = self._prepare_context(context_results)
        
        prompt = f"""
Based on the following context, generate {num_questions} quiz questions with difficulty level: {difficulty}.

Question types to include: {', '.join(question_types)}

CONTEXT:
{context_text}

Generate questions that test understanding of the key concepts and information in the context.
Return the response as a JSON object with the following structure:

{{
    "questions": [
        {{
            "id": 1,
            "question": "Question text",
            "type": "multiple-choice",
            "options": ["A", "B", "C", "D"],
            "correct_answer": 0,
            "explanation": "Why this answer is correct",
            "difficulty": "{difficulty}",
            "source_reference": "Reference to context"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Clean up response text (remove markdown formatting, etc.)
            response_text = response_text.strip()
            
            # Extract JSON from response if it's wrapped in markdown
            if response_text.startswith('```json'):
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]
            elif response_text.startswith('```'):
                start = response_text.find('{')
                end = response_text.rfind('}')
                if start != -1 and end != -1:
                    response_text = response_text[start:end+1]
            
            logger.info(f"Raw response: {response_text[:200]}...")
            
            # Try to parse JSON
            quiz_data = json.loads(response_text)
            
            result = GenerationResult(
                response=json.dumps(quiz_data, indent=2),
                context_used=[{
                    "doc_id": r.doc_id,
                    "similarity": r.similarity,
                    "source": r.metadata.get("source_file", "unknown")
                } for r in context_results],
                metadata={
                    "generation_type": "quiz_questions",
                    "num_questions": num_questions,
                    "difficulty": difficulty,
                    "question_types": question_types,
                    "context_count": len(context_results)
                }
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz JSON: {e}")
            raise ValueError("Generated quiz questions are not in valid JSON format")
        except Exception as e:
            logger.error(f"Failed to generate quiz questions: {e}")
            raise
    
    def generate_summary(
        self,
        context_results: List[RetrievalResult],
        summary_type: str = "comprehensive",
        max_length: int = 500
    ) -> GenerationResult:
        """Generate a summary from retrieved context."""
        context_text = self._prepare_context(context_results)
        
        summary_instructions = {
            "brief": "Create a brief, concise summary highlighting only the most important points.",
            "comprehensive": "Create a comprehensive summary covering all key points and details.",
            "executive": "Create an executive summary suitable for decision-makers.",
            "technical": "Create a technical summary focusing on detailed information and specifics."
        }
        
        instruction = summary_instructions.get(summary_type, summary_instructions["comprehensive"])
        
        prompt = f"""
{instruction}

Maximum length: approximately {max_length} words.

CONTEXT TO SUMMARIZE:
{context_text}

Create a well-structured summary that captures the essential information from the context.
Include key insights, important facts, and main conclusions.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            result = GenerationResult(
                response=response_text,
                context_used=[{
                    "doc_id": r.doc_id,
                    "similarity": r.similarity,
                    "source": r.metadata.get("source_file", "unknown")
                } for r in context_results],
                metadata={
                    "generation_type": "summary",
                    "summary_type": summary_type,
                    "max_length": max_length,
                    "context_count": len(context_results),
                    "actual_length": len(response_text.split())
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise
    
    def _prepare_context(self, context_results: List[RetrievalResult]) -> str:
        """Prepare context text from retrieval results."""
        if not context_results:
            return "No relevant context found."
        
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(context_results):
            # Add source information
            source = result.metadata.get("source_file", result.metadata.get("source", f"Document {i+1}"))
            chunk_info = ""
            if "chunk_index" in result.metadata:
                chunk_info = f" (Chunk {result.metadata['chunk_index'] + 1})"
            
            context_part = f"--- Source {i+1}: {source}{chunk_info} (Similarity: {result.similarity:.3f}) ---\n"
            context_part += result.content + "\n\n"
            
            # Check if adding this context would exceed the limit
            if total_length + len(context_part) > self.config.max_context_length:
                logger.warning(f"Context truncated to fit within {self.config.max_context_length} characters")
                break
            
            context_parts.append(context_part)
            total_length += len(context_part)
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self, query: str, context: str, response_type: str) -> str:
        """Create a system prompt for response generation."""
        system_instructions = {
            "comprehensive": "Provide a comprehensive, detailed answer using the given context.",
            "concise": "Provide a concise, to-the-point answer using the given context.",
            "analytical": "Provide an analytical response that examines and interprets the information.",
            "educational": "Provide an educational response suitable for learning purposes.",
            "conversational": "Provide a conversational, friendly response."
        }
        
        instruction = system_instructions.get(response_type, system_instructions["comprehensive"])
        
        return f"""
You are an intelligent assistant with access to relevant context information. {instruction}

IMPORTANT GUIDELINES:
1. Base your response primarily on the provided context
2. If the context doesn't fully answer the question, clearly state what information is missing
3. Be accurate and cite specific information from the context when possible
4. If you need to use external knowledge, clearly distinguish it from the context
5. Maintain a helpful and informative tone

USER QUESTION:
{query}

RELEVANT CONTEXT:
{context}

Please provide your response based on the above context:
"""
    
    def _create_custom_prompt(self, query: str, context: str, custom_template: str) -> str:
        """Create a custom prompt using a template."""
        return custom_template.format(
            query=query,
            context=context
        )
    
    def _add_source_citations(self, response: str, context_results: List[RetrievalResult]) -> str:
        """Add source citations to the response."""
        if not context_results:
            return response
        
        citations = "\n\n**Sources:**\n"
        for i, result in enumerate(context_results):
            source = result.metadata.get("source_file", result.metadata.get("source", f"Document {i+1}"))
            chunk_info = ""
            if "chunk_index" in result.metadata:
                chunk_info = f" (Section {result.metadata['chunk_index'] + 1})"
            
            citations += f"{i+1}. {source}{chunk_info} (Relevance: {result.similarity:.1%})\n"
        
        return response + citations
    
    def validate_response(self, response: str) -> Tuple[bool, str]:
        """Validate the generated response."""
        if not response or not response.strip():
            return False, "Empty response generated"
        
        if len(response) < 10:
            return False, "Response too short"
        
        if len(response) > self.config.max_output_tokens * 4:  # Rough character estimate
            return False, "Response too long"
        
        # Check for obvious errors or incomplete responses
        error_indicators = [
            "I don't have enough information",
            "I cannot answer",
            "Error:",
            "Failed to",
            "[ERROR]"
        ]
        
        response_lower = response.lower()
        for indicator in error_indicators:
            if indicator.lower() in response_lower:
                return False, f"Response contains error indicator: {indicator}"
        
        return True, "Response is valid"
    
    def get_generation_stats(self, results: List[GenerationResult]) -> Dict[str, Any]:
        """Get statistics about generation results."""
        if not results:
            return {}
        
        response_lengths = [len(r.response) for r in results]
        generation_times = [r.metadata.get("generation_time", 0) for r in results]
        context_counts = [r.metadata.get("context_count", 0) for r in results]
        
        return {
            "total_generations": len(results),
            "avg_response_length": sum(response_lengths) / len(response_lengths),
            "avg_generation_time": sum(generation_times) / len(generation_times),
            "avg_context_count": sum(context_counts) / len(context_counts),
            "response_types": [r.metadata.get("response_type", "unknown") for r in results],
            "model_used": results[0].metadata.get("model_used", "unknown") if results else "unknown"
        }
