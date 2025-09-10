"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { FileUpload } from "@/components/ui/file-upload"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Play, Wand2, Settings, Clock, Download, FileText } from "lucide-react"

export function VideoGeneratorSection() {
  const [textInput, setTextInput] = useState("")
  const [videoTitle, setVideoTitle] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVideo, setGeneratedVideo] = useState<string | null>(null)

  const handleGenerateVideo = async () => {
    if (!textInput.trim() && !selectedFile) {
      alert("Please provide text content or upload a PDF file")
      return
    }

    setIsGenerating(true)
    
    // Simulate video generation process
    setTimeout(() => {
      setGeneratedVideo("https://example.com/generated-video.mp4")
      setIsGenerating(false)
    }, 3000)
  }

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  return (
    <section id="video-generator" className="py-20 bg-slate-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            AI Video Generator
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Transform your content into engaging educational videos with AI-powered narration, 
            visual aids, and dynamic presentations
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Input Panel */}
          <Card className="shadow-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="h-6 w-6 text-cyan-400" />
                Create Your Video
              </CardTitle>
              <CardDescription>
                Upload a PDF or enter text content to generate an educational video
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Video Title</label>
                <Input
                  placeholder="Enter a title for your video..."
                  value={videoTitle}
                  onChange={(e) => setVideoTitle(e.target.value)}
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
                      Content for Video Generation
                    </label>
                    <Textarea
                      placeholder="Paste your educational content here... The AI will analyze your text and create an engaging video with narration, visual aids, and structured presentation."
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
                      maxSize={10}
                      placeholder="Upload your PDF document"
                    />
                  </div>
                </TabsContent>
              </Tabs>

              {/* Video Settings */}
              <div className="border-t pt-6">
                <h4 className="flex items-center gap-2 font-medium mb-4">
                  <Settings className="h-4 w-4" />
                  Video Settings
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Duration</label>
                    <select className="w-full p-2 border rounded-md bg-background">
                      <option>Auto (AI decides)</option>
                      <option>5 minutes</option>
                      <option>10 minutes</option>
                      <option>15 minutes</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Voice</label>
                    <select className="w-full p-2 border rounded-md bg-background">
                      <option>Professional (Default)</option>
                      <option>Casual</option>
                      <option>Academic</option>
                      <option>Friendly</option>
                    </select>
                  </div>
                </div>
              </div>

              <Button 
                onClick={handleGenerateVideo}
                disabled={isGenerating || (!textInput.trim() && !selectedFile)}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white py-3 text-lg"
              >
                {isGenerating ? (
                  <>
                    <Clock className="h-5 w-5 mr-2 animate-spin" />
                    Generating Video...
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 mr-2" />
                    Generate Educational Video
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Preview/Output Panel */}
          <Card className="shadow-xl border border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-6 w-6 text-cyan-400" />
                Video Preview
              </CardTitle>
              <CardDescription>
                Your generated video will appear here
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isGenerating ? (
                <div className="aspect-video bg-gradient-to-br from-slate-700 to-slate-600 rounded-lg flex items-center justify-center border border-slate-600">
                  <div className="text-center">
                    <div className="w-16 h-16 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-lg font-medium text-white">Generating your video...</p>
                    <p className="text-sm text-slate-300">This may take 1-3 minutes</p>
                  </div>
                </div>
              ) : generatedVideo ? (
                <div className="space-y-4">
                  <div className="aspect-video bg-black rounded-lg flex items-center justify-center">
                    <div className="text-center text-white">
                      <Play className="h-16 w-16 mx-auto mb-4 opacity-70" />
                      <p className="text-lg">Video Generated Successfully!</p>
                      <p className="text-sm opacity-70">Click to play your educational video</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button className="flex-1">
                      <Play className="h-4 w-4 mr-2" />
                      Play Video
                    </Button>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="aspect-video bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                  <div className="text-center text-slate-400">
                    <FileText className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">No video generated yet</p>
                    <p className="text-sm">Upload content and click generate to create your video</p>
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
