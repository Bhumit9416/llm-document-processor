import uvicorn
import os
import asyncio
from typing import List, Dict
import logging
from io import BytesIO

import requests
import pypdf
import faiss
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Change it to this
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# --- Basic Setup & Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- API Key Authentication ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "ac0ac1082ad0be4b45e97d50e02fd26a99a0dbfeaaf67f10515a87ce297fc647")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Optimized LLM Document Processing System",
    description="A system that processes queries with caching to ensure fast responses.",
    version="1.1.0"
)

# --- Add CORS Middleware (allowing all origins for the competition) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Data Validation ---
class HackRxRequest(BaseModel):
    documents: str = Field(..., description="URL to the PDF document.")
    questions: List[str] = Field(..., description="List of questions to answer based on the document.")

class HackRxResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to the questions.")

# --- In-Memory Cache for Processed Documents ---
# This dictionary is our "memory" to store the processed FAISS vector stores.
vector_store_cache: Dict[str, FAISS] = {}

# --- Security Dependency ---
async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {BEARER_TOKEN}":
        raise HTTPException(status_code=403, detail="Invalid authorization token.")
    return True

# --- Core Logic for Document Processing ---
def load_and_chunk_document(pdf_url: str) -> List[str]:
    try:
        logging.info(f"Downloading document from: {pdf_url}")
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_stream = BytesIO(response.content)
        
        pdf_reader = pypdf.PdfReader(pdf_stream)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        
        if not text:
            raise ValueError("Failed to extract text from the PDF.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        return chunks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF document: {e}")

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Welcome to the Optimized LLM Document Processing System"}

@app.post("/api/v1/hackrx/run", 
            response_model=HackRxResponse, 
            dependencies=[Depends(verify_token)],
            tags=["Q&A System"])
async def run_submission(request: HackRxRequest):
    doc_url = request.documents

    if doc_url in vector_store_cache:
        # If already in memory, use the saved version (FAST PATH 🚀)
        logging.info(f"✅ Cache HIT for document: {doc_url}")
        vector_store = vector_store_cache[doc_url]
    else:
        # If not in memory, do the heavy work once (SLOW PATH 🐢)
        logging.info(f"❌ Cache MISS for document: {doc_url}. Processing...")
        doc_chunks = load_and_chunk_document(doc_url)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_store = FAISS.from_texts(texts=doc_chunks, embedding=embeddings)
        
        # Save the result to our "memory" for next time
        vector_store_cache[doc_url] = vector_store
        logging.info(f"✅ Document processed and saved to cache.")

    # --- Use the vector_store (either from cache or newly created) to answer questions ---
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    prompt_template = """
    You are an expert Q&A assistant. Answer the user's question based ONLY on the provided context.
    If the answer is not in the context, say so. Do not make up information.
    CONTEXT: {context}
    QUESTION: {question}
    ANSWER:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    # Change it to this
    llm = Ollama(model="llama3:8b")
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    )
    
    tasks = [rag_chain.ainvoke(q) for q in request.questions]
    answers = await asyncio.gather(*tasks)
    
    return HackRxResponse(answers=answers)

# --- Allows running the app directly with 'python main.py' ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)