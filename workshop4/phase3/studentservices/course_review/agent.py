"""Course Review Agent — RAG queries against Bedrock Knowledge Base and DynamoDB reviews.

Usage:
    agentcore dev --runtime CourseReviewAgent
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import boto3
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID", "NCGF0S9LJR")
COURSE_REVIEWS_TABLE = os.environ.get("COURSE_REVIEWS_TABLE", "course_reviews")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Course Review Assistant for Any University (any.edu).
You help students find information about courses from the course catalog and student reviews.

Use the available tools to:
- Search the course catalog (knowledge base) for course descriptions, prerequisites, and details
- Look up student reviews and ratings for specific courses

Always provide helpful, accurate information based on the data returned by the tools.
"""


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def search_course_catalog(query: str) -> str:
    """Search the course catalog knowledge base for course information.

    Args:
        query: The search query about courses (e.g., "machine learning prerequisites")
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
            return "[Course Review Agent] No matching course catalog information found."

        output_parts = ["[Course Review Agent] Course Catalog Results:"]
        for i, result in enumerate(results, 1):
            content = result.get("content", {}).get("text", "No content")
            score = result.get("score", 0)
            output_parts.append(f"\n--- Result {i} (relevance: {score:.2f}) ---\n{content}")

        return "\n".join(output_parts)
    except Exception:
        return "[Course Review Agent] No matching course catalog information found."


@tool
def get_course_reviews(course_name: str) -> str:
    """Get student reviews for a specific course.

    Args:
        course_name: The course name to look up reviews for (e.g., "CS 441")
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(COURSE_REVIEWS_TABLE)

        # Try exact match first
        response = table.scan(
            FilterExpression="contains(course_name, :cn)",
            ExpressionAttributeValues={":cn": course_name},
        )
        items = response.get("Items", [])

        if not items:
            return f"[Course Review Agent] No reviews available for '{course_name}'."

        output_parts = [f"[Course Review Agent] Reviews for '{course_name}':"]
        for item in items[:10]:
            rating = item.get("rating", "N/A")
            review = item.get("review", "No review text")
            student = item.get("student_id", "Anonymous")
            output_parts.append(f"\n- Rating: {rating}/5 | Student: {student}\n  {review}")

        return "\n".join(output_parts)
    except Exception:
        return f"[Course Review Agent] No reviews available for '{course_name}'."


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
        tools=[search_course_catalog, get_course_reviews],
    )

    response = agent(prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
