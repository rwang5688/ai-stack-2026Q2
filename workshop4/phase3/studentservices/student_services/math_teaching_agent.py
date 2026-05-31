"""Math Teaching Agent — solves math problems with step-by-step explanations."""

import json

from strands import Agent, tool
from strands.models import BedrockModel

from .calculator import calculator


MATH_TEACHING_AGENT_PROMPT = """You are the Math Teaching Assistant for Any University (any.edu).
You solve math problems with clear, step-by-step explanations.
Use the calculator tool for all arithmetic to ensure accuracy.
Break complex problems into numbered steps and verify your final answer."""


@tool
def math_teaching_agent(query: str) -> str:
    """Solve math problems with step-by-step explanations using a local calculator."""
    # Lazy import to avoid circular dependency with student_services_agent
    from .student_services_agent import get_model_config

    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=MATH_TEACHING_AGENT_PROMPT,
        tools=[calculator],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → math_teaching_agent → calculator (local)",
    })
