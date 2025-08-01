import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Import our modules
from api.routes import router as api_router
from document_processor.processor import DocumentProcessor

# Create FastAPI app
app = FastAPI(
    title="LLM Document Processing System",
    description="A system that processes natural language queries and retrieves relevant information from documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Create a simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Document Processing System"}

if __name__ == "__main__":
    # Run the application
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)