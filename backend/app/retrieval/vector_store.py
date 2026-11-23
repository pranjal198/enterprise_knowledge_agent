
from pathlib import Path

from langchain_chroma import Chroma

from app.core.models import embeddings


# Project root / chroma_db
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "company_documents"


def create_vector_store(chunks):
    """
    Convert document chunks into embeddings
    and store them in ChromaDB.
    """

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_PATH)
    )

    return vector_store


def load_vector_store():
    """
    Load an existing ChromaDB collection.
    """

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH)
    )

    return vector_store
