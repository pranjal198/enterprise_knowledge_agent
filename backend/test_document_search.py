from app.agent.tools.document_search import DocumentSearchTool

document_tool = DocumentSearchTool()

result = document_tool.execute(
    "What is the annual leave policy?"
)

print(result)