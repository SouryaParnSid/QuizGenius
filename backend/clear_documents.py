#!/usr/bin/env python3
"""
Clear documents from RAG storage using bulk operations
"""
import requests
import json

def clear_all_documents():
    """Clear all documents from RAG storage"""
    try:
        print("🗑️  Clearing ALL documents from RAG storage...")
        
        # Use the bulk clear endpoint
        response = requests.delete('http://localhost:8001/documents?confirm=true')
        
        if response.status_code == 200:
            print("✅ Successfully cleared all documents!")
            return True
        else:
            print(f"❌ Failed to clear documents. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing documents: {e}")
        return False

def selective_delete_by_rebuilding():
    """Delete specific PDF by rebuilding the knowledge base without it"""
    try:
        print("🔄 Alternative approach: Rebuilding knowledge base...")
        
        # First, get all documents
        response = requests.get('http://localhost:8001/documents')
        if response.status_code != 200:
            print(f"❌ Error getting documents: {response.status_code}")
            return False
        
        data = response.json()
        documents = data.get('documents', [])
        
        # Find documents we want to KEEP (smaller PDF + text files)
        keep_sources = [
            'C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmp2iilos1g.pdf',  # Smaller PDF
            'C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmp8x_5yr0_.txt',   # Text file 1
            'C:\\Users\\Sourya Sarkar\\AppData\\Local\\Temp\\tmpbfmu2wkj.txt'    # Text file 2
        ]
        
        keep_content = []
        for doc in documents:
            source_file = doc.get('metadata', {}).get('source_file', '')
            if source_file in keep_sources:
                keep_content.append({
                    'content': doc.get('content', ''),
                    'metadata': doc.get('metadata', {})
                })
        
        print(f"📊 Found {len(keep_content)} chunks to preserve")
        
        # Clear all documents first
        if not clear_all_documents():
            return False
        
        print("⏳ Waiting for clear operation to complete...")
        import time
        time.sleep(2)
        
        # Re-upload the content we want to keep
        print(f"📤 Re-uploading {len(keep_content)} chunks...")
        
        for i, item in enumerate(keep_content):
            try:
                # Use the text ingestion endpoint to re-add content
                upload_data = {
                    'text': item['content'],
                    'source_name': item['metadata'].get('source_file', f'restored_content_{i}'),
                    'chunking_strategy': 'recursive',
                    'custom_metadata': json.dumps(item['metadata'])
                }
                
                response = requests.post('http://localhost:8001/ingest/text', json=upload_data)
                
                if response.status_code == 200:
                    print(f"   ✅ Restored chunk {i+1}/{len(keep_content)}")
                else:
                    print(f"   ❌ Failed to restore chunk {i+1}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error restoring chunk {i+1}: {e}")
        
        print("\n🎉 Rebuilding complete!")
        
        # Check final status
        response = requests.get('http://localhost:8001/documents')
        if response.status_code == 200:
            final_data = response.json()
            final_count = len(final_data.get('documents', []))
            print(f"📊 Final document count: {final_count}")
            return True
        
        return True
        
    except Exception as e:
        print(f"❌ Error in selective delete: {e}")
        return False

def main():
    print("=== RAG DOCUMENT DELETION TOOL (FIXED) ===\n")
    
    print("Current situation:")
    print("   • Large PDF deletion failed using individual chunk deletion")
    print("   • We'll use an alternative approach")
    print()
    
    print("Options:")
    print("   1. Clear ALL documents (start fresh)")
    print("   2. Smart rebuild (keep smaller PDF + text files, remove larger PDF)")
    print()
    
    choice = input("Choose an option (1 or 2): ").strip()
    
    if choice == '1':
        print("\n🗑️  Clearing ALL documents...")
        success = clear_all_documents()
    elif choice == '2':
        print("\n🔄 Using smart rebuild approach...")
        success = selective_delete_by_rebuilding()
    else:
        print("❌ Invalid choice.")
        return
    
    if success:
        print("\n✅ Operation completed successfully!")
        print("\n💡 You can now upload new documents using the RAG Quiz Generator interface.")
    else:
        print("\n❌ Operation failed. You may need to restart the RAG API.")

if __name__ == "__main__":
    main()
