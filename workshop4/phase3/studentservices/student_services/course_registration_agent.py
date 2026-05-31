"""Course Registration Agent — handles student course registration via MCP Gateway."""

import json

from strands import Agent, tool
from strands.models import BedrockModel


COURSE_REGISTRATION_AGENT_PROMPT = """You are the Course Registration Assistant for Any University (any.edu).
You help students register for courses. Use the register_course tool with student_id, course_name, and semester.
If any required field is missing from the user's request, ask for it before calling the tool."""


@tool
def course_registration_agent(query: str) -> str:
    """Register students in courses. Requires student_id, course_name, and semester."""
    # Lazy import to avoid circular dependency with student_services_agent
    from .student_services_agent import get_mcp_client, get_model_config

    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=COURSE_REGISTRATION_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → course_registration_agent → AgentCore Gateway → CourseRegistrationMcp",
    })
