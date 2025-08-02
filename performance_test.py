import time
import requests
import json
import statistics
from typing import List, Dict

# Test configuration
API_URL = "http://localhost:8080/api/v1"
API_KEY = "ac0ac1082ad0be4b45e97d50e02fd26a99a0dbfeaaf67f10515a87ce297fc647"
SAMPLE_DOCUMENT = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

# Test questions with expected answer patterns
TEST_QUESTIONS = [
    {
        "question": "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "expected_keywords": ["30 days", "grace period", "premium"]
    },
    {
        "question": "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "expected_keywords": ["waiting period", "pre-existing", "2 years", "4 years"]
    },
    {
        "question": "What are the coverage limits for hospitalization expenses?",
        "expected_keywords": ["coverage", "limit", "hospitalization"]
    }
]

def test_api_performance(num_runs: int = 5) -> Dict:
    """Test API performance and accuracy"""
    print(f"Running performance test with {num_runs} iterations...")
    
    results = []
    response_times = []
    accuracy_scores = []
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}")
        
        start_time = time.time()
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "documents": SAMPLE_DOCUMENT,
            "questions": [q["question"] for q in TEST_QUESTIONS]
        }
        
        try:
            response = requests.post(
                f"{API_URL}/hackrx/run",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                answers = data.get("answers", [])
                
                # Calculate accuracy for this run
                run_accuracy = calculate_accuracy(answers)
                accuracy_scores.append(run_accuracy)
                
                results.append({
                    "run": run + 1,
                    "response_time": response_time,
                    "accuracy": run_accuracy,
                    "answers": answers,
                    "status": "success"
                })
                
                print(f"  Response time: {response_time:.2f}s")
                print(f"  Accuracy: {run_accuracy:.2f}%")
                
            else:
                print(f"  Error: HTTP {response.status_code}")
                results.append({
                    "run": run + 1,
                    "response_time": response_time,
                    "accuracy": 0,
                    "status": "error",
                    "error": response.text
                })
                accuracy_scores.append(0)
                
        except Exception as e:
            response_time = time.time() - start_time
            response_times.append(response_time)
            accuracy_scores.append(0)
            
            print(f"  Exception: {str(e)}")
            results.append({
                "run": run + 1,
                "response_time": response_time,
                "accuracy": 0,
                "status": "exception",
                "error": str(e)
            })
    
    # Calculate summary statistics
    avg_response_time = statistics.mean(response_times) if response_times else 0
    avg_accuracy = statistics.mean(accuracy_scores) if accuracy_scores else 0
    max_response_time = max(response_times) if response_times else 0
    min_response_time = min(response_times) if response_times else 0
    
    summary = {
        "total_runs": num_runs,
        "avg_response_time": avg_response_time,
        "max_response_time": max_response_time,
        "min_response_time": min_response_time,
        "avg_accuracy": avg_accuracy,
        "success_rate": len([r for r in results if r["status"] == "success"]) / num_runs * 100,
        "results": results
    }
    
    return summary

def calculate_accuracy(answers: List[str]) -> float:
    """Calculate accuracy based on keyword matching"""
    if not answers or len(answers) != len(TEST_QUESTIONS):
        return 0.0
    
    total_score = 0
    
    for i, answer in enumerate(answers):
        if i < len(TEST_QUESTIONS):
            expected_keywords = TEST_QUESTIONS[i]["expected_keywords"]
            answer_lower = answer.lower()
            
            # Count keyword matches
            matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
            question_score = (matches / len(expected_keywords)) * 100
            total_score += question_score
    
    return total_score / len(TEST_QUESTIONS)

def print_summary(summary: Dict):
    """Print performance summary"""
    print("\n" + "="*50)
    print("PERFORMANCE TEST SUMMARY")
    print("="*50)
    print(f"Total Runs: {summary['total_runs']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Average Response Time: {summary['avg_response_time']:.2f}s")
    print(f"Max Response Time: {summary['max_response_time']:.2f}s")
    print(f"Min Response Time: {summary['min_response_time']:.2f}s")
    print(f"Average Accuracy: {summary['avg_accuracy']:.1f}%")
    
    # Performance targets
    print("\nTARGET ANALYSIS:")
    print(f"Response Time Target (<30s): {'✅ PASS' if summary['avg_response_time'] < 30 else '❌ FAIL'}")
    print(f"Accuracy Target (>70%): {'✅ PASS' if summary['avg_accuracy'] > 70 else '❌ FAIL'}")
    print(f"Success Rate Target (>95%): {'✅ PASS' if summary['success_rate'] > 95 else '❌ FAIL'}")

if __name__ == "__main__":
    # Test health endpoint first
    try:
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health check exception: {str(e)}")
    
    # Run performance test
    summary = test_api_performance(num_runs=3)
    print_summary(summary)
    
    # Save results
    with open("performance_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n📊 Results saved to performance_results.json")