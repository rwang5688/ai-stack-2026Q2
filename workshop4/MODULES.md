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

## Module 2: Building Weather Agent with Strands

**AWS Workshop Link:** [Module 2: Building Weather Agent with Strands](https://catalog.workshops.aws/strands/en-US/module-2-building-weather-agent-with-strands)

**Strands Agents Docs on GitHub Link:** [weather_forecaster.py](https://github.com/strands-agents/docs/blob/main/docs/examples/python/weather_forecaster.py)


### Description

This module demonstrates how to integrate Strands agents with external APIs using the built-in `http_request` tool. The example creates a weather forecasting agent that connects with the National Weather Service API to retrieve and present weather information through natural language interactions.

The code showcases:
- Creating an agent with HTTP capabilities using the `http_request` tool
- Multi-step API workflow (get coordinates, then forecast data)
- Processing JSON responses from external APIs
- Converting technical weather data into user-friendly language
- Error handling for HTTP requests and API responses
- Interactive command-line interface for weather queries

### How to Run

**All Platforms (Linux/macOS/Windows):**
```bash
cd workshop4/examples/module2
uv run weather_forecaster.py
```

*Note: This example works cross-platform without modification as it uses the standard Strands `http_request` tool.*

### Sample Questions

Try these example queries when the weather agent is running:

1. **Basic location queries:**
   ```
   What's the weather like in Seattle?
   ```

2. **Future weather:**
   ```
   Will it rain tomorrow in Miami?
   ```

3. **Comparative queries:**
   ```
   Compare the temperature in New York and Chicago this weekend
   ```

4. **Specific conditions:**
   ```
   What's the forecast for San Francisco this week?
   ```

5. **General weather questions:**
   ```
   Should I bring an umbrella in Boston today?
   ```

### API Details

This example uses the **National Weather Service API**:
- **No API key required** - completely free to use
- **US locations only** - covers all United States locations
- **Multi-step process**: First gets coordinates/grid info, then retrieves forecast
- **Rich data**: Temperature, precipitation, wind, detailed conditions
- **Production ready**: Reliable government API service

### Technical Implementation

The agent handles a sophisticated multi-step workflow:

1. **Location Resolution**: Converts location names to coordinates using NWS points API
2. **Forecast Retrieval**: Uses returned forecast URL to get detailed weather data
3. **Data Processing**: Transforms technical weather data into conversational responses
4. **Natural Language**: Presents information in user-friendly format with context

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
