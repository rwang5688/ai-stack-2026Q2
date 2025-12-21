# Workshop 4 Modules

This document provides an overview of all workshop modules with links to examples and instructions for running each module.

**⚠️ AWS Credentials Required:** All examples require AWS credentials with Amazon Bedrock permissions. Ensure your runtime environment has proper IAM permissions to invoke Bedrock models.

## Module 1: Building with Model Context Protocol (MCP)

**AWS Workshop Link:** [Module 1: Building with Model Context Protocol (MCP)](https://catalog.workshops.aws/strands/en-US/module-1-building-calculator-agent-with-mcp-and-strands)

**Strands Agents Docs on GitHub Link:** [mcp_calculator.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/mcp_calculator.py)

### Description

This module demonstrates how to integrate Strands agents with external tools using the Model Context Protocol (MCP). The example creates a simple MCP server that provides calculator functionality (add, subtract, multiply, divide) and shows how to connect a Strands agent to use these tools through natural language interactions.

The code showcases:
- Creating an MCP server with FastMCP that provides calculator tools
- Starting the server in a background thread using Streamable HTTP transport
- Connecting a Strands agent to the MCP server using MCPClient
- Converting MCP tools into standard AgentTools that the agent can use
- Interactive command-line interface for natural language calculator queries

### How to Run

**Standard Version (Linux/macOS):**
```bash
cd workshop4/examples/module1
uv run mcp_calculator.py
```

**Windows GitBash (if connection issues occur):**
```bash
cd workshop4/examples/module1
uv run mcp_calculator_windows.py
```

### Sample Questions

Try these example queries when the calculator agent is running:

1. **Basic arithmetic:**
   ```
   What is 16 times 16?
   ```

2. **Word problems:**
   ```
   If I have $1000 and spend $246, how much do I have left?
   ```

3. **Mathematical expressions:**
   ```
   What is pi by 4?
   ```

4. **Complex calculations:**
   ```
   What is 24 multiplied by 7 divided by 3?
   ```

5. **Simple operations:**
   ```
   What is 125 plus 375?
   ```

Type `exit` to quit the application, or press `Ctrl+C` to stop the program.

---

*Additional modules will be added as they are developed.*

---

## Platform Differences

For additional help with platform-specific commands and Windows-compatible versions, see [PLATFORM-DIFFERENCES.md](PLATFORM-DIFFERENCES.md).

---

## Windows Troubleshooting

If you encounter `ReadError` or `MCPClientInitializationError` on Windows:

1. **Use the Windows-compatible version** (recommended):
   ```bash
   uv run mcp_calculator_windows.py
   ```

2. **Check port availability**:
   ```bash
   netstat -an | findstr :8000
   ```

3. **Run as Administrator** if needed:
   - Right-click Git Bash → "Run as administrator"

4. **Windows Firewall**: Add Python to firewall exceptions if blocked

5. **Alternative troubleshooting**:
   - The Windows version uses 127.0.0.1 instead of localhost
   - Includes longer startup delays for Windows networking
   - Better error handling for connection issues
