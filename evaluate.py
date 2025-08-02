import requests
import time
import json

# --- Configuration ---
# IMPORTANT: Replace this with your current ngrok URL
API_URL = "https://a5af63e340fb.ngrok-free.app/api/v1/hackrx/run" 
BEARER_TOKEN = "ac0ac1082ad0be4b45e97d50e02fd26a99a0dbfeaaf67f10515a87ce297fc647"
DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

# --- Your Test Questions ---
# Add more questions to this list for a better evaluation
QUESTIONS = [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?"
]

def run_evaluation():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }
    
    total_time = 0
    results = []

    print(f"--- Starting Evaluation on {API_URL} ---")

    for i, question in enumerate(QUESTIONS):
        print(f"\n[{i+1}/{len(QUESTIONS)}] Testing Question: {question}")
        
        payload = {
            "documents": DOCUMENT_URL,
            "questions": [question] # Send one question at a time
        }
        
        try:
            start_time = time.time()
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=600) # 10-minute timeout            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            if response.status_code == 200:
                answer = response.json().get("answers", ["Error: No answer found"])[0]
                print(f"✅ Answer: {answer}")
                print(f"⏱️  Time: {response_time:.2f} seconds")
                results.append({"question": question, "answer": answer, "status": "Success"})
            else:
                print(f"❌ ERROR: Status Code {response.status_code} - {response.text}")
                results.append({"question": question, "answer": response.text, "status": "Error"})

        except requests.exceptions.RequestException as e:
            print(f"❌ CRITICAL ERROR: {e}")
            results.append({"question": question, "answer": str(e), "status": "Critical Error"})
    
    avg_time = total_time / len(QUESTIONS) if QUESTIONS else 0
    print("\n--- Evaluation Complete ---")
    print(f"Average Response Time: {avg_time:.2f} seconds")

if __name__ == "__main__":
    run_evaluation()