# Advanced PDF Text Extraction Setup Guide

This guide will help you set up the advanced PDF text extraction functionality for your QuizGenius application. The system uses a multi-layered approach with Python-based extraction for maximum accuracy and JavaScript fallbacks.

## Overview

The PDF extraction system provides:
- **4 extraction methods**: PyMuPDF, pdfplumber, pypdf, and OCR
- **Automatic fallback**: If Python fails, JavaScript methods are used
- **High accuracy**: Handles complex layouts, tables, and scanned documents
- **Smart method selection**: Automatically chooses the best extraction method

## Quick Start

### Option 1: JavaScript-Only (Basic Setup)
If you just want basic PDF extraction without Python dependencies:

1. Install the JavaScript PDF parser:
```bash
npm install pdf-parse
```

2. Your application will work with JavaScript-based PDF extraction (fallback mode).

### Option 2: Full Setup with Python (Recommended)
For the best PDF extraction quality, set up Python dependencies:

## Prerequisites

- **Node.js** 18+ (already installed)
- **Python** 3.7+ 
- **npm** or **yarn**

## Installation Steps

### 1. Install JavaScript Dependencies

```bash
npm install pdf-parse
```

### 2. Install Python and Dependencies

#### Windows
1. **Install Python**:
   - Download Python from https://python.org
   - **Important**: Check "Add Python to PATH" during installation

2. **Install Python PDF libraries**:
```cmd
pip install -r scripts/requirements.txt
```

3. **Install Tesseract OCR** (for scanned PDFs):
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH

#### macOS
1. **Install Python** (if not already installed):
```bash
brew install python
```

2. **Install Python PDF libraries**:
```bash
pip3 install -r scripts/requirements.txt
```

3. **Install Tesseract OCR**:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)
1. **Install Python** (usually pre-installed):
```bash
sudo apt update
sudo apt install python3 python3-pip
```

2. **Install Python PDF libraries**:
```bash
pip3 install -r scripts/requirements.txt
```

3. **Install Tesseract OCR**:
```bash
sudo apt install tesseract-ocr
```

### 3. Verify Installation

Run this command to test your setup:

```bash
python scripts/pdf_text_extractor.py --help
```

If successful, you should see the help message for the PDF extractor.

## Testing the Integration

### Test with a Sample PDF

1. **Create a test file**: Place any PDF file in your project root
2. **Test extraction**: 
```bash
python scripts/pdf_text_extractor.py your-test-file.pdf --compare-methods
```
3. **Check results**: The script will show which methods work and their accuracy

### Test in Your Application

1. **Start your Next.js application**:
```bash
npm run dev
```

2. **Navigate to the quiz generator section**
3. **Upload a PDF file**
4. **Check the browser console** for extraction method information

## How It Works

### Extraction Flow

1. **Upload PDF** → Next.js receives file
2. **API Route** (`/api/extract-pdf`) processes the file
3. **Python extraction** is attempted first (if available)
4. **JavaScript fallback** if Python fails
5. **Best result** is returned to the quiz generator

### Method Priority

The system tries methods in this order:

1. **PyMuPDF** - Fastest, works for most PDFs
2. **pdfplumber** - Best for complex layouts and tables
3. **pypdf** - Lightweight fallback
4. **OCR (Tesseract)** - For scanned/image-based PDFs
5. **JavaScript (pdf-parse)** - Browser-based fallback

## Troubleshooting

### Common Issues

#### "Python not found"
- **Windows**: Reinstall Python and check "Add to PATH"
- **macOS/Linux**: Install Python 3.7+
- **Alternative**: Use JavaScript-only mode

#### "No module named 'fitz'"
```bash
pip install PyMuPDF
```

#### "Tesseract not found"
- Install Tesseract OCR for your OS
- Add to system PATH
- **Note**: OCR is optional, other methods will still work

#### "PDF extraction failed"
- Check file is a valid PDF
- Try with a different PDF file
- Check browser console for specific errors

### Debug Mode

Enable verbose logging in the Python script:
```bash
python scripts/pdf_text_extractor.py your-file.pdf --verbose
```

## Advanced Configuration

### Custom Extraction Settings

You can modify the extraction behavior in `/api/extract-pdf/route.ts`:

- **Change method priority**
- **Adjust fallback behavior**
- **Add custom preprocessing**

### Performance Optimization

For better performance:
- **PyMuPDF**: Fastest for simple PDFs
- **pdfplumber**: Use for documents with tables
- **OCR**: Only for scanned documents (slowest)

## File Structure

```
quizgenius/
├── scripts/
│   ├── pdf_text_extractor.py    # Main Python extraction script
│   └── requirements.txt         # Python dependencies
├── app/api/extract-pdf/
│   └── route.ts                 # Next.js API endpoint
└── components/
    └── quiz-generator-section.tsx  # Updated component
```

## Environment Variables

No additional environment variables are required. The system automatically detects available Python installations and libraries.

## Supported File Types

- **PDF files** (.pdf) - All versions
- **Encrypted PDFs** - Limited support
- **Scanned PDFs** - Requires Tesseract OCR
- **Image-based PDFs** - OCR extraction

## Limitations

- **File size**: Recommended max 16MB per PDF
- **Language**: OCR optimized for English (can be configured)
- **Complex layouts**: Some complex PDFs may need manual processing

## Getting Help

If you encounter issues:

1. **Check the console** for specific error messages
2. **Test with simple PDFs** first
3. **Verify Python installation** with `python --version`
4. **Check dependencies** with `pip list`

The system is designed to be robust - even if Python setup fails, basic PDF extraction will still work through JavaScript fallbacks.
