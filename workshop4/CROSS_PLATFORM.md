# Cross-Platform Development Guide

This guide helps you work with Workshop 4 examples across different operating systems, with specific focus on Git Bash compatibility on Windows.

## Python Version Requirements

**Important**: This workshop requires Python 3.10.x, 3.11.x, or 3.12.x (recommended: 3.12.10)

## Python Version Requirements

**Recommended**: Python 3.12.x or 3.13.x for optimal experience

**Cross-Platform Consistency:**
- **Linux**: Python 3.12.x (stable, mature ecosystem)
- **Windows**: Python 3.12.x or 3.13.x (both work excellently with proper build tools)

**Why These Versions:**
- Pre-compiled wheels available for most packages (fast installation)
- Only specialized packages (like Bedrock AgentCore) require compilation
- Stable, well-tested ecosystem

**Installation Recommendations:**
- **Windows**: Download from python.org + Visual Studio Build Tools (see detailed steps below)
- **Linux**: Use your distribution's package manager (e.g., `apt install python3.12`)
- **macOS**: Use Homebrew (`brew install python@3.12`) or python.org installer

## Windows-Specific Setup Requirements

**CRITICAL for Windows Users**: Python packages that require compilation need Microsoft Visual C++ Build Tools.

### Optimal Windows Setup Process

#### Step 1: Install Python (Clean Installation)
1. Download Python 3.12.x or 3.13.x from [python.org](https://python.org)
2. **IMPORTANT**: During installation:
   - ✅ **DO**: Check "Add Python to PATH"
   - ❌ **DON'T**: Check Chocolatey checkbox (causes conflicts)
   - ❌ **DON'T**: Install VS Build Tools from Python installer (incomplete installation)
3. Use default installation settings

#### Step 2: Install Visual Studio Build Tools (Separately)
1. Download "Build Tools for Visual Studio 2022" from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the VS Build Tools installer
3. **CRITICAL**: Click **"Modify"** (not "Launch") to access workload selection
4. Under **Workloads**, check **"Desktop development with C++"**
   - This installs the complete C++ toolchain (~6GB)
   - Don't try to minimize components - full workload prevents issues
5. Click "Modify" to install
6. **Reboot your system** after installation

#### Step 3: Verify Build Tools Installation
Open a new terminal and run:
```cmd
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" && where cl
```
You should see the path to `cl.exe` (the C++ compiler).

#### Step 4: Run Workshop Setup
```bash
cd workshop4
./setup-environment.sh
```

### Why This Approach Works Best
- **Separate installations**: Avoids conflicts between Python installer and VS Build Tools
- **Complete toolchain**: Full "Desktop development with C++" workload includes everything needed
- **Fast package installation**: Pre-compiled wheels for common packages (NumPy, pandas, etc.)
- **Minimal compilation**: Only specialized packages (Bedrock AgentCore) need compilation
- **Cross-platform consistency**: Same Python versions work on Linux and Windows

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

### Virtual Environment Strategy

**Important**: All sample code in workshop4 shares the same virtual environment located at `workshop4/venv`. This approach ensures consistency and reduces setup complexity.

### UV Package Manager Setup

UV is a fast, cross-platform Python package manager that provides consistent behavior across platforms.

**Installation (same command for all platforms via Git Bash/Terminal):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

**Virtual Environment Setup with UV:**
```bash
# Navigate to workshop directory
cd workshop4

# Create virtual environment
uv venv

# Activate virtual environment (same command for all platforms)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

**Alternative: Standard Python (Fallback):**
```bash
# Navigate to workshop directory
cd workshop4

# Create virtual environment
python -m venv venv

# Activate virtual environment (same command for all platforms)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Requirements Management

- Use `requirements.txt` with OS-independent package specifications
- Avoid OS-specific packages in the main requirements file
- Document any OS-specific requirements separately

**Example Requirements Structure:**
```
workshop4/
├── requirements.txt          # Core dependencies (OS-independent)
├── requirements-linux.txt    # Linux-specific additions (if needed)
├── requirements-windows.txt  # Windows-specific additions (if needed)
├── venv/                    # Virtual environment (shared)
└── sample-code/             # All sample code using shared venv
```

### Development Workflow Best Practices

1. **Always activate the virtual environment first:**
   ```bash
   # From workshop4 directory (same command for all platforms)
   source .venv/bin/activate
   ```

2. **All sample code assumes the shared virtual environment is activated**

3. **Use relative imports and paths where possible**

4. **Use forward slashes in paths** (works in Git Bash and Linux)

5. **When adding new dependencies:**
   - Update `requirements.txt` with OS-independent packages
   - Test on both Windows (Git Bash) and Linux if possible
   - Document any OS-specific considerations

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

### Setup Troubleshooting

#### Git Bash Setup Issues
- Ensure Git for Windows is installed with Git Bash option
- Verify Python is accessible from Git Bash terminal
- Add Python to PATH if necessary

#### Environment Variables
- Document any required environment variables
- Use Linux-style syntax (works in Git Bash)

#### Package Conflicts
- If OS-specific packages are needed, use separate requirements files
- Document the installation order and any special considerations
- Try creating a fresh virtual environment if issues persist

## Runtime Execution

### Runtime Command Equivalents

| Task | Linux/macOS | Git Bash (Windows) | Windows CMD |
|------|-------------|-------------------|-------------|
| Check Python version | `python --version` | `python --version` | `python --version` |
| Environment variables | `export VAR=value` | `export VAR=value` | `set VAR=value` |
| Install with UV | `uv pip install package` | `uv pip install package` | `uv pip install package` |
| Run Python script | `uv run script.py` | `uv run script.py` | `uv run script.py` |

## Platform-Specific Coding Issues

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
