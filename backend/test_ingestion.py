
from app.ingestion.loader import load_pdf, split_documents

# Path to your PDF, relative to the backend directory
pdf_path = "../data/documents/Leave_policy.pdf"

# 1. Load PDF
documents = load_pdf(pdf_path)

print("Number of pages:", len(documents))
print("\nFirst page content:")
print(documents[0].page_content[:500])

print("\nFirst page metadata:")
print(documents[0].metadata)

# 2. Split into chunks
chunks = split_documents(documents)

print("\nNumber of chunks:", len(chunks))

# 3. Inspect a chunk
print("\nFirst chunk:")
print(chunks[0].page_content)

print("\nFirst chunk metadata:")
print(chunks[0].metadata)
