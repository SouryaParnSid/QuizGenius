"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileUpload } from "@/components/ui/file-upload"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Brain, Settings, Clock, Download, CheckCircle, Image, FileText, RotateCcw, AlertCircle } from "lucide-react"
import { generateQuizFromText, generateQuizFromFile, generateQuizFromImage, QuizQuestion } from "@/lib/gemini"

export function QuizGeneratorSection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [quizTitle, setQuizTitle] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedQuiz, setGeneratedQuiz] = useState<QuizQuestion[] | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{[key: number]: number}>({})
  const [error, setError] = useState<string | null>(null)
  const [numberOfQuestions, setNumberOfQuestions] = useState(5)
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard' | 'mixed'>('mixed')
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [showResults, setShowResults] = useState(false)

  const handleGenerateQuiz = async () => {
    if (!selectedFile) {
      alert("Please upload a PDF or image file")
      return
    }

    setIsGenerating(true)
    setError(null)
    
    try {
      let fileContent: string
      
      const options = {
        numberOfQuestions,
        difficulty,
        questionTypes: ['multiple-choice', 'true-false'] as ('multiple-choice' | 'true-false' | 'fill-blank')[]
      }

      let quiz: QuizQuestion[]
      
      if (selectedFile.type === 'application/pdf') {
        // Use advanced PDF extraction API
        console.log('Starting PDF extraction for:', selectedFile.name)
        fileContent = await extractPdfText(selectedFile)
        console.log('PDF extraction completed. Text length:', fileContent.length)
        console.log('Text preview:', fileContent.substring(0, 200))
        
        if (fileContent.length < 50) {
          throw new Error('PDF extraction returned insufficient text. Please try a different PDF file.')
        }
        
        quiz = await generateQuizFromText(fileContent, options)
      } else if (selectedFile.type.startsWith('image/')) {
        // For image files, we need to use Gemini Vision to read the text
        quiz = await generateQuizFromImage(selectedFile, options)
      } else {
        // For text files, use the old method
        fileContent = await readFileContent(selectedFile)
        quiz = await generateQuizFromText(fileContent, options)
      }
      
      setGeneratedQuiz(quiz)
      setCurrentQuestion(0)
      setSelectedAnswers({})
    } catch (error) {
      console.error('Quiz generation error:', error)
      setError(error instanceof Error ? error.message : 'Failed to generate quiz')
    } finally {
      setIsGenerating(false)
    }
  }

  const extractPdfText = async (file: File): Promise<string> => {
    try {
      // Check if we're in production environment
      const isProduction = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
      
      console.log('Starting PDF extraction...', {
        fileName: file.name,
        fileSize: file.size,
        isProduction
      })
      
      const formData = new FormData()
      formData.append('file', file)
      formData.append('method', 'auto') // Use auto method for best results
      // In production/Vercel, default to JavaScript extraction for reliability
      formData.append('usePython', isProduction ? 'false' : 'true')
      
      const response = await fetch('/api/extract-pdf', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        console.log('Python extraction failed, trying JavaScript fallback...')
        
        // Try JavaScript method as fallback
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
        
        if (!fallbackData.success || !fallbackData.text || fallbackData.text.length < 10) {
          throw new Error('PDF extraction returned insufficient text. The document might be scanned, encrypted, or contain only images.')
        }
        
        console.log('JavaScript fallback extraction successful:', {
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
      
      if (data.text.length < 50) {
        throw new Error('PDF extraction returned very little text. This might be a scanned document or contain mostly images. Please try a text-based PDF.')
      }
      
      console.log('PDF extraction successful:', {
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

  const readFileContent = async (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result
        if (typeof result === 'string') {
          // Clean up the content to focus on readable text
          let cleanContent = result
          
          // Remove obvious binary/metadata patterns
          cleanContent = cleanContent
            .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]/g, '') // Remove control characters
            .replace(/%PDF-[\d\.]+/g, '') // Remove PDF version info
            .replace(/\/[A-Za-z]+\s*\[[^\]]*\]/g, '') // Remove metadata arrays
            .replace(/\/[A-Za-z]+\s*\([^)]*\)/g, '') // Remove metadata parentheses
            .replace(/obj\s*\d+\s*\d+/g, '') // Remove object references
            .replace(/endobj/g, '')
            .replace(/stream[\s\S]*?endstream/g, '') // Remove binary streams
            .replace(/xref[\s\S]*?trailer/g, '') // Remove reference tables
            .replace(/\s+/g, ' ') // Normalize whitespace
            .trim()
          
          console.log('Original content length:', result.length)
          console.log('Cleaned content length:', cleanContent.length)
          console.log('Content preview:', cleanContent.substring(0, 200))
          
          if (cleanContent.length < 50) {
            reject(new Error('Document content appears to be mostly technical metadata. Please upload a document with readable text content.'))
            return
          }
          
          resolve(cleanContent)
        } else {
          reject(new Error('Failed to read file'))
        }
      }
      reader.onerror = () => reject(new Error('Error reading file'))
      reader.readAsText(file)
    })
  }

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleAnswerSelect = (questionId: number, answerIndex: number) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }))
  }

  const resetQuiz = () => {
    setSelectedAnswers({})
    setCurrentQuestion(0)
    setQuizCompleted(false)
    setShowResults(false)
  }

  const calculateScore = () => {
    if (!generatedQuiz) return { score: 0, total: 0, percentage: 0 }
    
    const correctAnswers = generatedQuiz.filter(
      (question) => selectedAnswers[question.id] === question.correctAnswer
    ).length
    
    const total = generatedQuiz.length
    const percentage = Math.round((correctAnswers / total) * 100)
    
    return { score: correctAnswers, total, percentage }
  }

  const completeQuiz = () => {
    setQuizCompleted(true)
    setShowResults(true)
  }

  const isQuizFullyAnswered = () => {
    if (!generatedQuiz) return false
    return generatedQuiz.every(q => selectedAnswers[q.id] !== undefined)
  }

  const exportResults = () => {
    if (!generatedQuiz || !quizCompleted) return
    
    const score = calculateScore()
    const timestamp = new Date().toLocaleString()
    
    const resultsData = {
      quizTitle: quizTitle || 'AI Generated Quiz',
      completedAt: timestamp,
      score: {
        correct: score.score,
        total: score.total,
        percentage: score.percentage
      },
      questions: generatedQuiz.map((question, index) => {
        const userAnswer = selectedAnswers[question.id]
        const isCorrect = userAnswer === question.correctAnswer
        
        return {
          questionNumber: index + 1,
          question: question.question,
          userAnswer: question.options[userAnswer] || 'Not answered',
          correctAnswer: question.options[question.correctAnswer],
          isCorrect,
          explanation: question.explanation || '',
          contentReference: question.contentReference || ''
        }
      })
    }
    
    // Export as JSON
    const exportAsJson = () => {
      const jsonString = JSON.stringify(resultsData, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `quiz-results-${Date.now()}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    
    // Export as CSV
    const exportAsCSV = () => {
      const csvHeaders = [
        'Question Number',
        'Question',
        'Your Answer',
        'Correct Answer',
        'Result',
        'Explanation'
      ]
      
      const csvRows = [
        csvHeaders.join(','),
        ...resultsData.questions.map(q => [
          q.questionNumber,
          `"${q.question.replace(/"/g, '""')}"`,
          `"${q.userAnswer.replace(/"/g, '""')}"`,
          `"${q.correctAnswer.replace(/"/g, '""')}"`,
          q.isCorrect ? 'Correct' : 'Incorrect',
          `"${q.explanation.replace(/"/g, '""')}"`
        ].join(','))
      ]
      
      const csvString = csvRows.join('\n')
      const blob = new Blob([csvString], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `quiz-results-${Date.now()}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    
    // Export as PDF (using HTML content)
    const exportAsPDF = () => {
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${resultsData.quizTitle} - Results</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
            .header { text-align: center; margin-bottom: 30px; }
            .score { background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }
            .question { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
            .correct { border-left: 4px solid #28a745; background: #f8fff9; }
            .incorrect { border-left: 4px solid #dc3545; background: #fff8f8; }
            .question-title { font-weight: bold; margin-bottom: 10px; }
            .answer { margin: 5px 0; }
            .explanation { margin-top: 10px; font-style: italic; color: #666; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${resultsData.quizTitle}</h1>
            <p>Completed on: ${resultsData.completedAt}</p>
          </div>
          
          <div class="score">
            <h2>Final Score: ${resultsData.score.percentage}%</h2>
            <p>${resultsData.score.correct} out of ${resultsData.score.total} questions correct</p>
          </div>
          
          <h3>Detailed Results:</h3>
          ${resultsData.questions.map(q => `
            <div class="question ${q.isCorrect ? 'correct' : 'incorrect'}">
              <div class="question-title">Question ${q.questionNumber}: ${q.question}</div>
              <div class="answer"><strong>Your Answer:</strong> ${q.userAnswer}</div>
              ${!q.isCorrect ? `<div class="answer"><strong>Correct Answer:</strong> ${q.correctAnswer}</div>` : ''}
              <div class="answer"><strong>Result:</strong> ${q.isCorrect ? '✓ Correct' : '✗ Incorrect'}</div>
              ${q.explanation ? `<div class="explanation"><strong>Explanation:</strong> ${q.explanation}</div>` : ''}
            </div>
          `).join('')}
        </body>
        </html>
      `
      
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `quiz-results-${Date.now()}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    
    // Show export options
    const exportFormat = prompt(
      'Choose export format:\n1. JSON (for developers)\n2. CSV (for spreadsheets)\n3. HTML (for viewing/printing)\n\nEnter 1, 2, or 3:'
    )
    
    switch(exportFormat) {
      case '1':
        exportAsJson()
        break
      case '2':
        exportAsCSV()
        break
      case '3':
        exportAsPDF()
        break
      default:
        // Default to CSV if no valid option selected
        exportAsCSV()
    }
  }

  return (
    <section id="quiz-creator" className="py-20 bg-slate-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            AI Quiz Generator
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Upload PDFs or images and instantly generate comprehensive quizzes with multiple question types 
            to test knowledge and reinforce learning
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Input Panel */}
          <Card className="shadow-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-6 w-6 text-purple-400" />
                Create Your Quiz
              </CardTitle>
              <CardDescription>
                Upload documents or images to generate intelligent quizzes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Quiz Title</label>
                <Input
                  placeholder="Enter a title for your quiz..."
                  value={quizTitle}
                  onChange={(e) => setQuizTitle(e.target.value)}
                  className="w-full"
                />
              </div>

              <Tabs defaultValue="pdf" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="pdf">PDF Upload</TabsTrigger>
                  <TabsTrigger value="image">Image Upload</TabsTrigger>
                </TabsList>
                
                <TabsContent value="pdf" className="mt-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Upload PDF Document
                    </label>
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      acceptedTypes={['application/pdf']}
                      maxSize={10}
                      placeholder="Upload your PDF document for quiz generation"
                    />
                  </div>
                </TabsContent>
                
                <TabsContent value="image" className="mt-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Upload Images
                    </label>
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      acceptedTypes={['image/jpeg', 'image/png', 'image/webp']}
                      maxSize={5}
                      placeholder="Upload images with text content"
                    />
                  </div>
                </TabsContent>
              </Tabs>

              {/* Quiz Settings */}
              <div className="border-t pt-6">
                <h4 className="flex items-center gap-2 font-medium mb-4">
                  <Settings className="h-4 w-4" />
                  Quiz Settings
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2 text-white">Questions</label>
                    <select 
                      className="w-full p-2 border border-slate-600 rounded-md bg-slate-700 text-white"
                      value={numberOfQuestions}
                      onChange={(e) => setNumberOfQuestions(Number(e.target.value))}
                    >
                      <option value={5}>5 questions</option>
                      <option value={10}>10 questions</option>
                      <option value={15}>15 questions</option>
                      <option value={20}>20 questions</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2 text-white">Difficulty</label>
                    <select 
                      className="w-full p-2 border border-slate-600 rounded-md bg-slate-700 text-white"
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value as 'easy' | 'medium' | 'hard' | 'mixed')}
                    >
                      <option value="mixed">Mixed</option>
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                    </select>
                  </div>
                </div>
              </div>

              <Button 
                onClick={handleGenerateQuiz}
                disabled={isGenerating || !selectedFile}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white py-3 text-lg"
              >
                {isGenerating ? (
                  <>
                    <Clock className="h-5 w-5 mr-2 animate-spin" />
                    Generating Quiz...
                  </>
                ) : (
                  <>
                    <Brain className="h-5 w-5 mr-2" />
                    Generate Interactive Quiz
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Quiz Preview/Taking Panel */}
          <Card className="shadow-xl border border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-6 w-6 text-emerald-400" />
                Quiz Preview
              </CardTitle>
              <CardDescription>
                Take your generated quiz here
              </CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="mb-6 p-4 bg-red-900/20 border border-red-500 rounded-lg flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
                  <div>
                    <p className="text-red-200 font-medium">Quiz Generation Failed</p>
                    <p className="text-red-300 text-sm">{error}</p>
                  </div>
                </div>
              )}
              
              {isGenerating ? (
                <div className="min-h-[400px] bg-gradient-to-br from-slate-700 to-slate-600 rounded-lg flex items-center justify-center border border-slate-600">
                  <div className="text-center">
                    <div className="w-16 h-16 border-4 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-lg font-medium text-white">Analyzing content with AI...</p>
                    <p className="text-sm text-slate-300">Using Gemini AI to generate personalized quiz questions</p>
                  </div>
                </div>
              ) : generatedQuiz ? (
                <div className="space-y-6">
                  {!showResults ? (
                    <>
                      <div className="flex justify-between items-center">
                        <h3 className="text-lg font-semibold">
                          Question {currentQuestion + 1} of {generatedQuiz.length}
                        </h3>
                        <div className="flex gap-2">
                          <Button onClick={resetQuiz} variant="outline" size="sm">
                            <RotateCcw className="h-4 w-4 mr-2" />
                            Reset
                          </Button>
                          {isQuizFullyAnswered() && (
                            <Button onClick={completeQuiz} size="sm" className="bg-green-600 hover:bg-green-700">
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Show Results
                            </Button>
                          )}
                        </div>
                      </div>

                      <div className="bg-slate-700 p-6 rounded-lg border border-slate-600">
                        <h4 className="text-lg font-medium mb-4 text-white">
                          {generatedQuiz[currentQuestion].question}
                        </h4>
                        
                        <div className="space-y-3">
                          {generatedQuiz[currentQuestion].options.map((option, index) => (
                            <button
                              key={index}
                              onClick={() => handleAnswerSelect(generatedQuiz[currentQuestion].id, index)}
                              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                                selectedAnswers[generatedQuiz[currentQuestion].id] === index
                                  ? 'bg-purple-500/20 border-purple-400 text-white'
                                  : 'bg-slate-600 border-slate-500 hover:bg-slate-500 text-slate-200'
                              }`}
                            >
                              <span className="font-medium mr-2">{String.fromCharCode(65 + index)}.</span>
                              {option}
                            </button>
                          ))}
                        </div>

                        {generatedQuiz[currentQuestion].contentReference && (
                          <div className="mt-4 p-3 bg-slate-600/50 rounded border-l-4 border-cyan-400">
                            <p className="text-sm text-slate-300">
                              <strong>Document Reference:</strong> {generatedQuiz[currentQuestion].contentReference}
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="flex justify-between">
                        <Button
                          onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                          disabled={currentQuestion === 0}
                          variant="outline"
                        >
                          Previous
                        </Button>
                        <div className="text-center">
                          <p className="text-sm text-slate-400">
                            Progress: {Object.keys(selectedAnswers).length} / {generatedQuiz.length} answered
                          </p>
                        </div>
                        <Button
                          onClick={() => setCurrentQuestion(Math.min(generatedQuiz.length - 1, currentQuestion + 1))}
                          disabled={currentQuestion === generatedQuiz.length - 1}
                        >
                          Next
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="space-y-6">
                      {/* Quiz Results */}
                      <div className="text-center">
                        <h3 className="text-2xl font-bold text-white mb-2">Quiz Completed!</h3>
                        <div className="inline-block p-6 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg border border-cyan-400/30">
                          <div className="text-4xl font-bold text-cyan-400 mb-2">
                            {calculateScore().percentage}%
                          </div>
                          <p className="text-lg text-white">
                            {calculateScore().score} out of {calculateScore().total} correct
                          </p>
                          <p className="text-sm text-slate-300 mt-2">
                            {calculateScore().percentage >= 80 ? '🎉 Excellent!' : 
                             calculateScore().percentage >= 60 ? '👍 Good job!' : 
                             '📚 Keep studying!'}
                          </p>
                        </div>
                      </div>

                      {/* Detailed Results */}
                      <div className="space-y-4">
                        <h4 className="text-lg font-semibold text-white">Review Your Answers:</h4>
                        {generatedQuiz.map((question, index) => {
                          const userAnswer = selectedAnswers[question.id]
                          const isCorrect = userAnswer === question.correctAnswer
                          
                          return (
                            <div key={question.id} className={`p-4 rounded-lg border ${
                              isCorrect ? 'bg-green-900/20 border-green-500' : 'bg-red-900/20 border-red-500'
                            }`}>
                              <div className="flex items-start gap-3">
                                {isCorrect ? 
                                  <CheckCircle className="h-5 w-5 text-green-400 mt-1 flex-shrink-0" /> :
                                  <AlertCircle className="h-5 w-5 text-red-400 mt-1 flex-shrink-0" />
                                }
                                <div className="flex-1">
                                  <p className="font-medium text-white mb-2">
                                    {index + 1}. {question.question}
                                  </p>
                                  <div className="text-sm space-y-1">
                                    <p className={isCorrect ? 'text-green-300' : 'text-red-300'}>
                                      Your answer: {question.options[userAnswer]}
                                    </p>
                                    {!isCorrect && (
                                      <p className="text-green-300">
                                        Correct answer: {question.options[question.correctAnswer]}
                                      </p>
                                    )}
                                    {question.explanation && (
                                      <p className="text-slate-300 mt-2">
                                        <strong>Explanation:</strong> {question.explanation}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>

                      <div className="flex gap-3">
                        <Button onClick={() => setShowResults(false)} variant="outline" className="flex-1">
                          Review Questions
                        </Button>
                        <Button onClick={resetQuiz} className="flex-1">
                          <RotateCcw className="h-4 w-4 mr-2" />
                          Retake Quiz
                        </Button>
                        <Button onClick={exportResults} variant="outline" className="flex-1">
                          <Download className="h-4 w-4 mr-2" />
                          Export Results
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="min-h-[400px] bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                  <div className="text-center text-slate-400">
                    <Image className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">No quiz generated yet</p>
                    <p className="text-sm">Upload a document or image to create your quiz</p>
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
