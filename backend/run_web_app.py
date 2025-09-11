#!/usr/bin/env python3
"""
Quick Start Script for PDF Text Extractor Web Application

This script helps you quickly start the web application with proper setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask', 'PyMuPDF', 'pdfplumber', 'pypdf', 'pytesseract', 'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is not installed")
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies."""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ Tesseract OCR: {version}")
            return True
        else:
            print("❌ Tesseract OCR not found")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR not found")
        return False

def print_tesseract_install_instructions():
    """Print Tesseract installation instructions."""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("📖 TESSERACT OCR INSTALLATION INSTRUCTIONS")
    print("="*60)
    
    if system == "windows":
        print("Windows:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install the executable")
        print("3. Add to PATH environment variable")
    elif system == "darwin":
        print("macOS:")
        print("brew install tesseract")
    elif system == "linux":
        print("Linux (Ubuntu/Debian):")
        print("sudo apt-get install tesseract-ocr")
        print("\nLinux (CentOS/RHEL):")
        print("sudo yum install tesseract")
    
    print("\nNote: Tesseract is only required for OCR extraction of scanned PDFs.")
    print("Other extraction methods will work without it.")

def create_directories():
    """Create necessary directories."""
    directories = ['uploads', 'extracted_texts', 'static', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Created necessary directories")

def start_web_application():
    """Start the Flask web application."""
    print("\n" + "="*60)
    print("🚀 STARTING PDF TEXT EXTRACTOR WEB APPLICATION")
    print("="*60)
    print("Opening web browser at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    # Try to open web browser
    try:
        import webbrowser
        import threading
        import time
        
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    except Exception:
        pass
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using PDF Text Extractor!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main function to set up and start the application."""
    print("🔧 PDF Text Extractor - Setup and Launch")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check if requirements.txt exists
    if not Path('requirements.txt').exists():
        print("❌ Error: requirements.txt not found")
        print("Please ensure you're in the correct directory.")
        return
    
    # Check dependencies
    missing_packages = check_dependencies()
    
    # Install missing packages
    if missing_packages:
        print(f"\n📋 Missing packages detected: {', '.join(missing_packages)}")
        install_choice = input("Install missing packages now? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes']:
            if not install_dependencies(missing_packages):
                print("❌ Failed to install dependencies. Please install manually.")
                return
        else:
            print("⚠️  Some features may not work without all dependencies.")
    
    # Check Tesseract (optional)
    tesseract_available = check_tesseract()
    if not tesseract_available:
        print_tesseract_install_instructions()
        
        continue_choice = input("\nContinue without Tesseract OCR? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            return
    
    # Create directories
    create_directories()
    
    # Start application
    start_web_application()

if __name__ == "__main__":
    main()
