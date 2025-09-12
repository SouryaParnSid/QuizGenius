import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

const API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY
const genAI = new GoogleGenerativeAI(API_KEY || '')

export interface PodcastOptions {
  style: 'conversational' | 'educational' | 'interview' | 'narrative'
  duration: string
  voiceType: 'professional' | 'casual' | 'academic' | 'friendly'
  includeIntro: boolean
  title?: string
}

export interface PodcastScript {
  title: string
  description: string
  duration: string
  script: string
  segments: PodcastSegment[]
  topics: string[]
}

export interface PodcastSegment {
  type: 'intro' | 'content' | 'transition' | 'outro'
  text: string
  timestamp: string
  voice_settings?: {
    speed: number
    pitch: number
    emphasis: string[]
  }
}

export async function POST(request: NextRequest) {
  try {
    const { content, options }: { content: string; options: PodcastOptions } = await request.json()

    if (!API_KEY) {
      return NextResponse.json(
        { error: 'Gemini API key is not configured. Please set NEXT_PUBLIC_GEMINI_API_KEY in your environment variables.' },
        { status: 500 }
      )
    }

    if (!content || content.length < 100) {
      return NextResponse.json(
        { error: 'Content is too short. Please provide at least 100 characters of content for podcast generation.' },
        { status: 400 }
      )
    }

    console.log('Generating podcast script with Gemini AI...', {
      contentLength: content.length,
      style: options.style,
      duration: options.duration
    })

    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' })

    const prompt = `
You are an expert podcast script writer and educational content creator. Create an engaging, educational podcast script based on the provided content.

CONTENT TO TRANSFORM INTO PODCAST:
"""
${content}
"""

PODCAST REQUIREMENTS:
- Style: ${options.style}
- Duration: ${options.duration}
- Voice Type: ${options.voiceType}
- Include Intro/Outro: ${options.includeIntro}
- Title: ${options.title || 'Educational Podcast'}

SCRIPT GUIDELINES:
1. CREATE A FULL-LENGTH EDUCATIONAL PODCAST SCRIPT (minimum 1000-1500 words for proper ${options.duration} duration)
2. EXPAND on the provided content - don't just summarize it, elaborate with examples, explanations, and detailed discussion
3. Use natural, conversational language that's easy to follow when spoken aloud
4. Include engaging hooks, smooth transitions, and clear explanations
5. Break down complex topics into digestible segments with detailed explanations
6. Add natural pauses, emphasis cues, and speaking directions
7. Make it sound like a professional educational podcast host who takes time to explain concepts thoroughly

DETAILED STRUCTURE REQUIREMENTS FOR ${options.duration} PODCAST:
${options.includeIntro ? '- INTRO (2-3 minutes): Engaging hook, topic introduction, what listeners will learn, personal welcome' : ''}
- MAIN CONTENT (${options.duration === 'auto' ? '8-12' : parseInt(options.duration.split(' ')[0]) - 2} minutes): 
  * Deep dive into each major concept from the content
  * Multiple examples and real-world applications  
  * Detailed explanations that expand beyond the source material
  * Conversational elaboration on key points
  * Questions and answers to engage the listener
- TRANSITIONS: Smooth bridges between topics with preview of what's coming next
- Include natural speech patterns (pauses, emphasis, conversational phrases)
- Add speaking cues like [PAUSE], [EMPHASIS], [SLOW], [EXCITED] where appropriate
${options.includeIntro ? '- OUTRO (1-2 minutes): Comprehensive summary, key takeaways, call-to-action, thank you' : ''}

MINIMUM WORD COUNT TARGET: ${options.duration === 'auto' ? '1200-1800' : Math.max(parseInt(options.duration.split(' ')[0]) * 180, 900)} words
(This ensures proper speaking duration - average 150-180 words per minute)

VOICE AND TONE FOR "${options.voiceType}" STYLE:
${options.voiceType === 'professional' ? '- Professional, authoritative, clear and polished delivery' :
  options.voiceType === 'casual' ? '- Relaxed, friendly, approachable with personal anecdotes' :
  options.voiceType === 'academic' ? '- Scholarly, detailed, methodical with precise terminology' :
  '- Warm, encouraging, supportive with simple explanations'}

CRITICAL: Return ONLY a valid JSON object with this exact structure:

{
  "title": "Engaging podcast title based on the content",
  "description": "Brief description of what listeners will learn",
  "duration": "Estimated duration based on script length",
  "script": "Complete podcast script with speaking cues and natural flow",
  "segments": [
    {
      "type": "intro|content|transition|outro",
      "text": "Script text for this segment",
      "timestamp": "0:00-2:30",
      "voice_settings": {
        "speed": 1.0,
        "pitch": 0,
        "emphasis": ["key", "words", "to", "emphasize"]
      }
    }
  ],
  "topics": ["key", "topic", "list", "covered", "in", "podcast"]
}

CRITICAL REQUIREMENTS: 
- The script MUST be substantial enough to fill the requested duration (${options.duration})
- DON'T just summarize - EXPAND, ELABORATE, and DISCUSS the content in detail
- Include multiple examples, analogies, and real-world applications
- Make the script sound natural when spoken aloud with conversational flow
- Include [PAUSE] markers for natural breathing spots
- Add [EMPHASIS] markers for important points
- Use conversational transitions between ideas
- Keep sentences at reasonable length for speech
- Make it educational but engaging and listenable
- If the source content is brief, elaborate extensively with related concepts and detailed explanations
`

    const result = await model.generateContent(prompt)
    const response = await result.response
    const text = response.text()

    console.log('Raw Gemini response length:', text.length)

    // Parse the JSON response with multiple strategies
    let podcastScript: PodcastScript
    
    try {
      // Strategy 1: Direct JSON parse
      podcastScript = JSON.parse(text)
    } catch (e1) {
      try {
        // Strategy 2: Extract JSON from code blocks
        const jsonMatch = text.match(/```json\s*(\{[\s\S]*?\})\s*```/)
        if (jsonMatch) {
          podcastScript = JSON.parse(jsonMatch[1])
        } else {
          // Strategy 3: Extract any JSON object
          const objectMatch = text.match(/\{[\s\S]*\}/)
          if (objectMatch) {
            podcastScript = JSON.parse(objectMatch[0])
          } else {
            throw new Error('No valid JSON found in response')
          }
        }
      } catch (e2) {
        console.error('Failed to parse Gemini response:', text.substring(0, 500))
        return NextResponse.json(
          { error: 'Failed to parse AI response. Please try again.' },
          { status: 500 }
        )
      }
    }

    // Validate the response structure
    if (!podcastScript.title || !podcastScript.script || !podcastScript.segments) {
      console.error('Invalid response structure:', podcastScript)
      return NextResponse.json(
        { error: 'Invalid response structure from AI. Please try again.' },
        { status: 500 }
      )
    }

    // Ensure we have topics
    if (!podcastScript.topics || podcastScript.topics.length === 0) {
      // Extract topics from content if not provided
      const words = content.toLowerCase().split(/\s+/)
      const commonWords = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those']
      const significantWords = words.filter(word => word.length > 4 && !commonWords.includes(word))
      podcastScript.topics = [...new Set(significantWords)].slice(0, 5)
    }

    console.log('Podcast script generated successfully:', {
      title: podcastScript.title,
      segmentsCount: podcastScript.segments.length,
      scriptLength: podcastScript.script.length,
      topics: podcastScript.topics.length
    })

    return NextResponse.json({
      success: true,
      podcastScript
    })

  } catch (error) {
    console.error('Podcast generation error:', error)
    return NextResponse.json(
      { 
        error: `Failed to generate podcast script: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: error instanceof Error ? error.stack : undefined
      },
      { status: 500 }
    )
  }
}

