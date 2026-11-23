
from app.agent import create_tool_registry
from app.agent.controller import AgentController


registry = create_tool_registry()

agent = AgentController(
    registry=registry,
    max_iterations=5
)


question = """
According to our company policy, if I have 12 casual
leaves and take 25% of them, how many casual leaves
will remain?
"""

result = agent.answer(question)

print("\nFINAL ANSWER:")
print(result["answer"])

print("\nTOOLS EXECUTED:")

for tool in result["tool_calls"]:
    print("Tool:", tool["tool"])
    print("Input:", tool["input"])
    print("Result:", tool["result"])
    print("-" * 40)
