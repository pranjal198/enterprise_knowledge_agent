
from app.ingestion.loader import load_pdf, split_documents
from app.retrieval.vector_store import create_vector_store

# 1. Load and split the PDF
documents = load_pdf("../data/documents/Leave_Policy.pdf")
chunks = split_documents(documents)

print("Total chunks:", len(chunks))

# 2. Generate embeddings and store chunks
vector_store = create_vector_store(chunks)

print("\nDocuments indexed successfully!")

# 3. Test semantic search
query = "How many days of annual leave do employees get?"

results = vector_store.similarity_search(
    query=query,
    k=3
)

print("\nRetrieved documents:")

for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Content:", doc.page_content)
    print("Metadata:", doc.metadata)
