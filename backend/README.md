# High-Accuracy PDF Text Extractor

A comprehensive Python script for extracting text from PDF files with high accuracy using multiple extraction methods and libraries.

## Features

✨ **Multiple Extraction Methods**: Uses 4 different libraries for optimal results
- **PyMuPDF (fitz)**: Fast and efficient for most PDFs
- **pdfplumber**: Excellent for complex layouts and tables
- **pypdf**: Lightweight fallback option
- **Tesseract OCR**: For scanned PDFs and image-based text

🎯 **High Accuracy**: Automatically selects the best method or compares all methods
📊 **Table Extraction**: Detects and extracts tables from PDFs
🔍 **Smart Fallback**: If one method fails, others are tried automatically
📋 **Detailed Reporting**: Generate comprehensive extraction reports
🖥️ **Command Line Interface**: Easy to use from terminal
🛡️ **Error Handling**: Robust error handling and validation

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for scanned PDFs)

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH environment variable

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

## Quick Start

### Basic Usage

```bash
# Extract text using the best available method
python pdf_text_extractor.py document.pdf

# Use a specific method
python pdf_text_extractor.py document.pdf --method pymupdf

# Compare all methods and generate report
python pdf_text_extractor.py document.pdf --compare-methods --save-report
```

### Python Code Usage

```python
from pdf_text_extractor import PDFTextExtractor

# Initialize extractor
extractor = PDFTextExtractor("document.pdf")

# Get best extraction automatically
text, metadata = extractor.get_best_extraction()
print(f"Extracted {len(text)} characters using {metadata['best_method']}")

# Try specific method
text, metadata = extractor.extract_with_pdfplumber()

# Compare all methods
all_results = extractor.extract_all_methods()
```

## Command Line Options

```bash
python pdf_text_extractor.py [PDF_FILE] [OPTIONS]

Arguments:
  PDF_FILE              Path to the PDF file

Options:
  --method {auto,pymupdf,pdfplumber,pypdf,ocr}
                        Extraction method (default: auto)
  --output-dir DIR      Directory to save extracted text
  --output-file FILE    Output filename
  --compare-methods     Compare all available methods
  --save-report         Save detailed extraction report
  --verbose, -v         Enable verbose logging
```

## Examples

### Extract from a regular PDF
```bash
python pdf_text_extractor.py report.pdf
# Output: report_extracted.txt
```

### Extract from a scanned PDF using OCR
```bash
python pdf_text_extractor.py scanned_document.pdf --method ocr
```

### Compare all methods and save report
```bash
python pdf_text_extractor.py complex_document.pdf --compare-methods --save-report
# Outputs: complex_document_extracted.txt and complex_document_report.txt
```

### Extract to specific directory
```bash
python pdf_text_extractor.py document.pdf --output-dir ./extracted_texts/
```

## Method Comparison

| Method | Best For | Speed | Tables | OCR |
|--------|----------|-------|--------|-----|
| **PyMuPDF** | General PDFs | ⚡⚡⚡ | ❌ | ❌ |
| **pdfplumber** | Complex layouts, tables | ⚡⚡ | ✅ | ❌ |
| **pypdf** | Simple PDFs, fallback | ⚡⚡⚡ | ❌ | ❌ |
| **OCR** | Scanned PDFs, images | ⚡ | ❌ | ✅ |

## Output Format

The extracted text includes:
- Page markers (`--- Page X ---`)
- Original text formatting preserved
- Table data (when using pdfplumber)
- Metadata about extraction success

## Troubleshooting

### Common Issues

**"No text extracted"**
- PDF might be image-based → Use `--method ocr`
- PDF might be encrypted → Check if password protected
- PDF might be corrupted → Try different methods

**"Tesseract not found"**
- Install Tesseract OCR (see installation section)
- Ensure it's in your system PATH

**"Library not installed"**
- Run `pip install -r requirements.txt`
- Check for specific library installation errors

### Performance Tips

1. **For speed**: Use `--method pymupdf`
2. **For accuracy**: Use `--compare-methods` and select best result
3. **For tables**: Use `--method pdfplumber`
4. **For scanned PDFs**: Use `--method ocr`

## Dependencies

- **PyMuPDF**: Fast PDF processing
- **pdfplumber**: Advanced layout analysis
- **pypdf**: Standard PDF reading
- **pytesseract**: OCR capabilities
- **Pillow**: Image processing for OCR

## License

This project is open source and available under the MIT License.

## Web Application

A user-friendly web interface is also available! 

### Quick Start (Web Interface)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web application
python run_web_app.py
```

The web app will automatically:
- Check for missing dependencies and offer to install them
- Check for Tesseract OCR installation
- Create necessary directories
- Start the server at http://localhost:5000
- Open your web browser

### Web Features

🌐 **Modern Web Interface**: Beautiful, responsive design with drag-and-drop file upload
📊 **Real-time Progress**: Live progress indicators during extraction
🔄 **Method Comparison**: Visual comparison of all extraction methods
📋 **Detailed Reports**: Downloadable extraction reports
📱 **Mobile Friendly**: Works on desktop, tablet, and mobile devices

### Manual Web Setup

```bash
# Start Flask app manually
python app.py

# Or use Flask CLI
export FLASK_APP=app.py
flask run
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the PDF text extraction capabilities.
