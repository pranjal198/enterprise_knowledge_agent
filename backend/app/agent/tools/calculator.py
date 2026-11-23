
import ast
import operator

from app.agent.base import Tool


class CalculatorTool(Tool):

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @property
    def name(self):
        return "calculator"

    @property
    def description(self):
        return (
            "Performs mathematical calculations. "
            "Use this tool for arithmetic, percentages, "
            "multiplication, division and powers."
        )

    def _evaluate(self, node):

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numeric values are allowed.")

            return node.value

        if isinstance(node, ast.BinOp):
            operation = self.OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported mathematical operation.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large.")

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            operation = self.OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported unary operation.")

            return operation(self._evaluate(node.operand))

        raise ValueError("Invalid mathematical expression.")

    def execute(self, tool_input: str):

        try:
            expression = ast.parse(
                tool_input,
                mode="eval"
            )

            result = self._evaluate(expression.body)

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
