"""
Course Registration Agent

Handles student course registration by writing to DynamoDB.
"""

import sys
import os
import uuid

import boto3
from botocore.config import Config
from strands import Agent, tool

# Add docker_app directory to path for sibling imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_aws_region, get_course_registration_table, get_model_config
from shared.model_factory import create_model_from_config


BOTO_CONFIG = Config(read_timeout=30, connect_timeout=10, retries={"max_attempts": 2})

COURSE_REGISTRATION_SYSTEM_PROMPT = """You are a course registration assistant. You help students register for courses.

To register a student, you need three pieces of information:
1. Student ID (e.g., "STU001")
2. Course name (e.g., "CS 441 Machine Learning")
3. Semester (e.g., "Fall 2026")

If any information is missing, ask the student to provide it before proceeding.
After successful registration, confirm the details back to the student."""


@tool
def register_student(student_id: str, course_name: str, semester: str) -> str:
    """
    Register a student for a course by writing to DynamoDB.

    Args:
        student_id: The student's ID (e.g., "STU001")
        course_name: The course to register for (e.g., "CS 441 Machine Learning")
        semester: The semester for registration (e.g., "Fall 2026")

    Returns:
        Confirmation message with registration details, or error message.
    """
    # Validate parameters
    missing = []
    if not student_id or not student_id.strip():
        missing.append("student_id")
    if not course_name or not course_name.strip():
        missing.append("course_name")
    if not semester or not semester.strip():
        missing.append("semester")

    if missing:
        return f"Registration failed. Missing required parameters: {', '.join(missing)}"

    table_name = get_course_registration_table()
    region = get_aws_region()

    try:
        dynamodb = boto3.resource("dynamodb", region_name=region, config=BOTO_CONFIG)
        table = dynamodb.Table(table_name)

        reg_id = str(uuid.uuid4())

        table.put_item(
            Item={
                "reg_id": reg_id,
                "student_id": student_id.strip(),
                "course_name": course_name.strip(),
                "semester": semester.strip(),
            }
        )

        return (
            f"Registration successful!\n"
            f"  Registration ID: {reg_id}\n"
            f"  Student: {student_id.strip()}\n"
            f"  Course: {course_name.strip()}\n"
            f"  Semester: {semester.strip()}\n"
            f"A confirmation has been recorded."
        )

    except Exception as e:
        # Sanitize error — don't expose table names, ARNs, or account IDs
        error_msg = str(e)
        if "arn:" in error_msg.lower() or "table/" in error_msg.lower():
            return "Registration failed due to a database error. Please try again later."
        return f"Registration failed: {error_msg}"


@tool
def course_registration_assistant(query: str) -> str:
    """
    Process course registration requests.

    Args:
        query: A registration request from a student (should include student ID, course, and semester).

    Returns:
        Registration confirmation or request for missing information.
    """
    try:
        print("Routed to Course Registration Assistant")

        model_config = get_model_config()
        model = create_model_from_config(model_config)

        agent = Agent(
            model=model,
            system_prompt=COURSE_REGISTRATION_SYSTEM_PROMPT,
            tools=[register_student],
        )

        response = agent(query)
        text_response = str(response)

        if text_response.strip():
            return f"[Course Registration Agent]\n\n{text_response}"

        return "[Course Registration Agent]\n\nI couldn't process your registration request. Please provide your student ID, course name, and semester."

    except Exception as e:
        return f"[Course Registration Agent]\n\nError: {str(e)}"
