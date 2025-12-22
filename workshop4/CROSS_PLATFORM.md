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
