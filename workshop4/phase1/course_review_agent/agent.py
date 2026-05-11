"""
Course Review Agent

Provides RAG capabilities combining Bedrock Knowledge Base (course catalog)
with DynamoDB (course reviews) to answer questions about courses.
"""

import json
import sys
import os

import boto3
from botocore.config import Config
from strands import Agent, tool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from streamlit_app.config import (
    get_aws_region,
    get_course_reviews_table,
    get_knowledge_base_id,
    get_model_config,
)
from shared.model_factory import create_model_from_config


BOTO_CONFIG = Config(read_timeout=30, connect_timeout=10, retries={"max_attempts": 2})

COURSE_REVIEW_SYSTEM_PROMPT = """You are a course review specialist for Any University (any.edu). You help students find information about courses by combining catalog information from the knowledge base with student reviews from the database.

Important context:
- You serve students at Any University. Always assume questions are about this university.
- Do NOT ask which university or institution the student is asking about.
- The knowledge base contains the official Any University course catalog.
- The reviews database contains student reviews for Any University courses.

When answering questions:
1. Search the course catalog for official course information (descriptions, prerequisites, credits)
2. Look up student reviews for ratings, difficulty, and student experiences
3. Combine both sources to give comprehensive answers
4. If no information is found, clearly state what's unavailable

Be helpful, concise, and factual. Cite whether information comes from the catalog or student reviews."""


@tool
def retrieve_course_catalog(query: str) -> str:
    """
    Query the Bedrock Knowledge Base for course catalog information.

    Args:
        query: A search query about courses (e.g., "machine learning prerequisites")

    Returns:
        Relevant course catalog information from the knowledge base.
    """
    kb_id = get_knowledge_base_id()
    region = get_aws_region()

    if not kb_id:
        return "Knowledge Base not configured. Please check SSM parameters."

    try:
        client = boto3.client(
            "bedrock-agent-runtime", region_name=region, config=BOTO_CONFIG
        )

        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": 5}
            },
        )

        results = response.get("retrievalResults", [])
        if not results:
            return "No matching courses found in the catalog."

        # Format results
        formatted = []
        for i, result in enumerate(results, 1):
            content = result.get("content", {}).get("text", "")
            score = result.get("score", 0)
            if content:
                formatted.append(f"[Result {i}] (relevance: {score:.2f})\n{content}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Error querying course catalog: {str(e)}"


@tool
def query_course_reviews(course_name: str) -> str:
    """
    Query DynamoDB for student reviews of a specific course.

    Args:
        course_name: The course name to look up reviews for (e.g., "CS 441")

    Returns:
        Student reviews for the specified course.
    """
    table_name = get_course_reviews_table()
    region = get_aws_region()

    if not table_name:
        return "Course reviews table not configured."

    try:
        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table(table_name)

        response = table.get_item(Key={"course_name": course_name})

        item = response.get("Item")
        if not item:
            # Try partial match with first 6 chars (e.g., "CS 441")
            short_name = course_name[:6].strip() if len(course_name) > 6 else course_name
            response = table.get_item(Key={"course_name": short_name})
            item = response.get("Item")

        if not item:
            # Scan for partial matches as last resort
            scan_response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr("course_name").contains(
                    course_name[:6] if len(course_name) > 6 else course_name
                ),
                Limit=10,
            )
            items = scan_response.get("Items", [])
            if not items:
                return f"No reviews available for '{course_name}'."
            # Format multiple results
            formatted = []
            for review in items:
                formatted.append(json.dumps(review, default=str, indent=2))
            return f"Found {len(items)} review(s):\n\n" + "\n\n".join(formatted)

        return json.dumps(item, default=str, indent=2)

    except Exception as e:
        return f"Error querying course reviews: {str(e)}"


@tool
def course_review_assistant(query: str) -> str:
    """
    Process course review and catalog queries using RAG (Knowledge Base + DynamoDB).

    Args:
        query: A question about courses, reviews, ratings, or course information.

    Returns:
        A comprehensive answer combining catalog and review information.
    """
    try:
        print("Routed to Course Review Assistant")

        model_config = get_model_config()
        model = create_model_from_config(model_config)

        agent = Agent(
            model=model,
            system_prompt=COURSE_REVIEW_SYSTEM_PROMPT,
            tools=[retrieve_course_catalog, query_course_reviews],
        )

        response = agent(query)
        text_response = str(response)

        if text_response.strip():
            return f"[Course Review Agent]\n\n{text_response}"

        return "[Course Review Agent]\n\nI couldn't find relevant course information. Please try rephrasing your question."

    except Exception as e:
        return f"[Course Review Agent]\n\nError: {str(e)}"
