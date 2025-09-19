#!/usr/bin/env python3
"""
Delete specific documents from the RAG system
"""
import requests
import json

def list_documents_for_deletion():
    """List documents with their IDs so user can choose what to delete"""
    try:
        response = requests.get('http://localhost:8001/documents')
        
        if response.status_code != 200:
            print(f"Error: API returned status code {response.status_code}")
            return
            
        data = response.json()
        documents = data.get('documents', [])
        
        if not documents:
            print("No documents found in storage!")
            return
        
        # Group documents by source file
        source_groups = {}
        for doc in documents:
            source_file = doc.get('metadata', {}).get('source_file', 'unknown')
            if source_file not in source_groups:
                source_groups[source_file] = []
            source_groups[source_file].append(doc)
        
        print("=== DOCUMENTS AVAILABLE FOR DELETION ===\n")
        
        pdf_files = {k: v for k, v in source_groups.items() if k.lower().endswith('.pdf')}
        
        if pdf_files:
            print("📑 PDF FILES:")
            for i, (source_file, docs) in enumerate(pdf_files.items(), 1):
                print(f"   {i}. {source_file}")
                print(f"      • Chunks: {len(docs)}")
                print(f"      • Content size: {sum(len(d.get('content', '')) for d in docs):,} characters")
                print()
        
        other_files = {k: v for k, v in source_groups.items() if not k.lower().endswith('.pdf')}
        if other_files:
            print("📝 OTHER FILES:")
            for i, (source_file, docs) in enumerate(other_files.items(), len(pdf_files) + 1):
                print(f"   {i}. {source_file}")
                print(f"      • Chunks: {len(docs)}")
                print()
        
        return source_groups
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to RAG API: {e}")
        return None
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        return None

def delete_documents_by_source(source_file, documents_dict):
    """Delete all documents from a specific source file"""
    if source_file not in documents_dict:
        print(f"❌ Source file '{source_file}' not found!")
        return False
    
    docs = documents_dict[source_file]
    doc_ids = [doc['id'] for doc in docs]
    
    print(f"🗑️  Deleting {len(doc_ids)} chunks from: {source_file}")
    
    deleted_count = 0
    failed_count = 0
    
    for doc_id in doc_ids:
        try:
            response = requests.delete(f'http://localhost:8001/documents/{doc_id}')
            
            if response.status_code == 200:
                deleted_count += 1
                print(f"   ✅ Deleted chunk: {doc_id}")
            else:
                failed_count += 1
                print(f"   ❌ Failed to delete: {doc_id} (Status: {response.status_code})")
                
        except Exception as e:
            failed_count += 1
            print(f"   ❌ Error deleting {doc_id}: {e}")
    
    print(f"\n📊 DELETION SUMMARY:")
    print(f"   • Successfully deleted: {deleted_count} chunks")
    print(f"   • Failed to delete: {failed_count} chunks")
    
    return failed_count == 0

def main():
    print("RAG DOCUMENT DELETION TOOL\n")
    
    # List available documents
    documents_dict = list_documents_for_deletion()
    
    if not documents_dict:
        return
    
    # Show your specific options
    pdf_files = [k for k in documents_dict.keys() if k.lower().endswith('.pdf')]
    
    if len(pdf_files) >= 2:
        print("🎯 YOUR PDF FILES:")
        print("   1. Smaller PDF (5 chunks) - C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmp2iilos1g.pdf")
        print("   2. Larger PDF (96 chunks) - C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmpcinoff34.pdf")
        print()
        print("⚠️  To delete a PDF, uncomment one of the lines below and run the script:")
        print()
        print("# To delete the SMALLER PDF (5 chunks):")
        print("# delete_documents_by_source('C:\\\\Users\\\\Sourya Sarkar\\\\AppData\\\\Local\\\\Temp\\\\tmp2iilos1g.pdf', documents_dict)")
        print()
        print("# To delete the LARGER PDF (96 chunks):")
        print("# delete_documents_by_source('C:\\\\Users\\\\Sourya Sarkar\\\\AppData\\\\Local\\\\Temp\\\\tmpcinoff34.pdf', documents_dict)")
        print()
        print("💡 RECOMMENDATION: Delete the smaller PDF to keep the larger one with more content.")
    
    # Uncomment ONE of these lines to actually delete:
    
    # DELETE SMALLER PDF (uncomment next line):
    # delete_documents_by_source('C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmp2iilos1g.pdf', documents_dict)
    
    # DELETE LARGER PDF (uncomment next line):
    # delete_documents_by_source('C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmpcinoff34.pdf', documents_dict)

if __name__ == "__main__":
    main()
