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