import os
import time
import json
import statistics
from datetime import datetime

# Import the document processor
import sys
sys.path.append(os.path.abspath("."))

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

# Sample questions
SAMPLE_QUESTIONS = [
    "What is the grace period for premium payment?",
    "What is the waiting period for pre-existing diseases?",
    "Does this policy cover maternity expenses?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered?",
    "What is the No Claim Discount offered?",
    "Is there a benefit for preventive health check-ups?",
    "How does the policy define a 'Hospital'?",
    "What is the extent of coverage for AYUSH treatments?",
    "Are there any sub-limits on room rent and ICU charges?"
]

def run_benchmark(num_runs=3):
    """Run benchmark tests on the document processor"""
    print(f"Running benchmark with {num_runs} iterations...")
    
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Load the document
    document_path = os.path.abspath(SAMPLE_DOCUMENT)
    if not os.path.exists(document_path):
        print(f"Sample document not found: {document_path}")
        return
    
    # Metrics to track
    metrics = {
        "query_parsing_time": [],
        "embedding_search_time": [],
        "decision_evaluation_time": [],
        "total_processing_time": [],
        "token_usage": []
    }
    
    # Run the benchmark
    for i in range(num_runs):
        print(f"\nRun {i+1}/{num_runs}")
        
        for j, question in enumerate(SAMPLE_QUESTIONS):
            print(f"  Processing question {j+1}/{len(SAMPLE_QUESTIONS)}: {question}")
            
            # Process the query and measure time
            start_time = time.time()
            
            # Track individual component times
            query_parsing_start = time.time()
            structured_query = processor.query_parser.parse_query(question)
            query_parsing_time = time.time() - query_parsing_start
            
            embedding_search_start = time.time()
            relevant_clauses = processor.embedding_search.search(structured_query, document_path)
            embedding_search_time = time.time() - embedding_search_start
            
            decision_evaluation_start = time.time()
            result = processor.decision_evaluator.evaluate(structured_query, relevant_clauses)
            decision_evaluation_time = time.time() - decision_evaluation_start
            
            total_time = time.time() - start_time
            
            # Record metrics
            metrics["query_parsing_time"].append(query_parsing_time)
            metrics["embedding_search_time"].append(embedding_search_time)
            metrics["decision_evaluation_time"].append(decision_evaluation_time)
            metrics["total_processing_time"].append(total_time)
            
            # Estimate token usage (this is a rough estimate)
            token_estimate = len(question) // 4 + len(str(relevant_clauses)) // 4 + len(str(result)) // 4
            metrics["token_usage"].append(token_estimate)
            
            print(f"    Time: {total_time:.2f}s (Parse: {query_parsing_time:.2f}s, Search: {embedding_search_time:.2f}s, Evaluate: {decision_evaluation_time:.2f}s)")
    
    # Calculate and display statistics
    print("\n=== Benchmark Results ===")
    print(f"Total questions processed: {num_runs * len(SAMPLE_QUESTIONS)}")
    
    for metric, values in metrics.items():
        if values:
            print(f"\n{metric.replace('_', ' ').title()}:")
            print(f"  Min: {min(values):.4f}")
            print(f"  Max: {max(values):.4f}")
            print(f"  Mean: {statistics.mean(values):.4f}")
            print(f"  Median: {statistics.median(values):.4f}")
            if len(values) > 1:
                print(f"  Std Dev: {statistics.stdev(values):.4f}")
    
    # Save results to file
    results = {
        "timestamp": datetime.now().isoformat(),
        "num_runs": num_runs,
        "num_questions": len(SAMPLE_QUESTIONS),
        "metrics": {
            metric: {
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0
            } for metric, values in metrics.items() if values
        }
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to benchmark_results.json")

def main():
    """Main function to run the benchmark"""
    print("=== LLM Document Processing System Benchmark ===")
    
    # Run the benchmark
    run_benchmark(num_runs=3)

if __name__ == "__main__":
    main()