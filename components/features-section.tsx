"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  Zap, 
  Globe, 
  Shield, 
  BarChart3, 
  Palette, 
  Users, 
  Clock, 
  CheckCircle,
  Play,
  Brain,
  FileText,
  Image as ImageIcon
} from "lucide-react"

export function FeaturesSection() {
  const features = [
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Lightning Fast AI",
      description: "Generate videos and quizzes in minutes, not hours. Our advanced AI processes content at incredible speed.",
      color: "text-yellow-600"
    },
    {
      icon: <Play className="h-8 w-8" />,
      title: "Interactive Videos",
      description: "Create engaging educational videos with AI narration, visual aids, and dynamic presentations.",
      color: "text-blue-600"
    },
    {
      icon: <Brain className="h-8 w-8" />,
      title: "Smart Quiz Generation",
      description: "Automatically generate diverse question types from any content with intelligent difficulty adaptation.",
      color: "text-purple-600"
    },
    {
      icon: <FileText className="h-8 w-8" />,
      title: "Multi-Format Support",
      description: "Support for PDFs, images, text documents, and more. No format limitations.",
      color: "text-green-600"
    },
    {
      icon: <Palette className="h-8 w-8" />,
      title: "Customizable Content",
      description: "Tailor video styles, quiz difficulty, and presentation formats to match your needs.",
      color: "text-pink-600"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Learning Analytics",
      description: "Track progress, identify knowledge gaps, and optimize learning paths with detailed analytics.",
      color: "text-indigo-600"
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Collaborative Learning",
      description: "Share quizzes and videos with teams, track group progress, and enable collaborative learning.",
      color: "text-cyan-600"
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Secure & Private",
      description: "Enterprise-grade security ensures your content and data remain private and protected.",
      color: "text-red-600"
    },
    {
      icon: <Globe className="h-8 w-8" />,
      title: "Multi-Language Support",
      description: "Generate content in multiple languages with automatic translation and localization.",
      color: "text-orange-600"
    }
  ]

  const stats = [
    { number: "50M+", label: "Videos Generated" },
    { number: "200K+", label: "Active Users" },
    { number: "85%", label: "Learning Improvement" },
    { number: "24/7", label: "AI Availability" }
  ]

  return (
    <section id="features" className="py-20 bg-slate-900">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            Powerful Features for Modern Learning
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Everything you need to transform traditional content into engaging, 
            interactive learning experiences powered by cutting-edge AI technology
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-cyan-400 mb-2">
                {stat.number}
              </div>
              <div className="text-slate-300 font-medium">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={index} className="border border-slate-700 bg-slate-800 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="pb-4">
                <div className={`${feature.color} mb-4`}>
                  {feature.icon}
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-300">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* How It Works */}
        <div id="how-it-works" className="mt-20">
          <div className="text-center mb-12">
            <h3 className="text-2xl md:text-4xl font-bold text-white mb-4">
              How It Works
            </h3>
            <p className="text-lg text-slate-300">
              Transform your content in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-blue-400/30">
                <FileText className="h-8 w-8 text-cyan-400" />
              </div>
              <h4 className="text-xl font-semibold mb-4 text-white">1. Upload Content</h4>
              <p className="text-slate-300">
                Upload your PDFs, images, or paste text content. Our AI supports multiple formats and languages.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-purple-400/30">
                <Zap className="h-8 w-8 text-purple-400" />
              </div>
              <h4 className="text-xl font-semibold mb-4 text-white">2. AI Processing</h4>
              <p className="text-slate-300">
                Our advanced AI analyzes your content, extracts key concepts, and structures the information optimally.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-400/30">
                <CheckCircle className="h-8 w-8 text-emerald-400" />
              </div>
              <h4 className="text-xl font-semibold mb-4 text-white">3. Get Results</h4>
              <p className="text-slate-300">
                Receive polished videos and interactive quizzes ready for immediate use in your learning environment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
