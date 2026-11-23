
from app.agent import create_tool_registry
from app.agent.controller import AgentController


registry = create_tool_registry()
agent = AgentController(registry)


test_cases = [
    "Calculate 25% of 64000",

    "How many casual leaves do employees receive?",

    "What are the latest developments in generative AI?",

    "What is 500 multiplied by 12?",

    "According to our company policy, how many earned leaves are allowed?"
]


for question in test_cases:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    result = agent.answer(question)

    print("ANSWER:", result["answer"])

    print("TOOLS USED:")

    for tool in result["tool_calls"]:
        print("-", tool["tool"])
