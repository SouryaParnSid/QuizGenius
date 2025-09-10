"use client"

import { Button } from "@/components/ui/button"
import { Play, BookOpen, Brain, Sparkles } from "lucide-react"
import { Header } from "./header"

export function QuizGeniusHero() {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      <Header />
      
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-32 w-96 h-96 bg-cyan-400 rounded-full opacity-10 blur-3xl" />
        <div className="absolute -bottom-40 -left-32 w-96 h-96 bg-blue-400 rounded-full opacity-10 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-blue-500/20 text-cyan-300 px-4 py-2 rounded-full text-sm font-medium mb-8 border border-cyan-500/30">
            <Sparkles className="h-4 w-4" />
            AI-Powered Learning Revolution
          </div>

          {/* Main headline */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
            Transform Content into
            <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              Interactive Learning
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            Upload PDFs, text, or images and let our AI create engaging educational videos 
            and personalized quizzes that boost learning retention by up to 85%
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Button 
              onClick={() => scrollToSection('video-generator')}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-8 py-4 text-lg rounded-full shadow-lg transform transition-all hover:scale-105"
            >
              <Play className="h-5 w-5 mr-2" />
              Create Learning Video
            </Button>
            <Button 
              onClick={() => scrollToSection('quiz-creator')}
              variant="outline" 
              className="border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-slate-900 px-8 py-4 text-lg rounded-full transition-all hover:scale-105 bg-slate-800/50 backdrop-blur-sm"
            >
              <Brain className="h-5 w-5 mr-2" />
              Generate Quiz
            </Button>
          </div>

          {/* Feature highlights */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-blue-400/30">
                <Play className="h-8 w-8 text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                AI Video Generation
              </h3>
              <p className="text-slate-300">
                Transform any text or PDF into engaging educational videos with narration and visuals
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-purple-400/30">
                <Brain className="h-8 w-8 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Smart Quiz Creation
              </h3>
              <p className="text-slate-300">
                Generate interactive quizzes from PDFs and images with multiple question types
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-400/30">
                <BookOpen className="h-8 w-8 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Personalized Learning
              </h3>
              <p className="text-slate-300">
                Adaptive content that adjusts to learning styles and knowledge levels
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
