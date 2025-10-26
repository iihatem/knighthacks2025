"""Simple test for AI agents"""
import requests

BASE_URL = "http://localhost:5001"

def test_orchestrator():
    """Test the orchestrator agent"""
    print("\n🧪 Testing Orchestrator Agent...")
    
    test_data = {
        "case_id": "test-001",
        "query": "Draft an email to John Smith about his settlement offer"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/agent/process",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test passed!")
            print(f"\nResponse: {result}")
            return True
        else:
            print(f"❌ Test failed with status {response.status_code}")
            print(f"Error: {response.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: flask run --port 5001")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI AGENT TEST")
    print("=" * 50)
    test_orchestrator()
