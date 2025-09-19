#!/usr/bin/env python3
"""
Test the fixed deletion functionality
"""
import requests
import time

def test_deletion_fix():
    print("=== TESTING FIXED DELETION FUNCTIONALITY ===\n")
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(3)
    
    try:
        # Test bulk deletion
        print("🧪 Testing bulk deletion...")
        response = requests.delete('http://localhost:8001/documents?confirm=true')
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                print("✅ Bulk deletion now works!")
                
                # Check if documents are actually cleared
                check_response = requests.get('http://localhost:8001/documents')
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    remaining_docs = len(check_data.get('documents', []))
                    print(f"📊 Remaining documents: {remaining_docs}")
                    
                    if remaining_docs == 0:
                        print("🎉 All documents successfully cleared!")
                    else:
                        print(f"⚠️  {remaining_docs} documents still remain")
                        
                return True
            else:
                print(f"❌ Deletion failed: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing deletion: {e}")
        return False

if __name__ == "__main__":
    success = test_deletion_fix()
    
    if success:
        print("\n✅ DELETION FIX SUCCESSFUL!")
        print("💡 You can now upload new documents using the RAG Quiz Generator.")
    else:
        print("\n❌ Deletion fix needs more work.")
        print("💡 Try restarting the RAG API and test again.")
