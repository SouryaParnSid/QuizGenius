#!/usr/bin/env python3
"""
PDF Text Extractor Web Application

A Flask web application that provides a user-friendly interface
for uploading PDF files and extracting text with high accuracy.
"""

import os
import uuid
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify, send_file, flash, redirect, url_for
from pdf_text_extractor import PDFTextExtractor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'extracted_texts'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf'}

# Create necessary directories
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
Path('static').mkdir(exist_ok=True)
Path('templates').mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up old uploaded and extracted files."""
    import time
    current_time = time.time()
    # Remove files older than 1 hour
    max_age = 3600
    
    for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getmtime(file_path) > max_age:
                    try:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error cleaning up file {file_path}: {e}")

@app.route('/')
def index():
    """Main page with upload form."""
    cleanup_old_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and text extraction."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file
        if not file or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
        
        # Get extraction method
        method = request.form.get('method', 'auto')
        compare_methods = request.form.get('compare_methods') == 'true'
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        unique_filename = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(filepath)
        logger.info(f"File uploaded: {filepath}")
        
        # Extract text
        extractor = PDFTextExtractor(filepath, app.config['OUTPUT_FOLDER'])
        
        result = {
            'filename': filename,
            'unique_id': unique_id,
            'method_used': method,
            'extraction_results': {}
        }
        
        if compare_methods:
            # Compare all methods
            all_results = extractor.extract_all_methods()
            
            for method_name, (text, metadata) in all_results.items():
                result['extraction_results'][method_name] = {
                    'success': 'error' not in metadata,
                    'metadata': metadata,
                    'text_length': len(text) if text else 0,
                    'preview': text[:200] if text else ""
                }
            
            # Get best result
            best_text, best_metadata = extractor.get_best_extraction()
            if best_text:
                # Save best result
                output_filename = f"{unique_id}_extracted.txt"
                output_path = extractor.save_text(best_text, output_filename)
                
                result['best_result'] = {
                    'method': best_metadata.get('best_method', 'unknown'),
                    'text_length': len(best_text),
                    'pages_with_text': best_metadata.get('pages_with_text', 0),
                    'total_characters': best_metadata.get('total_characters', 0),
                    'download_url': f"/download/{unique_id}_extracted.txt",
                    'preview': best_text[:500]
                }
                
                # Generate comparison report
                report = extractor.generate_report(all_results)
                report_filename = f"{unique_id}_report.txt"
                extractor.save_text(report, report_filename)
                result['report_url'] = f"/download/{report_filename}"
        else:
            # Single method extraction
            if method == 'auto':
                text, metadata = extractor.get_best_extraction()
            elif method == 'pymupdf':
                text, metadata = extractor.extract_with_pymupdf()
            elif method == 'pdfplumber':
                text, metadata = extractor.extract_with_pdfplumber()
            elif method == 'pypdf':
                text, metadata = extractor.extract_with_pypdf()
            elif method == 'ocr':
                text, metadata = extractor.extract_with_ocr()
            else:
                return jsonify({'error': f'Invalid method: {method}'}), 400
            
            if 'error' in metadata:
                return jsonify({'error': f"Extraction failed: {metadata['error']}"}), 500
            
            if text:
                # Save extracted text
                output_filename = f"{unique_id}_extracted.txt"
                output_path = extractor.save_text(text, output_filename)
                
                result['extraction_results'][method] = {
                    'success': True,
                    'metadata': metadata,
                    'text_length': len(text),
                    'preview': text[:200]
                }
                
                result['result'] = {
                    'method': metadata.get('method', method),
                    'text_length': len(text),
                    'pages_with_text': metadata.get('pages_with_text', 0),
                    'total_characters': metadata.get('total_characters', 0),
                    'tables_found': metadata.get('tables_found', 0),
                    'download_url': f"/download/{unique_id}_extracted.txt",
                    'preview': text[:500]
                }
            else:
                return jsonify({'error': 'No text could be extracted from the PDF'}), 500
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except Exception as e:
            logger.error(f"Error removing uploaded file: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return jsonify({'error': f'An error occurred during extraction: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download extracted text file."""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({'error': 'Error downloading file'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'PDF Text Extractor'})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
