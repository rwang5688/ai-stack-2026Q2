"""
Math Teaching Agent

Provides step-by-step mathematical problem solving with calculator tools.
Uses real-world analogies and intermediate calculations to teach concepts.
"""

import sys
import os

from strands import Agent, tool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.config import get_model_config
from shared.cross_platform_tools import get_math_tools
from shared.model_factory import create_model_from_config


MATH_TEACHING_SYSTEM_PROMPT = """You are a mathematics teaching assistant. Your approach:

1. Mathematical Operations:
   - Arithmetic calculations
   - Algebraic problem-solving
   - Geometric analysis
   - Statistical computations

2. Teaching Method:
   - Show step-by-step solutions
   - Use the calculator for intermediate calculations
   - Explain reasoning at each step
   - Provide real-world analogies when helpful
   - Link concepts to practical applications

3. Guidelines:
   - Always show your work
   - Break complex problems into smaller steps
   - Verify answers with the calculator
   - If a question is not math-related, suggest how to rephrase it as a math problem

Focus on clarity and systematic problem-solving while ensuring students understand the underlying concepts."""


@tool
def math_assistant(query: str) -> str:
    """
    Process mathematical queries with step-by-step solutions.

    Args:
        query: A mathematical question or problem from the user.

    Returns:
        A detailed solution with explanations and intermediate steps.
    """
    try:
        print("Routed to Math Teaching Assistant")

        model_config = get_model_config()
        model = create_model_from_config(model_config)

        math_tools = get_math_tools()

        agent = Agent(
            model=model,
            system_prompt=MATH_TEACHING_SYSTEM_PROMPT,
            tools=math_tools,
        )

        formatted_query = (
            f"Please solve the following mathematical problem, "
            f"showing all steps and explaining concepts clearly: {query}"
        )

        response = agent(formatted_query)
        text_response = str(response)

        if text_response.strip():
            return f"[Math Teaching Agent]\n\n{text_response}"

        return "[Math Teaching Agent]\n\nI couldn't solve this problem. Please try rephrasing it as a specific math question."

    except Exception as e:
        return f"[Math Teaching Agent]\n\nError: {str(e)}"
