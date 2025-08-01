import os
import sys
import json
import time
import statistics
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath("."))

# Import the document processor
try:
    from src.document_processor.processor import DocumentProcessor
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Sample document path
SAMPLE_DOCUMENT = "data/sample_policy.txt"

# Sample questions with expected answers
EVALUATION_QUESTIONS = [
    {
        "question": "What is the grace period for premium payment?",
        "expected_answer": "A grace period of thirty days is allowed following the expiry of the policy period to maintain continuity of coverage.",
        "weight": 1.0
    },
    {
        "question": "What is the waiting period for pre-existing diseases?",
        "expected_answer": "All Pre-Existing Diseases and their direct complications shall not be covered until 36 months of continuous coverage have elapsed since inception of the first policy with the Company.",
        "weight": 1.0
    },
    {
        "question": "Does this policy cover maternity expenses?",
        "expected_answer": "Yes, the policy covers maternity expenses incurred for the delivery of a child and/or expenses related to medically necessary and lawful termination of pregnancy, subject to the female insured person being continuously covered for at least 24 months and limited to two deliveries or terminations.",
        "weight": 1.0
    },
    {
        "question": "What is the waiting period for cataract surgery?",
        "expected_answer": "The waiting period for cataract surgery is 24 months.",
        "weight": 1.0
    },
    {
        "question": "Are the medical expenses for an organ donor covered?",
        "expected_answer": "Yes, the policy covers medical expenses incurred by the Insured Person towards in-patient hospitalization of an organ donor for harvesting the organ, provided the organ donation complies with the Transplantation of Human Organs Act 1994.",
        "weight": 1.0
    }
]

def calculate_similarity(answer1, answer2):
    """Calculate similarity between two answers (simple implementation)"""
    # Convert to lowercase and remove punctuation
    a1 = ''.join(c.lower() for c in answer1 if c.isalnum() or c.isspace())
    a2 = ''.join(c.lower() for c in answer2 if c.isalnum() or c.isspace())
    
    # Split into words
    words1 = set(a1.split())
    words2 = set(a2.split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0

def evaluate_accuracy(results):
    """Evaluate accuracy of the answers"""
    scores = []
    
    for i, result in enumerate(results):
        expected = EVALUATION_QUESTIONS[i]["expected_answer"]
        actual = result["answer"]
        weight = EVALUATION_QUESTIONS[i]["weight"]
        
        # Calculate similarity score
        similarity = calculate_similarity(expected, actual)
        weighted_score = similarity * weight
        
        scores.append({
            "question": EVALUATION_QUESTIONS[i]["question"],
            "similarity": similarity,
            "weighted_score": weighted_score
        })
    
    # Calculate overall accuracy
    total_weight = sum(q["weight"] for q in EVALUATION_QUESTIONS)
    overall_accuracy = sum(s["weighted_score"] for s in scores) / total_weight if total_weight > 0 else 0
    
    return {
        "scores": scores,
        "overall_accuracy": overall_accuracy
    }

def evaluate_token_efficiency(results):
    """Evaluate token efficiency"""
    # Estimate token usage (rough approximation)
    token_counts = []
    
    for result in results:
        # Estimate tokens in question
        question_tokens = len(result["question"]) // 4
        
        # Estimate tokens in answer
        answer_tokens = len(result["answer"]) // 4
        
        # Estimate tokens in justification
        justification_tokens = len(result["justification"]) // 4
        
        # Total tokens
        total_tokens = question_tokens + answer_tokens + justification_tokens
        token_counts.append(total_tokens)
    
    # Calculate statistics
    avg_tokens = statistics.mean(token_counts) if token_counts else 0
    max_tokens = max(token_counts) if token_counts else 0
    min_tokens = min(token_counts) if token_counts else 0
    
    return {
        "token_counts": token_counts,
        "average_tokens": avg_tokens,
        "max_tokens": max_tokens,
        "min_tokens": min_tokens
    }

def evaluate_latency(results):
    """Evaluate latency of the system"""
    times = [result["time"] for result in results]
    
    # Calculate statistics
    avg_time = statistics.mean(times) if times else 0
    max_time = max(times) if times else 0
    min_time = min(times) if times else 0
    
    if len(times) > 1:
        std_dev = statistics.stdev(times)
    else:
        std_dev = 0
    
    return {
        "times": times,
        "average_time": avg_time,
        "max_time": max_time,
        "min_time": min_time,
        "std_dev": std_dev
    }

def evaluate_explainability(results):
    """Evaluate explainability of the system"""
    explanation_scores = []
    
    for result in results:
        # Check if justification references specific clauses
        has_clause_references = "clause" in result["justification"].lower() or "section" in result["justification"].lower()
        
        # Check if justification has reasonable length
        has_reasonable_length = 50 <= len(result["justification"]) <= 500
        
        # Check if justification is relevant to the question
        relevance_score = calculate_similarity(result["question"], result["justification"])
        
        # Calculate explainability score (simple heuristic)
        score = (0.4 if has_clause_references else 0) + \
                (0.3 if has_reasonable_length else 0) + \
                (0.3 * relevance_score)
        
        explanation_scores.append(score)
    
    # Calculate overall explainability score
    overall_score = statistics.mean(explanation_scores) if explanation_scores else 0
    
    return {
        "explanation_scores": explanation_scores,
        "overall_explainability": overall_score
    }

def run_evaluation():
    """Run the evaluation of the system"""
    print("=== System Evaluation ===\n")
    
    # Check if document exists
    document_path = os.path.abspath(SAMPLE_DOCUMENT)
    if not os.path.exists(document_path):
        print(f"Sample document not found: {document_path}")
        return
    
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Process each question
    results = []
    
    for i, question_data in enumerate(EVALUATION_QUESTIONS):
        question = question_data["question"]
        print(f"Processing question {i+1}/{len(EVALUATION_QUESTIONS)}: {question}")
        
        # Process the query and measure time
        start_time = time.time()
        result = processor.process_query(question, document_path)
        elapsed_time = time.time() - start_time
        
        # Print result
        print(f"Answer: {result['answer']}")
        print(f"Time: {elapsed_time:.2f} seconds\n")
        
        # Store result
        results.append({
            "question": question,
            "answer": result["answer"],
            "decision": result["decision"],
            "amount": result["amount"],
            "justification": result["justification"],
            "time": elapsed_time
        })
    
    # Evaluate the system
    accuracy_results = evaluate_accuracy(results)
    token_efficiency_results = evaluate_token_efficiency(results)
    latency_results = evaluate_latency(results)
    explainability_results = evaluate_explainability(results)
    
    # Calculate overall score
    overall_score = (
        accuracy_results["overall_accuracy"] * 0.4 +
        (1.0 - (token_efficiency_results["average_tokens"] / 1000)) * 0.2 +
        (1.0 - min(latency_results["average_time"] / 10.0, 1.0)) * 0.2 +
        explainability_results["overall_explainability"] * 0.2
    )
    
    # Print evaluation results
    print("=== Evaluation Results ===\n")
    print(f"Accuracy: {accuracy_results['overall_accuracy']:.4f}")
    print(f"Token Efficiency: {token_efficiency_results['average_tokens']:.2f} tokens per query")
    print(f"Latency: {latency_results['average_time']:.2f} seconds per query")
    print(f"Explainability: {explainability_results['overall_explainability']:.4f}")
    print(f"\nOverall Score: {overall_score:.4f}")
    
    # Save evaluation results to file
    evaluation_results = {
        "timestamp": datetime.now().isoformat(),
        "document_path": document_path,
        "accuracy": accuracy_results,
        "token_efficiency": token_efficiency_results,
        "latency": latency_results,
        "explainability": explainability_results,
        "overall_score": overall_score,
        "results": results
    }
    
    with open("evaluation_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    print("\nEvaluation results saved to evaluation_results.json")

def main():
    """Main function"""
    run_evaluation()

if __name__ == "__main__":
    main()