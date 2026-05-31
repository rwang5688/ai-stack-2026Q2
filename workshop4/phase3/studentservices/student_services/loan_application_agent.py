"""Loan Application Agent — predicts loan acceptance via MCP Gateway."""

import json

from strands import Agent, tool
from strands.models import BedrockModel


LOAN_APPLICATION_AGENT_PROMPT = """You are the Loan Offering Assistant for Any University (any.edu).
You predict loan acceptance based on customer features. Use the predict_loan tool with the CSV features string.
CRITICAL: Pass the user's CSV string EXACTLY as-is to predict_loan. Do NOT reformat, recount, or modify it.
Interpret results: score >= 0.5 = Accept, score < 0.5 = Reject. Confidence = distance from 0.5 threshold."""


@tool
def loan_application_agent(query: str) -> str:
    """Predict loan acceptance based on 59 numeric feature values provided as CSV."""
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
        system_prompt=LOAN_APPLICATION_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → loan_application_agent → AgentCore Gateway → LoanApplicationMcp",
    })
