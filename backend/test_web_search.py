from app.agent.tools.web_search import WebSearchTool

search_tool = WebSearchTool()

result = search_tool.execute(
    "Latest developments in artificial intelligence in 2026"
)

print(result)