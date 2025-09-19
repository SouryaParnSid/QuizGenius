"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Database, Brain, Mic, MessageSquare, CheckCircle, AlertCircle, ExternalLink } from "lucide-react"
import { ragClient } from "@/lib/rag-client"

export function RAGIntegrationStatus() {
  const [ragStatus, setRagStatus] = useState<{
    isHealthy: boolean
    documentsCount: number
    systemInfo: any
  }>({
    isHealthy: false,
    documentsCount: 0,
    systemInfo: null
  })
  
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    checkRAGStatus()
  }, [])

  const checkRAGStatus = async () => {
    setIsLoading(true)
    try {
      // Check health
      const health = await ragClient.healthCheck()
      const isHealthy = health.status === "healthy"
      
      // Get document count
      let documentsCount = 0
      let systemInfo = null
      
      if (isHealthy) {
        try {
          const docs = await ragClient.listDocuments(1)
          documentsCount = docs.count
          
          systemInfo = await ragClient.getSystemInfo()
        } catch (error) {
          console.warn("Could not fetch additional info:", error)
        }
      }
      
      setRagStatus({
        isHealthy,
        documentsCount,
        systemInfo
      })
    } catch (error) {
      console.error("RAG status check failed:", error)
      setRagStatus({
        isHealthy: false,
        documentsCount: 0,
        systemInfo: null
      })
    } finally {
      setIsLoading(false)
    }
  }

  const features = [
    {
      icon: <Database className="w-5 h-5" />,
      name: "Knowledge Base",
      description: "Upload and manage documents",
      status: ragStatus.isHealthy,
      details: `${ragStatus.documentsCount} documents stored`
    },
    {
      icon: <Brain className="w-5 h-5" />,
      name: "Smart Quiz Generation",
      description: "AI-powered quiz creation from your content",
      status: ragStatus.isHealthy,
      details: ragStatus.systemInfo?.embedding_model?.model_name || "Sentence Transformers"
    },
    {
      icon: <Mic className="w-5 h-5" />,
      name: "Intelligent Podcasts",
      description: "Generate podcasts from knowledge base",
      status: ragStatus.isHealthy,
      details: "RAG + Gemini AI + TTS"
    },
    {
      icon: <MessageSquare className="w-5 h-5" />,
      name: "Smart Q&A",
      description: "Ask questions about your documents",
      status: ragStatus.isHealthy,
      details: ragStatus.systemInfo?.vector_store?.document_count ? 
        `${ragStatus.systemInfo.vector_store.document_count} searchable chunks` : 
        "Vector search enabled"
    }
  ]

  return (
    <section className="py-16 bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
            🚀 RAG System Integration
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            Advanced AI-powered features now available in QuizGenius
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-6">
          {/* System Status Card */}
          <Card className="border-2 border-dashed border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${
                  ragStatus.isHealthy 
                    ? "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400"
                    : "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400"
                }`}>
                  {ragStatus.isHealthy ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                </div>
                RAG System Status
                {isLoading && <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>}
              </CardTitle>
              <CardDescription>
                {ragStatus.isHealthy 
                  ? "All systems operational and ready to use"
                  : "System offline - please start the RAG API server"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-slate-600 dark:text-slate-400">
                    API Endpoint: <code className="bg-slate-100 dark:bg-slate-800 px-1 rounded">http://localhost:8001</code>
                  </p>
                  {ragStatus.systemInfo && (
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Vector Store: {ragStatus.systemInfo.vector_store?.name || "FAISS"}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button 
                    onClick={checkRAGStatus} 
                    variant="outline" 
                    size="sm"
                    disabled={isLoading}
                  >
                    Refresh
                  </Button>
                  <Button 
                    asChild 
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <a href="http://localhost:8001/docs" target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="w-4 h-4 mr-1" />
                      API Docs
                    </a>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <Card key={index} className={`transition-all duration-200 ${
                feature.status 
                  ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950" 
                  : "border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900"
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${
                      feature.status 
                        ? "bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400"
                        : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                    }`}>
                      {feature.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-slate-900 dark:text-white mb-1">
                        {feature.name}
                      </h3>
                      <p className="text-sm text-slate-600 dark:text-slate-300 mb-2">
                        {feature.description}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {feature.details}
                      </p>
                    </div>
                    <div className={`w-3 h-3 rounded-full ${
                      feature.status ? "bg-green-500" : "bg-gray-400"
                    }`}></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Getting Started */}
          {!ragStatus.isHealthy && (
            <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
              <CardHeader>
                <CardTitle className="text-yellow-800 dark:text-yellow-200">
                  🚧 Get Started with RAG
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-yellow-700 dark:text-yellow-300">
                  <p><strong>To start the RAG system:</strong></p>
                  <ol className="list-decimal list-inside space-y-1 ml-4">
                    <li>Open terminal and navigate to <code>backend/</code> folder</li>
                    <li>Run: <code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">python start_rag_api.py</code></li>
                    <li>Wait for "Server running on http://localhost:8001" message</li>
                    <li>Refresh this page to see the system status</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </section>
  )
}
