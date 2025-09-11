# QuizGenius Vercel Deployment Guide

This guide will help you deploy your QuizGenius application to Vercel with advanced PDF text extraction capabilities.

## 🚀 Quick Deploy

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy from your project root:**
```bash
vercel
```

### Option 2: Deploy via GitHub + Vercel Dashboard

1. **Push to GitHub** (if not already done)
2. **Connect to Vercel** at [vercel.com](https://vercel.com)
3. **Import your repository**
4. **Configure environment variables** (see below)

## ⚙️ Environment Variables Setup

Your application needs the **Gemini API key** to function. Set this up in Vercel:

### Via Vercel Dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add:
   - **Key**: `NEXT_PUBLIC_GEMINI_API_KEY`
   - **Value**: Your Gemini API key
   - **Environment**: Production, Preview, Development

### Via Vercel CLI:
```bash
vercel env add NEXT_PUBLIC_GEMINI_API_KEY
```

## 📋 Pre-Deployment Checklist

✅ **Files Updated for Vercel:**
- `vercel.json` - Configured with function timeouts and memory limits
- `app/api/extract-pdf/route.ts` - Updated for serverless environment
- `components/quiz-generator-section.tsx` - Production-optimized extraction

✅ **Dependencies Installed:**
- `pdf-parse` - For JavaScript PDF extraction in production
- All other Next.js dependencies

✅ **Environment Variables:**
- `NEXT_PUBLIC_GEMINI_API_KEY` - Required for quiz generation

## 🔧 Deployment Configuration

### Vercel Settings (`vercel.json`):
```json
{
  "functions": {
    "app/api/extract-pdf/route.ts": {
      "maxDuration": 60,
      "memory": 1024
    }
  }
}
```

### Build Settings:
- **Framework**: Next.js (auto-detected)
- **Build Command**: `npm run build` (default)
- **Install Command**: `npm install` (default)
- **Node.js Version**: 18.x (recommended)

## 🎯 How PDF Extraction Works in Production

### Local Development:
- **Primary**: Python-based extraction (PyMuPDF, pdfplumber, etc.)
- **Fallback**: JavaScript pdf-parse
- **Last Resort**: Basic JavaScript extraction

### Vercel Production:
- **Primary**: JavaScript pdf-parse library
- **Fallback**: Basic JavaScript extraction
- **Note**: Python extraction is disabled in serverless environment

## 📊 Expected Performance

### PDF Extraction Quality:
- **Simple PDFs**: Excellent (JavaScript handles most cases well)
- **Complex layouts**: Good (pdf-parse is quite capable)
- **Scanned PDFs**: Limited (no OCR in production, consider preprocessing)

### Performance Metrics:
- **Function timeout**: 60 seconds (configured)
- **Memory limit**: 1024MB (configured)
- **Cold start**: ~2-3 seconds first time
- **Warm requests**: ~500ms-2s depending on PDF size

## 🚀 Deployment Steps

### Step 1: Final Checks
```bash
# Ensure everything builds locally
npm run build

# Test PDF extraction locally
npm run dev
# Upload a test PDF in the quiz generator
```

### Step 2: Deploy to Vercel
```bash
# If using CLI
vercel

# Follow the prompts:
# ? Set up and deploy "quizgenius"? [Y/n] y
# ? Which scope? [your-account]
# ? Link to existing project? [y/N] n
# ? What's your project's name? quizgenius
# ? In which directory is your code located? ./
```

### Step 3: Configure Environment Variables
```bash
# Add your Gemini API key
vercel env add NEXT_PUBLIC_GEMINI_API_KEY
# Enter your actual API key when prompted
```

### Step 4: Redeploy with Environment Variables
```bash
vercel --prod
```

## 🔍 Testing Your Deployment

### 1. Basic Functionality Test:
- Visit your deployed URL
- Navigate to the quiz generator section
- Upload a simple PDF
- Verify quiz generation works

### 2. PDF Extraction Test:
- Try different PDF types:
  - Text-based PDFs ✅ (should work well)
  - PDFs with tables ✅ (good support)
  - Image-heavy PDFs ⚠️ (limited, text only)
  - Scanned PDFs ❌ (will show error, expected)

### 3. Performance Test:
- Check function logs in Vercel dashboard
- Monitor execution time and memory usage
- Verify fallback mechanisms work

## 🐛 Troubleshooting

### Common Issues:

#### "API key not configured"
**Solution**: Ensure `NEXT_PUBLIC_GEMINI_API_KEY` is set in Vercel environment variables

#### "Failed to extract text from PDF"
**Cause**: PDF might be scanned or image-based
**Solution**: Use text-based PDFs for best results

#### "Function timeout"
**Cause**: Large PDF or slow processing
**Solution**: PDFs are automatically limited to prevent timeouts

#### "Memory limit exceeded"
**Cause**: Very large PDF files
**Solution**: Reduce PDF file size or use smaller files

### Debug Tools:

1. **Vercel Function Logs:**
   - Go to Vercel dashboard
   - Navigate to your project
   - Check "Functions" tab for logs

2. **Browser Console:**
   - Open developer tools
   - Check console for extraction progress
   - Look for specific error messages

3. **Test Endpoints:**
   ```bash
   # Test PDF extraction directly
   curl -X POST https://your-app.vercel.app/api/extract-pdf \
     -F "file=@test.pdf" \
     -F "usePython=false"
   ```

## 📈 Optimization Tips

### For Better Performance:
1. **Use text-based PDFs** (not scanned documents)
2. **Keep PDFs under 5MB** for faster processing
3. **Simple layouts** work better than complex designs
4. **Modern PDF formats** have better text extraction

### For Better Reliability:
1. **Test with various PDF types** before going live
2. **Monitor Vercel function logs** for issues
3. **Set up error tracking** (optional: Sentry, LogRocket)
4. **Consider PDF preprocessing** for complex documents

## 🎉 Post-Deployment

### Success Checklist:
- ✅ Application loads without errors
- ✅ Quiz generator interface works
- ✅ PDF upload and processing successful
- ✅ Quiz questions generated from PDF content
- ✅ All interactive features working

### Next Steps:
1. **Share your deployment** - Your QuizGenius is now live!
2. **Monitor usage** - Check Vercel analytics
3. **Collect feedback** - Test with real users
4. **Scale as needed** - Upgrade Vercel plan if necessary

## 📞 Support

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review Vercel logs** for specific errors
3. **Test locally first** to isolate issues
4. **Check PDF file compatibility** with text-based documents

Your QuizGenius application is now ready for the world! 🌟
