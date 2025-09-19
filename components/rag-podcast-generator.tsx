"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Mic, Database, Search, Play, Download, Loader2, MessageSquare, FileText } from "lucide-react"
import { ragClient } from "@/lib/rag-client"

interface PodcastMetadata {
  title: string
  description: string
  duration: string
  topics: string[]
}

export function RAGPodcastGenerator() {
  const [activeTab, setActiveTab] = useState("search")
  
  // Search & Content State
  const [searchQuery, setSearchQuery] = useState("")
  const [customQuery, setCustomQuery] = useState("")
  const [searchResults, setSearchResults] = useState<any>(null)
  const [isSearching, setIsSearching] = useState(false)
  
  // Podcast Generation State
  const [podcastTopic, setPodcastTopic] = useState("")
  const [podcastStyle, setPodcastStyle] = useState("educational")
  const [podcastDuration, setPodcastDuration] = useState("5-7 minutes")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedPodcast, setGeneratedPodcast] = useState<{
    script: string
    metadata: PodcastMetadata
    audioUrl?: string
  } | null>(null)
  
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError("Please enter a search query")
      return
    }

    setIsSearching(true)
    setError(null)

    try {
      const result = await ragClient.query(searchQuery, {
        response_type: 'comprehensive',
        include_sources: true,
        top_k: 5
      })

      setSearchResults(result)
      
      // Auto-populate podcast topic if search was successful
      if (result.success && result.answer) {
        setPodcastTopic(searchQuery)
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Search failed")
    } finally {
      setIsSearching(false)
    }
  }

  const handleCustomQuery = async () => {
    if (!customQuery.trim()) {
      setError("Please enter a question")
      return
    }

    setIsSearching(true)
    setError(null)

    try {
      const result = await ragClient.query(customQuery, {
        response_type: 'conversational',
        include_sources: true
      })

      setSearchResults(result)
    } catch (error) {
      setError(error instanceof Error ? error.message : "Query failed")
    } finally {
      setIsSearching(false)
    }
  }

  const handleGeneratePodcast = async () => {
    if (!podcastTopic.trim()) {
      setError("Please enter a podcast topic")
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      // First, get comprehensive content about the topic from RAG
      const contentResult = await ragClient.query(podcastTopic, {
        response_type: 'comprehensive',
        include_sources: true,
        top_k: 8 // Get more context for podcast
      })

      if (!contentResult.success || !contentResult.answer) {
        throw new Error("Could not find relevant content for this topic")
      }

      // Then generate podcast script using the existing API with RAG content
      const scriptResponse = await fetch('/api/generate-podcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: contentResult.answer,
          options: {
            style: podcastStyle,
            duration: podcastDuration,
            voiceType: 'friendly',
            includeIntro: true,
            title: `${podcastTopic} - AI Generated Podcast`
          }
        })
      })

      if (!scriptResponse.ok) {
        const errorData = await scriptResponse.json()
        throw new Error(errorData.error || 'Failed to generate podcast script')
      }

      const { podcastScript } = await scriptResponse.json()

      // Generate audio (optional)
      let audioUrl = ""
      try {
        const audioResponse = await fetch('/api/text-to-speech', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: podcastScript.script,
            options: {
              voice: 'friendly',
              rate: '0',
              pitch: '0',
              volume: '0'
            }
          })
        })

        if (audioResponse.ok) {
          const { audioUrl: generatedAudioUrl } = await audioResponse.json()
          audioUrl = generatedAudioUrl
        }
      } catch (audioError) {
        console.warn("Audio generation failed, providing script only")
      }

      setGeneratedPodcast({
        script: podcastScript.script,
        metadata: {
          title: podcastScript.title,
          description: podcastScript.description,
          duration: podcastScript.duration,
          topics: podcastScript.topics || [podcastTopic]
        },
        audioUrl
      })

      setActiveTab("podcast")
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to generate podcast")
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <section className="py-20 bg-slate-900 text-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            🎙️ RAG-Powered Podcast Generator
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Search your knowledge base and generate intelligent podcasts with AI narration
          </p>
        </div>

        <Card className="max-w-5xl mx-auto bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white">
              <Mic className="w-6 h-6 text-purple-400" />
              Intelligent Podcast Creation
            </CardTitle>
            <CardDescription className="text-slate-300">
              Search your documents, explore content, and create engaging podcasts
            </CardDescription>
          </CardHeader>

          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3 bg-slate-700">
                <TabsTrigger value="search" className="data-[state=active]:bg-slate-600">Search</TabsTrigger>
                <TabsTrigger value="generate" className="data-[state=active]:bg-slate-600">Generate</TabsTrigger>
                <TabsTrigger value="podcast" className="data-[state=active]:bg-slate-600">Podcast</TabsTrigger>
              </TabsList>

              {/* Search Tab */}
              <TabsContent value="search" className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Topic Search */}
                  <Card className="bg-slate-700 border-slate-600">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2 text-white">
                        <Search className="w-5 h-5" />
                        Search Knowledge Base
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Input
                        placeholder="Search for topics in your documents..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        className="bg-slate-600 border-slate-500 text-white placeholder-slate-400"
                      />

                      <Button 
                        onClick={handleSearch} 
                        disabled={!searchQuery.trim() || isSearching}
                        className="w-full bg-purple-600 hover:bg-purple-700"
                      >
                        {isSearching ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Searching...
                          </>
                        ) : (
                          <>
                            <Search className="w-4 h-4 mr-2" />
                            Search Documents
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Custom Query */}
                  <Card className="bg-slate-700 border-slate-600">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2 text-white">
                        <MessageSquare className="w-5 h-5" />
                        Ask Questions
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Textarea
                        placeholder="Ask specific questions about your content..."
                        value={customQuery}
                        onChange={(e) => setCustomQuery(e.target.value)}
                        rows={3}
                        className="bg-slate-600 border-slate-500 text-white placeholder-slate-400"
                      />

                      <Button 
                        onClick={handleCustomQuery} 
                        disabled={!customQuery.trim() || isSearching}
                        className="w-full bg-blue-600 hover:bg-blue-700"
                      >
                        {isSearching ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          <>
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Ask Question
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* Search Results */}
                {searchResults && searchResults.success && (
                  <Card className="bg-slate-700 border-slate-600">
                    <CardHeader>
                      <CardTitle className="text-white">Search Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="prose prose-invert max-w-none">
                        <p className="text-slate-200">{searchResults.answer}</p>
                      </div>
                      
                      {searchResults.context_used.length > 0 && (
                        <div className="mt-4 p-4 bg-slate-600 rounded-lg">
                          <p className="text-sm font-medium mb-2 text-white">Sources:</p>
                          <ul className="text-sm space-y-1">
                            {searchResults.context_used.map((source: any, index: number) => (
                              <li key={index} className="flex items-center gap-2 text-slate-300">
                                <span className="w-2 h-2 bg-purple-400 rounded-full"></span>
                                {source.source} (Relevance: {(source.similarity * 100).toFixed(1)}%)
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <Button
                        onClick={() => {
                          setPodcastTopic(searchQuery || customQuery)
                          setActiveTab("generate")
                        }}
                        className="mt-4 bg-green-600 hover:bg-green-700"
                      >
                        <Mic className="w-4 h-4 mr-2" />
                        Create Podcast from This Content
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Generate Tab */}
              <TabsContent value="generate" className="space-y-6">
                <Card className="bg-slate-700 border-slate-600">
                  <CardHeader>
                    <CardTitle className="text-white">Podcast Generation Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2 text-white">Podcast Topic</label>
                      <Input
                        placeholder="What should the podcast be about?"
                        value={podcastTopic}
                        onChange={(e) => setPodcastTopic(e.target.value)}
                        className="bg-slate-600 border-slate-500 text-white placeholder-slate-400"
                      />
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2 text-white">Style</label>
                        <select 
                          className="w-full p-2 rounded-lg bg-slate-600 border-slate-500 text-white"
                          value={podcastStyle}
                          onChange={(e) => setPodcastStyle(e.target.value)}
                        >
                          <option value="educational">Educational</option>
                          <option value="conversational">Conversational</option>
                          <option value="narrative">Narrative</option>
                          <option value="interview">Interview Style</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2 text-white">Duration</label>
                        <select 
                          className="w-full p-2 rounded-lg bg-slate-600 border-slate-500 text-white"
                          value={podcastDuration}
                          onChange={(e) => setPodcastDuration(e.target.value)}
                        >
                          <option value="3-5 minutes">3-5 minutes</option>
                          <option value="5-7 minutes">5-7 minutes</option>
                          <option value="7-10 minutes">7-10 minutes</option>
                          <option value="10-15 minutes">10-15 minutes</option>
                        </select>
                      </div>
                    </div>

                    <Button 
                      onClick={handleGeneratePodcast} 
                      disabled={!podcastTopic.trim() || isGenerating}
                      className="w-full bg-purple-600 hover:bg-purple-700"
                      size="lg"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating Podcast...
                        </>
                      ) : (
                        <>
                          <Mic className="w-4 h-4 mr-2" />
                          Generate RAG-Powered Podcast
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Podcast Tab */}
              <TabsContent value="podcast" className="space-y-6">
                {generatedPodcast ? (
                  <div className="space-y-6">
                    {/* Podcast Header */}
                    <Card className="bg-slate-700 border-slate-600">
                      <CardHeader>
                        <CardTitle className="text-white">{generatedPodcast.metadata.title}</CardTitle>
                        <CardDescription className="text-slate-300">
                          {generatedPodcast.metadata.description}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2 mb-4">
                          <span className="px-2 py-1 bg-purple-600 text-white text-xs rounded">
                            {generatedPodcast.metadata.duration}
                          </span>
                          {generatedPodcast.metadata.topics.map((topic, index) => (
                            <span key={index} className="px-2 py-1 bg-slate-600 text-slate-200 text-xs rounded">
                              {topic}
                            </span>
                          ))}
                        </div>

                        {/* Audio Player */}
                        {generatedPodcast.audioUrl ? (
                          <div className="p-4 bg-slate-600 rounded-lg">
                            <div className="flex items-center gap-4">
                              <Play className="w-8 h-8 text-green-400" />
                              <div className="flex-1">
                                <audio controls className="w-full">
                                  <source src={generatedPodcast.audioUrl} type="audio/mpeg" />
                                  Your browser does not support the audio element.
                                </audio>
                              </div>
                              <Button size="sm" asChild className="bg-green-600 hover:bg-green-700">
                                <a href={generatedPodcast.audioUrl} download>
                                  <Download className="w-4 h-4" />
                                </a>
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="p-4 bg-yellow-900 border border-yellow-600 rounded-lg">
                            <p className="text-yellow-200">
                              Audio generation is temporarily unavailable. Script is available below.
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>

                    {/* Podcast Script */}
                    <Card className="bg-slate-700 border-slate-600">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-white">
                          <FileText className="w-5 h-5" />
                          Podcast Script
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="prose prose-invert max-w-none">
                          <pre className="whitespace-pre-wrap text-slate-200 text-sm leading-relaxed">
                            {generatedPodcast.script}
                          </pre>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Actions */}
                    <div className="flex gap-4">
                      <Button
                        onClick={() => {
                          setGeneratedPodcast(null)
                          setActiveTab("generate")
                        }}
                        variant="outline"
                        className="flex-1 border-slate-600 text-slate-200 hover:bg-slate-700"
                      >
                        Generate New Podcast
                      </Button>
                      <Button
                        onClick={() => setActiveTab("search")}
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                      >
                        Search More Content
                      </Button>
                    </div>
                  </div>
                ) : (
                  <Card className="bg-slate-700 border-slate-600">
                    <CardContent className="py-12 text-center">
                      <Mic className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                      <p className="text-slate-300">
                        Generate a podcast first to listen and read the script!
                      </p>
                      <Button
                        onClick={() => setActiveTab("generate")}
                        className="mt-4 bg-purple-600 hover:bg-purple-700"
                      >
                        Go to Generate Tab
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>

            {/* Error Display */}
            {error && (
              <div className="mt-4 p-4 bg-red-900 border border-red-600 rounded-lg">
                <div className="flex items-center gap-2 text-red-200">
                  <MessageSquare className="w-5 h-5" />
                  {error}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  )
}
