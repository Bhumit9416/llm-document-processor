import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modules to test
from src.document_processor.processor import DocumentProcessor
from src.query_parser.parser import QueryParser
from src.retrieval.embedding_search import EmbeddingSearch
from src.decision_engine.evaluator import DecisionEvaluator

class TestDocumentProcessor(unittest.TestCase):
    """Test cases for the DocumentProcessor class"""
    
    def setUp(self):
        """Set up the test environment"""
        # Mock the dependencies
        self.query_parser_mock = MagicMock(spec=QueryParser)
        self.embedding_search_mock = MagicMock(spec=EmbeddingSearch)
        self.decision_evaluator_mock = MagicMock(spec=DecisionEvaluator)
        
        # Create patches
        self.query_parser_patch = patch('src.document_processor.processor.QueryParser', return_value=self.query_parser_mock)
        self.embedding_search_patch = patch('src.document_processor.processor.EmbeddingSearch', return_value=self.embedding_search_mock)
        self.decision_evaluator_patch = patch('src.document_processor.processor.DecisionEvaluator', return_value=self.decision_evaluator_mock)
        
        # Start the patches
        self.query_parser_patch.start()
        self.embedding_search_patch.start()
        self.decision_evaluator_patch.start()
        
        # Create the document processor
        self.document_processor = DocumentProcessor()
    
    def tearDown(self):
        """Clean up after the tests"""
        # Stop the patches
        self.query_parser_patch.stop()
        self.embedding_search_patch.stop()
        self.decision_evaluator_patch.stop()
    
    def test_process_query(self):
        """Test the process_query method"""
        # Set up the mock returns
        self.query_parser_mock.parse.return_value = {
            "age": "46",
            "gender": "male",
            "procedure": "knee surgery",
            "location": "Pune",
            "policy_duration": "3 months",
            "query_type": "coverage"
        }
        
        self.embedding_search_mock.search.return_value = [
            {
                "clause": "Knee surgery is covered under the policy after a waiting period of 2 months.",
                "source": "policy.pdf",
                "score": 0.85
            }
        ]
        
        self.decision_evaluator_mock.evaluate.return_value = {
            "decision": "APPROVED",
            "amount": 50000,
            "justification": {
                "reason": "Knee surgery is covered under the policy as the waiting period of 2 months has been satisfied.",
                "clause_references": ["policy.pdf"]
            }
        }
        
        # Call the method
        query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
        documents = ["https://example.com/policy.pdf"]
        result = self.document_processor.process_query(query, documents)
        
        # Check the result
        self.assertEqual(result["decision"], "APPROVED")
        self.assertEqual(result["amount"], 50000)
        self.assertIn("Knee surgery is covered", result["justification"]["reason"])
        
        # Verify the mocks were called correctly
        self.query_parser_mock.parse.assert_called_once_with(query)
        self.embedding_search_mock.search.assert_called_once()
        self.decision_evaluator_mock.evaluate.assert_called_once()

if __name__ == '__main__':
    unittest.main()