"""
Compatibility fixes for RAG system dependencies.

Handles SQLite and library version conflicts on different platforms.
"""

import sys
import os
import platform
import warnings


def fix_sqlite_compatibility():
    """Fix SQLite compatibility issues for ChromaDB on Windows."""
    if platform.system() == "Windows":
        try:
            # Try to import pysqlite3 as sqlite3 for better compatibility
            import pysqlite3
            sys.modules['sqlite3'] = pysqlite3
            print("✓ Using pysqlite3 for better SQLite compatibility")
        except ImportError:
            # Fallback: check if system SQLite is compatible
            import sqlite3
            sqlite_version = sqlite3.sqlite_version_info
            required_version = (3, 35, 0)
            
            if sqlite_version < required_version:
                print(f"⚠ Warning: SQLite version {'.'.join(map(str, sqlite_version))} < 3.35.0")
                print("ChromaDB may not work properly. Consider upgrading SQLite or using FAISS.")
                return False
            else:
                print(f"✓ SQLite version {'.'.join(map(str, sqlite_version))} is compatible")
                return True
    return True


def fix_torch_transformers_compatibility():
    """Fix PyTorch and Transformers compatibility issues."""
    try:
        import torch
        torch_version = torch.__version__
        
        # Suppress specific warnings that cause issues
        warnings.filterwarnings("ignore", message=".*torch.utils._pytree.*")
        warnings.filterwarnings("ignore", message=".*register_pytree_node.*")
        
        # Check for problematic version combinations
        if torch_version.startswith("2.2") or torch_version.startswith("2.3"):
            print(f"⚠ Warning: PyTorch {torch_version} may have compatibility issues")
            print("Consider downgrading to PyTorch 2.0.x or 2.1.x")
        
        print(f"✓ PyTorch version: {torch_version}")
        return True
        
    except ImportError:
        print("⚠ PyTorch not found - some features may not work")
        return False


def check_dependencies():
    """Check and fix dependency compatibility issues."""
    print("Checking dependency compatibility...")
    
    fixes_applied = []
    
    # Fix SQLite issues
    if fix_sqlite_compatibility():
        fixes_applied.append("SQLite compatibility")
    
    # Fix PyTorch/Transformers issues
    if fix_torch_transformers_compatibility():
        fixes_applied.append("PyTorch compatibility")
    
    if fixes_applied:
        print(f"✓ Applied compatibility fixes: {', '.join(fixes_applied)}")
    
    return True


def get_fallback_vector_store():
    """Get fallback vector store configuration if ChromaDB fails."""
    return {
        "type": "faiss",
        "description": "FAISS-based vector store (fallback for ChromaDB issues)",
        "persist_directory": "./data/faiss_index"
    }


# Apply compatibility fixes on import
if __name__ != "__main__":
    try:
        check_dependencies()
    except Exception as e:
        print(f"Warning: Compatibility check failed: {e}")
