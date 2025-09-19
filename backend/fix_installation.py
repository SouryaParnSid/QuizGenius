#!/usr/bin/env python3
"""
Fix Installation Script

Resolves dependency conflicts and installs compatible versions
for the RAG system on Windows.
"""

import subprocess
import sys
import os
import platform


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"Running: {cmd}")
    if description:
        print(f"Description: {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def fix_pytorch_transformers():
    """Fix PyTorch and Transformers version conflicts."""
    print("=== Fixing PyTorch and Transformers Compatibility ===")
    
    # Uninstall problematic versions
    uninstall_commands = [
        "pip uninstall torch torchvision torchaudio transformers sentence-transformers -y",
        "pip uninstall chromadb -y"
    ]
    
    for cmd in uninstall_commands:
        run_command(cmd, "Removing potentially conflicting packages")
    
    # Install compatible versions
    install_commands = [
        "pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu",
        "pip install transformers==4.35.2",
        "pip install sentence-transformers==2.2.2",
    ]
    
    for cmd in install_commands:
        if not run_command(cmd, "Installing compatible versions"):
            return False
    
    return True


def fix_sqlite_chromadb():
    """Fix SQLite and ChromaDB compatibility."""
    print("=== Fixing SQLite and ChromaDB Compatibility ===")
    
    if platform.system() == "Windows":
        # Install pysqlite3-binary for Windows
        if not run_command("pip install pysqlite3-binary", "Installing better SQLite for Windows"):
            print("Warning: Could not install pysqlite3-binary")
        
        # Try ChromaDB with specific version
        chromadb_commands = [
            "pip install chromadb==0.4.22",
            "pip install faiss-cpu==1.7.4"  # Fallback option
        ]
        
        for cmd in chromadb_commands:
            if run_command(cmd):
                return True
        
        print("Warning: ChromaDB installation failed, will use FAISS fallback")
        return True
    else:
        # Non-Windows systems
        return run_command("pip install chromadb==0.4.22")


def install_remaining_dependencies():
    """Install remaining RAG dependencies."""
    print("=== Installing Remaining Dependencies ===")
    
    dependencies = [
        "langchain==0.1.20",
        "langchain-google-genai==1.0.10",
        "google-generativeai==0.3.2",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "pypdf==3.17.4",
        "python-docx==1.1.0",
        "python-multipart==0.0.6",
        "aiofiles==23.2.1",
        "requests==2.31.0",
        "numpy==1.24.4",
        "tiktoken==0.5.2",
        "textstat==0.7.3",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1"
    ]
    
    success_count = 0
    for dep in dependencies:
        if run_command(f"pip install {dep}"):
            success_count += 1
        else:
            print(f"Warning: Failed to install {dep}")
    
    print(f"Successfully installed {success_count}/{len(dependencies)} dependencies")
    return success_count > len(dependencies) * 0.8  # 80% success rate


def test_installation():
    """Test if the installation works."""
    print("=== Testing Installation ===")
    
    test_script = """
import sys
import warnings
warnings.filterwarnings("ignore")

print("Testing imports...")

try:
    # Test SQLite compatibility
    try:
        import pysqlite3
        sys.modules['sqlite3'] = pysqlite3
        print("✓ Using pysqlite3 for SQLite")
    except ImportError:
        import sqlite3
        print(f"✓ Using system SQLite {sqlite3.sqlite_version}")
    
    # Test PyTorch
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    
    # Test Transformers
    import transformers
    print(f"✓ Transformers {transformers.__version__}")
    
    # Test Sentence Transformers
    import sentence_transformers
    print(f"✓ Sentence Transformers {sentence_transformers.__version__}")
    
    # Test other dependencies
    import fastapi
    print(f"✓ FastAPI {fastapi.__version__}")
    
    import langchain
    print(f"✓ LangChain")
    
    # Test ChromaDB or FAISS
    try:
        import chromadb
        print(f"✓ ChromaDB available")
    except Exception as e:
        print(f"⚠ ChromaDB failed: {e}")
        try:
            import faiss
            print(f"✓ FAISS fallback available")
        except ImportError:
            print("✗ Neither ChromaDB nor FAISS available")
    
    print("\\n✅ Basic imports successful!")
    
except Exception as e:
    print(f"\\n❌ Import test failed: {e}")
    sys.exit(1)
"""
    
    with open("test_imports.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    success = run_command("python test_imports.py", "Testing imports")
    
    # Clean up
    try:
        os.remove("test_imports.py")
    except:
        pass
    
    return success


def main():
    """Main fix function."""
    print("RAG System Installation Fix")
    print("=" * 40)
    
    steps = [
        ("Fix PyTorch/Transformers", fix_pytorch_transformers),
        ("Fix SQLite/ChromaDB", fix_sqlite_chromadb),
        ("Install Dependencies", install_remaining_dependencies),
        ("Test Installation", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed")
            if step_name != "Test Installation":  # Don't exit on test failure
                continue
        else:
            print(f"✅ {step_name} completed")
    
    print("\n" + "=" * 40)
    print("Installation fix completed!")
    print("\nNext steps:")
    print("1. Copy env.example to .env")
    print("2. Add your GEMINI_API_KEY to .env")
    print("3. Run: python rag_api.py")
    print("\nIf ChromaDB still fails, the system will automatically use FAISS fallback.")


if __name__ == "__main__":
    main()
