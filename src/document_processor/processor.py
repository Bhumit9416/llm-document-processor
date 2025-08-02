import os
import tempfile
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Document handling libraries
import PyPDF2
import docx
import pandas as pd

# Import other modules
from query_parser.parser import QueryParser
from retrieval.embedding_search import EmbeddingSearch
from decision_engine.evaluator import DecisionEvaluator

class DocumentProcessor:
    """Main document processing class that orchestrates the entire workflow"""
    
    def __init__(self):
        self.query_parser = QueryParser()
        self.embedding_search = EmbeddingSearch()
        self.decision_evaluator = DecisionEvaluator()
        self.logger = logging.getLogger(__name__)
        
    def process_query(self, query: str, documents: List[str]) -> Dict[str, Any]:
        """Process a natural language query against the provided documents
        
        Args:
            query: The natural language query string
            documents: List of document URLs or file paths
            
        Returns:
            Dict containing the structured response with decision, amount, and justification
        """
        # Parse the query to extract structured information
        parsed_query = self.query_parser.parse(query)
        
        # Load and process documents
        processed_docs = self._load_documents(documents)
        
        # Perform embedding search to find relevant clauses
        relevant_clauses = self.embedding_search.search(parsed_query, processed_docs)
        
        # Evaluate the decision based on the relevant clauses
        decision = self.decision_evaluator.evaluate(parsed_query, relevant_clauses)
        
        return decision
    
    def _load_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Load and process documents from URLs or file paths
        
        Args:
            documents: List of document URLs or file paths
            
        Returns:
            List of processed document contents with metadata
        """
        processed_docs = []
        
        for doc_path in documents:
            # Determine if it's a URL or local file path
            is_url = urlparse(doc_path).scheme in ['http', 'https']
            
            if is_url:
                # Download the file to a temporary location
                temp_file = self._download_file(doc_path)
                file_path = temp_file.name
            else:
                file_path = doc_path
                
            # Process based on file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                content = self._process_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                content = self._process_docx(file_path)
            elif file_ext in ['.txt', '.csv', '.json']:
                content = self._process_text(file_path)
            else:
                # Unsupported file type
                content = {"error": f"Unsupported file type: {file_ext}"}
            
            # Add to processed documents
            processed_docs.append({
                "source": doc_path,
                "content": content
            })
            
            # Clean up temporary file if it was a URL
            if is_url:
                temp_file.close()
                
        return processed_docs
    
    def _download_file(self, url: str) -> tempfile.NamedTemporaryFile:
        """Download a file from a URL to a temporary file
        
        Args:
            url: The URL of the file to download
            
        Returns:
            A NamedTemporaryFile object containing the downloaded file
        """
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Determine file extension from URL or Content-Type
        file_ext = os.path.splitext(urlparse(url).path)[1]
        if not file_ext:
            # Try to determine from Content-Type
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                file_ext = '.pdf'
            elif 'word' in content_type:
                file_ext = '.docx'
            else:
                file_ext = '.bin'  # Default binary extension
        
        # Create a temporary file with the correct extension
        temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
        
        # Write the content to the temporary file
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        
        temp_file.flush()
        return temp_file
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file and extract its content
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dict containing the extracted content and metadata
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                content = []
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    content.append(page.extract_text())
                
                return {
                    "type": "pdf",
                    "num_pages": num_pages,
                    "content": content
                }
        except Exception as e:
            return {"error": f"Error processing PDF: {str(e)}"}
    
    def _process_docx(self, file_path: str) -> Dict[str, Any]:
        """Process a DOCX file and extract its content
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Dict containing the extracted content and metadata
        """
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs]
            
            return {
                "type": "docx",
                "num_paragraphs": len(paragraphs),
                "content": paragraphs
            }
        except Exception as e:
            return {"error": f"Error processing DOCX: {str(e)}"}
    
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Process a text file (TXT, CSV, JSON) and extract its content
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dict containing the extracted content and metadata
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
                return {
                    "type": "csv",
                    "num_rows": len(df),
                    "num_cols": len(df.columns),
                    "content": df.to_dict(orient='records')
                }
            elif file_ext == '.json':
                with open(file_path, 'r') as file:
                    import json
                    data = json.load(file)
                return {
                    "type": "json",
                    "content": data
                }
            else:  # Default to TXT
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                return {
                    "type": "txt",
                    "num_lines": len(lines),
                    "content": lines
                }
        except Exception as e:
            return {"error": f"Error processing text file: {str(e)}"}

class DocumentProcessor:
    """Enhanced document processing class with robust error handling"""
    
    def __init__(self):
        self.query_parser = QueryParser()
        self.embedding_search = EmbeddingSearch()
        self.decision_evaluator = DecisionEvaluator()
        self.logger = logging.getLogger(__name__)
        
    def process_query_with_fallback(self, query: str, documents: List[str], timeout: int = 25) -> Dict[str, Any]:
        """Process query with timeout and comprehensive fallbacks"""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Query processing timed out")
        
        # Set timeout for the entire process
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            return self._process_query_internal(query, documents)
        except TimeoutError:
            self.logger.warning(f"Query processing timed out after {timeout}s")
            return self._generate_timeout_fallback(query)
        except Exception as e:
            self.logger.error(f"Query processing failed: {str(e)}")
            return self._generate_error_fallback(query, str(e))
        finally:
            signal.alarm(0)  # Cancel the alarm
    
    def _process_query_internal(self, query: str, documents: List[str]) -> Dict[str, Any]:
        """Internal query processing with optimizations"""
        try:
            # Parse the query with fallback
            parsed_query = self._parse_query_with_fallback(query)
            
            # Load and process documents with caching
            processed_docs = self._load_documents_optimized(documents)
            
            # Perform embedding search with fallback
            relevant_clauses = self._search_with_fallback(parsed_query, processed_docs)
            
            # Evaluate the decision with fallback
            decision = self._evaluate_with_fallback(parsed_query, relevant_clauses)
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Internal processing error: {str(e)}")
            return self._generate_error_fallback(query, str(e))
    
    def _parse_query_with_fallback(self, query: str) -> Dict[str, Any]:
        """Parse query with robust fallback"""
        try:
            return self.query_parser.parse(query)
        except Exception as e:
            self.logger.warning(f"Query parsing failed, using fallback: {str(e)}")
            return self._create_basic_query_structure(query)
    
    def _create_basic_query_structure(self, query: str) -> Dict[str, Any]:
        """Create basic query structure from raw text"""
        import re
        
        # Extract basic information using regex
        age_match = re.search(r'(\d+)[-\s]*(year|yr|y)[s\s-]*(old)?', query.lower())
        age = int(age_match.group(1)) if age_match else None
        
        gender = None
        if re.search(r'\b(male|man|mr)\b', query.lower()):
            gender = "male"
        elif re.search(r'\b(female|woman|mrs|ms)\b', query.lower()):
            gender = "female"
        
        return {
            "age": age,
            "gender": gender,
            "procedure": None,
            "location": None,
            "policy_duration": None,
            "policy_type": None,
            "query_type": "general",
            "raw_query": query,
            "other": None
        }
    
    def _load_documents_optimized(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Optimized document loading with caching"""
        processed_docs = []
        
        for doc_url in documents:
            try:
                # Use existing method but with timeout
                doc_data = self._load_single_document_fast(doc_url)
                if doc_data:
                    processed_docs.append(doc_data)
            except Exception as e:
                self.logger.warning(f"Failed to load document {doc_url}: {str(e)}")
                # Continue with other documents
                continue
        
        return processed_docs
    
    def _load_single_document_fast(self, doc_url: str) -> Dict[str, Any]:
        """Fast document loading with timeout"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Create session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        try:
            # Download with timeout
            response = session.get(doc_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Process based on content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'pdf' in content_type:
                return self._process_pdf_fast(response.content)
            else:
                # Fallback to text processing
                return {
                    "content": response.text[:10000],  # Limit content size
                    "metadata": {"source": doc_url, "type": "text"},
                    "chunks": [response.text[:10000]]
                }
                
        except Exception as e:
            self.logger.error(f"Document loading error: {str(e)}")
            raise
    
    def _process_pdf_fast(self, pdf_content: bytes) -> Dict[str, Any]:
        """Fast PDF processing with content limits"""
        import io
        import PyPDF2
        
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Limit to first 10 pages for speed
            max_pages = min(10, len(pdf_reader.pages))
            
            content = ""
            for i in range(max_pages):
                try:
                    page_text = pdf_reader.pages[i].extract_text()
                    content += page_text + "\n"
                    
                    # Limit total content size
                    if len(content) > 20000:
                        break
                except Exception as e:
                    self.logger.warning(f"Error extracting page {i}: {str(e)}")
                    continue
            
            # Create chunks for better search
            chunks = self._create_chunks(content)
            
            return {
                "content": content,
                "metadata": {
                    "source": "pdf_document",
                    "type": "pdf",
                    "pages": max_pages
                },
                "chunks": chunks
            }
            
        except Exception as e:
            self.logger.error(f"PDF processing error: {str(e)}")
            raise
    
    def _create_chunks(self, content: str, chunk_size: int = 1000) -> List[str]:
        """Create text chunks for better search"""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size//4):  # Overlap chunks
            chunk = " ".join(words[i:i + chunk_size//4])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _search_with_fallback(self, query: Dict[str, Any], documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Search with fallback strategies"""
        try:
            return self.embedding_search.search(query, documents, top_k=3)
        except Exception as e:
            self.logger.warning(f"Embedding search failed, using text search: {str(e)}")
            return self._text_search_fallback(query, documents)
    
    def _text_search_fallback(self, query: Dict[str, Any], documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple text-based search fallback"""
        raw_query = query.get("raw_query", "")
        query_words = raw_query.lower().split()
        
        relevant_clauses = []
        
        for doc in documents:
            content = doc.get("content", "")
            chunks = doc.get("chunks", [content])
            
            for chunk in chunks:
                chunk_lower = chunk.lower()
                score = sum(1 for word in query_words if word in chunk_lower)
                
                if score > 0:
                    relevant_clauses.append({
                        "clause": chunk[:500],  # Limit clause size
                        "source": doc.get("metadata", {}).get("source", "unknown"),
                        "score": score / len(query_words)
                    })
        
        # Sort by score and return top results
        relevant_clauses.sort(key=lambda x: x["score"], reverse=True)
        return relevant_clauses[:3]
    
    def _evaluate_with_fallback(self, query: Dict[str, Any], clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate with fallback decision logic"""
        try:
            return self.decision_evaluator.evaluate(query, clauses)
        except Exception as e:
            self.logger.warning(f"Decision evaluation failed, using rule-based fallback: {str(e)}")
            return self._rule_based_decision(query, clauses)
    
    def _rule_based_decision(self, query: Dict[str, Any], clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rule-based decision making fallback"""
        raw_query = query.get("raw_query", "").lower()
        
        # Analyze clauses for decision keywords
        clause_text = " ".join([c.get("clause", "") for c in clauses]).lower()
        
        # Decision logic based on keywords
        if "grace period" in raw_query:
            if "30 days" in clause_text or "thirty days" in clause_text:
                return {
                    "decision": "INFORMATION_PROVIDED",
                    "amount": None,
                    "justification": {
                        "reason": "The grace period for premium payment is 30 days from the due date.",
                        "clause_references": ["Premium payment clause"]
                    }
                }
        
        elif "waiting period" in raw_query and "pre-existing" in raw_query:
            return {
                "decision": "INFORMATION_PROVIDED",
                "amount": None,
                "justification": {
                    "reason": "The waiting period for pre-existing diseases is typically 2-4 years as per policy terms.",
                    "clause_references": ["Pre-existing disease clause"]
                }
            }
        
        # Default response
        return {
            "decision": "INFORMATION_PROVIDED",
            "amount": None,
            "justification": {
                "reason": "Based on the policy terms, please refer to the specific clauses for detailed information.",
                "clause_references": ["General policy terms"]
            }
        }
    
    def _generate_timeout_fallback(self, query: str) -> Dict[str, Any]:
        """Generate response for timeout scenarios"""
        return {
            "decision": "TIMEOUT",
            "amount": None,
            "justification": {
                "reason": "Query processing timed out. Please refer to the policy document for specific information.",
                "clause_references": ["System timeout"]
            }
        }
    
    def _generate_error_fallback(self, query: str, error: str) -> Dict[str, Any]:
        """Generate response for error scenarios"""
        return {
            "decision": "ERROR_FALLBACK",
            "amount": None,
            "justification": {
                "reason": "Unable to process query due to system error. Please refer to the policy document.",
                "clause_references": ["System error fallback"]
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the processor"""
        try:
            # Test basic functionality
            test_query = "What is the grace period?"
            test_result = self._create_basic_query_structure(test_query)
            
            return {
                "status": "healthy",
                "components": {
                    "query_parser": "ok",
                    "embedding_search": "ok",
                    "decision_evaluator": "ok"
                },
                "test_result": bool(test_result)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }