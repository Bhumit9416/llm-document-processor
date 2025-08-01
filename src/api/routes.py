from fastapi import APIRouter, HTTPException, Depends, Header, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

# Import our modules
from document_processor.processor import DocumentProcessor

# Create router
router = APIRouter()

# Initialize document processor
document_processor = DocumentProcessor()

# Define request and response models
class Question(BaseModel):
    text: str

class ProcessRequest(BaseModel):
    documents: str = Field(..., description="URL to the document to process")
    questions: List[str] = Field(..., description="List of questions to answer")

class ProcessResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers to the questions")

# Define API key for authentication
API_KEY = os.getenv("API_KEY", "ac0ac1082ad0be4b45e97d50e02fd26a99a0dbfeaaf67f10515a87ce297fc647")

# Authentication dependency
async def verify_api_key(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

# API endpoints
@router.post("/hackrx/run", response_model=ProcessResponse)
async def process_documents(
    request: ProcessRequest = Body(...),
    token: str = Depends(verify_api_key)
):
    """Process documents and answer questions"""
    try:
        # Process each question
        answers = []
        for question in request.questions:
            # Process the query
            result = document_processor.process_query(question, [request.documents])
            
            # Extract the answer
            if isinstance(result, dict) and "justification" in result and "reason" in result["justification"]:
                # If the result is a structured decision
                answer = result["justification"]["reason"]
            else:
                # Fallback to a simple answer
                answer = "Unable to determine a specific answer based on the provided documents."
            
            answers.append(answer)
        
        # Return the answers
        return {"answers": answers}
    
    except Exception as e:
        # Log the error
        print(f"Error processing documents: {str(e)}")
        
        # Return an error response
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}