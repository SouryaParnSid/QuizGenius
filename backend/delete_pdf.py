#!/usr/bin/env python3
"""
Simple script to delete one of your PDFs from RAG storage
"""
import requests

def delete_smaller_pdf():
    """Delete the smaller PDF (5 chunks)"""
    source_file = 'C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmp2iilos1g.pdf'
    return delete_pdf_by_source(source_file)

def delete_larger_pdf():
    """Delete the larger PDF (96 chunks)"""
    source_file = 'C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmpcinoff34.pdf'
    return delete_pdf_by_source(source_file)

def delete_pdf_by_source(source_file):
    """Delete all chunks from a specific PDF source file"""
    try:
        print(f"🔍 Finding chunks for: {source_file}")
        
        # Get all documents
        response = requests.get('http://localhost:8001/documents')
        if response.status_code != 200:
            print(f"❌ Error getting documents: {response.status_code}")
            return False
        
        data = response.json()
        documents = data.get('documents', [])
        
        # Find chunks from this specific PDF
        target_chunks = []
        for doc in documents:
            doc_source = doc.get('metadata', {}).get('source_file', '')
            if doc_source == source_file:
                target_chunks.append(doc['id'])
        
        if not target_chunks:
            print(f"❌ No chunks found for: {source_file}")
            return False
        
        print(f"📊 Found {len(target_chunks)} chunks to delete")
        
        # Delete each chunk
        deleted_count = 0
        for chunk_id in target_chunks:
            try:
                delete_response = requests.delete(f'http://localhost:8001/documents/{chunk_id}')
                if delete_response.status_code == 200:
                    deleted_count += 1
                    print(f"   ✅ Deleted chunk {deleted_count}/{len(target_chunks)}")
                else:
                    print(f"   ❌ Failed to delete chunk: {chunk_id}")
            except Exception as e:
                print(f"   ❌ Error deleting chunk {chunk_id}: {e}")
        
        print(f"\n🎉 SUCCESS! Deleted {deleted_count}/{len(target_chunks)} chunks from the PDF")
        
        # Show updated statistics
        print("\n📊 Updated storage:")
        response = requests.get('http://localhost:8001/documents')
        if response.status_code == 200:
            data = response.json()
            remaining_docs = len(data.get('documents', []))
            print(f"   • Remaining document chunks: {remaining_docs}")
        
        return deleted_count == len(target_chunks)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=== PDF DELETION TOOL ===\n")
    print("Your current PDFs:")
    print("   1. Smaller PDF: 5 chunks (tmp2iilos1g.pdf)")
    print("   2. Larger PDF: 96 chunks (tmpcinoff34.pdf)")
    print()
    
    choice = input("Which PDF do you want to delete? (1 for smaller, 2 for larger): ").strip()
    
    if choice == '1':
        print("\n🗑️  Deleting SMALLER PDF (5 chunks)...")
        success = delete_smaller_pdf()
    elif choice == '2':
        print("\n🗑️  Deleting LARGER PDF (96 chunks)...")
        success = delete_larger_pdf()
    else:
        print("❌ Invalid choice. Please enter 1 or 2.")
        return
    
    if success:
        print("\n✅ PDF successfully deleted from RAG storage!")
    else:
        print("\n❌ Some errors occurred during deletion.")

if __name__ == "__main__":
    main()
