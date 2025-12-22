"""
MCP Calculator Example - Windows Compatible Version

This example demonstrates how to:
1. Create a simple MCP server that provides calculator functionality
2. Connect a Strands agent to the MCP server
3. Use the calculator tools through natural language

Windows-specific fixes:
- Increased startup delay for server initialization
- Better error handling for connection issues
- Uses 127.0.0.1 instead of localhost for better Windows compatibility
"""

import threading
import time
import sys
import platform

from mcp.client.streamable_http import streamablehttp_client
from mcp.server import FastMCP
from strands import Agent
from strands.tools.mcp.mcp_client import MCPClient


def start_calculator_server():
    """
    Initialize and start an MCP calculator server.

    This function creates a FastMCP server instance that provides calculator tools
    for performing basic arithmetic operations. The server uses Streamable HTTP
    transport for communication.
    """
    # Create an MCP server with a descriptive name
    mcp = FastMCP("Calculator Server")

    # Define a simple addition tool
    @mcp.tool(description="Add two numbers together")
    def add(x: int, y: int) -> int:
        """Add two numbers and return the result.

        Args:
            x: First number
            y: Second number

        Returns:
            The sum of x and y
        """
        return x + y

    # Define a subtraction tool
    @mcp.tool(description="Subtract one number from another")
    def subtract(x: int, y: int) -> int:
        """Subtract y from x and return the result.

        Args:
            x: Number to subtract from
            y: Number to subtract

        Returns:
            The difference (x - y)
        """
        return x - y

    # Define a multiplication tool
    @mcp.tool(description="Multiply two numbers together")
    def multiply(x: int, y: int) -> int:
        """Multiply two numbers and return the result.

        Args:
            x: First number
            y: Second number

        Returns:
            The product of x and y
        """
        return x * y

    # Define a division tool
    @mcp.tool(description="Divide one number by another")
    def divide(x: float, y: float) -> float:
        """Divide x by y and return the result.

        Args:
            x: Numerator
            y: Denominator (must not be zero)

        Returns:
            The quotient (x / y)

        Raises:
            ValueError: If y is zero
        """
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

    # Run the server with Streamable HTTP transport on the default port (8000)
    print("Starting MCP Calculator Server on http://127.0.0.1:8000")
    mcp.run(transport="streamable-http")


def wait_for_server(max_attempts=10, delay=1):
    """
    Wait for the MCP server to be ready by attempting connections.
    
    Args:
        max_attempts: Maximum number of connection attempts
        delay: Delay between attempts in seconds
    
    Returns:
        bool: True if server is ready, False otherwise
    """
    import requests
    
    for attempt in range(max_attempts):
        try:
            # Try to connect to the server
            response = requests.get("http://127.0.0.1:8000", timeout=2)
            print(f"Server ready after {attempt + 1} attempts")
            return True
        except requests.exceptions.RequestException:
            print(f"Attempt {attempt + 1}/{max_attempts}: Server not ready, waiting...")
            time.sleep(delay)
    
    print("Server failed to start after maximum attempts")
    return False


def main():
    """
    Main function that starts the MCP server in a background thread
    and creates a Strands agent that uses the MCP tools.
    """
    print(f"Running on {platform.system()} {platform.release()}")
    
    # Start the MCP server in a background thread
    server_thread = threading.Thread(target=start_calculator_server, daemon=True)
    server_thread.start()

    # Wait for the server to start with better detection
    print("Waiting for MCP server to start...")
    
    # Use longer delay on Windows due to networking differences
    startup_delay = 5 if platform.system() == "Windows" else 3
    time.sleep(startup_delay)
    
    # Verify server is actually ready
    if not wait_for_server():
        print("Failed to start MCP server. Exiting.")
        return

    # Connect to the MCP server using Streamable HTTP transport
    print("Connecting to MCP server...")

    def create_streamable_http_transport():
        # Use 127.0.0.1 instead of localhost for better Windows compatibility
        return streamablehttp_client("http://127.0.0.1:8000/mcp/")

    streamable_http_mcp_client = MCPClient(create_streamable_http_transport)

    # Create a system prompt that explains the calculator capabilities
    system_prompt = """
    You are a helpful calculator assistant that can perform basic arithmetic operations.
    You have access to the following calculator tools:
    - add: Add two numbers together
    - subtract: Subtract one number from another
    - multiply: Multiply two numbers together
    - divide: Divide one number by another
    
    When asked to perform calculations, use the appropriate tool rather than calculating the result yourself.
    Explain the calculation and show the result clearly.
    """

    # Use the MCP client in a context manager with better error handling
    try:
        with streamable_http_mcp_client:
            # Get the tools from the MCP server
            tools = streamable_http_mcp_client.list_tools_sync()

            print(f"Available MCP tools: {[tool.tool_name for tool in tools]}")

            # Create an agent with the MCP tools
            agent = Agent(system_prompt=system_prompt, tools=tools)

            # Interactive loop
            print("\nCalculator Agent Ready! Type 'exit' to quit.\n")
            while True:
                try:
                    # Get user input
                    user_input = input("Question: ")

                    # Check if the user wants to exit
                    if user_input.lower() in ["exit", "quit"]:
                        break

                    # Process the user's request
                    print("\nThinking...\n")
                    response = agent(user_input)

                    # Print the agent's response
                    print(f"Answer: {response}\n")
                    
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break
                except Exception as e:
                    print(f"Error processing request: {e}")
                    print("Please try again or type 'exit' to quit.\n")
                    
    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure no other application is using port 8000")
        print("2. Try running as administrator if on Windows")
        print("3. Check Windows Firewall settings")
        print("4. Ensure Python has network permissions")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)