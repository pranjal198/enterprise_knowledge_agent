from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Document
from app.ingestion.loader import load_pdf, split_documents
from app.retrieval.vector_store import create_vector_store


def process_document(
    file_path: str,
    user_id: int,
    document_id: int,
):
    db: Session = SessionLocal()

    try:
        # 1. Load PDF
        documents = load_pdf(file_path)

        # 2. Split into chunks
        chunks = split_documents(documents)

        if not chunks:
            raise ValueError("No readable text chunks found.")

        # 3. Store chunks in ChromaDB
        create_vector_store(
            chunks,
            user_id=user_id,
            document_id=document_id,
        )

        # 4. Update document status
        document = db.get(Document, document_id)

        if document is None:
            raise ValueError("Document record not found.")

        document.status = "indexed"
        db.commit()

    except Exception:
        db.rollback()

        document = db.get(Document, document_id)

        if document:
            document.status = "failed"
            db.commit()

    finally:
        db.close()