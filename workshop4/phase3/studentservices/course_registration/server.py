"""Course Registration MCP Server — register students in courses via DynamoDB."""

import os
import uuid

import boto3
from fastmcp import FastMCP

mcp = FastMCP("course-registration-mcp-server")

TABLE_NAME = os.environ.get("COURSE_REGISTRATION_TABLE", "course_registration")
REGION = os.environ.get("AWS_REGION", "us-west-2")


@mcp.tool()
def register_course(student_id: str, course_name: str, semester: str) -> dict:
    """Register a student in a course.

    Args:
        student_id: The student's unique identifier.
        course_name: Name of the course to register for.
        semester: The semester for registration (e.g. "Fall 2026").

    Returns:
        Success dict with registration details, or error dict if validation fails.
    """
    # Validate all required parameters
    missing = [
        field
        for field, value in [
            ("student_id", student_id),
            ("course_name", course_name),
            ("semester", semester),
        ]
        if not value or not value.strip()
    ]
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}"}

    # Strip whitespace from all parameters
    student_id = student_id.strip()
    course_name = course_name.strip()
    semester = semester.strip()

    # Generate registration ID
    reg_id = str(uuid.uuid4())

    # Write to DynamoDB
    try:
        dynamodb = boto3.resource("dynamodb", region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                "reg_id": reg_id,
                "student_id": student_id,
                "course_name": course_name,
                "semester": semester,
            }
        )
    except Exception as e:
        return {"error": f"Failed to register course: {str(e)}"}

    return {
        "success": True,
        "reg_id": reg_id,
        "student_id": student_id,
        "course_name": course_name,
        "semester": semester,
    }


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
