"""Course Catalog MCP Server — search the course catalog knowledge base."""

import os

import boto3
from fastmcp import FastMCP

mcp = FastMCP("course-catalog-mcp-server")

KB_ID = os.environ.get("KNOWLEDGE_BASE_ID", "NCGF0S9LJR")
REGION = os.environ.get("AWS_REGION", "us-west-2")


@mcp.tool()
def search_course_catalog(query: str) -> dict:
    """Search the course catalog knowledge base for course information.

    Args:
        query: Natural language search query about courses.

    Returns:
        Dict with list of matching content snippets, relevance scores, and count.
    """
    try:
        client = boto3.client("bedrock-agent-runtime", region_name=REGION)
        response = client.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": 5}
            },
        )
        results = []
        for item in response.get("retrievalResults", []):
            content = item.get("content", {}).get("text", "")
            score = item.get("score", 0.0)
            results.append({"content": content, "score": score})
        return {"results": results, "count": len(results)}
    except Exception as e:
        return {"error": f"Failed to search course catalog: {str(e)}"}


if __name__ == "__main__":
    if os.environ.get("MCP_TRANSPORT") == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", stateless_http=True)
    else:
        mcp.run()
