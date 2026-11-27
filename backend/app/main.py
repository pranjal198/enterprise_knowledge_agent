
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.generation.chain import answer_question

from pathlib import Path
import shutil

from fastapi import UploadFile, File

from app.ingestion.loader import load_pdf, split_documents
from app.retrieval.vector_store import create_vector_store

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Conversation, Message, User, Document

from datetime import datetime
from app.auth.routes import router as auth_router

from sqlalchemy import select
from app.auth.dependencies import get_current_user
from uuid import uuid4

from fastapi import BackgroundTasks, status

from app.tasks.document_tasks import process_document
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise Knowledge Assistant",
    description="Ask questions about company documents using RAG.",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)

# Request schema
class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question about the uploaded company documents"
    )
    conversation_id: int | None = None

# Source schema
class Source(BaseModel):
    source: str
    page: int | None = None


# Response schema
class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    conversation_id: int

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: int
    title: str | None
    created_at: datetime
    messages: list[MessageResponse]

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

@app.get("/db-health")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))

    return {
        "status": "connected",
        "database": "enterprise_knowledge_db"
    }




@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # 1. Find an existing conversation or create a new one
        if request.conversation_id is not None:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id,
                )
            )

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

        else:
            conversation = Conversation(
                title=request.question[:255],
                user_id=current_user.id,
            )

            db.add(conversation)
            db.flush()

        # 2. Retrieve the 10 most recent messages
        history_messages = db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(
                Message.created_at.desc(),
                Message.id.desc(),
            )
            .limit(10)
        ).all()

        # 3. Convert history into chronological order
        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in reversed(history_messages)
        ]

        # 4. Generate the answer using the RAG pipeline
        result = answer_question(
            request.question,
            user_id=current_user.id,
            conversation_history=conversation_history,
        )

        # 5. Create the user's message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.question
        )

        # 6. Create the assistant's message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"]
        )

        # 7. Add both messages to the database session
        db.add_all([user_message, assistant_message])

        # 8. Commit the transaction
        db.commit()

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=conversation.id
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        print(f"Chat endpoint error: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the answer."
        )



@app.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[
            MessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in conversation.messages
        ],
    )


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Directory where uploaded PDFs will be stored
UPLOAD_DIR = PROJECT_ROOT / "data" / "documents"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # 1. Validate file extension
        if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # 2. Generate a unique filename
        safe_filename = Path(file.filename).name
        unique_filename = f"{uuid4().hex}_{safe_filename}"
        file_path = UPLOAD_DIR / unique_filename

        # 3. Save uploaded PDF
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 4. Create document record
        document = Document(
            user_id=current_user.id,
            filename=unique_filename,
            status="processing",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        # 5. Schedule background processing
        background_tasks.add_task(
            process_document,
            str(file_path),
            current_user.id,
            document.id,
        )

        return {
            "message": "PDF uploaded. Processing started.",
            "document_id": document.id,
            "filename": safe_filename,
            "status": "processing",
        }

    except HTTPException:
        db.rollback()
        if "file_path" in locals() and file_path.exists():
            file_path.unlink()
        raise

    except Exception:
        db.rollback()
        if "file_path" in locals() and file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="PDF upload failed."
        )

    finally:
        await file.close()