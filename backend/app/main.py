
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.generation.chain import answer_question

from pathlib import Path
import shutil

from fastapi import UploadFile, File

from app.ingestion.loader import load_pdf, split_documents
from app.retrieval.vector_store import create_vector_store


app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Ask questions about company documents using RAG.",
    version="1.0.0"
)


# Request schema
class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question about the uploaded company documents"
    )


# Source schema
class Source(BaseModel):
    source: str
    page: int | None = None


# Response schema
class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/")
def home():
    return {
        "message": "Enterprise Knowledge Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = answer_question(request.question)

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except Exception as e:
        print(f"Chat endpoint error: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the answer."
        )


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Directory where uploaded PDFs will be stored
UPLOAD_DIR = PROJECT_ROOT / "data" / "documents"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # 1. Validate file extension
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # 2. Create a safe filename
    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    # 3. Save uploaded PDF
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Load PDF
        documents = load_pdf(str(file_path))

        # 5. Split into chunks
        chunks = split_documents(documents)

        if not chunks:
            raise ValueError("No readable text chunks found.")

        # 6. Add chunks to ChromaDB
        create_vector_store(chunks)

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": safe_filename,
            "pages": len(documents),
            "chunks": len(chunks)
        }

    except Exception as e:
        # Remove invalid or unsuccessfully processed file
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )

    finally:
        await file.close()
