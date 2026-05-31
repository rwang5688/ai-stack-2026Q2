"""
Student Services Agent (Orchestrator)

Routes user queries to the appropriate specialist agent:
- Course Review Agent: course information, catalog, reviews
- Course Registration Agent: enrolling in courses
- Loan Application Agent: loan acceptance predictions
- Math Teaching Agent: mathematical problem solving
"""

from strands import Agent

from shared.model_factory import create_model_from_config

# Import specialist tool functions
from .course_registration_agent import course_registration_assistant
from .course_review_agent import course_review_assistant
from .loan_application_agent import loan_offering_assistant
from .math_teaching_agent import math_assistant


ORCHESTRATOR_SYSTEM_PROMPT = """You are the Student Services Assistant, an orchestrator that routes student queries to specialized agents.

Available services:
1. **Course Review Assistant** (course_review_assistant): For questions about courses, course catalog, course reviews, ratings, difficulty, prerequisites, and course recommendations.
2. **Course Registration Assistant** (course_registration_assistant): For registering students in courses. Requires student ID, course name, and semester.
3. **Loan Offering Assistant** (loan_offering_assistant): For predicting loan acceptance based on customer features (59 CSV values).
4. **Math Assistant** (math_assistant): For mathematical problem solving, calculations, equations, and math tutoring.

Routing rules:
- Course information, reviews, ratings, catalog queries → course_review_assistant
- Registration, enrollment, sign up for a course → course_registration_assistant
- Loan predictions, loan acceptance, financial features → loan_offering_assistant
- Math problems, calculations, equations, tutoring → math_assistant
- Out-of-domain queries → Respond directly listing the available services above

Always route to the appropriate specialist. Do not attempt to answer domain-specific questions yourself.
When you receive a tool result, pass it through to the user verbatim. Do not summarize or reformat.

CRITICAL for loan predictions: When the user provides comma-separated numeric values, pass the ENTIRE string to loan_offering_assistant EXACTLY as the user typed it. Do NOT count the values, do NOT validate the count, do NOT modify or truncate the string. The specialist will handle validation."""


def create_orchestrator(model_config: dict) -> Agent:
    """
    Create the orchestrator agent with all specialist tools.

    Args:
        model_config: Dictionary with model configuration (provider, model_id, temperature, region).

    Returns:
        Configured Agent instance ready to handle queries.
    """
    model = create_model_from_config(model_config)

    tools = [
        course_review_assistant,
        course_registration_assistant,
        loan_offering_assistant,
        math_assistant,
    ]

    return Agent(
        model=model,
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=tools,
    )
