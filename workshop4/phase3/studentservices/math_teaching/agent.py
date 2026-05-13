"""Math Teaching Agent — step-by-step mathematical tutoring with calculator tools.

Usage:
    agentcore dev --runtime MathTeachingAgent
"""

import math
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Math Teaching Assistant for Any University (any.edu).
You help students solve math problems with clear, step-by-step explanations.

Guidelines:
- Break complex problems into numbered sub-steps
- Show intermediate calculations using the calculator tool
- Explain the reasoning behind each step
- Use real-world analogies where applicable
- Verify your final answer with the calculator

Use the calculator tool for all arithmetic operations to ensure accuracy.
"""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 3 * 4", "math.sqrt(16)")
    """
    try:
        # Allow math module functions
        allowed_names = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"[Math Teaching Agent] {expression} = {result}"
    except Exception as e:
        return f"[Math Teaching Agent] Error evaluating '{expression}': {str(e)}"


# ---------------------------------------------------------------------------
# BedrockAgentCoreApp entrypoint
# ---------------------------------------------------------------------------
app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict, context: dict | None = None) -> dict:
    prompt = payload.get("prompt", "")
    if not prompt or not prompt.strip():
        return {"response": "Error: 'prompt' field is required."}

    model = BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name="us-west-2",
        max_tokens=4096,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[calculator],
    )

    response = agent(prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
