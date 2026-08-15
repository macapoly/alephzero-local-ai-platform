import ast
import operator


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str):
    """
    Safely evaluate a mathematical expression.
    """

    expression = expression.strip()

    if not expression:
        raise ValueError("Expression cannot be empty.")

    expression = expression.replace("^", "**")

    try:
        tree = ast.parse(
            expression,
            mode="eval"
        )

        def evaluate(node):

            if isinstance(node, ast.Constant):

                if isinstance(
                    node.value,
                    (int, float)
                ):
                    return node.value

                raise ValueError(
                    "Invalid number."
                )

            if isinstance(node, ast.BinOp):

                left = evaluate(node.left)
                right = evaluate(node.right)

                operation = ALLOWED_OPERATORS.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError(
                        "Operator not allowed."
                    )

                return operation(left, right)

            if isinstance(node, ast.UnaryOp):

                operand = evaluate(node.operand)

                operation = ALLOWED_OPERATORS.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError(
                        "Operator not allowed."
                    )

                return operation(operand)

            raise ValueError(
                "Invalid mathematical expression."
            )

        return evaluate(tree.body)

    except ZeroDivisionError:
        raise ValueError(
            "Cannot divide by zero."
        )

    except ValueError:
        raise

    except Exception:
        raise ValueError(
            "Could not calculate expression."
        )
