
from app.core.models import llm, embeddings

# Test 1: Chat model
response = llm.invoke(
    "Explain Retrieval Augmented Generation in two sentences."
)

print("CHAT MODEL RESPONSE:")
print(response.content)


# Test 2: Embedding model
vector = embeddings.embed_query(
    "What is Retrieval Augmented Generation?"
)

print("\nEMBEDDING MODEL:")
print("Vector dimensions:", len(vector))
print("First five values:", vector[:5])
