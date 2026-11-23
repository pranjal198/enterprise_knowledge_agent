
import os

from dotenv import load_dotenv
from tavily import TavilyClient

from app.agent.base import Tool


load_dotenv()


class WebSearchTool(Tool):

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY is missing from .env")

        self.client = TavilyClient(api_key=api_key)

    @property
    def name(self):
        return "web_search"

    @property
    def description(self):
        return (
            "Searches the internet for current information. "
            "Use for recent news, current events, latest "
            "technology updates, and information not available "
            "in the company's internal documents."
        )

    def execute(self, tool_input: str):

        try:
            response = self.client.search(
                query=tool_input,
                search_depth="basic",
                max_results=5
            )

            results = response.get("results", [])

            return {
                "success": True,
                "results": [
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": item.get("content")
                    }
                    for item in results
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
