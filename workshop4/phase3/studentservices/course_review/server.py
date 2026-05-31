"""Course Reviews MCP Server — retrieve student reviews from DynamoDB."""

import os

import boto3
from fastmcp import FastMCP

mcp = FastMCP("course-reviews-mcp-server")

TABLE_NAME = os.environ.get("COURSE_REVIEW_TABLE", "course_review")
REGION = os.environ.get("AWS_REGION", "us-west-2")


@mcp.tool()
def get_course_reviews(course_name: str) -> dict:
    """Get student reviews for a course from DynamoDB.

    Args:
        course_name: Full or partial course name to search for.

    Returns:
        Dict with list of matching reviews and count, or error dict.
    """
    try:
        dynamodb = boto3.resource("dynamodb", region_name=REGION)
        table = dynamodb.Table(TABLE_NAME)

        response = table.scan(
            FilterExpression="contains(course_name, :cn)",
            ExpressionAttributeValues={":cn": course_name},
        )

        items = response.get("Items", [])
        if not items:
            return {"message": f"No reviews found for '{course_name}'", "reviews": [], "count": 0}

        reviews = [
            {
                "course_name": item.get("course_name", ""),
                "rating": item.get("rating", ""),
                "review": item.get("review", ""),
                "student_id": item.get("student_id", ""),
            }
            for item in items[:10]
        ]

        return {"reviews": reviews, "count": len(reviews)}
    except Exception as e:
        return {"error": f"Failed to retrieve reviews: {str(e)}"}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
