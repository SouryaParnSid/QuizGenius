#!/usr/bin/env python3
"""
Check how many documents and PDFs are stored in the RAG system
"""
import requests
import json
from collections import defaultdict

def check_rag_documents():
    try:
        # Get all documents from RAG API
        response = requests.get('http://localhost:8001/documents')
        
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return
            
        data = response.json()
        
        print("=== RAG DOCUMENT STORAGE ANALYSIS ===\n")
        
        # Basic statistics
        total_count = data.get('total_count', 0)
        documents = data.get('documents', [])
        
        print(f"📊 SUMMARY:")
        print(f"   • Total document chunks: {len(documents)}")
        print(f"   • Total count reported: {total_count}")
        
        if not documents:
            print("\n❌ No documents found in storage!")
            return
        
        # Analyze by source file type
        source_files = set()
        file_types = defaultdict(int)
        upload_methods = defaultdict(int)
        
        pdf_chunks = 0
        text_chunks = 0
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            
            # Count source files
            source_file = metadata.get('source_file', 'unknown')
            if source_file != 'unknown':
                source_files.add(source_file)
            
            # Count file types
            file_type = metadata.get('file_type', 'unknown')
            if 'pdf' in file_type.lower():
                pdf_chunks += 1
            elif 'text' in file_type.lower():
                text_chunks += 1
            
            file_types[file_type] += 1
            
            # Count upload methods
            upload_method = metadata.get('uploaded_via', 'unknown')
            upload_methods[upload_method] += 1
        
        print(f"\n📁 FILE ANALYSIS:")
        print(f"   • Unique source files: {len(source_files)}")
        print(f"   • PDF chunks: {pdf_chunks}")
        print(f"   • Text chunks: {text_chunks}")
        
        print(f"\n📋 FILE TYPES:")
        for file_type, count in sorted(file_types.items()):
            print(f"   • {file_type}: {count} chunks")
        
        print(f"\n📤 UPLOAD METHODS:")
        for method, count in sorted(upload_methods.items()):
            print(f"   • {method}: {count} chunks")
        
        print(f"\n📄 SOURCE FILES:")
        if source_files:
            pdf_files = [f for f in source_files if f.lower().endswith('.pdf')]
            other_files = [f for f in source_files if not f.lower().endswith('.pdf')]
            
            if pdf_files:
                print(f"   📑 PDF Files ({len(pdf_files)}):")
                for pdf_file in sorted(pdf_files):
                    # Count chunks for this file
                    file_chunks = sum(1 for doc in documents 
                                    if doc.get('metadata', {}).get('source_file') == pdf_file)
                    print(f"      • {pdf_file} ({file_chunks} chunks)")
            
            if other_files:
                print(f"   📝 Other Files ({len(other_files)}):")
                for other_file in sorted(other_files):
                    file_chunks = sum(1 for doc in documents 
                                    if doc.get('metadata', {}).get('source_file') == other_file)
                    print(f"      • {other_file} ({file_chunks} chunks)")
        else:
            print("   • No specific source files found in metadata")
        
        # Storage size estimate
        content_length = sum(len(doc.get('content', '')) for doc in documents)
        print(f"\n💾 STORAGE INFO:")
        print(f"   • Total content length: {content_length:,} characters")
        print(f"   • Estimated size: {content_length / 1024:.1f} KB")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to RAG API: {e}")
        print("Make sure the RAG API is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Error analyzing documents: {e}")

if __name__ == "__main__":
    check_rag_documents()
