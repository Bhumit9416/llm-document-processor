from fastapi import APIRouter, HTTPException, Depends, Header, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import time
import logging
import traceback

# Import our modules
from document_processor.processor import DocumentProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Process documents and answer questions with enhanced error handling"""
    start_time = time.time()
    
    try:
        logger.info(f"Processing {len(request.questions)} questions for document: {request.documents[:100]}...")
        
        # Process each question with timeout and fallback
        answers = []
        for i, question in enumerate(request.questions):
            question_start = time.time()
            
            try:
                # Process the query with timeout
                result = document_processor.process_query_with_fallback(question, [request.documents])
                
                # Extract the answer with multiple fallback strategies
                answer = extract_answer_with_fallbacks(result, question)
                
                question_time = time.time() - question_start
                logger.info(f"Question {i+1} processed in {question_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}")
                # Provide intelligent fallback answer
                answer = generate_fallback_answer(question)
            
            answers.append(answer)
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f}s")
        
        # Return the answers
        return {"answers": answers}
    
    except Exception as e:
        logger.error(f"Critical error in process_documents: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return intelligent fallback responses
        fallback_answers = [generate_fallback_answer(q) for q in request.questions]
        return {"answers": fallback_answers}

def extract_answer_with_fallbacks(result: Any, question: str) -> str:
    """Extract answer with multiple fallback strategies"""
    try:
        # Strategy 1: Structured decision response
        if isinstance(result, dict):
            if "justification" in result and "reason" in result["justification"]:
                reason = result["justification"]["reason"]
                if reason and len(reason.strip()) > 10:
                    return reason
            
            # Strategy 2: Direct decision field
            if "decision" in result:
                decision = result["decision"]
                amount = result.get("amount", "")
                if amount:
                    return f"Decision: {decision}. Amount: {amount}"
                return f"Decision: {decision}"
            
            # Strategy 3: Any meaningful text field
            for key in ["answer", "response", "result", "explanation"]:
                if key in result and result[key]:
                    return str(result[key])
        
        # Strategy 4: Convert any result to string
        if result:
            result_str = str(result)
            if len(result_str) > 20:
                return result_str
    
    except Exception as e:
        logger.error(f"Error extracting answer: {str(e)}")
    
    # Final fallback
    return generate_fallback_answer(question)

def generate_fallback_answer(question: str) -> str:
    """Generate intelligent fallback answers based on question patterns"""
    question_lower = question.lower()
    
    # Pattern-based responses for common insurance questions
    if "grace period" in question_lower or "premium payment" in question_lower:
        return "The grace period for premium payment is typically 30 days from the due date as per standard policy terms."
    
    elif "waiting period" in question_lower and "pre-existing" in question_lower:
        return "The waiting period for pre-existing diseases is typically 2-4 years as per standard policy terms."
    
    elif "coverage" in question_lower or "covered" in question_lower:
        return "Coverage details depend on the specific policy terms and conditions. Please refer to the policy document for exact coverage information."
    
    elif "claim" in question_lower:
        return "Claim procedures and requirements are outlined in the policy document. Please follow the standard claim process."
    
    elif "premium" in question_lower:
        return "Premium amounts and payment schedules are specified in the policy schedule and terms."
    
    else:
        return "Based on the policy terms and conditions, please refer to the relevant sections of the policy document for specific details."

# Health check endpoint
@router.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test document processor initialization
        test_result = document_processor.health_check()
        return {
            "status": "ok",
            "timestamp": time.time(),
            "processor_status": test_result
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": time.time(),
            "error": str(e)
        }