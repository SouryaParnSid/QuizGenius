import { NextRequest, NextResponse } from 'next/server'
import { writeFile, unlink, mkdir } from 'fs/promises'
import { join } from 'path'
import { spawn } from 'child_process'
import { existsSync } from 'fs'

// TypeScript interface for PDF extraction results
interface ExtractionMetadata {
  method: string
  page_count?: number
  pages_with_text?: number
  total_characters?: number
  tables_found?: number
  best_method?: string
  error?: string
}

interface ExtractionResult {
  text: string
  metadata: ExtractionMetadata
  success: boolean
}

// Ensure uploads directory exists
async function ensureUploadsDir() {
  const uploadsDir = join(process.cwd(), 'uploads')
  if (!existsSync(uploadsDir)) {
    await mkdir(uploadsDir, { recursive: true })
  }
  return uploadsDir
}

// Function to run Python PDF extraction
async function runPythonExtraction(pdfPath: string, method: string = 'auto'): Promise<ExtractionResult> {
  return new Promise((resolve, reject) => {
    const scriptPath = join(process.cwd(), 'scripts', 'pdf_text_extractor.py')
    const pythonCommand = process.platform === 'win32' ? 'python' : 'python3'
    
    const args = [scriptPath, pdfPath, '--method', method]
    
    let stdoutData = ''
    let stderrData = ''
    
    const pythonProcess = spawn(pythonCommand, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' } // Fix encoding issues
    })
    
    pythonProcess.stdout.on('data', (data) => {
      stdoutData += data.toString('utf8')
    })
    
    pythonProcess.stderr.on('data', (data) => {
      stderrData += data.toString('utf8')
    })
    
    pythonProcess.on('close', async (code) => {
      if (code === 0) {
        try {
          // Read the generated text file
          const outputPath = pdfPath.replace('.pdf', '_extracted.txt')
          
          try {
            const { readFile } = await import('fs/promises')
            const extractedText = await readFile(outputPath, 'utf8')
            
            // Clean up the temporary extracted file
            try {
              const { unlink } = await import('fs/promises')
              await unlink(outputPath)
            } catch (cleanupError) {
              console.warn('Failed to cleanup extracted text file:', cleanupError)
            }
            
            resolve({
              text: extractedText,
              metadata: {
                method: 'Python (auto)',
                total_characters: extractedText.length,
                pages_with_text: extractedText.split('--- Page').length - 1
              },
              success: true
            })
          } catch (fileError) {
            // Fallback to stdout if file reading fails
            resolve({
              text: stdoutData,
              metadata: {
                method: 'Python (stdout)',
                total_characters: stdoutData.length,
                pages_with_text: 1
              },
              success: true
            })
          }
        } catch (error) {
          reject(new Error(`Failed to parse extraction result: ${error}`))
        }
      } else {
        // Clean stderr output for better error messages
        const cleanError = stderrData.replace(/[\u2713\u2717\u2022]/g, '').trim()
        reject(new Error(`Python extraction failed: ${cleanError || 'Unknown error'}`))
      }
    })
    
    pythonProcess.on('error', (error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })
  })
}

// JavaScript-based PDF extraction as fallback
async function extractTextWithJavaScript(buffer: Buffer): Promise<ExtractionResult> {
  try {
    // Try to use a simple PDF parsing approach
    const pdfContent = buffer.toString('binary')
    
    // Basic text extraction - look for text between stream markers
    const textRegex = /stream\s*([\s\S]*?)\s*endstream/g
    const matches = pdfContent.match(textRegex)
    
    let extractedText = ''
    if (matches) {
      for (const match of matches) {
        // Clean up the match
        const text = match
          .replace(/stream\s*/, '')
          .replace(/\s*endstream/, '')
          .replace(/[^\x20-\x7E\n\r\t]/g, '') // Keep only printable ASCII characters
          .trim()
        
        if (text.length > 10) { // Only include meaningful text chunks
          extractedText += text + '\n'
        }
      }
    }
    
    // If no text found via streams, try other patterns
    if (extractedText.length < 50) {
      // Look for text in a different pattern
      const altTextRegex = /\[([^\]]+)\]/g
      let match
      while ((match = altTextRegex.exec(pdfContent)) !== null) {
        const text = match[1].replace(/[^\x20-\x7E]/g, '').trim()
        if (text.length > 3) {
          extractedText += text + ' '
        }
      }
    }
    
    return {
      text: extractedText.trim(),
      metadata: {
        method: 'JavaScript (Basic)',
        total_characters: extractedText.length,
        pages_with_text: extractedText.length > 0 ? 1 : 0
      },
      success: extractedText.length > 0
    }
  } catch (error) {
    throw new Error(`JavaScript extraction failed: ${error}`)
  }
}

// Advanced JavaScript PDF extraction using pdf-parse
async function extractTextWithPdfParse(buffer: Buffer): Promise<ExtractionResult> {
  try {
    // Try to require pdf-parse using different approaches
    let pdfParse: any
    
    try {
      // First try direct require
      pdfParse = require('pdf-parse')
    } catch (e1) {
      try {
        // Try dynamic import
        const pdfParseModule = await import('pdf-parse')
        pdfParse = pdfParseModule.default || pdfParseModule
      } catch (e2) {
        throw new Error('pdf-parse not available. Install with: npm install pdf-parse')
      }
    }
    
    const data = await pdfParse(buffer)
    
    return {
      text: data.text,
      metadata: {
        method: 'pdf-parse',
        total_characters: data.text.length,
        pages_with_text: data.numpages,
        page_count: data.numpages
      },
      success: data.text.length > 0
    }
  } catch (error) {
    throw new Error(`pdf-parse extraction failed: ${error}`)
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const method = formData.get('method') as string || 'auto'
    const usePython = formData.get('usePython') === 'true'
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }
    
    if (file.type !== 'application/pdf') {
      return NextResponse.json({ error: 'File must be a PDF' }, { status: 400 })
    }
    
    // Convert file to buffer
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    
    let result: ExtractionResult
    
    if (usePython) {
      // Use Python-based extraction (more accurate)
      try {
        const uploadsDir = await ensureUploadsDir()
        const timestamp = Date.now()
        const fileName = `${timestamp}_${file.name}`
        const filePath = join(uploadsDir, fileName)
        
        // Save file temporarily
        await writeFile(filePath, buffer)
        
        try {
          result = await runPythonExtraction(filePath, method)
          console.log('Python extraction successful:', {
            method: result.metadata.method,
            textLength: result.text.length,
            success: result.success
          })
        } finally {
          // Clean up temporary file
          try {
            await unlink(filePath)
          } catch (error) {
            console.warn('Failed to delete temporary file:', error)
          }
        }
      } catch (pythonError) {
        console.warn('Python extraction failed, falling back to JavaScript:', pythonError)
        // Fall back to JavaScript extraction
        result = await extractTextWithFallback(buffer)
      }
    } else {
      // Use JavaScript-based extraction
      result = await extractTextWithFallback(buffer)
    }
    
    if (!result.success || result.text.length < 10) {
      return NextResponse.json(
        { 
          error: 'Failed to extract meaningful text from PDF. The file might be scanned, encrypted, or contain only images.',
          metadata: result.metadata 
        }, 
        { status: 422 }
      )
    }
    
    return NextResponse.json({
      text: result.text,
      metadata: result.metadata,
      success: true
    })
    
  } catch (error) {
    console.error('PDF extraction error:', error)
    return NextResponse.json(
      { error: `Failed to extract text from PDF: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
}

// Fallback extraction with multiple JavaScript methods
async function extractTextWithFallback(buffer: Buffer): Promise<ExtractionResult> {
  const methods = [
    { name: 'pdf-parse', fn: extractTextWithPdfParse },
    { name: 'JavaScript (Basic)', fn: extractTextWithJavaScript }
  ]
  
  let lastError: Error | null = null
  
  for (const method of methods) {
    try {
      const result = await method.fn(buffer)
      if (result.success && result.text.length > 10) {
        return result
      }
    } catch (error) {
      console.warn(`${method.name} failed:`, error)
      lastError = error instanceof Error ? error : new Error(String(error))
    }
  }
  
  throw lastError || new Error('All extraction methods failed')
}
