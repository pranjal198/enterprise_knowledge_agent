
from app.agent.base import Tool


class ToolRegistry:

    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool):
        """Register a tool using its unique name."""

        if tool.name in self.tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self.tools[tool.name] = tool

    def get_tool(self, name: str):
        """Retrieve a registered tool by name."""

        return self.tools.get(name)

    def get_all_tools(self):
        """Return all registered tools."""

        return list(self.tools.values())

    def get_tool_descriptions(self):
        """Return tool names and descriptions."""

        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
