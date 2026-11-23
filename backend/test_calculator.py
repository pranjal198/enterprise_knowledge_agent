from app.agent.tools.calculator import CalculatorTool

calculator = CalculatorTool()

print(calculator.execute("100 + 200"))
print(calculator.execute("500 * 0.15"))
print(calculator.execute("(1000 + 500) / 3"))
print(calculator.execute("2 ** 5"))
print(calculator.execute("10 / 0"))