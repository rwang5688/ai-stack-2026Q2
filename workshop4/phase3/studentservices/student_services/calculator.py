import math

from strands import tool

ALLOWED_NAMES = {
    "abs": abs,
    "max": max,
    "min": min,
    "pow": pow,
    "round": round,
    "sum": sum,
    **{k: getattr(math, k) for k in dir(math) if not k.startswith("_")},
}


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Args:
        expression: A mathematical expression (e.g., "2 + 3 * 4", "math.sqrt(16)")
    """
    try:
        result = eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {str(e)}"
