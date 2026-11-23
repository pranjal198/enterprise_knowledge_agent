
from app.agent.registry import ToolRegistry

from app.agent.tools.calculator import CalculatorTool
from app.agent.tools.web_search import WebSearchTool
from app.agent.tools.document_search import DocumentSearchTool


def create_tool_registry():

    registry = ToolRegistry()

    registry.register(CalculatorTool())
    registry.register(WebSearchTool())
    registry.register(DocumentSearchTool())

    return registry
