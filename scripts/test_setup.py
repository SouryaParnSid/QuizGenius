#!/usr/bin/env python3
"""
PDF Extraction Setup Test Script

This script helps verify that your Python environment is properly configured
for PDF text extraction in QuizGenius.
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test if Python version is compatible."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def test_dependencies():
    """Test if required dependencies are installed."""
    dependencies = [
        ('PyMuPDF', 'fitz'),
        ('pdfplumber', 'pdfplumber'),
        ('pypdf', 'pypdf'),
        ('pytesseract', 'pytesseract'),
        ('Pillow', 'PIL')
    ]
    
    print("\n🔍 Checking Python dependencies...")
    results = {}
    
    for display_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {display_name} - Installed")
            results[display_name] = True
        except ImportError:
            print(f"❌ {display_name} - Not installed")
            results[display_name] = False
    
    return results

def test_tesseract():
    """Test if Tesseract OCR is available."""
    print("\n🔍 Checking Tesseract OCR...")
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ Tesseract OCR - {version_line}")
            return True
        else:
            print("❌ Tesseract OCR - Command failed")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR - Not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Tesseract OCR - Command timeout")
        return False
    except Exception as e:
        print(f"❌ Tesseract OCR - Error: {e}")
        return False

def test_pdf_extraction():
    """Test PDF extraction with a simple test."""
    print("\n🔍 Testing PDF extraction functionality...")
    
    # Check if the main extractor exists
    script_dir = Path(__file__).parent
    extractor_path = script_dir / 'pdf_text_extractor.py'
    
    if not extractor_path.exists():
        print("❌ pdf_text_extractor.py not found")
        return False
    
    try:
        # Import the extractor
        sys.path.insert(0, str(script_dir))
        from pdf_text_extractor import PDFTextExtractor
        print("✅ PDF extractor module - Available")
        return True
    except ImportError as e:
        print(f"❌ PDF extractor module - Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PDF extractor module - Error: {e}")
        return False

def generate_report(results):
    """Generate a setup report."""
    print("\n" + "="*60)
    print("📋 SETUP REPORT")
    print("="*60)
    
    # Count successful components
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"Overall Status: {passed_tests}/{total_tests} components working")
    
    if passed_tests == total_tests:
        print("🎉 Perfect! Full PDF extraction capabilities available.")
        setup_quality = "Excellent"
    elif passed_tests >= 4:
        print("👍 Good! Most PDF extraction methods will work.")
        setup_quality = "Good"
    elif passed_tests >= 2:
        print("⚠️  Basic PDF extraction will work, but some features may be limited.")
        setup_quality = "Basic"
    else:
        print("🔧 Setup needs attention. Limited PDF extraction capabilities.")
        setup_quality = "Needs Work"
    
    print(f"Setup Quality: {setup_quality}")
    
    # Provide specific recommendations
    print("\n📝 Recommendations:")
    
    if not results.get('Python Version', False):
        print("- Install Python 3.7 or higher")
    
    missing_deps = [name for name, status in results.items() 
                   if name in ['PyMuPDF', 'pdfplumber', 'pypdf', 'pytesseract', 'Pillow'] and not status]
    
    if missing_deps:
        print(f"- Install missing dependencies: pip install {' '.join(missing_deps).lower()}")
    
    if not results.get('Tesseract OCR', False):
        print("- Install Tesseract OCR for scanned PDF support (optional)")
    
    print("\n🚀 Next Steps:")
    if setup_quality in ["Excellent", "Good"]:
        print("- Your setup is ready! Try uploading a PDF in QuizGenius.")
    else:
        print("- Follow the installation guide in PDF_SETUP.md")
        print("- Run this test again after installing missing components")
    
    return setup_quality

def main():
    """Main test function."""
    print("🔧 QuizGenius PDF Extraction Setup Test")
    print("="*50)
    print("This script will test your Python environment for PDF extraction.\n")
    
    results = {}
    
    # Run all tests
    results['Python Version'] = test_python_version()
    
    deps = test_dependencies()
    results.update(deps)
    
    results['Tesseract OCR'] = test_tesseract()
    results['PDF Extractor'] = test_pdf_extraction()
    
    # Generate report
    generate_report(results)
    
    print("\n" + "="*60)
    print("For detailed setup instructions, see PDF_SETUP.md")
    print("="*60)

if __name__ == "__main__":
    main()
