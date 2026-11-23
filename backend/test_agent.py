
from app.agent import create_tool_registry
from app.agent.controller import AgentController


# 1. Create the tool registry
registry = create_tool_registry()

# 2. Create the agent
agent = AgentController(registry)


# 3. Test different questions
questions = [
    "What is 15% of 80000?",

    "What is our company's annual leave policy?",

    "What are the latest developments in artificial intelligence?"
]


for question in questions:

    print("\n" + "=" * 60)
    print("QUESTION:", question)

    result = agent.answer(question)

    print("\nANSWER:", result["answer"])

    print("\nTOOLS USED:")

    for tool in result["tool_calls"]:
        print(tool["tool"])
