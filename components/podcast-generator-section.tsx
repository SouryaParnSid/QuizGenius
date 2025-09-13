"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { FileUpload } from "@/components/ui/file-upload"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Mic, Wand2, Settings, Clock, Download, FileText, Play, Pause, Volume2, AlertCircle } from "lucide-react"

interface PodcastMetadata {
  title: string
  duration: string
  host: string
  description: string
  topics: string[]
}

interface PodcastSegment {
  type: 'intro' | 'content' | 'transition' | 'outro'
  text: string
  timestamp: string
  voice_settings?: {
    speed: number
    pitch: number
    emphasis: string[]
  }
}

interface GeneratedPodcast {
  audioUrl: string
  transcript: string
  metadata: PodcastMetadata
  script: string
  segments: PodcastSegment[]
}

export function PodcastGeneratorSection() {
  const [textInput, setTextInput] = useState("")
  const [podcastTitle, setPodcastTitle] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedPodcast, setGeneratedPodcast] = useState<GeneratedPodcast | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [audioDuration, setAudioDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  
  // Audio refs and controls
  const audioRef = useRef<HTMLAudioElement>(null)
  
  // Audio control functions
  const handlePlayPause = useCallback(async () => {
    const audio = audioRef.current
    if (!audio) return

    try {
      if (isPlaying) {
        await audio.pause()
      } else {
        await audio.play()
      }
    } catch (error) {
      console.error('Error controlling audio playback:', error)
      setError('Failed to play audio. Please check the audio file.')
    }
  }, [isPlaying])
  
  // Audio event handlers
  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setAudioDuration(audio.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [generatedPodcast])

  // Keyboard controls for audio player
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (!generatedPodcast?.audioUrl) return
      
      // Only handle shortcuts when no input is focused
      if (document.activeElement?.tagName === 'INPUT' || 
          document.activeElement?.tagName === 'TEXTAREA') {
        return
      }

      switch (event.key) {
        case ' ': // Spacebar for play/pause
          event.preventDefault()
          handlePlayPause()
          break
        case 'ArrowLeft': // Left arrow for -10s
          event.preventDefault()
          const audio = audioRef.current
          if (audio) {
            audio.currentTime = Math.max(0, audio.currentTime - 10)
          }
          break
        case 'ArrowRight': // Right arrow for +10s
          event.preventDefault()
          const audioRight = audioRef.current
          if (audioRight) {
            audioRight.currentTime = Math.min(audioRight.duration, audioRight.currentTime + 10)
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [generatedPodcast?.audioUrl, handlePlayPause])
  
  // Podcast settings
  const [podcastStyle, setPodcastStyle] = useState("conversational")
  const [duration, setDuration] = useState("auto")
  const [voiceType, setVoiceType] = useState("professional")
  const [includeIntro, setIncludeIntro] = useState(true)

  const extractPdfText = async (file: File): Promise<string> => {
    try {
      const isProduction = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
      
      console.log('Starting PDF extraction for podcast...', {
        fileName: file.name,
        fileSize: file.size,
        isProduction
      })
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('method', 'auto')
      formData.append('usePython', isProduction ? 'false' : 'true')
      
      const response = await fetch('/api/extract-pdf', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        console.log('Python extraction failed, trying JavaScript fallback...')
        
        const fallbackFormData = new FormData()
        fallbackFormData.append('file', file)
        fallbackFormData.append('method', 'auto')
        fallbackFormData.append('usePython', 'false')
        
        const fallbackResponse = await fetch('/api/extract-pdf', {
          method: 'POST',
          body: fallbackFormData
        })
        
        if (!fallbackResponse.ok) {
          const errorData = await fallbackResponse.json().catch(() => ({ error: 'Unknown error' }))
          throw new Error(errorData.error || 'Both Python and JavaScript PDF extraction methods failed')
        }
        
        const fallbackData = await fallbackResponse.json()
        
        if (!fallbackData.success || !fallbackData.text || fallbackData.text.length < 50) {
          throw new Error('PDF extraction returned insufficient text. This might be a scanned document or contain mostly images. Please try a text-based PDF.')
        }
        
        console.log('JavaScript fallback extraction successful for podcast:', {
          method: fallbackData.metadata?.method,
          characters: fallbackData.text.length,
          pages: fallbackData.metadata?.pages_with_text
        })
        
        return fallbackData.text
      }
      
      const data = await response.json()
      
      if (!data.success || !data.text) {
        throw new Error('PDF extraction failed. The document might be scanned, encrypted, or contain only images.')
      }
      
      if (data.text.length < 100) {
        throw new Error('PDF extraction returned very little text. This might be a scanned document or contain mostly images. Please try a text-based PDF with more content.')
      }
      
      console.log('PDF extraction successful for podcast:', {
        method: data.metadata?.method,
        characters: data.text.length,
        pages: data.metadata?.pages_with_text,
        preview: data.text.substring(0, 100) + '...'
      })
      
      return data.text
    } catch (error) {
      console.error('PDF extraction error:', error)
      throw new Error(`Failed to extract text from PDF: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const generatePodcastContent = async (content: string): Promise<GeneratedPodcast> => {
    try {
      console.log('Generating podcast script with Gemini AI...')
      
      // Step 1: Generate podcast script with Gemini
      const scriptResponse = await fetch('/api/generate-podcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          options: {
            style: podcastStyle,
            duration,
            voiceType,
            includeIntro,
            title: podcastTitle || 'AI Generated Podcast'
          }
        })
      })

      if (!scriptResponse.ok) {
        const errorData = await scriptResponse.json()
        throw new Error(errorData.error || 'Failed to generate podcast script')
      }

      const { podcastScript } = await scriptResponse.json()
      
      console.log('Podcast script generated successfully:', {
        title: podcastScript.title,
        scriptLength: podcastScript.script.length,
        segments: podcastScript.segments.length
      })

      // Step 2: Generate audio with Edge TTS
      console.log('Generating audio with Edge TTS...')
      
      const ttsResponse = await fetch('/api/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: podcastScript.script,
          options: {
            voice: voiceType,
            rate: '0',
            pitch: '0',
            volume: '0'
          }
        })
      })

      let audioUrl = ''
      let ttsWarning = ''

      if (!ttsResponse.ok) {
        console.warn('TTS generation failed, using fallback audio')
        audioUrl = generateFallbackAudio(podcastScript.script.length)
        ttsWarning = '🔊 Playing placeholder audio with correct duration. Full transcript available!'
      } else {
        const ttsData = await ttsResponse.json()
        audioUrl = ttsData.audioUrl
        ttsWarning = ttsData.warning || ttsData.message || ''
        
        // If we got a fallback response
        if (ttsData.voice === 'Text-to-Speech Unavailable' || ttsData.voice === 'Placeholder Audio' || ttsData.isFallback) {
          ttsWarning = '🔊 Playing placeholder audio with correct duration. Full transcript available!'
        }
      }

      // Step 3: Create the final podcast object
      const metadata: PodcastMetadata = {
        title: podcastScript.title,
        duration: podcastScript.duration,
        host: "AI Podcast Host",
        description: podcastScript.description,
        topics: podcastScript.topics
      }

      console.log('Podcast generation completed successfully!')

      return {
        audioUrl,
        transcript: podcastScript.script,
        script: podcastScript.script,
        segments: podcastScript.segments,
        metadata: {
          ...metadata,
          description: ttsWarning ? `${metadata.description} (${ttsWarning})` : metadata.description
        }
      }

    } catch (error) {
      console.error('Podcast generation error:', error)
      throw new Error(`Failed to generate podcast: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  const generateFallbackAudio = (textLength: number): string => {
    // Calculate realistic duration based on speech rate (150 words per minute)
    const words = Math.floor(textLength / 5) // Approximate words from character count
    const speechMinutes = words / 150 // 150 words per minute average
    const duration = Math.max(speechMinutes * 60, 30) // Minimum 30 seconds, no maximum
    
    const sampleRate = 22050
    const samples = Math.floor(duration * sampleRate)
    
    // Create audio buffer for proper duration
    const buffer = new ArrayBuffer(44 + samples * 2)
    const view = new DataView(buffer)
    
    // WAV header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i))
      }
    }
    
    writeString(0, 'RIFF')
    view.setUint32(4, 36 + samples * 2, true)
    writeString(8, 'WAVE')
    writeString(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, 1, true)
    view.setUint16(22, 1, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, sampleRate * 2, true)
    view.setUint16(32, 2, true)
    view.setUint16(34, 16, true)
    writeString(36, 'data')
    view.setUint32(40, samples * 2, true)
    
    // Generate a pleasant, audible tone that clearly indicates this is a placeholder
    // Make it audible but not annoying - like a meditation bell
    for (let i = 0; i < samples; i++) {
      const time = i / sampleRate
      
      // Create a gentle bell-like sound with soft attack and decay
      const frequency = 440 // A4 note - more pleasant and audible
      const amplitude = 0.12 // 12% volume - clearly audible but not harsh
      
      // Add gentle decay over time to make it more pleasant
      const decay = Math.exp(-time * 0.5) // Gradual decay
      const envelope = Math.min(1, time * 10) * decay // Soft attack + decay
      
      // Sine wave with envelope
      const sample = Math.sin(2 * Math.PI * frequency * time) * amplitude * envelope * 32767
      view.setInt16(44 + i * 2, Math.floor(sample), true)
    }
    
    // Convert to base64
    const bytes = new Uint8Array(buffer)
    const binary = Array.from(bytes, byte => String.fromCharCode(byte)).join('')
    return `data:audio/wav;base64,${btoa(binary)}`
  }

  const handleGeneratePodcast = async () => {
    if (!textInput.trim() && !selectedFile) {
      setError("Please provide text content or upload a PDF file")
      return
    }

    setIsGenerating(true)
    setError(null)
    
    try {
      let fileContent: string

      if (selectedFile && selectedFile.type === 'application/pdf') {
        console.log('Starting PDF extraction for podcast...', selectedFile.name)
        fileContent = await extractPdfText(selectedFile)
        console.log('PDF extraction completed. Text length:', fileContent.length)
        
        if (fileContent.length < 100) {
          throw new Error('PDF extraction returned insufficient text for podcast generation. Please try a different PDF file.')
        }
      } else {
        fileContent = textInput
      }

      // Generate podcast content
      const podcast = await generatePodcastContent(fileContent)
      setGeneratedPodcast(podcast)
      
      // Reset audio state for new podcast
      setIsPlaying(false)
      setCurrentTime(0)
      setAudioDuration(0)
      
    } catch (error) {
      console.error('Podcast generation error:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate podcast')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setError(null)
  }

  const handleSeek = (event: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    if (!audio || !audioDuration) return

    const rect = event.currentTarget.getBoundingClientRect()
    const clickX = event.clientX - rect.left
    const width = rect.width
    const percentage = clickX / width
    const newTime = percentage * audioDuration

    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleVolumeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(event.target.value)
    setVolume(newVolume)
    
    const audio = audioRef.current
    if (audio) {
      audio.volume = newVolume
    }
  }

  const formatTime = (time: number): string => {
    if (isNaN(time)) return '0:00'
    
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const handleDownload = () => {
    if (!generatedPodcast?.audioUrl) return

    const link = document.createElement('a')
    link.href = generatedPodcast.audioUrl
    link.download = `${generatedPodcast.metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.mp3`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleDownloadScript = () => {
    if (!generatedPodcast?.script) return

    // Create formatted script content
    const scriptContent = `${generatedPodcast.metadata.title}
${'='.repeat(generatedPodcast.metadata.title.length)}

Description: ${generatedPodcast.metadata.description}
Duration: ${generatedPodcast.metadata.duration}
Host: ${generatedPodcast.metadata.host}

${'='.repeat(50)}
PODCAST SCRIPT
${'='.repeat(50)}

${generatedPodcast.script}

${'='.repeat(50)}
Generated by QuizGenius AI Podcast Generator
${'='.repeat(50)}`

    // Create blob and download
    const blob = new Blob([scriptContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    link.href = url
    link.download = `${generatedPodcast.metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_script.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Clean up the URL
    URL.revokeObjectURL(url)
  }

  return (
    <section id="podcast-generator" className="py-20 bg-slate-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            AI Podcast Generator
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Transform your documents into engaging podcasts with AI-powered narration,
            natural conversation flow, and professional audio production using Gemini AI and Edge TTS
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Input Panel */}
          <Card className="shadow-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="h-6 w-6 text-purple-400" />
                Create Your Podcast
              </CardTitle>
              <CardDescription>
                Upload a PDF or enter text content to generate an AI-powered podcast with Gemini AI script generation and Edge TTS audio
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {error && (
                <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Podcast Title</label>
                <Input
                  placeholder="Enter a title for your podcast..."
                  value={podcastTitle}
                  onChange={(e) => setPodcastTitle(e.target.value)}
                  className="w-full"
                />
              </div>

              <Tabs defaultValue="text" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="text">Text Input</TabsTrigger>
                  <TabsTrigger value="pdf">PDF Upload</TabsTrigger>
                </TabsList>
                
                <TabsContent value="text" className="mt-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Content for Podcast Generation
                    </label>
                    <Textarea
                      placeholder="Paste your content here... The AI will analyze your text and create an engaging podcast with natural narration, discussion points, and professional audio flow using Gemini AI."
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      className="min-h-[200px] w-full"
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="pdf" className="mt-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Upload PDF Document
                    </label>
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      acceptedTypes={['application/pdf']}
                      maxSize={16}
                      placeholder="Upload your PDF document for AI podcast generation"
                    />
                    {selectedFile && (
                      <p className="text-sm text-slate-400 mt-2">
                        Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                      </p>
                    )}
                  </div>
                </TabsContent>
              </Tabs>

              {/* Podcast Settings */}
              <div className="border-t pt-6">
                <h4 className="flex items-center gap-2 font-medium mb-4">
                  <Settings className="h-4 w-4" />
                  Podcast Settings
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Style</label>
                    <select 
                      className="w-full p-2 border rounded-md bg-background"
                      value={podcastStyle}
                      onChange={(e) => setPodcastStyle(e.target.value)}
                    >
                      <option value="conversational">Conversational</option>
                      <option value="educational">Educational</option>
                      <option value="interview">Interview Style</option>
                      <option value="narrative">Narrative</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Duration</label>
                    <select 
                      className="w-full p-2 border rounded-md bg-background"
                      value={duration}
                      onChange={(e) => setDuration(e.target.value)}
                    >
                      <option value="auto">Auto (AI decides)</option>
                      <option value="5 minutes">5 minutes</option>
                      <option value="10 minutes">10 minutes</option>
                      <option value="15 minutes">15 minutes</option>
                      <option value="20 minutes">20 minutes</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Voice Type (Edge TTS)</label>
                    <select 
                      className="w-full p-2 border rounded-md bg-background"
                      value={voiceType}
                      onChange={(e) => setVoiceType(e.target.value)}
                    >
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="academic">Academic</option>
                      <option value="friendly">Friendly</option>
                    </select>
                  </div>
                  <div className="flex items-center space-x-2 pt-8">
                    <input 
                      type="checkbox" 
                      id="intro"
                      checked={includeIntro}
                      onChange={(e) => setIncludeIntro(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="intro" className="text-sm font-medium">Include intro/outro</label>
                  </div>
                </div>
              </div>

              <Button 
                onClick={handleGeneratePodcast}
                disabled={isGenerating || (!textInput.trim() && !selectedFile)}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white py-3 text-lg"
              >
                {isGenerating ? (
                  <>
                    <Clock className="h-5 w-5 mr-2 animate-spin" />
                    Generating AI Podcast...
                  </>
                ) : (
                  <>
                    <Mic className="h-5 w-5 mr-2" />
                    Generate AI Podcast
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Podcast Player Panel */}
          <Card className="shadow-xl border border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-6 w-6 text-purple-400" />
                AI Podcast Player
              </CardTitle>
              <CardDescription>
                Your AI-generated podcast with Gemini script and Edge TTS audio will appear here
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isGenerating ? (
                <div className="bg-gradient-to-br from-slate-700 to-slate-600 rounded-lg p-8 border border-slate-600">
                  <div className="text-center">
                    <div className="w-16 h-16 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-lg font-medium text-white">Generating your AI podcast...</p>
                    <p className="text-sm text-slate-300">This may take 2-4 minutes</p>
                    <div className="mt-4 space-y-2">
                      <div className="text-xs text-slate-400">
                        • Extracting text from PDF...
                      </div>
                      <div className="text-xs text-slate-400">
                        • Generating script with Gemini AI...
                      </div>
                      <div className="text-xs text-slate-400">
                        • Creating audio with Edge TTS...
                      </div>
                    </div>
                  </div>
                </div>
              ) : generatedPodcast ? (
                <div className="space-y-6">
                  {/* Podcast Metadata */}
                  <div className="bg-slate-700 rounded-lg p-4 space-y-2">
                    <h3 className="font-semibold text-white">{generatedPodcast.metadata.title}</h3>
                    <p className="text-sm text-slate-300">{generatedPodcast.metadata.description}</p>
                    {generatedPodcast.metadata.description.includes('🔊') && (
                      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-3 mt-2">
                        <p className="text-blue-200 text-sm">
                          <span className="text-blue-400">ℹ️ Audio Note:</span> This is placeholder audio with the correct duration. 
                          The full script is available in the transcript. Real TTS audio generation is temporarily unavailable.
                        </p>
                      </div>
                    )}
                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span>Duration: {generatedPodcast.metadata.duration}</span>
                      <span>Host: {generatedPodcast.metadata.host}</span>
                      <span>Generated with: Gemini AI + gTTS</span>
                    </div>
                  </div>

                  {/* Audio Player */}
                  <div className="bg-slate-700 rounded-lg p-6">
                    {/* Hidden Audio Element */}
                    <audio
                      ref={audioRef}
                      src={generatedPodcast.audioUrl}
                      preload="metadata"
                      className="hidden"
                    />
                    
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <Button
                          onClick={handlePlayPause}
                          size="lg"
                          className="rounded-full bg-purple-500 hover:bg-purple-600 p-3"
                          disabled={!generatedPodcast.audioUrl}
                        >
                          {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
                        </Button>
                        <div>
                          <p className="font-medium text-white">
                            {isPlaying ? 'Now Playing' : 'Ready to Play'}
                          </p>
                          <p className="text-sm text-slate-300">{generatedPodcast.metadata.title}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Volume2 className="h-4 w-4 text-slate-400" />
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={volume}
                          onChange={handleVolumeChange}
                          className="w-20 h-1 bg-slate-600 rounded-lg appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div 
                      className="w-full bg-slate-600 rounded-full h-2 mb-4 cursor-pointer"
                      onClick={handleSeek}
                    >
                      <div 
                        className="bg-purple-500 h-2 rounded-full transition-all duration-100 ease-out"
                        style={{ 
                          width: audioDuration > 0 ? `${(currentTime / audioDuration) * 100}%` : '0%' 
                        }}
                      ></div>
                    </div>
                    
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>{formatTime(currentTime)}</span>
                      <span>{formatTime(audioDuration)}</span>
                    </div>
                    
                    {/* Keyboard controls hint */}
                    <div className="mt-2 text-xs text-slate-500 text-center">
                      Keyboard: Space = Play/Pause, ← = -10s, → = +10s
                    </div>
                  </div>

                  {/* Topics Covered */}
                  <div className="space-y-2">
                    <h4 className="font-medium text-white">Topics Covered:</h4>
                    <div className="flex flex-wrap gap-2">
                      {generatedPodcast.metadata.topics.map((topic, index) => (
                        <span 
                          key={index}
                          className="bg-purple-900/30 text-purple-200 px-2 py-1 rounded text-xs"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <Button 
                      onClick={handleDownload}
                      disabled={!generatedPodcast.audioUrl}
                      className="flex-1 bg-purple-600 hover:bg-purple-700"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download MP3
                    </Button>
                    <Button 
                      onClick={handleDownloadScript}
                      variant="outline" 
                      className="flex-1"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Script
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-700 rounded-lg p-8 border border-slate-600">
                  <div className="text-center text-slate-400">
                    <Mic className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">No podcast generated yet</p>
                    <p className="text-sm">Upload content and click generate to create your AI podcast with Gemini + Edge TTS</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
