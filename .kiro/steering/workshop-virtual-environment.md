# Workshop Virtual Environment Management

## Purpose
Establish consistent Python virtual environment setup across all workshop materials and sample code, supporting both Windows (via Git Bash) and Linux development environments.

## Rules

### Shared Virtual Environment Strategy
- All sample code under the same workshop directory MUST share the same virtual environment
- Virtual environment should be created at `workshop4/venv` (or similar workshop directory structure)
- This approach ensures consistency and reduces setup complexity for students

### Cross-Platform Python Environment Setup

#### Prerequisites
- **All Platforms**: Python 3.12 or higher
- **Linux**: Git is typically pre-installed
- **Windows**: Install Git for Windows (includes Git Bash terminal)

#### UV Package Manager (Recommended)
UV is a fast, cross-platform Python package manager. Using Git Bash on Windows provides consistent Linux-like commands across platforms.

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

#### Alternative: Standard Python (Fallback)
For environments where UV is not available:

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

#### OS-Independent Dependencies
- Use `requirements.txt` with OS-independent package specifications
- Avoid OS-specific packages in the main requirements file
- Document any OS-specific requirements separately

#### Example Requirements Structure
```
workshop4/
├── requirements.txt          # Core dependencies (OS-independent)
├── requirements-linux.txt    # Linux-specific additions (if needed)
├── requirements-windows.txt  # Windows-specific additions (if needed)
├── venv/                    # Virtual environment (shared)
└── sample-code/             # All sample code using shared venv
```

### Development Workflow

#### Environment Activation
Students should activate the virtual environment before working on any sample code:
```bash
# From workshop4 directory (same command for all platforms)
source .venv/bin/activate
```

#### Dependency Updates
When adding new dependencies:
1. Update `requirements.txt` with OS-independent packages
2. Test on both Windows (Git Bash) and Linux if possible
3. Document any OS-specific considerations

### Best Practices

#### Environment Consistency
- Use the same Python version across all platforms (recommend Python 3.12)
- Pin major versions in requirements.txt for stability
- Test sample code in fresh virtual environments periodically
- Use Git Bash on Windows for consistent Linux-like command experience

#### Documentation
- Include clear setup instructions assuming Git Bash on Windows
- Provide troubleshooting guidance for common environment issues
- Document any platform-specific behavior differences

#### Sample Code Organization
- All sample code should assume the shared virtual environment is activated
- Use relative imports and paths where possible
- Use forward slashes in paths (works in Git Bash and Linux)

### Troubleshooting Common Issues

#### Git Bash Setup
- Ensure Git for Windows is installed with Git Bash option
- Verify Python is accessible from Git Bash terminal
- Add Python to PATH if necessary

#### Path Separators
- Use forward slashes in paths (compatible with Git Bash and Linux)
- Use `os.path.join()` or `pathlib.Path` for programmatic path handling

#### Environment Variables
- Document any required environment variables
- Use Linux-style syntax (works in Git Bash)

#### Package Conflicts
- If OS-specific packages are needed, use separate requirements files
- Document the installation order and any special considerations