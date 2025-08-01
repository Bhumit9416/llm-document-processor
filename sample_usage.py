import os
import json
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the DocumentProcessor
from src.document_processor.processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Sample queries
sample_queries = [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?",
    "What is the No Claim Discount (NCD) offered in this policy?",
    "Is there a benefit for preventive health check-ups?",
    "How does the policy define a 'Hospital'?",
    "What is the extent of coverage for AYUSH treatments?",
    "Are there any sub-limits on room rent and ICU charges for Plan A?"
]

# Sample document URL
sample_document = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"

# For local testing, use the local sample policy file
local_document = os.path.join(os.path.dirname(__file__), "data", "sample_policy.txt")

def main():
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Process each query
    results = []
    
    print("Processing queries...")
    
    for i, query in enumerate(sample_queries):
        print(f"\nQuery {i+1}: {query}")
        
        # Process the query using the local document for testing
        # In production, use the sample_document URL
        result = processor.process_query(query, [local_document])
        
        # Extract the answer
        if isinstance(result, dict) and "justification" in result and "reason" in result["justification"]:
            # If the result is a structured decision
            answer = result["justification"]["reason"]
        else:
            # Fallback to a simple answer
            answer = "Unable to determine a specific answer based on the provided documents."
        
        print(f"Answer: {answer}")
        
        # Add to results
        results.append({
            "query": query,
            "answer": answer
        })
    
    # Save the results to a file
    with open("results.json", "w") as f:
        json.dump({"results": results}, f, indent=2)
    
    print("\nResults saved to results.json")

if __name__ == "__main__":
    main()