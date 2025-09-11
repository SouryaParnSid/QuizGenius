#!/usr/bin/env python3
"""
Example usage of the PDF Text Extractor

This script demonstrates various ways to use the PDFTextExtractor class
for extracting text from PDF files with high accuracy.
"""

import os
from pdf_text_extractor import PDFTextExtractor

def example_basic_extraction():
    """Example: Basic text extraction with automatic method selection."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Extraction (Auto Method)")
    print("=" * 60)
    
    # Replace with your PDF file path
    pdf_path = "sample_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"⚠️  PDF file not found: {pdf_path}")
        print("Please place a PDF file named 'sample_document.pdf' in this directory")
        return
    
    try:
        # Initialize extractor
        extractor = PDFTextExtractor(pdf_path)
        
        # Extract text using the best available method
        text, metadata = extractor.get_best_extraction()
        
        if text:
            print(f"✅ Successfully extracted text using: {metadata.get('best_method', 'unknown')}")
            print(f"📄 Pages with text: {metadata.get('pages_with_text', 0)}")
            print(f"📊 Total characters: {metadata.get('total_characters', 0):,}")
            
            # Save to file
            output_file = extractor.save_text(text)
            print(f"💾 Text saved to: {output_file}")
            
            # Show first 200 characters as preview
            preview = text[:200].replace('\n', ' ')
            print(f"📖 Preview: {preview}...")
        else:
            print("❌ No text could be extracted from the PDF")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_method_comparison():
    """Example: Compare all extraction methods."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Method Comparison")
    print("=" * 60)
    
    pdf_path = "sample_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"⚠️  PDF file not found: {pdf_path}")
        return
    
    try:
        extractor = PDFTextExtractor(pdf_path)
        
        # Get results from all methods
        all_results = extractor.extract_all_methods()
        
        print("Comparison of extraction methods:")
        print("-" * 40)
        
        for method, (text, metadata) in all_results.items():
            if 'error' in metadata:
                print(f"❌ {method:12} | Failed: {metadata['error']}")
            else:
                chars = metadata.get('total_characters', 0)
                pages = metadata.get('pages_with_text', 0)
                tables = metadata.get('tables_found', 0)
                
                status = "✅"
                extra_info = ""
                if method == 'pdfplumber' and tables > 0:
                    extra_info = f" ({tables} tables)"
                
                print(f"{status} {method:12} | {chars:,} chars, {pages} pages{extra_info}")
        
        # Generate and save report
        report = extractor.generate_report(all_results)
        report_file = extractor.save_text(report, "comparison_report.txt")
        print(f"\n📋 Detailed report saved to: {report_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_specific_methods():
    """Example: Using specific extraction methods."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Specific Methods")
    print("=" * 60)
    
    pdf_path = "sample_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"⚠️  PDF file not found: {pdf_path}")
        return
    
    try:
        extractor = PDFTextExtractor(pdf_path)
        
        # Try PyMuPDF (fastest)
        print("🚀 Trying PyMuPDF (fastest method)...")
        text, metadata = extractor.extract_with_pymupdf()
        if 'error' not in metadata:
            print(f"   ✅ Success: {metadata.get('total_characters', 0):,} characters")
        else:
            print(f"   ❌ Failed: {metadata['error']}")
        
        # Try pdfplumber (best for tables)
        print("📊 Trying pdfplumber (best for tables)...")
        text, metadata = extractor.extract_with_pdfplumber()
        if 'error' not in metadata:
            tables = metadata.get('tables_found', 0)
            print(f"   ✅ Success: {metadata.get('total_characters', 0):,} characters, {tables} tables")
        else:
            print(f"   ❌ Failed: {metadata['error']}")
        
        # Try OCR (for scanned PDFs)
        print("🔍 Trying OCR (for scanned PDFs)...")
        text, metadata = extractor.extract_with_ocr()
        if 'error' not in metadata:
            print(f"   ✅ Success: {metadata.get('total_characters', 0):,} characters")
        else:
            print(f"   ❌ Failed: {metadata['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_batch_processing():
    """Example: Process multiple PDF files."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Batch Processing")
    print("=" * 60)
    
    # Look for PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️  No PDF files found in current directory")
        print("Place some PDF files here to try batch processing")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
    
    results = {}
    
    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file}")
        try:
            extractor = PDFTextExtractor(pdf_file, output_dir="extracted_texts")
            
            # Extract using best method
            text, metadata = extractor.get_best_extraction()
            
            if text:
                # Save extracted text
                output_file = extractor.save_text(text)
                
                results[pdf_file] = {
                    'success': True,
                    'method': metadata.get('best_method', 'unknown'),
                    'characters': metadata.get('total_characters', 0),
                    'pages': metadata.get('pages_with_text', 0),
                    'output': output_file
                }
                print(f"   ✅ Success: {results[pdf_file]['characters']:,} characters")
            else:
                results[pdf_file] = {'success': False, 'error': 'No text extracted'}
                print(f"   ❌ Failed: No text extracted")
                
        except Exception as e:
            results[pdf_file] = {'success': False, 'error': str(e)}
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 40)
    
    successful = sum(1 for r in results.values() if r['success'])
    total_chars = sum(r.get('characters', 0) for r in results.values() if r['success'])
    
    print(f"📊 Successfully processed: {successful}/{len(pdf_files)} files")
    print(f"📝 Total characters extracted: {total_chars:,}")
    
    for filename, result in results.items():
        if result['success']:
            print(f"✅ {filename}: {result['characters']:,} chars ({result['method']})")
        else:
            print(f"❌ {filename}: {result['error']}")

def main():
    """Run all examples."""
    print("🚀 PDF Text Extractor - Example Usage")
    print("=" * 60)
    
    # Run examples
    example_basic_extraction()
    example_method_comparison()
    example_specific_methods()
    example_batch_processing()
    
    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    print("Check the generated files and try with your own PDFs.")
    print("=" * 60)

if __name__ == "__main__":
    main()
