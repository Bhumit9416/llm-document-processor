import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("API_KEY", "ac0ac1082ad0be4b45e97d50e02fd26a99a0dbfeaaf67f10515a87ce297fc647")

# Sample document URL
SAMPLE_DOCUMENT = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

# Sample questions
SAMPLE_QUESTIONS = [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?"
]

def test_health_endpoint():
    """Test the health endpoint"""
    url = f"{API_URL}/health"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        print("Health endpoint test: SUCCESS")
        print(f"Response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print("Health endpoint test: FAILED")
        print(f"Error: {e}")
        return False

def test_process_endpoint():
    """Test the process endpoint"""
    url = f"{API_URL}/hackrx/run"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "documents": SAMPLE_DOCUMENT,
        "questions": SAMPLE_QUESTIONS
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        print("Process endpoint test: SUCCESS")
        print("Answers:")
        for i, answer in enumerate(response.json()["answers"]):
            print(f"Q{i+1}: {SAMPLE_QUESTIONS[i]}")
            print(f"A{i+1}: {answer}")
            print()
        
        return True
    except requests.exceptions.RequestException as e:
        print("Process endpoint test: FAILED")
        print(f"Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def main():
    """Main function to run the tests"""
    print("=== API Tests ===")
    
    # Test health endpoint
    health_success = test_health_endpoint()
    print()
    
    # Test process endpoint if health endpoint is successful
    if health_success:
        test_process_endpoint()

if __name__ == "__main__":
    main()