"""Course Registration Agent — registers students in courses via DynamoDB.

Usage:
    agentcore dev --runtime CourseRegistrationAgent
"""

import os
import sys
import uuid

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import boto3
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
COURSE_REGISTRATION_TABLE = os.environ.get("COURSE_REGISTRATION_TABLE", "course_registration")

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Course Registration Assistant for Any University (any.edu).
You help students register for courses.

To register a student, you need:
- student_id: The student's ID (e.g., STU001)
- course_name: The full course name (e.g., CS 441 Machine Learning)
- semester: The semester (e.g., Fall 2026)

Use the register_course tool to complete registrations.
If any required field is missing, ask the student to provide it.
"""


# ---------------------------------------------------------------------------
# Pure validation function
# ---------------------------------------------------------------------------
def validate_registration(student_id, course_name, semester) -> list[str]:
    """Returns list of field names that are missing or empty."""
    errors = []
    if not student_id or not str(student_id).strip():
        errors.append("student_id")
    if not course_name or not str(course_name).strip():
        errors.append("course_name")
    if not semester or not str(semester).strip():
        errors.append("semester")
    return errors


# ---------------------------------------------------------------------------
# DynamoDB registration
# ---------------------------------------------------------------------------
def do_registration(student_id: str, course_name: str, semester: str) -> dict:
    """Write registration record to DynamoDB. Returns result dict."""
    invalid_fields = validate_registration(student_id, course_name, semester)
    if invalid_fields:
        return {"error": f"Missing or empty fields: {', '.join(invalid_fields)}"}

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
        return {"error": "Registration failed due to a database error. Please try again later."}

    return {
        "success": True,
        "reg_id": reg_id,
        "student_id": student_id.strip(),
        "course_name": course_name.strip(),
        "semester": semester.strip(),
    }


# ---------------------------------------------------------------------------
# Tool function
# ---------------------------------------------------------------------------
from strands import tool


@tool
def register_course(student_id: str, course_name: str, semester: str) -> str:
    """Register a student for a course.

    Args:
        student_id: The student's ID (e.g., STU001)
        course_name: The full course name (e.g., CS 441 Machine Learning)
        semester: The semester (e.g., Fall 2026)
    """
    result = do_registration(student_id, course_name, semester)
    if "error" in result:
        return f"[Course Registration Agent] Error: {result['error']}"
    return (
        f"[Course Registration Agent] Registration successful!\n"
        f"Registration ID: {result['reg_id']}\n"
        f"Student: {result['student_id']}\n"
        f"Course: {result['course_name']}\n"
        f"Semester: {result['semester']}"
    )


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
        tools=[register_course],
    )

    response = agent(prompt)
    return {"response": str(response)}


if __name__ == "__main__":
    app.run()
