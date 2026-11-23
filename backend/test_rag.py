
from app.generation.chain import answer_question

question = "How many days of annual leave do employees receive?"

result = answer_question(question)

print("\nQUESTION:")
print(question)

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")

for source in result["sources"]:
    print(
        f"Document: {source['source']} | "
        f"Page: {source['page']}"
    )
