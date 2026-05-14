"""Course Review MCP Server — Strands Agent wrapped as MCP tool via FastMCP.

The MCP tool delegates to an internal Strands Agent that handles course catalog
queries and review lookups using Bedrock Knowledge Base and DynamoDB.

Usage:
    agentcore dev --runtime CourseReviewMcp
"""

import os

import boto3
from fastmcp import FastMCP
from strands import Agent, tool
from strands.models import BedrockModel

mcp = FastMCP("course-review-mcp-server")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
COURSE_REVIEWS_TABLE = os.environ.get("COURSE_REVIEWS_TABLE", "course_reviews")
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "NCGF0S9LJR")
RUNTIME_NAME = "CourseReviewMcp"

SYSTEM_PROMPT = """You are the Course Review Assistant for Any University (any.edu).
You help students find information about courses from the course catalog and student reviews.

Use the available tools to:
- search_course_catalog: Search the knowledge base for course descriptions, prerequisites, and details
- get_course_reviews: Look up student reviews and ratings for specific courses

Always provide helpful, accurate information based on the data returned by the tools.
If no results are found, let the student know clearly.
"""


# ---------------------------------------------------------------------------
# Inner Strands tools
# ---------------------------------------------------------------------------
@tool
def get_course_reviews(course_name: str) -> str:
    """Get student reviews for a specific course.

    Args:
        course_name: The course name to look up reviews for
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(COURSE_REVIEWS_TABLE)

        response = table.scan(
            FilterExpression="contains(course_name, :cn)",
            ExpressionAttributeValues={":cn": course_name},
        )
        items = response.get("Items", [])

        if not items:
            return f"No reviews available for '{course_name}'."

        output_parts = [f"Reviews for '{course_name}':"]
        for item in items[:10]:
            rating = item.get("rating", "N/A")
            review = item.get("review", "No review text")
            student = item.get("student_id", "Anonymous")
            output_parts.append(f"\n- Rating: {rating}/5 | Student: {student}\n  {review}")

        return "\n".join(output_parts)
    except Exception:
        return f"No reviews available for '{course_name}'."


@tool
def search_course_catalog(query: str) -> str:
    """Search the course catalog knowledge base for course information.

    Args:
        query: The search query about courses
    """
    try:
        client = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)
        response = client.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": 5}
            },
        )
        results = response.get("retrievalResults", [])
        if not results:
            return "No matching course catalog information found."

        output_parts = ["Course Catalog Results:"]
        for i, result in enumerate(results, 1):
            content = result.get("content", {}).get("text", "No content")
            score = result.get("score", 0)
            output_parts.append(f"\n--- Result {i} (relevance: {score:.2f}) ---\n{content}")

        return "\n".join(output_parts)
    except Exception:
        return "No matching course catalog information found."


# ---------------------------------------------------------------------------
# MCP tool (exposed to the gateway — wraps the Strands Agent)
# ---------------------------------------------------------------------------
@mcp.tool()
def course_review_assistant(prompt: str) -> dict:
    """Course Review — search course catalog and student reviews at Any University.

    This agent handles questions about courses, prerequisites, ratings, and reviews.

    Args:
        prompt: Natural language question about courses (e.g., "What are the reviews for CS 441?")

    Returns:
        Dict with the agent's response and runtime identifier.
    """
    model = BedrockModel(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name=AWS_REGION,
        max_tokens=4096,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_course_reviews, search_course_catalog],
    )

    response = agent(prompt)
    return {"response": str(response), "runtime": RUNTIME_NAME}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
