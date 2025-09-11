#!/usr/bin/env python3
"""
High-Accuracy PDF Text Extractor

This script provides multiple methods for extracting text from PDF files with high accuracy.
It uses multiple libraries and fallback mechanisms to ensure the best possible text extraction.

Libraries used:
- PyMuPDF (fitz): Fast and efficient for most PDFs
- pdfplumber: Excellent for complex layouts and tables
- pypdf: Lightweight fallback option
- Tesseract OCR: For scanned PDFs and images

Author: AI Assistant
Date: 2024
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """A comprehensive PDF text extraction class with multiple methods for high accuracy."""
    
    def __init__(self, pdf_path: str, output_dir: Optional[str] = None):
        """
        Initialize the PDF text extractor.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str, optional): Directory to save extracted text and images
        """
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent
        self.output_dir.mkdir(exist_ok=True)
        
        # Validate PDF file
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path}")
    
    def extract_with_pymupdf(self) -> Tuple[str, Dict]:
        """
        Extract text using PyMuPDF (fitz) - fastest method.
        
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            import fitz  # PyMuPDF
            logger.info("Extracting text using PyMuPDF...")
            
            doc = fitz.open(str(self.pdf_path))
            text_content = []
            metadata = {
                'method': 'PyMuPDF',
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'pages_with_text': 0,
                'total_characters': 0
            }
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text.strip():
                    metadata['pages_with_text'] += 1
                    text_content.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            
            full_text = "\n".join(text_content)
            metadata['total_characters'] = len(full_text)
            
            logger.info(f"PyMuPDF extraction completed: {metadata['pages_with_text']} pages with text")
            return full_text, metadata
            
        except ImportError:
            logger.warning("PyMuPDF not available. Install with: pip install pymupdf")
            return "", {'method': 'PyMuPDF', 'error': 'Library not installed'}
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            return "", {'method': 'PyMuPDF', 'error': str(e)}
    
    def extract_with_pdfplumber(self) -> Tuple[str, Dict]:
        """
        Extract text using pdfplumber - excellent for complex layouts.
        
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            import pdfplumber
            logger.info("Extracting text using pdfplumber...")
            
            text_content = []
            tables_found = 0
            metadata = {
                'method': 'pdfplumber',
                'page_count': 0,
                'pages_with_text': 0,
                'tables_found': 0,
                'total_characters': 0
            }
            
            with pdfplumber.open(str(self.pdf_path)) as pdf:
                metadata['page_count'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    page_text = page.extract_text()
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        tables_found += len(tables)
                        table_text = "\n[TABLES FOUND ON THIS PAGE]\n"
                        for table in tables:
                            for row in table:
                                if row:
                                    table_text += " | ".join([cell or "" for cell in row]) + "\n"
                        page_text = (page_text or "") + table_text
                    
                    if page_text and page_text.strip():
                        metadata['pages_with_text'] += 1
                        text_content.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
            
            metadata['tables_found'] = tables_found
            full_text = "\n".join(text_content)
            metadata['total_characters'] = len(full_text)
            
            logger.info(f"pdfplumber extraction completed: {metadata['pages_with_text']} pages with text, {tables_found} tables found")
            return full_text, metadata
            
        except ImportError:
            logger.warning("pdfplumber not available. Install with: pip install pdfplumber")
            return "", {'method': 'pdfplumber', 'error': 'Library not installed'}
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            return "", {'method': 'pdfplumber', 'error': str(e)}
    
    def extract_with_pypdf(self) -> Tuple[str, Dict]:
        """
        Extract text using pypdf - lightweight fallback option.
        
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            from pypdf import PdfReader
            logger.info("Extracting text using pypdf...")
            
            reader = PdfReader(str(self.pdf_path))
            text_content = []
            metadata = {
                'method': 'pypdf',
                'page_count': len(reader.pages),
                'pages_with_text': 0,
                'total_characters': 0,
                'encrypted': reader.is_encrypted
            }
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                
                if page_text.strip():
                    metadata['pages_with_text'] += 1
                    text_content.append(f"\n--- Page {page_num + 1} ---\n{page_text}")
            
            full_text = "\n".join(text_content)
            metadata['total_characters'] = len(full_text)
            
            logger.info(f"pypdf extraction completed: {metadata['pages_with_text']} pages with text")
            return full_text, metadata
            
        except ImportError:
            logger.warning("pypdf not available. Install with: pip install pypdf")
            return "", {'method': 'pypdf', 'error': 'Library not installed'}
        except Exception as e:
            logger.error(f"pypdf extraction failed: {e}")
            return "", {'method': 'pypdf', 'error': str(e)}
    
    def extract_with_ocr(self) -> Tuple[str, Dict]:
        """
        Extract text using OCR for scanned PDFs.
        
        Returns:
            Tuple[str, Dict]: Extracted text and metadata
        """
        try:
            import fitz  # PyMuPDF for image extraction
            import pytesseract
            from PIL import Image
            import io
            
            logger.info("Extracting text using OCR (Tesseract)...")
            
            doc = fitz.open(str(self.pdf_path))
            text_content = []
            metadata = {
                'method': 'OCR (Tesseract)',
                'page_count': len(doc),
                'pages_processed': 0,
                'total_characters': 0,
                'images_processed': 0
            }
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Convert page to image
                mat = fitz.Matrix(2.0, 2.0)  # High resolution
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # OCR the image
                image = Image.open(io.BytesIO(img_data))
                page_text = pytesseract.image_to_string(image, config='--psm 6')
                
                if page_text.strip():
                    metadata['pages_processed'] += 1
                    text_content.append(f"\n--- Page {page_num + 1} (OCR) ---\n{page_text}")
                
                metadata['images_processed'] += 1
            
            doc.close()
            
            full_text = "\n".join(text_content)
            metadata['total_characters'] = len(full_text)
            
            logger.info(f"OCR extraction completed: {metadata['pages_processed']} pages processed")
            return full_text, metadata
            
        except ImportError as e:
            logger.warning(f"OCR dependencies not available: {e}")
            logger.warning("Install with: pip install pytesseract pillow")
            logger.warning("Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
            return "", {'method': 'OCR', 'error': f'Dependencies not installed: {e}'}
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", {'method': 'OCR', 'error': str(e)}
    
    def extract_all_methods(self) -> Dict[str, Tuple[str, Dict]]:
        """
        Extract text using all available methods for comparison.
        
        Returns:
            Dict[str, Tuple[str, Dict]]: Results from all methods
        """
        results = {}
        
        # Try each method
        methods = [
            ('pymupdf', self.extract_with_pymupdf),
            ('pdfplumber', self.extract_with_pdfplumber),
            ('pypdf', self.extract_with_pypdf),
            ('ocr', self.extract_with_ocr)
        ]
        
        for method_name, method_func in methods:
            try:
                text, metadata = method_func()
                results[method_name] = (text, metadata)
            except Exception as e:
                logger.error(f"Method {method_name} failed: {e}")
                results[method_name] = ("", {'error': str(e)})
        
        return results
    
    def get_best_extraction(self) -> Tuple[str, Dict]:
        """
        Get the best text extraction by comparing all methods.
        
        Returns:
            Tuple[str, Dict]: Best extracted text and its metadata
        """
        all_results = self.extract_all_methods()
        
        best_text = ""
        best_metadata = {}
        best_score = 0
        
        for method, (text, metadata) in all_results.items():
            if 'error' in metadata:
                continue
            
            # Score based on text length and successful pages
            score = len(text) + metadata.get('pages_with_text', 0) * 100
            
            if score > best_score:
                best_score = score
                best_text = text
                best_metadata = metadata
                best_metadata['best_method'] = method
        
        if not best_text:
            logger.warning("No method successfully extracted text. The PDF might be encrypted, corrupted, or image-only.")
            return "", {'error': 'All extraction methods failed'}
        
        logger.info(f"Best extraction method: {best_metadata['best_method']} (score: {best_score})")
        return best_text, best_metadata
    
    def save_text(self, text: str, filename: Optional[str] = None) -> str:
        """
        Save extracted text to a file.
        
        Args:
            text (str): Text to save
            filename (str, optional): Output filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            filename = f"{self.pdf_path.stem}_extracted.txt"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Text saved to: {output_path}")
        return str(output_path)
    
    def generate_report(self, all_results: Dict[str, Tuple[str, Dict]]) -> str:
        """
        Generate a comparison report of all extraction methods.
        
        Args:
            all_results (Dict): Results from all methods
            
        Returns:
            str: Report text
        """
        report_lines = [
            "=" * 60,
            "PDF TEXT EXTRACTION REPORT",
            "=" * 60,
            f"PDF File: {self.pdf_path}",
            f"File Size: {self.pdf_path.stat().st_size / 1024:.2f} KB",
            ""
        ]
        
        for method, (text, metadata) in all_results.items():
            report_lines.extend([
                f"--- {method.upper()} ---",
                f"Status: {'Success' if 'error' not in metadata else 'Failed'}",
            ])
            
            if 'error' in metadata:
                report_lines.append(f"Error: {metadata['error']}")
            else:
                report_lines.extend([
                    f"Pages with text: {metadata.get('pages_with_text', 'N/A')}",
                    f"Total characters: {metadata.get('total_characters', 'N/A')}",
                    f"Special features: {metadata.get('tables_found', '')} tables" if 'tables_found' in metadata else ""
                ])
            
            report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files with high accuracy using multiple methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_text_extractor.py document.pdf
  python pdf_text_extractor.py document.pdf --method pymupdf
  python pdf_text_extractor.py document.pdf --output-dir ./extracted_text
  python pdf_text_extractor.py document.pdf --compare-methods --save-report
        """
    )
    
    parser.add_argument('pdf_file', help='Path to the PDF file')
    parser.add_argument('--method', 
                       choices=['auto', 'pymupdf', 'pdfplumber', 'pypdf', 'ocr'],
                       default='auto',
                       help='Extraction method to use (default: auto - selects best)')
    parser.add_argument('--output-dir', 
                       help='Directory to save extracted text (default: same as PDF)')
    parser.add_argument('--output-file',
                       help='Output filename (default: PDF_name_extracted.txt)')
    parser.add_argument('--compare-methods', 
                       action='store_true',
                       help='Compare all available methods')
    parser.add_argument('--save-report',
                       action='store_true',
                       help='Save detailed extraction report')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize extractor
        extractor = PDFTextExtractor(args.pdf_file, args.output_dir)
        
        if args.compare_methods:
            # Compare all methods
            logger.info("Comparing all extraction methods...")
            all_results = extractor.extract_all_methods()
            
            # Generate and save report
            if args.save_report:
                report = extractor.generate_report(all_results)
                report_file = extractor.save_text(report, f"{extractor.pdf_path.stem}_report.txt")
                print(f"Report saved to: {report_file}")
            
            # Display summary
            print("\nEXTRACTION SUMMARY:")
            print("-" * 40)
            for method, (text, metadata) in all_results.items():
                status = "✓" if 'error' not in metadata else "✗"
                chars = metadata.get('total_characters', 0)
                print(f"{status} {method:12} | {chars:,} characters")
            
            # Get best result
            best_text, best_metadata = extractor.get_best_extraction()
            if best_text:
                output_file = extractor.save_text(best_text, args.output_file)
                print(f"\nBest result saved to: {output_file}")
                print(f"Best method: {best_metadata.get('best_method', 'unknown')}")
        else:
            # Single method extraction
            if args.method == 'auto':
                text, metadata = extractor.get_best_extraction()
            elif args.method == 'pymupdf':
                text, metadata = extractor.extract_with_pymupdf()
            elif args.method == 'pdfplumber':
                text, metadata = extractor.extract_with_pdfplumber()
            elif args.method == 'pypdf':
                text, metadata = extractor.extract_with_pypdf()
            elif args.method == 'ocr':
                text, metadata = extractor.extract_with_ocr()
            
            if 'error' in metadata:
                print(f"Extraction failed: {metadata['error']}")
                sys.exit(1)
            
            # Save extracted text
            output_file = extractor.save_text(text, args.output_file)
            
            # Display results
            print(f"✓ Extraction completed using {metadata.get('method', args.method)}")
            print(f"✓ {metadata.get('pages_with_text', 0)} pages with text extracted")
            print(f"✓ {metadata.get('total_characters', 0):,} characters extracted")
            print(f"✓ Text saved to: {output_file}")
            
            if 'tables_found' in metadata and metadata['tables_found'] > 0:
                print(f"✓ {metadata['tables_found']} tables detected and extracted")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
