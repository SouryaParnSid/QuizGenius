import { GoogleGenerativeAI } from '@google/generative-ai'

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY
const genAI = new GoogleGenerativeAI(API_KEY || '')

export interface QuizQuestion {
  id: number
  question: string
  options: string[]
  correctAnswer: number
  type: 'multiple-choice' | 'true-false' | 'fill-blank'
  explanation?: string
  contentReference?: string
}

export interface QuizGenerationOptions {
  numberOfQuestions: number
  difficulty: 'easy' | 'medium' | 'hard' | 'mixed'
  questionTypes: ('multiple-choice' | 'true-false' | 'fill-blank')[]
}

export async function generateQuizFromText(
  content: string, 
  options: QuizGenerationOptions
): Promise<QuizQuestion[]> {
  try {
    if (!API_KEY) {
      throw new Error('Gemini API key is not configured. Please set NEXT_PUBLIC_GEMINI_API_KEY in your environment variables.')
    }
    
    console.log('API Key available:', API_KEY ? 'Yes' : 'No')
    
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' })
    
    // First, let's analyze what kind of content we have
    const contentPreview = content.substring(0, 500)
    console.log('Content preview:', contentPreview)
    
    const prompt = `
You are an expert quiz generator. I will provide you with document content, and you must create quiz questions ONLY about the actual information contained in that content.

DOCUMENT CONTENT TO ANALYZE:
"""
${content}
"""

CRITICAL RULES - FOLLOW EXACTLY:
1. READ the content above carefully and identify what it's actually about
2. IGNORE any technical metadata, file format information, or encoding details
3. ONLY create questions about the SUBSTANTIVE CONTENT (the actual information, topics, concepts, data, facts, or subject matter)
4. If the content appears to be mostly technical/metadata, respond with an error

BEFORE creating questions, analyze:
- What is the main topic or subject of this content?
- What are the key facts, concepts, or information presented?
- What would someone learn from reading this content?

QUIZ REQUIREMENTS:
- Generate exactly ${options.numberOfQuestions} questions
- Difficulty: ${options.difficulty}
- Types: ${options.questionTypes.join(', ')}
- Base ALL questions on actual content information
- Each question must test understanding of what the document teaches/explains

FORBIDDEN TOPICS (DO NOT ask about):
- File formats (PDF, PNG, etc.)
- Technical specifications
- Creation dates or metadata
- Software or encoding details
- File structure information

IMPORTANT: You MUST respond with ONLY valid JSON in this exact format. Do not include any explanatory text before or after the JSON.

{
  "questions": [
    {
      "id": 1,
      "question": "According to the content, [specific question about the actual subject matter]",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": 0,
      "type": "multiple-choice",
      "explanation": "The content states: [specific reference to the actual information]",
      "contentReference": "Direct quote or reference from the meaningful content"
    }
  ]
}

CRITICAL: Return ONLY the JSON object above, no additional text, no markdown formatting, no explanations.
`

    const result = await model.generateContent(prompt)
    const response = await result.response
    const text = response.text()
    
    console.log('Raw Gemini response:', text)
    
    // Try to extract JSON from the response with multiple strategies
    let parsedResponse
    
    // Strategy 1: Look for JSON wrapped in code blocks
    let jsonMatch = text.match(/```json\s*(\{[\s\S]*?\})\s*```/)
    if (jsonMatch) {
      try {
        parsedResponse = JSON.parse(jsonMatch[1])
      } catch (e) {
        console.log('Failed to parse JSON from code block')
      }
    }
    
    // Strategy 2: Look for any JSON object in the response
    if (!parsedResponse) {
      jsonMatch = text.match(/\{[\s\S]*\}/)
      if (jsonMatch) {
        try {
          // Try to clean up the JSON by finding the balanced braces
          const jsonStr = jsonMatch[0]
          let braceCount = 0
          let endIndex = 0
          
          for (let i = 0; i < jsonStr.length; i++) {
            if (jsonStr[i] === '{') braceCount++
            if (jsonStr[i] === '}') braceCount--
            if (braceCount === 0) {
              endIndex = i + 1
              break
            }
          }
          
          const cleanJson = jsonStr.substring(0, endIndex)
          parsedResponse = JSON.parse(cleanJson)
        } catch (e) {
          console.log('Failed to parse JSON with brace matching')
        }
      }
    }
    
    // Strategy 3: If still no valid JSON, create fallback questions
    if (!parsedResponse) {
      console.log('No valid JSON found, creating fallback questions')
      console.log('Raw response:', text.substring(0, 1000))
      
      // Try to create basic questions from the content
      const contentWords = content.trim().split(/\s+/)
      if (contentWords.length < 10) {
        throw new Error('Content is too short to generate meaningful questions. Please upload a document with more substantial text content.')
      }
      
      // Create a simple fallback question
      const fallbackQuestions: QuizQuestion[] = [{
        id: 1,
        question: "Based on the uploaded content, what type of document was this?",
        options: ["Text document", "Educational material", "Reference document", "Other"],
        correctAnswer: 1,
        type: "multiple-choice" as const,
        explanation: "This question is based on the content analysis of your uploaded document.",
        contentReference: "Document content analysis"
      }]
      
      return fallbackQuestions
    }
    
    const finalResponse = parsedResponse
    
    if (!finalResponse.questions || !Array.isArray(finalResponse.questions)) {
      throw new Error(`Invalid response format. Expected questions array, got: ${JSON.stringify(finalResponse)}`)
    }
    
    if (finalResponse.questions.length === 0) {
      throw new Error('No questions were generated. The content might not contain sufficient information for quiz generation.')
    }
    
    return finalResponse.questions.map((q: any, index: number) => ({
      id: index + 1,
      question: q.question || `Question ${index + 1}`,
      options: q.options || (q.type === 'true-false' ? ['True', 'False'] : ['Option A', 'Option B', 'Option C', 'Option D']),
      correctAnswer: q.correctAnswer || 0,
      type: q.type || 'multiple-choice',
      explanation: q.explanation || 'No explanation provided',
      contentReference: q.contentReference || 'No reference provided'
    }))
    
  } catch (error) {
    console.error('Error generating quiz:', error)
    throw new Error(`Failed to generate quiz: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

export async function generateQuizFromImage(
  imageFile: File,
  options: QuizGenerationOptions
): Promise<QuizQuestion[]> {
  try {
    if (!API_KEY) {
      throw new Error('Gemini API key is not configured. Please set NEXT_PUBLIC_GEMINI_API_KEY in your environment variables.')
    }
    
    console.log('Processing image file:', imageFile.name)
    
    // Convert image to base64
    const imageBase64 = await fileToBase64(imageFile)
    
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' })
    
    const prompt = `
You are analyzing an image that contains text content. Your task is to:

1. FIRST: Read and extract ALL text content visible in this image
2. SECOND: Create ${options.numberOfQuestions} quiz questions based ONLY on the text content you can see

CRITICAL INSTRUCTIONS:
- Read the image carefully and identify all text content
- ONLY create questions about information explicitly shown in the image text
- DO NOT make up questions about topics not visible in the image
- Focus on the actual subject matter and content shown
- Ignore any technical image information (file format, etc.)

QUIZ REQUIREMENTS:
- Generate exactly ${options.numberOfQuestions} questions
- Difficulty: ${options.difficulty}
- Types: ${options.questionTypes.join(', ')}
- Base questions on the actual text content visible in the image

Response format (JSON only):
{
  "questions": [
    {
      "id": 1,
      "question": "Based on the text in the image, [question about actual content]",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correctAnswer": 0,
      "type": "multiple-choice",
      "explanation": "The image text states: [reference to specific text from image]",
      "contentReference": "Quote from the visible text in the image"
    }
  ]
}

VALIDATION: Each question must be about text content that is actually visible and readable in the image.
`

    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          data: imageBase64.split(',')[1], // Remove data:image/... prefix
          mimeType: imageFile.type
        }
      }
    ])
    
    const response = await result.response
    const text = response.text()
    
    console.log('Gemini vision response:', text)
    
    // Extract JSON from the response
    const jsonMatch = text.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
      throw new Error('No valid JSON found in response')
    }
    
    const parsedResponse = JSON.parse(jsonMatch[0])
    
    if (!parsedResponse.questions || !Array.isArray(parsedResponse.questions)) {
      throw new Error('Invalid response format')
    }
    
    return parsedResponse.questions.map((q: any, index: number) => ({
      id: index + 1,
      question: q.question,
      options: q.options || (q.type === 'true-false' ? ['True', 'False'] : []),
      correctAnswer: q.correctAnswer,
      type: q.type,
      explanation: q.explanation,
      contentReference: q.contentReference
    }))
    
  } catch (error) {
    console.error('Error generating quiz from image:', error)
    throw new Error(`Failed to generate quiz from image: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

// Helper function to convert file to base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result)
      } else {
        reject(new Error('Failed to convert file to base64'))
      }
    }
    reader.onerror = reject
  })
}

export async function generateQuizFromFile(
  fileContent: string,
  fileName: string,
  options: QuizGenerationOptions
): Promise<QuizQuestion[]> {
  try {
    return generateQuizFromText(fileContent, options)
  } catch (error) {
    console.error('Error generating quiz from file:', error)
    throw error
  }
}
