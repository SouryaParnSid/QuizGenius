import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'
import { writeFile, unlink, mkdir } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

interface TTSOptions {
  voice: string
  rate: string
  pitch: string
  volume: string
}

// Map voice types to gTTS language/accent combinations
const VOICE_MAPPING = {
  'professional': { lang: 'en', tld: 'com' }, // US English
  'casual': { lang: 'en', tld: 'co.uk' },     // UK English  
  'academic': { lang: 'en', tld: 'com.au' },  // Australian English
  'friendly': { lang: 'en', tld: 'ca' }       // Canadian English
}

async function ensureAudioDir() {
  const audioDir = join(process.cwd(), 'public', 'audio')
  if (!existsSync(audioDir)) {
    await mkdir(audioDir, { recursive: true })
  }
  return audioDir
}

export async function POST(request: NextRequest) {
  try {
    const { text, options }: { text: string; options: TTSOptions } = await request.json()

    if (!text || text.length === 0) {
      return NextResponse.json({ error: 'No text provided' }, { status: 400 })
    }

    // Clean text for TTS (remove markdown, special characters)
    const cleanText = text
      .replace(/\[PAUSE\]/g, ' ')
      .replace(/\[EMPHASIS\]/g, '')
      .replace(/\[SLOW\]/g, '')
      .replace(/\[EXCITED\]/g, '')
      .replace(/\*/g, '')
      .replace(/#{1,6}\s/g, '')
      .replace(/[^\w\s.,!?;:'"-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()

    if (cleanText.length > 10000) {
      return NextResponse.json({ 
        error: 'Text too long for TTS. Maximum 10,000 characters.' 
      }, { status: 400 })
    }

    console.log('Generating TTS audio...', {
      textLength: cleanText.length,
      voice: options.voice
    })

    const audioDir = await ensureAudioDir()
    const fileName = `podcast_${Date.now()}.mp3`
    const outputPath = join(audioDir, fileName)

    // Use gTTS via Python
    const voiceSettings = VOICE_MAPPING[options.voice as keyof typeof VOICE_MAPPING] || { lang: 'en', tld: 'com' }
    
    try {
      // Check if we're in a development environment and TTS is available
      const isLocalDev = process.env.NODE_ENV === 'development'
      
      if (isLocalDev) {
        console.log('Attempting gTTS generation...')
        await generateWithGTTS(cleanText, voiceSettings, outputPath)
        
        const audioUrl = `/audio/${fileName}`
        
        // Clean up old files (optional)
        setTimeout(async () => {
          try {
            await unlink(outputPath)
          } catch (error) {
            console.warn('Failed to cleanup audio file:', error)
          }
        }, 300000) // Delete after 5 minutes

        return NextResponse.json({
          success: true,
          audioUrl,
          duration: estimateDuration(cleanText),
          voice: `gTTS ${voiceSettings.lang}-${voiceSettings.tld}`
        })
      } else {
        // In production, skip TTS and use fallback
        throw new Error('TTS service not available in production environment')
      }

    } catch (ttsError) {
      console.log('gTTS unavailable, using enhanced fallback:', ttsError instanceof Error ? ttsError.message : String(ttsError))
      
      // Enhanced fallback: Return a professional fallback response
      const fallbackAudio = generateFallbackAudio(cleanText.length)
      
      return NextResponse.json({
        success: true,
        audioUrl: fallbackAudio,
        duration: estimateDuration(cleanText),
        voice: 'Text-to-Speech Unavailable',
        warning: 'TTS service temporarily unavailable. Full transcript available for download.',
        message: 'The podcast script has been generated successfully. Audio synthesis is temporarily unavailable, but you can read the full transcript below.'
      })
    }

  } catch (error) {
    console.error('TTS error:', error)
    return NextResponse.json(
      { error: `TTS generation failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
}

async function generateWithGTTS(text: string, voiceSettings: { lang: string; tld: string }, outputPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    // Use gTTS Python package
    const pythonCommand: string = process.platform === 'win32' ? 'python' : 'python3'
    
    const args = [
      '-c',
      `
from gtts import gTTS
import sys
import os

def main():
    try:
        text = """${text.replace(/"/g, '\\"')}"""
        output = "${outputPath.replace(/\\/g, '\\\\')}"
        lang = "${voiceSettings.lang}"
        tld = "${voiceSettings.tld}"
        
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        
        # Save to file
        tts.save(output)
        
        # Verify file was created
        if os.path.exists(output) and os.path.getsize(output) > 0:
            print("TTS_SUCCESS")
        else:
            print("TTS_ERROR: File not created or empty")
            sys.exit(1)
            
    except Exception as e:
        print(f"TTS_ERROR: {e}")
        sys.exit(1)

main()
      `
    ]

    let stdout = ''
    let stderr = ''

    const pythonProcess = spawn(pythonCommand, args, {
      stdio: ['pipe', 'pipe', 'pipe']
    })

    pythonProcess.stdout.on('data', (data: Buffer) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on('data', (data: Buffer) => {
      stderr += data.toString()
    })

    pythonProcess.on('close', (code: number | null) => {
      if (code === 0 && stdout.includes('TTS_SUCCESS')) {
        resolve()
      } else {
        reject(new Error(`gTTS failed: ${stderr || stdout}`))
      }
    })

    pythonProcess.on('error', (error: Error) => {
      reject(new Error(`Failed to start Python process: ${error.message}`))
    })

    // Timeout after 30 seconds
    setTimeout(() => {
      pythonProcess.kill()
      reject(new Error('TTS generation timeout'))
    }, 30000)
  })
}

function estimateDuration(text: string): string {
  // Estimate ~150 words per minute for speech
  const words = text.split(/\s+/).length
  const minutes = Math.ceil(words / 150)
  return `${minutes}:00`
}

function generateFallbackAudio(textLength: number): string {
  // Generate a simple audio data URL for fallback
  // This creates a short silence/beep sound
  const duration = Math.min(textLength / 50, 60) // Max 60 seconds
  const sampleRate = 22050
  const samples = Math.floor(duration * sampleRate)
  
  // Create a simple sine wave or silence
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
  
  // Generate silence
  for (let i = 0; i < samples; i++) {
    view.setInt16(44 + i * 2, 0, true)
  }
  
  // Convert to base64
  const bytes = new Uint8Array(buffer)
  const binary = Array.from(bytes, byte => String.fromCharCode(byte)).join('')
  return `data:audio/wav;base64,${btoa(binary)}`
}
