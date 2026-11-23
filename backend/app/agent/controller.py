
import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.tools import StructuredTool

from app.core.models import llm
from app.agent.executor import ToolExecutor
from app.agent.registry import ToolRegistry


def convert_to_langchain_tools(registry: ToolRegistry):

    langchain_tools = []

    for custom_tool in registry.get_all_tools():

        def run_tool(tool_input: str, current_tool=custom_tool):

            result = current_tool.execute(tool_input)

            return json.dumps(
                result,
                ensure_ascii=False,
                default=str
            )

        run_tool.__name__ = custom_tool.name

        langchain_tool = StructuredTool.from_function(
            func=run_tool,
            name=custom_tool.name,
            description=custom_tool.description
        )

        langchain_tools.append(langchain_tool)

    return langchain_tools


class AgentController:

    def __init__(
        self,
        registry: ToolRegistry,
        max_iterations: int = 5
    ):

        self.executor = ToolExecutor(registry)
        self.tools = convert_to_langchain_tools(registry)

        self.llm_with_tools = llm.bind_tools(self.tools)

        self.max_iterations = max_iterations

    def answer(self, question: str):

        messages = [
            SystemMessage(content="""
You are an intelligent enterprise AI assistant.

Available tools:

1. calculator:
   Performs mathematical calculations.

2. document_search:
   Searches internal company documents for
   policies, benefits and procedures.

3. web_search:
   Searches the internet for current information.

Instructions:
- Use document_search for company-specific information.
- Use calculator for mathematical calculations.
- Use web_search for current external information.
- If a question requires multiple tools, call them
  in the appropriate sequence.
- Use the results returned by previous tools.
- Never invent information.
- Provide a clear final answer.
"""),
            HumanMessage(content=question)
        ]

        executed_tools = []

        for iteration in range(self.max_iterations):

            # Ask Gemini what to do next
            response = self.llm_with_tools.invoke(messages)

            # Add Gemini's response to conversation history
            messages.append(response)

            # If no tool calls, Gemini has produced its final answer
            if not response.tool_calls:

                return {
                    "answer": response.content,
                    "tool_calls": executed_tools
                }

            # Execute every requested tool
            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]

                tool_input = tool_call["args"].get(
                    "tool_input",
                    ""
                )

                result = self.executor.execute(
                    tool_name,
                    tool_input
                )

                executed_tools.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "result": result
                })

                # Send execution result back to Gemini
                messages.append(
                    ToolMessage(
                        content=json.dumps(
                            result,
                            default=str
                        ),
                        tool_call_id=tool_call["id"]
                    )
                )

        return {
            "answer": (
                "I could not complete the request "
                "within the allowed tool-call iterations."
            ),
            "tool_calls": executed_tools
        }
