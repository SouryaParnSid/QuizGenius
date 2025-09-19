/**
 * RAG System Client
 * 
 * Client library for integrating with the RAG API backend
 */

const RAG_API_BASE_URL = 'http://localhost:8001'

export interface RAGDocument {
  id: string
  content: string
  metadata: Record<string, any>
}

export interface RAGQueryResult {
  success: boolean
  query: string
  answer: string
  retrieved_documents: number
  context_used: Array<{
    doc_id: string
    similarity: number
    source: string
    chunk_index: number
    content_preview: string
  }>
  metadata: Record<string, any>
  error?: string
}

export interface RAGQuizResult {
  success: boolean
  topic: string
  quiz: string // JSON string containing quiz questions
  context_used: Array<{
    doc_id: string
    similarity: number
    source: string
  }>
  metadata: Record<string, any>
  error?: string
}

export interface RAGIngestionResult {
  success: boolean
  file_path?: string
  source_name?: string
  documents_created: number
  document_ids: string[]
  chunking_strategy: string
  metadata: Record<string, any>
  error?: string
}

class RAGClient {
  private baseUrl: string

  constructor(baseUrl: string = RAG_API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Check if RAG API is healthy
   */
  async healthCheck(): Promise<{ status: string; system_info?: any }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`)
      return await response.json()
    } catch (error) {
      throw new Error(`RAG API health check failed: ${error}`)
    }
  }

  /**
   * Ingest a file into the RAG system
   */
  async ingestFile(
    file: File,
    chunkingStrategy: string = 'recursive',
    customMetadata?: Record<string, any>
  ): Promise<RAGIngestionResult> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('chunking_strategy', chunkingStrategy)
      
      if (customMetadata) {
        formData.append('custom_metadata', JSON.stringify(customMetadata))
      }

      const response = await fetch(`${this.baseUrl}/ingest/file`, {
        method: 'POST',
        body: formData
      })

      return await response.json()
    } catch (error) {
      throw new Error(`File ingestion failed: ${error}`)
    }
  }

  /**
   * Ingest text content into the RAG system
   */
  async ingestText(
    text: string,
    sourceName: string = 'text_input',
    chunkingStrategy: string = 'recursive',
    customMetadata?: Record<string, any>
  ): Promise<RAGIngestionResult> {
    try {
      const response = await fetch(`${this.baseUrl}/ingest/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text,
          source_name: sourceName,
          chunking_strategy: chunkingStrategy,
          custom_metadata: customMetadata
        })
      })

      return await response.json()
    } catch (error) {
      throw new Error(`Text ingestion failed: ${error}`)
    }
  }

  /**
   * Query the RAG system
   */
  async query(
    question: string,
    options: {
      top_k?: number
      similarity_threshold?: number
      response_type?: string
      include_sources?: boolean
      filter_metadata?: Record<string, any>
    } = {}
  ): Promise<RAGQueryResult> {
    try {
      const response = await fetch(`${this.baseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question,
          top_k: options.top_k || 8,  // Get more chunks for podcast content
          similarity_threshold: options.similarity_threshold || 0.1,  // Use lower threshold for better retrieval
          response_type: options.response_type || 'comprehensive',
          include_sources: options.include_sources !== false,
          filter_metadata: options.filter_metadata
        })
      })

      return await response.json()
    } catch (error) {
      throw new Error(`Query failed: ${error}`)
    }
  }

  /**
   * Generate quiz questions using RAG
   */
  async generateQuiz(
    topic: string,
    options: {
      num_questions?: number
      difficulty?: string
      question_types?: string[]
      filter_metadata?: Record<string, any>
    } = {}
  ): Promise<RAGQuizResult> {
    try {
      const response = await fetch(`${this.baseUrl}/generate/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          topic,
          num_questions: options.num_questions || 5,
          difficulty: options.difficulty || 'medium',
          question_types: options.question_types || ['multiple-choice', 'true-false'],
          filter_metadata: options.filter_metadata
        })
      })

      return await response.json()
    } catch (error) {
      throw new Error(`Quiz generation failed: ${error}`)
    }
  }

  /**
   * Generate summary using RAG
   */
  async generateSummary(
    query: string,
    options: {
      summary_type?: string
      max_length?: number
      filter_metadata?: Record<string, any>
    } = {}
  ): Promise<RAGQueryResult> {
    try {
      const response = await fetch(`${this.baseUrl}/generate/summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          summary_type: options.summary_type || 'comprehensive',
          max_length: options.max_length || 500,
          filter_metadata: options.filter_metadata
        })
      })

      return await response.json()
    } catch (error) {
      throw new Error(`Summary generation failed: ${error}`)
    }
  }

  /**
   * Search documents without generating a response
   */
  async searchDocuments(
    query: string,
    options: {
      top_k?: number
      similarity_threshold?: number
    } = {}
  ): Promise<{ query: string; results: any[]; count: number }> {
    try {
      const params = new URLSearchParams({
        query,
        top_k: (options.top_k || 5).toString(),
        similarity_threshold: (options.similarity_threshold || 0.7).toString()
      })

      const response = await fetch(`${this.baseUrl}/search?${params}`)
      return await response.json()
    } catch (error) {
      throw new Error(`Document search failed: ${error}`)
    }
  }

  /**
   * List documents in the RAG system
   */
  async listDocuments(limit?: number): Promise<{ success: boolean; documents: RAGDocument[]; count: number }> {
    try {
      const params = limit ? `?limit=${limit}` : ''
      const response = await fetch(`${this.baseUrl}/documents${params}`)
      return await response.json()
    } catch (error) {
      throw new Error(`Failed to list documents: ${error}`)
    }
  }

  /**
   * Delete a document from the RAG system
   */
  async deleteDocument(docId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/documents/${docId}`, {
        method: 'DELETE'
      })
      return await response.json()
    } catch (error) {
      throw new Error(`Failed to delete document: ${error}`)
    }
  }

  /**
   * Get system information
   */
  async getSystemInfo(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/system/info`)
      return await response.json()
    } catch (error) {
      throw new Error(`Failed to get system info: ${error}`)
    }
  }
}

// Export singleton instance
export const ragClient = new RAGClient()

// Export class for custom instances
export { RAGClient }
