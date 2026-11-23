from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf(file_path: str):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    if not documents or not any(doc.page_content.strip() for doc in documents):
        raise ValueError("No readable text found in the PDF.")

    return documents

def split_documents(documents):
    """
    Split loaded documents into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    return chunks