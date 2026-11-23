
from app.agent import create_tool_registry


registry = create_tool_registry()

# Print all registered tools
for tool in registry.get_all_tools():
    print(tool.name, ":", tool.description)


# Retrieve the calculator
calculator = registry.get_tool("calculator")

print("\nCalculator test:")
print(calculator.execute("100 * 5"))


# Retrieve document search
document_tool = registry.get_tool("document_search")

print("\nDocument search test:")
print(document_tool.execute("What is the annual leave policy?"))
