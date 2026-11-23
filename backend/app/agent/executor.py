
from app.agent.registry import ToolRegistry


class ToolExecutor:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_name: str, tool_input: str):

        # 1. Find the requested tool
        tool = self.registry.get_tool(tool_name)

        # 2. Handle unknown tools
        if tool is None:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found."
            }

        # 3. Execute the tool
        try:
            result = tool.execute(tool_input)

            return {
                "tool": tool_name,
                "input": tool_input,
                "output": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
