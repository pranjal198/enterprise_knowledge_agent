
from app.retrieval.vector_store import load_vector_store

# Load the previously created database
vector_store = load_vector_store()

# Search without loading or embedding the PDF again
query = "What is the company's leave policy?"

results = vector_store.similarity_search(
    query=query,
    k=3
)

for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}")
    print(doc.page_content)
    print(doc.metadata)
