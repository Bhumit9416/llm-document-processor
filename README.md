# LLM-Powered Intelligent Query-Retrieval System

## Overview

This system processes large documents and makes contextual decisions using LLM technology. It can handle real-world scenarios in insurance, legal, HR, and compliance domains by parsing natural language queries, retrieving relevant information from unstructured documents, and providing explainable decisions with structured JSON responses.

## Features

- **Document Processing**: Support for PDFs, DOCX, emails, and other document formats
- **Natural Language Query Parsing**: Extract structured information from user queries
- **Semantic Search**: Embedding-based retrieval using FAISS/Pinecone
- **Clause Matching**: Identify relevant clauses in documents
- **Decision Evaluation**: Make contextual decisions with justifications
- **Structured Output**: Return JSON responses with decisions, amounts, and rationales
- **Explainable AI**: Provide clear decision reasoning with clause references

## System Architecture

![System Architecture](https://mermaid.ink/img/pako:eNp1kk1PwzAMhv9KlBOgSf3YpE1w2A6cEBJiB8QOaRo3Dd0H-VgFVf87SdtNGmXkYsd-_dp2TkQZKyQRkZJbVDYr4QnuQOe6BmNRwdpoC1fQGVUBfGgLNfzAHdwjPMKTcU9wD1ajKkFZZ9RnUJW2BZRGl6BNDe_GZmALUDlYVIBWO1DWGVXwDFqBRQcFKGthY_L8S_UKtoCPXNegbJ7_Jv8FO4fcFPkGlM3ydZZvnV2BsnmWrbNs5-wGlM2ybJtl-3_sHpTNsmydZQdn96BslmXrLDs4-wDKZlm2zrKjs0-gbJZl6yw7OvsCyroD2GXZ0dlXUDbLsnWWHZ19A2WzLFtn2dHZd1A2y7J1lh2d_QBlsyxbZ9nR2U9QNsuydZYdnf0CZbMsW2fZ0dlvUDbLsnWWHZ39AWWzLFtn2dHZX1A2y7J1lh2d_QNlXRvssmzfnCmJqKMJxVRQX1NKY0oLGtOQhm7_QBMa0pgmdEZjOqcJXdAFXdKULumKrqmgG7qla7qhO3qgkh7pkR5oSU_0TJ_0RV_0Td_0g1b0i37TH_qb0D_6nzQN?type=png)

1. **Input Documents**: System processes PDFs, DOCX, emails, and other document formats
2. **LLM Parser**: Extracts structured information from natural language queries
3. **Embedding Search**: Uses FAISS/Pinecone for semantic retrieval of relevant document sections
4. **Clause Matching**: Identifies specific clauses that match the query intent
5. **Logic Evaluation**: Applies business rules and context to make decisions
6. **JSON Output**: Returns structured responses with decisions, amounts, and justifications

## Project Structure

```
├── src/
│   ├── document_processor/     # Document processing orchestration
│   ├── query_parser/           # Natural language query parsing
│   ├── retrieval/              # Embedding-based semantic search
│   ├── decision_engine/        # Decision evaluation logic
│   ├── api/                    # FastAPI endpoints
│   └── main.py                 # Application entry point
├── data/                       # Sample documents and test data
├── tests/                      # Unit and integration tests
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
└── sample_usage.py             # Example usage script
```

## Setup and Installation

### Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)

### Local Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd hackRx
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the template:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Initialize the project structure:

```bash
python init_project.py
```

6. Generate sample documents (optional):

```bash
python generate_all_samples.py
```

### Docker Setup

1. Build and start the container:

```bash
docker-compose up -d
```

## Usage

### Running the API Server

```bash
python src/main.py
```

The API will be available at http://localhost:8000/api/v1

### API Endpoints

#### Process Documents and Answer Questions

```
POST /hackrx/run
```

Request:

```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?"
    ]
}
```

Response:

```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
    ]
}
```

#### Health Check

```
GET /health
```

Response:

```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

### Sample Usage Script

You can use the provided sample script to test the system:

```bash
python sample_usage.py
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Test the API endpoints:

```bash
python test_api.py
```

Evaluate system performance:

```bash
python evaluate_system.py
```

## Evaluation Parameters

The system is evaluated based on the following criteria:

1. **Accuracy**: Precision of query understanding and clause matching
2. **Token Efficiency**: Optimized LLM token usage and cost-effectiveness
3. **Latency**: Response speed and real-time performance
4. **Reusability**: Code modularity and extensibility
5. **Explainability**: Clear decision reasoning and clause traceability

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for GPT models
- Pinecone for vector database
- FastAPI for API framework
- HuggingFace for transformer models