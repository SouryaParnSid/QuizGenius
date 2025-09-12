# 🎙️ Podcast Generator Setup Guide

This guide will help you set up the AI Podcast Generator feature in QuizGenius, which uses **Gemini AI** for script generation and **Edge TTS** for high-quality text-to-speech conversion.

## 🚀 Features

- **Advanced PDF Extraction**: Same robust system as the quiz generator
- **AI Script Generation**: Uses Gemini AI to create engaging podcast scripts
- **Professional TTS**: Edge TTS for natural-sounding audio
- **Multiple Voice Styles**: Professional, casual, academic, friendly
- **Customizable Settings**: Duration, style, intro/outro options
- **Fallback System**: Works even if TTS service is unavailable

## 📋 Prerequisites

1. **Gemini API Key**: Already configured (same as quiz generator)
2. **Python 3.7+**: For Edge TTS (local development only)
3. **Node.js Environment**: For the Next.js application

## 🛠️ Setup Instructions

### 1. Install Python Dependencies (Local Development)

For local development with high-quality TTS:

```bash
# Install Edge TTS
pip install edge-tts>=6.1.9

# Or use the requirements file
pip install -r scripts/requirements-tts.txt
```

### 2. Test TTS Setup

Run the setup verification script:

```bash
python scripts/setup_tts.py
```

This will:
- ✅ Check Python version compatibility
- ✅ Verify Edge TTS installation
- ✅ Test audio generation
- ✅ List available voices

### 3. Environment Configuration

Your existing `.env.local` should already have:

```env
NEXT_PUBLIC_GEMINI_API_KEY=your_gemini_api_key_here
```

No additional environment variables needed!

## 🎯 How It Works

### 1. PDF Processing
- Uses the same advanced extraction system as quiz generator
- Supports Python (local) and JavaScript (production) fallbacks
- Handles complex PDFs with high accuracy

### 2. Script Generation
- **Gemini AI** analyzes content and creates engaging podcast scripts
- Customizable style (conversational, educational, interview, narrative)
- Natural speech patterns with emphasis cues
- Structured segments with timestamps

### 3. Audio Generation
- **Edge TTS** converts script to high-quality audio
- Multiple voice options based on style selection
- Fallback to silent audio if TTS unavailable
- Production-ready streaming

## 🎨 Voice Options

| Style | Voice | Description |
|-------|--------|-------------|
| Professional | Jenny Neural | Clear, authoritative delivery |
| Casual | Guy Neural | Relaxed, friendly approach |
| Academic | Aria Neural | Scholarly, detailed presentation |
| Friendly | Davis Neural | Warm, encouraging tone |

## 🌐 Production Deployment

### Vercel Deployment

The podcast generator works seamlessly in production:

1. **Script Generation**: Always uses Gemini AI (cloud-based)
2. **PDF Extraction**: Uses JavaScript fallback (no Python needed)
3. **TTS**: Falls back to silent audio with transcript available
4. **Zero Additional Config**: Works with existing Vercel setup

### Local vs Production

| Feature | Local Development | Production |
|---------|------------------|------------|
| PDF Extraction | Python + JS fallback | JavaScript only |
| Script Generation | Gemini AI | Gemini AI |
| TTS Audio | Edge TTS + fallback | Fallback audio |
| User Experience | Full audio + transcript | Transcript + placeholder audio |

## 🧪 Testing

### Test PDF Upload
1. Upload a PDF document
2. Configure podcast settings
3. Click "Generate AI Podcast"
4. Verify script generation and audio creation

### Test Text Input
1. Paste educational content
2. Customize title and settings
3. Generate podcast
4. Check audio quality and transcript

## 🔧 Troubleshooting

### Common Issues

**"TTS service unavailable"**
- Edge TTS not installed or Python not found
- Solution: Install Edge TTS or use fallback mode

**"Failed to generate podcast script"**
- Gemini API key missing or invalid
- Solution: Check environment variables

**"PDF extraction failed"**
- File too large or corrupted
- Solution: Use smaller PDF or text input

### Debug Commands

```bash
# Test TTS installation
python -c "import edge_tts; print('TTS available')"

# Test Gemini connection
curl -X POST http://localhost:3000/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{"content":"Test content","options":{"style":"conversational"}}'
```

## 🆕 What's New

### Gemini Integration
- **Advanced Script Generation**: Creates natural, engaging podcast content
- **Style Customization**: Multiple podcast formats and tones
- **Structured Output**: Organized segments with timestamps
- **Topic Extraction**: Automatic identification of key themes

### Edge TTS Integration
- **High-Quality Audio**: Professional-grade text-to-speech
- **Multiple Voices**: Different personalities and styles
- **Natural Speech**: Proper pacing, emphasis, and intonation
- **Production Ready**: Optimized for web delivery

### Enhanced UI
- **Real-time Progress**: Shows generation steps and status
- **Audio Player**: Built-in podcast player with controls
- **Metadata Display**: Title, duration, topics, and description
- **Download Options**: MP3 audio and full transcript

## 🚀 Usage Tips

1. **Optimal Content Length**: 500-3000 words work best for podcasts
2. **Clear Structure**: Well-organized content generates better scripts
3. **Descriptive Titles**: Help Gemini create more engaging content
4. **Style Selection**: Choose based on your audience and content type
5. **Duration Settings**: "Auto" usually provides optimal length

## 🔮 Future Enhancements

- Multiple speaker support (conversations)
- Background music integration
- Advanced voice customization
- Podcast RSS feed generation
- Analytics and listening metrics

---

**Ready to create engaging podcasts from your documents!** 🎙️✨

