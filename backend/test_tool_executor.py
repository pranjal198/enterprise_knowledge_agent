from app.agent import create_tool_registry
from app.agent.executor import ToolExecutor


registry = create_tool_registry()

executor = ToolExecutor(registry)


# Test calculator
print("Calculator:")
print(
    executor.execute(
        "calculator",
        "100 * 15"
    )
)


# Test unknown tool
print("\nUnknown tool:")
print(
    executor.execute(
        "unknown_tool",
        "test"
    )
)


# Test document search
print("\nDocument search:")
print(
    executor.execute(
        "document_search",
        "What is the annual leave policy?"
    )
)