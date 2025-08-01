import os
import sys
import json
import time
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

def test_document_processor(document_path, document_type):
    """Test the document processor with a specific document type"""
    print(f"\n=== Testing Document Processor with {document_type} ===\n")
    
    # Check if document exists
    if not os.path.exists(document_path):
        print(f"Document not found: {document_path}")
        return False
    
    # Initialize the document processor
    processor = DocumentProcessor()
    
    # Process each question
    results = []
    total_time = 0
    
    for i, question in enumerate(SAMPLE_QUESTIONS):
        print(f"Processing question {i+1}/{len(SAMPLE_QUESTIONS)}: {question}")
        
        # Process the query and measure time
        start_time = time.time()
        result = processor.process_query(question, document_path)
        elapsed_time = time.time() - start_time
        total_time += elapsed_time
        
        # Print result
        print(f"Answer: {result['answer']}")
        print(f"Decision: {result['decision']}")
        print(f"Amount: {result['amount']}")
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
    
    # Calculate average time
    avg_time = total_time / len(SAMPLE_QUESTIONS) if SAMPLE_QUESTIONS else 0
    print(f"Average processing time: {avg_time:.2f} seconds")
    
    # Save results to file
    output_file = f"results_{document_type.lower()}.json"
    with open(output_file, "w") as f:
        json.dump({
            "document_type": document_type,
            "document_path": document_path,
            "timestamp": datetime.now().isoformat(),
            "average_time": avg_time,
            "results": results
        }, f, indent=2)
    
    print(f"Results saved to {output_file}")
    return True

def main():
    """Main function to test the document processor with different document types"""
    print("=== Document Processor Test ===\n")
    
    # Define test documents
    test_documents = [
        ("data/sample_policy.txt", "TXT"),
        ("data/sample_policy.pdf", "PDF"),
        ("data/sample_policy.docx", "DOCX"),
        ("data/sample_policy_email.eml", "Email"),
        ("data/sample_policies.csv", "CSV"),
        ("data/sample_policies.json", "JSON")
    ]
    
    # Test each document type
    success_count = 0
    for document_path, document_type in test_documents:
        if os.path.exists(document_path):
            if test_document_processor(document_path, document_type):
                success_count += 1
        else:
            print(f"Skipping {document_type} test: {document_path} not found")
    
    # Summary
    print(f"\nSuccessfully tested {success_count}/{len(test_documents)} document types")

if __name__ == "__main__":
    main()