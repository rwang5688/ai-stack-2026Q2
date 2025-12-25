# Cross-Platform Development Guide

This guide helps you work with Workshop 4 examples across different operating systems, with specific focus on Git Bash compatibility on Windows.

## Quick Reference

### Essential Commands for Workshop

```bash
# Setup (same on all platforms with Git Bash)
cd workshop4
source .venv/bin/activate  # Linux/macOS
source .venv/Scripts/activate  # Windows Git Bash

# Run examples
uv run modules/module1/mcp_calculator.py  # Linux/macOS
uv run modules/module1/mcp_calculator_windows.py  # Windows (if issues)

# Check what's running
netstat -an | grep :8000  # Linux/macOS/Git Bash
netstat -an | findstr :8000  # Windows CMD
```

## Best Practices

### Cross-Platform Development

1. **Use Git Bash on Windows** for consistent command experience
2. **Test on both platforms** when possible
3. **Use `os.path.join()`** for path construction in Python
4. **Use forward slashes** in documentation and examples
5. **Provide platform-specific alternatives** when needed

### Workshop-Specific Tips

1. **Always activate virtual environment first**
2. **Use UV package manager** for consistent dependency management
3. **Check platform-specific examples** (e.g., `mcp_calculator_windows.py`)
4. **Use 127.0.0.1 instead of localhost** on Windows
5. **Allow extra startup time** for Windows networking

## Platform Commands

### File Operations

| Operation | Linux/macOS | Windows (Git Bash) | Windows (CMD) |
|-----------|-------------|-------------------|---------------|
| List files | `ls -la` | `ls -la` | `dir` |
| Change directory | `cd workshop4` | `cd workshop4` | `cd workshop4` |
| Create directory | `mkdir modules` | `mkdir modules` | `mkdir modules` |
| Remove file | `rm file.txt` | `rm file.txt` | `del file.txt` |
| Copy file | `cp src dest` | `cp src dest` | `copy src dest` |

### Network Commands

| Operation | Linux/macOS | Windows (Git Bash) | Windows (CMD) |
|-----------|-------------|-------------------|---------------|
| Check port | `netstat -an \| grep :8000` | `netstat -an \| grep :8000` | `netstat -an \| findstr :8000` |
| Kill process | `kill -9 PID` | `kill -9 PID` | `taskkill /PID PID /F` |
| Find process | `ps aux \| grep python` | `ps aux \| grep python` | `tasklist \| findstr python` |

## Environment Setup

### Making Scripts Executable

**Linux/macOS:**
```bash
chmod +x setup-environment.sh
./setup-environment.sh
```

**Git Bash (Windows):**
```bash
chmod +x setup-environment.sh
./setup-environment.sh
```

**Windows (if script doesn't work):**
```bash
bash setup-environment.sh
```

### Activating Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (Git Bash - Recommended):**
```bash
source .venv/Scripts/activate
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

### Setting AWS Credentials

**Linux/macOS & Git Bash:**
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**Windows CMD:**
```cmd
set AWS_ACCESS_KEY_ID=your_key
set AWS_SECRET_ACCESS_KEY=your_secret
set AWS_DEFAULT_REGION=us-east-1
```

**Windows PowerShell:**
```powershell
$env:AWS_ACCESS_KEY_ID="your_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret"
$env:AWS_DEFAULT_REGION="us-east-1"
```

## Runtime Execution

### Runtime Command Equivalents

| Task | Linux/macOS | Git Bash (Windows) | Windows CMD |
|------|-------------|-------------------|-------------|
| Check Python version | `python --version` | `python --version` | `python --version` |
| Environment variables | `export VAR=value` | `export VAR=value` | `set VAR=value` |
| Install with UV | `uv pip install package` | `uv pip install package` | `uv pip install package` |
| Run Python script | `uv run script.py` | `uv run script.py` | `uv run script.py` |

## Platform-Specific Coding Issues

### MCP Client Windows Connection

**Issue:** MCP client fails with `ReadError` on Windows but works on Linux

**Root Cause:** Windows networking stack handles localhost connections differently

**Solutions:**

1. **Use the Windows-compatible version:**
   ```bash
   uv run mcp_calculator_windows.py
   ```

2. **Use 127.0.0.1 instead of localhost:**
   ```python
   # Instead of:
   streamablehttp_client("http://localhost:8000/mcp/")
   
   # Use:
   streamablehttp_client("http://127.0.0.1:8000/mcp/")
   ```

3. **Increase startup delays:**
   ```python
   # Linux typically needs 2-3 seconds
   time.sleep(2)
   
   # Windows may need 5+ seconds
   time.sleep(5)
   ```

### Cross-Platform Tool Imports (Multi-Agent Systems)

**Issue:** Strands tools `python_repl` and `shell` fail on Windows due to Unix-only dependencies (`fcntl`, `pty`, `termios`)

**Root Cause:** These tools import Unix-specific modules that don't exist on Windows

**Solution:** Dynamic platform detection with tool fallbacks using `cross_platform_tools.py`

#### Implementation Pattern

**1. Create Cross-Platform Tool Module:**
```python
# cross_platform_tools.py
import platform

def get_platform_info():
    """Get detailed platform information."""
    return {
        'system': platform.system(),
        'is_windows': platform.system().lower() == 'windows',
        'is_linux': platform.system().lower() == 'linux',
        'is_macos': platform.system().lower() == 'darwin'
    }

def import_platform_tools():
    """Import platform-specific tools with fallbacks."""
    platform_info = get_platform_info()
    
    if platform_info['is_windows']:
        # Windows: Skip problematic tools
        print("Detected Windows - using limited tool set")
        python_repl = None
        shell = None
    else:
        # Linux/macOS: Import all tools
        try:
            from strands_tools import python_repl, shell
            print(f"Detected {platform_info['system']} - full tool set available")
        except ImportError:
            python_repl = None
            shell = None

def get_computer_science_tools():
    """Get tools available for Computer Science Assistant."""
    tools = [file_read, file_write, editor]  # Always available
    
    if python_repl:
        tools.append(python_repl)
    if shell:
        tools.append(shell)
    
    return tools
```

**2. Update Agent Imports:**
```python
# Before (fails on Windows):
from strands_tools import python_repl, shell, file_read, file_write, editor

# After (cross-platform):
from cross_platform_tools import get_computer_science_tools, get_platform_capabilities
```

**3. Dynamic Tool Assignment:**
```python
# Before (static tool list):
cs_agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    tools=[python_repl, shell, file_read, file_write, editor]
)

# After (dynamic tool list):
available_tools = get_computer_science_tools()
cs_agent = Agent(
    system_prompt=enhanced_prompt,
    tools=available_tools
)
```

**4. Platform-Aware System Prompts:**
```python
capabilities = get_platform_capabilities()
platform_note = ""

if not capabilities['available_tools']['python_repl']:
    platform_note += "\nNote: Python code execution not available. Provide code examples with explanations."

if not capabilities['available_tools']['shell']:
    platform_note += "\nNote: Shell execution not available. Provide command examples with explanations."

enhanced_prompt = BASE_SYSTEM_PROMPT + platform_note
```

#### Tool Availability Matrix

| Tool | Linux | macOS | Windows | Fallback Behavior |
|------|-------|-------|---------|-------------------|
| `calculator` | ✓ | ✓ | ✓ | Always available |
| `http_request` | ✓ | ✓ | ✓ | Always available |
| `file_read` | ✓ | ✓ | ✓ | Always available |
| `file_write` | ✓ | ✓ | ✓ | Always available |
| `editor` | ✓ | ✓ | ✓ | Always available |
| `python_repl` | ✓ | ✓ | ✗ | Code examples instead of execution |
| `shell` | ✓ | ✓ | ✗ | Command examples instead of execution |

#### Platform Detection Output

**Linux/macOS:**
```
Detected Linux platform - full tool set available
Platform: Linux (Linux-5.15.0-generic-x86_64-with-glibc2.35)
Available tools:
    ✓ calculator
    ✓ http_request
    ✓ file_read
    ✓ file_write
    ✓ editor
    ✓ python_repl
    ✓ shell
```

**Windows:**
```
Detected Windows platform - using limited tool set (python_repl and shell not available)
Platform: Windows (Windows-11-10.0.26100-SP0)
Note: Some tools are not available on Windows: python_repl, shell
Computer Science Assistant will provide code examples with explanations instead of execution.
Available tools:
    ✓ calculator
    ✓ http_request
    ✓ file_read
    ✓ file_write
    ✓ editor
    ✗ python_repl
    ✗ shell
```

#### Benefits of This Approach

1. **Automatic Detection**: No manual platform configuration needed
2. **Graceful Degradation**: Agents adapt behavior based on available tools
3. **Consistent Interface**: Same code works across all platforms
4. **Clear Feedback**: Users understand platform limitations
5. **Future-Proof**: Easy to add new tools or platforms
6. **Reusable**: Can be used across multiple workshop steps (CLI, Streamlit, etc.)

#### Usage in Multi-Agent Systems

**Step 1 (CLI):** Direct integration with `teachers_assistant.py`
**Step 2 (Streamlit):** Import `cross_platform_tools` in `app.py`
**Step 3 (Knowledge Base):** Enhanced agents maintain cross-platform compatibility
**Step 4 (Production):** Docker containers can use appropriate base images per platform

### Path Handling

**Linux/macOS:**
```python
import os
path = "workshop4/modules/module1"
full_path = os.path.join("workshop4", "modules", "module1")
```

**Windows (Git Bash Compatible):**
```python
import os
# Use forward slashes - Git Bash handles them correctly
path = "workshop4/modules/module1"
full_path = os.path.join("workshop4", "modules", "module1")  # Still use os.path.join
```

**Windows (Native):**
```python
import os
path = "workshop4\\modules\\module1"
full_path = os.path.join("workshop4", "modules", "module1")
```
