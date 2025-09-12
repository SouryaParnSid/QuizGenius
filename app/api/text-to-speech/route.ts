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
    let cleanText = text
      .replace(/\[PAUSE\]/g, ' ')
      .replace(/\[EMPHASIS\]/g, '')
      .replace(/\[SLOW\]/g, '')
      .replace(/\[EXCITED\]/g, '')
      .replace(/\*/g, '')
      .replace(/#{1,6}\s/g, '')
      .replace(/[^\w\s.,!?;:'"-]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()

    // Split long text into smaller chunks for better TTS processing
    if (cleanText.length > 5000) {
      console.log('Long text detected, splitting for better TTS processing...')
      // For very long text, truncate to first 5000 characters for better performance
      cleanText = cleanText.substring(0, 5000) + "... [Content continues in full transcript]"
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
      // Always try TTS first, regardless of environment
      // This allows TTS to work in development and potentially in production
      console.log('Attempting gTTS generation...')
      await generateWithGTTS(cleanText, voiceSettings, outputPath)
      
      const audioUrl = `/audio/${fileName}`
      
      // Clean up old files after reasonable time
      setTimeout(async () => {
        try {
          await unlink(outputPath)
        } catch (error) {
          console.warn('Failed to cleanup audio file:', error)
        }
      }, 1800000) // Delete after 30 minutes (longer for better UX)

      return NextResponse.json({
        success: true,
        audioUrl,
        duration: estimateDuration(cleanText),
        voice: `gTTS ${voiceSettings.lang}-${voiceSettings.tld}`,
        message: 'High-quality TTS audio generated successfully!'
      })

    } catch (ttsError) {
      console.log('gTTS unavailable, using enhanced fallback:', ttsError instanceof Error ? ttsError.message : String(ttsError))
      
      // Enhanced fallback: Return a professional fallback response
      const fallbackAudio = generateFallbackAudio(cleanText.length)
      
      return NextResponse.json({
        success: true,
        audioUrl: fallbackAudio,
        duration: estimateDuration(text), // Use original text length for duration
        voice: 'Placeholder Audio',
        warning: 'Audio synthesis temporarily unavailable - using placeholder audio.',
        message: 'Generated placeholder audio with correct duration. You can read the full transcript or try regenerating for TTS audio.',
        isFallback: true
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

    // Timeout after 60 seconds (extended for better reliability)
    setTimeout(() => {
      pythonProcess.kill()
      reject(new Error('TTS generation timeout'))
    }, 60000)
  })
}

function estimateDuration(text: string): string {
  // Estimate ~150 words per minute for speech
  const words = text.split(/\s+/).length
  const minutes = Math.ceil(words / 150)
  return `${minutes}:00`
}

function generateFallbackAudio(textLength: number): string {
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
    const amplitude = 0.15 // 15% volume - clearly audible but not harsh
    
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
