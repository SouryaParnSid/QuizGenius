"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FileUpload } from "@/components/ui/file-upload";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Brain, 
  Database, 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Settings, 
  ArrowLeft, 
  ArrowRight, 
  RotateCcw 
} from "lucide-react";
import { ragClient } from "@/lib/rag-client";

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correct_answer: number;
  type: string;
  explanation?: string;
  difficulty?: string;
}

export function RAGQuizGenerator() {
  const [activeTab, setActiveTab] = useState("upload");
  
  // RAG System State
  const [ragStatus, setRagStatus] = useState<"unknown" | "healthy" | "unhealthy">("unknown");
  const [documentsCount, setDocumentsCount] = useState(0);
  
  // Upload & Ingestion State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState("");
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestionSuccess, setIngestionSuccess] = useState<string | null>(null);
  
  // Quiz Generation State
  const [quizTopic, setQuizTopic] = useState("");
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedQuiz, setGeneratedQuiz] = useState<QuizQuestion[] | null>(null);
  
  // Quiz Taking State
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{[key: number]: number}>({});
  const [showResults, setShowResults] = useState(false);
  
  const [error, setError] = useState<string | null>(null);

  // Check RAG system health on component mount
  useEffect(() => {
    checkRAGHealth();
    loadDocumentsCount();
  }, []);

  const checkRAGHealth = async () => {
    try {
      const health = await ragClient.healthCheck();
      setRagStatus(health.status === "healthy" ? "healthy" : "unhealthy");
    } catch (error) {
      setRagStatus("unhealthy");
      console.error("RAG health check failed:", error);
    }
  };

  const loadDocumentsCount = async () => {
    try {
      const docs = await ragClient.listDocuments(1);
      setDocumentsCount(docs.count);
    } catch (error) {
      console.error("Failed to load document count:", error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file to upload");
      return;
    }

    setIsIngesting(true);
    setError(null);
    setIngestionSuccess(null);

    try {
      const result = await ragClient.ingestFile(selectedFile, 'recursive', {
        uploaded_via: 'quiz_generator',
        file_type: selectedFile.type,
        upload_time: new Date().toISOString()
      });

      if (result.success) {
        setIngestionSuccess(`Successfully ingested ${selectedFile.name}! Created ${result.documents_created} chunks.`);
        setSelectedFile(null);
        loadDocumentsCount();
      } else {
        setError(result.error || "Failed to ingest file");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to ingest file");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleTextUpload = async () => {
    if (!textInput.trim()) {
      setError("Please enter some text to upload");
      return;
    }

    setIsIngesting(true);
    setError(null);
    setIngestionSuccess(null);

    try {
      const result = await ragClient.ingestText(
        textInput,
        `text_input_${Date.now()}`,
        'recursive',
        {
          uploaded_via: 'quiz_generator',
          content_type: 'manual_text',
          upload_time: new Date().toISOString()
        }
      );

      if (result.success) {
        setIngestionSuccess(`Successfully ingested text! Created ${result.documents_created} chunks.`);
        setTextInput("");
        loadDocumentsCount();
      } else {
        setError(result.error || "Failed to ingest text");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to ingest text");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizTopic.trim()) {
      setError("Please enter a topic for the quiz");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const result = await ragClient.generateQuiz(quizTopic, {
        num_questions: numberOfQuestions,
        difficulty: difficulty,
        question_types: ['multiple-choice', 'true-false']
      });

      if (result.success) {
        // Parse the quiz JSON
        const quizData = JSON.parse(result.quiz);
        setGeneratedQuiz(quizData.questions);
        setCurrentQuestion(0);
        setSelectedAnswers({});
        setShowResults(false);
      } else {
        setError(result.error || "Failed to generate quiz");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to generate quiz");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAnswerSelect = (questionId: number, answerIndex: number) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: answerIndex
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestion < (generatedQuiz?.length || 0) - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleFinishQuiz = () => {
    setShowResults(true);
  };

  const calculateScore = () => {
    if (!generatedQuiz) return 0;
    let correct = 0;
    generatedQuiz.forEach((question) => {
      if (selectedAnswers[question.id] === question.correct_answer) {
        correct++;
      }
    });
    return Math.round((correct / generatedQuiz.length) * 100);
  };

  return (
    <section id="rag-quiz-creator" className="py-20 bg-slate-900">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            🧠 RAG-Powered Quiz Generator
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Upload documents to build your knowledge base, then generate intelligent quizzes 
            that leverage advanced retrieval-augmented generation for contextually accurate questions
          </p>
          
          {/* RAG Status */}
          <div className="flex justify-center items-center gap-6 mt-8 p-4 bg-slate-800/50 rounded-lg backdrop-blur-sm border border-slate-700 max-w-md mx-auto">
            <div className={`flex items-center gap-2 text-sm ${
              ragStatus === "healthy" 
                ? "text-green-400"
                : ragStatus === "unhealthy"
                ? "text-red-400" 
                : "text-slate-400"
            }`}>
              <div className={`w-3 h-3 rounded-full ${
                ragStatus === "healthy" ? "bg-green-500" : ragStatus === "unhealthy" ? "bg-red-500" : "bg-slate-500"
              }`} />
              RAG System: {ragStatus === "healthy" ? "Online" : ragStatus === "unhealthy" ? "Offline" : "Checking..."}
            </div>
            <div className="flex items-center gap-2 text-sm text-blue-400">
              <Database className="w-4 h-4" />
              Documents: {documentsCount}
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Input Panel */}
          <Card className="shadow-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Brain className="h-6 w-6 text-purple-400" />
                Intelligent Quiz Generation
              </CardTitle>
              <CardDescription className="text-slate-300">
                Upload documents to build your knowledge base, then generate contextual quizzes
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2 bg-slate-700/50">
                  <TabsTrigger value="upload" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white">
                    Upload
                  </TabsTrigger>
                  <TabsTrigger value="generate" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white">
                    Generate
                  </TabsTrigger>
                </TabsList>

                {/* Upload Tab */}
                <TabsContent value="upload" className="space-y-6">
                  <div className="space-y-6">
                    {/* File Upload */}
                    <div className="border border-slate-600 rounded-lg p-4 bg-slate-800/30">
                      <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                        <Upload className="w-5 h-5 text-purple-400" />
                        Upload Document
                      </h3>
                      <div className="space-y-4">
                        <FileUpload
                          onFileSelect={setSelectedFile}
                          acceptedTypes={[".pdf", ".docx", ".txt", ".md", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/markdown"]}
                          accept=".pdf,.docx,.txt,.md"
                          placeholder="Upload PDF, Word, or text files"
                        />
                        
                        {selectedFile && (
                          <div className="p-3 bg-blue-900/30 border border-blue-700 rounded-lg">
                            <p className="text-sm text-blue-300">
                              Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                            </p>
                          </div>
                        )}

                        <Button 
                          onClick={handleFileUpload} 
                          disabled={!selectedFile || isIngesting || ragStatus !== "healthy"}
                          className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                        >
                          {isIngesting ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Uploading...
                            </>
                          ) : (
                            <>
                              <Upload className="w-4 h-4 mr-2" />
                              Upload to Knowledge Base
                            </>
                          )}
                        </Button>
                      </div>
                    </div>

                    {/* Text Input */}
                    <div className="border border-slate-600 rounded-lg p-4 bg-slate-800/30">
                      <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-purple-400" />
                        Add Text Content
                      </h3>
                      <div className="space-y-4">
                        <Textarea
                          placeholder="Paste your text content here..."
                          value={textInput}
                          onChange={(e) => setTextInput(e.target.value)}
                          rows={6}
                          className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
                        />

                        <Button 
                          onClick={handleTextUpload} 
                          disabled={!textInput.trim() || isIngesting || ragStatus !== "healthy"}
                          className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                        >
                          {isIngesting ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Adding...
                            </>
                          ) : (
                            <>
                              <FileText className="w-4 h-4 mr-2" />
                              Add to Knowledge Base
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Status Messages */}
                  {ingestionSuccess && (
                    <div className="p-4 bg-green-900/30 border border-green-700 rounded-lg">
                      <div className="flex items-center gap-2 text-green-300">
                        <CheckCircle className="w-5 h-5" />
                        {ingestionSuccess}
                      </div>
                    </div>
                  )}
                </TabsContent>

                {/* Generate Tab */}
                <TabsContent value="generate" className="space-y-6">
                  <div className="border border-slate-600 rounded-lg p-4 bg-slate-800/30">
                    <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
                      <Settings className="w-5 h-5 text-purple-400" />
                      Quiz Generation Settings
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2 text-white">Quiz Topic</label>
                        <Input
                          placeholder="What topic should the quiz cover?"
                          value={quizTopic}
                          onChange={(e) => setQuizTopic(e.target.value)}
                          className="bg-slate-700/50 border-slate-600 text-white placeholder-slate-400"
                        />
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2 text-white">Number of Questions</label>
                          <Input
                            type="number"
                            min="1"
                            max="20"
                            value={numberOfQuestions}
                            onChange={(e) => setNumberOfQuestions(parseInt(e.target.value) || 5)}
                            className="bg-slate-700/50 border-slate-600 text-white"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2 text-white">Difficulty</label>
                          <select 
                            className="w-full p-2 border border-slate-600 rounded-md bg-slate-700 text-white"
                            value={difficulty}
                            onChange={(e) => setDifficulty(e.target.value as 'easy' | 'medium' | 'hard')}
                          >
                            <option value="easy">Easy</option>
                            <option value="medium">Medium</option>
                            <option value="hard">Hard</option>
                          </select>
                        </div>
                      </div>

                      <Button 
                        onClick={handleGenerateQuiz} 
                        disabled={!quizTopic.trim() || isGenerating || ragStatus !== "healthy" || documentsCount === 0}
                        className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                        size="lg"
                      >
                        {isGenerating ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Generating Quiz...
                          </>
                        ) : (
                          <>
                            <Brain className="w-4 h-4 mr-2" />
                            Generate Quiz with AI
                          </>
                        )}
                      </Button>

                      {documentsCount === 0 && (
                        <div className="p-4 bg-yellow-900/30 border border-yellow-700 rounded-lg">
                          <div className="flex items-center gap-2 text-yellow-300">
                            <AlertCircle className="w-5 h-5" />
                            Upload documents first to build your knowledge base
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Results Panel */}
          <Card className="shadow-xl border border-slate-700 bg-gradient-to-br from-slate-800 to-slate-700 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Brain className="h-6 w-6 text-green-400" />
                Quiz Results
              </CardTitle>
              <CardDescription className="text-slate-300">
                Your generated quiz and results appear here
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Generated Quiz Display */}
              {generatedQuiz && generatedQuiz.length > 0 ? (
                <div className="space-y-6">
                  {!showResults ? (
                    // Quiz Taking Mode
                    <div className="space-y-6">
                      <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium text-white">
                          Question {currentQuestion + 1} of {generatedQuiz.length}
                        </h3>
                        <div className="text-sm text-slate-300">
                          Progress: {Math.round(((currentQuestion + 1) / generatedQuiz.length) * 100)}%
                        </div>
                      </div>

                      <div className="border border-slate-600 rounded-lg p-6 bg-slate-800/50">
                        <h4 className="text-xl font-medium text-white mb-4">
                          {generatedQuiz[currentQuestion]?.question}
                        </h4>
                        
                        <div className="space-y-3">
                          {generatedQuiz[currentQuestion]?.options?.map((option: string, index: number) => (
                            <button
                              key={index}
                              onClick={() => handleAnswerSelect(generatedQuiz[currentQuestion].id, index)}
                              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                                selectedAnswers[generatedQuiz[currentQuestion].id] === index
                                  ? 'border-purple-500 bg-purple-900/30 text-purple-300'
                                  : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                              }`}
                            >
                              <span className="font-medium mr-3">{String.fromCharCode(65 + index)}.</span>
                              {option}
                            </button>
                          ))}
                        </div>

                        <div className="flex justify-between mt-6">
                          <Button
                            onClick={handlePreviousQuestion}
                            disabled={currentQuestion === 0}
                            variant="outline"
                            className="border-slate-600 text-slate-300 hover:bg-slate-700"
                          >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Previous
                          </Button>
                          
                          {currentQuestion === generatedQuiz.length - 1 ? (
                            <Button
                              onClick={handleFinishQuiz}
                              disabled={!selectedAnswers[generatedQuiz[currentQuestion].id] && selectedAnswers[generatedQuiz[currentQuestion].id] !== 0}
                              className="bg-green-600 hover:bg-green-700 text-white"
                            >
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Finish Quiz
                            </Button>
                          ) : (
                            <Button
                              onClick={handleNextQuestion}
                              disabled={!selectedAnswers[generatedQuiz[currentQuestion].id] && selectedAnswers[generatedQuiz[currentQuestion].id] !== 0}
                              className="bg-purple-600 hover:bg-purple-700 text-white"
                            >
                              Next
                              <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    // Results Display Mode
                    <div className="space-y-6">
                      <div className="text-center">
                        <h3 className="text-2xl font-bold text-white mb-2">Quiz Complete!</h3>
                        <p className="text-lg text-slate-300">Your Score: {calculateScore()}%</p>
                      </div>

                      <div className="space-y-4">
                        {generatedQuiz.map((question, index) => {
                          const userAnswer = selectedAnswers[question.id];
                          const isCorrect = userAnswer === question.correct_answer;
                          
                          return (
                            <div key={question.id} className={`p-4 rounded-lg border ${
                              isCorrect ? 'border-green-600 bg-green-900/20' : 'border-red-600 bg-red-900/20'
                            }`}>
                              <h4 className="font-medium mb-2 text-white">
                                {index + 1}. {question.question}
                              </h4>
                              
                              <div className="text-sm space-y-1">
                                <p className={`${isCorrect ? 'text-green-400' : 'text-red-400'}`}>
                                  Your answer: {question.options[userAnswer]} {isCorrect ? '✓' : '✗'}
                                </p>
                                {!isCorrect && (
                                  <p className="text-green-400">
                                    Correct answer: {question.options[question.correct_answer]}
                                  </p>
                                )}
                                {question.explanation && (
                                  <p className="text-slate-300 mt-2">
                                    <strong>Explanation:</strong> {question.explanation}
                                  </p>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      <div className="flex gap-4">
                        <Button
                          onClick={() => {
                            setShowResults(false);
                            setCurrentQuestion(0);
                          }}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                        >
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Retake Quiz
                        </Button>
                        <Button
                          onClick={() => {
                            setGeneratedQuiz(null);
                            setActiveTab("generate");
                            setShowResults(false);
                          }}
                          className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                        >
                          Generate New Quiz
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                // Empty State
                <div className="text-center py-12">
                  <Brain className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-xl font-medium text-white mb-2">No Quiz Generated Yet</h3>
                  <p className="text-slate-400 mb-6">
                    Upload documents and generate a quiz to get started!
                  </p>
                  <Button
                    onClick={() => setActiveTab("generate")}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    Generate Quiz
                  </Button>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg">
                  <div className="flex items-center gap-2 text-red-300">
                    <AlertCircle className="w-5 h-5" />
                    {error}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}
