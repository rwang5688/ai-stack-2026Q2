"""Course Registration MCP Server — Strands Agent wrapped as MCP tool via FastMCP.

The MCP tool delegates to an internal Strands Agent that handles course registration
with validation, DynamoDB writes, and conversational responses.

Usage:
    agentcore dev --runtime CourseRegistrationMcp
"""

import os
import uuid

import boto3
from fastmcp import FastMCP
from strands import Agent, tool
from strands.models import BedrockModel

mcp = FastMCP("course-registration-mcp-server")

# ---------------------------------------------------------------------------
# Model configuration — reads from SSM Parameter Store (no caching)
# ---------------------------------------------------------------------------
def get_model_config() -> dict:
    """Get model config from SSM. Resolution: env var → SSM → hardcoded default."""
    model_id = os.environ.get("MODEL_ID")
    if not model_id:
        try:
            ssm = boto3.client("ssm", region_name="us-west-2")
            response = ssm.get_parameter(Name="/student-services/model-id")
            model_id = response["Parameter"]["Value"]
        except Exception:
            model_id = None
    if not model_id:
        model_id = "us.amazon.nova-2-lite-v1:0"
    return {"model_id": model_id, "region": "us-west-2", "max_tokens": 4096}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
COURSE_REGISTRATION_TABLE = os.environ.get("COURSE_REGISTRATION_TABLE", "course_registration")
RUNTIME_NAME = "CourseRegistrationMcp"

SYSTEM_PROMPT = """You are the Course Registration Assistant for Any University (any.edu).
You help students register for courses.

To register a student, you need:
- student_id: The student's ID (e.g., STU001)
- course_name: The full course name (e.g., CS 441 Machine Learning)
- semester: The semester (e.g., Fall 2026)

Use the register_course tool to complete registrations.
If any required field is missing, ask the student to provide it.
Always confirm the registration details in your response.
"""


# ---------------------------------------------------------------------------
# Inner Strands tool
# ---------------------------------------------------------------------------
@tool
def register_course(student_id: str, course_name: str, semester: str) -> str:
    """Register a student for a course in DynamoDB.

    Args:
        student_id: The student's ID
        course_name: The full course name
        semester: The semester
    """
    errors = []
    if not student_id or not student_id.strip():
        errors.append("student_id")
    if not course_name or not course_name.strip():
        errors.append("course_name")
    if not semester or not semester.strip():
        errors.append("semester")

    if errors:
        return f"Error: Missing or empty fields: {', '.join(errors)}"

    reg_id = str(uuid.uuid4())
    try:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        table = dynamodb.Table(COURSE_REGISTRATION_TABLE)
        table.put_item(Item={
            "reg_id": reg_id,
            "student_id": student_id.strip(),
            "course_name": course_name.strip(),
            "semester": semester.strip(),
        })
    except Exception:
        return "Error: Registration failed due to a database error. Please try again later."

    return (
        f"Registration successful!\n"
        f"Registration ID: {reg_id}\n"
        f"Student: {student_id.strip()}\n"
        f"Course: {course_name.strip()}\n"
        f"Semester: {semester.strip()}"
    )


# ---------------------------------------------------------------------------
# MCP tool (exposed to the gateway — wraps the Strands Agent)
# ---------------------------------------------------------------------------
@mcp.tool()
def course_registration_assistant(prompt: str) -> dict:
    """Course Registration — register students in courses at Any University.

    This agent handles course registration requests. Provide a natural language
    request including student_id, course_name, and semester.

    Args:
        prompt: Natural language registration request (e.g., "Register STU001 for CS 441 in Fall 2026")

    Returns:
        Dict with the agent's response and runtime identifier.
    """
    model_config = get_model_config()
    model = BedrockModel(
        model_id=model_config["model_id"],
        region_name=model_config["region"],
        max_tokens=model_config["max_tokens"],
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[register_course],
    )

    response = agent(prompt)
    return {"response": str(response), "runtime": RUNTIME_NAME}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
