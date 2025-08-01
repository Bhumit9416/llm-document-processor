import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import openai

# For vector database
import pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
# Import Pinecone with new API format
from pinecone import Pinecone

class EmbeddingSearch:
    """Class for performing embedding-based semantic search on documents"""
    
    def __init__(self):
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.local_model = None
        self.use_pinecone = os.getenv("USE_PINECONE", "false").lower() == "true"
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "document-search")
        
        # Initialize local embedding model if not using OpenAI
        if os.getenv("USE_LOCAL_EMBEDDINGS", "false").lower() == "true":
            model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.local_model = SentenceTransformer(model_name)
        
        # Initialize Pinecone index if using Pinecone
        if self.use_pinecone:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY", ""))
            
            # Check if index exists and create if needed
            if self.pinecone_index_name not in self.pc.list_indexes().names():
                # Create the index if it doesn't exist
                from pinecone import ServerlessSpec
                self.pc.create_index(
                    name=self.pinecone_index_name,
                    dimension=1536,  # OpenAI embeddings dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
            self.index = self.pc.Index(self.pinecone_index_name)
    
    def search(self, query: Dict[str, Any], documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant clauses in the documents based on the query
        
        Args:
            query: The structured query dictionary
            documents: List of processed document contents with metadata
            top_k: Number of top results to return
            
        Returns:
            List of relevant clauses with their metadata
        """
        # Process the documents into chunks/clauses if not already done
        clauses = self._process_documents_to_clauses(documents)
        
        # Convert the query to a search string
        search_query = self._query_to_search_string(query)
        
        # Get the embedding for the search query
        query_embedding = self._get_embedding(search_query)
        
        # If using Pinecone, store the clauses and search
        if self.use_pinecone:
            # Store the clauses in Pinecone (if not already stored)
            self._store_clauses_in_pinecone(clauses)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract the matched clauses
            matched_clauses = [
                {"clause": match.metadata["clause"], 
                 "source": match.metadata["source"],
                 "score": match.score}
                for match in results.matches
            ]
        else:
            # Local search using embeddings
            matched_clauses = self._local_search(clauses, query_embedding, top_k)
        
        return matched_clauses
    
    def _process_documents_to_clauses(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process documents into smaller chunks or clauses for better search
        
        Args:
            documents: List of processed document contents with metadata
            
        Returns:
            List of clauses with their metadata
        """
        clauses = []
        
        for doc in documents:
            source = doc["source"]
            content = doc["content"]
            
            # Handle different document types
            if isinstance(content, dict) and "content" in content:
                # Extract the actual content
                if isinstance(content["content"], list):
                    # For PDFs and DOCXs with list of pages/paragraphs
                    text_content = "\n".join(content["content"])
                else:
                    text_content = str(content["content"])
            elif isinstance(content, list):
                # For list of strings
                text_content = "\n".join(content)
            else:
                # Default case
                text_content = str(content)
            
            # Split the content into clauses or chunks
            # This is a simple split by paragraphs, but more sophisticated methods can be used
            paragraphs = text_content.split("\n\n")
            
            for i, paragraph in enumerate(paragraphs):
                # Skip empty paragraphs
                if not paragraph.strip():
                    continue
                
                # Add the paragraph as a clause
                clauses.append({
                    "id": f"{source}-{i}",
                    "source": source,
                    "clause": paragraph.strip(),
                    "clause_number": i
                })
        
        return clauses
    
    def _query_to_search_string(self, query: Dict[str, Any]) -> str:
        """Convert a structured query dictionary to a search string
        
        Args:
            query: The structured query dictionary
            
        Returns:
            A search string for embedding
        """
        # Extract relevant fields from the query
        search_parts = []
        
        if query.get("procedure"):
            search_parts.append(f"Procedure: {query['procedure']}")
        
        if query.get("query_type"):
            search_parts.append(f"Query type: {query['query_type']}")
        
        if query.get("age"):
            search_parts.append(f"Age: {query['age']}")
        
        if query.get("gender"):
            search_parts.append(f"Gender: {query['gender']}")
        
        if query.get("location"):
            search_parts.append(f"Location: {query['location']}")
        
        if query.get("policy_duration"):
            search_parts.append(f"Policy duration: {query['policy_duration']}")
        
        if query.get("policy_type"):
            search_parts.append(f"Policy type: {query['policy_type']}")
        
        # If no structured fields were found, use the original query
        if not search_parts and query.get("original_query"):
            return query["original_query"]
        
        # Join the parts into a search string
        return ". ".join(search_parts)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get the embedding vector for a text string
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector as a list of floats
        """
        if self.local_model:
            # Use local model for embeddings
            return self.local_model.encode(text).tolist()
        else:
            # Use OpenAI for embeddings
            response = openai.Embedding.create(
                input=text,
                model=self.embedding_model
            )
            return response["data"][0]["embedding"]
    
    def _store_clauses_in_pinecone(self, clauses: List[Dict[str, Any]]) -> None:
        """Store clause embeddings in Pinecone
        
        Args:
            clauses: List of clauses with their metadata
        """
        # Prepare the vectors for upsert
        vectors_to_upsert = []
        
        for clause in clauses:
            # Get the embedding for the clause text
            embedding = self._get_embedding(clause["clause"])
            
            # Prepare the vector with metadata
            vector = {
                "id": clause["id"],
                "values": embedding,
                "metadata": {
                    "clause": clause["clause"],
                    "source": clause["source"],
                    "clause_number": clause["clause_number"]
                }
            }
            
            vectors_to_upsert.append(vector)
        
        # Upsert the vectors in batches (Pinecone has a limit on batch size)
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i+batch_size]
            self.index.upsert(vectors=batch)
    
    def _local_search(self, clauses: List[Dict[str, Any]], query_embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Perform local search using embeddings
        
        Args:
            clauses: List of clauses with their metadata
            query_embedding: The embedding vector for the query
            top_k: Number of top results to return
            
        Returns:
            List of relevant clauses with their metadata and scores
        """
        # Convert query embedding to numpy array
        query_embedding_np = np.array(query_embedding)
        
        # Calculate embeddings for all clauses
        clause_embeddings = []
        for clause in clauses:
            embedding = self._get_embedding(clause["clause"])
            clause_embeddings.append(embedding)
        
        # Convert to numpy array
        clause_embeddings_np = np.array(clause_embeddings)
        
        # Calculate cosine similarity
        similarities = np.dot(clause_embeddings_np, query_embedding_np) / \
                      (np.linalg.norm(clause_embeddings_np, axis=1) * np.linalg.norm(query_embedding_np))
        
        # Get the indices of the top_k highest similarities
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Prepare the results
        results = []
        for idx in top_indices:
            results.append({
                "clause": clauses[idx]["clause"],
                "source": clauses[idx]["source"],
                "score": float(similarities[idx])
            })
        
        return results