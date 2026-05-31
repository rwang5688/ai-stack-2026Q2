"""Course Review Agent — handles course catalog and review queries via MCP Gateway."""

import json

from strands import Agent, tool
from strands.models import BedrockModel


COURSE_REVIEW_AGENT_PROMPT = """You are the Course Review Assistant for Any University (any.edu).
You help students find information about courses from the course catalog and student reviews.

CRITICAL WORKFLOW: For ANY course-related query, you MUST:
1. FIRST call search_course_catalog to find relevant courses
2. THEN call get_course_reviews for EACH course found (use the course code, e.g., "CS 441")
3. Combine both sources in your response — catalog info AND student reviews

NEVER skip step 2. Even if the user only asks about course descriptions, always include available student reviews."""


@tool
def course_review_agent(query: str) -> str:
    """Handle course catalog and review queries. Use for ANY question about courses, difficulty, reviews, ratings, recommendations, prerequisites, or course information."""
    # Lazy import to avoid circular dependency with student_services_agent
    from student_services_agent import get_mcp_client, get_model_config

    mcp_client = get_mcp_client()
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )
    agent = Agent(
        model=model,
        system_prompt=COURSE_REVIEW_AGENT_PROMPT,
        tools=[mcp_client],
    )
    response = agent(query)
    return json.dumps({
        "response": str(response),
        "routing_path": "StudentServicesAgent → course_review_agent → AgentCore Gateway → CourseCatalogMcp + CourseReviewMcp",
    })
