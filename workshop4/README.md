# Workshop 4: AI Application Development on AWS

This workshop provides hands-on experience with AI Application Development on AWS, featuring Strands Agents SDK, Amazon Bedrock, and Amazon SageMaker AI.

## Quick Start

### Prerequisites

- **All Operating Systems**: Python 3.12 or higher
- **Linux**: Git (typically pre-installed)
- **Windows**: Git for Windows (includes Git Bash terminal)

### Environment Setup

See [Cross-Platform Develompent Guide](CROSS_PLATFORM.md) for detailed information about environment setup and runtime execution across different platforms.

#### Option 1: Automated Setup (Recommended)

```bash
# Make setup script executable (Linux/Git Bash)
chmod +x setup-environment.sh

# Run setup script
./setup-environment.sh
```

#### Option 2: Manual Setup

**With UV (Recommended):**
```bash
# Install UV (same command for all platforms via Git Bash/Terminal)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal

# Create virtual environment
uv venv

# Activate virtual environment (platform-specific)
# Linux/macOS:
source .venv/bin/activate
# Windows (Git Bash):
source .venv/Scripts/activate

# Install dependencies
uv pip install -r requirements.txt
```

**With Standard Python:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (platform-specific)
# Linux/macOS:
source venv/bin/activate
# Windows (Git Bash):
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import strands_agents; print('Strands Agents SDK installed successfully')"
```

## Workshop Structure

- **Bedrock Track**: Multi-agent examples using Amazon Bedrock models
- **SageMaker Track**: Equivalent functionality using SageMaker AI models

### Agentic AI with Strands (Agents) SDK and (Amazon Bedrock) AgentCore Workshop Modules

See [Agentic AI with Strands (Agents) SDK and (Amazon Bedrock) AgentCore Workshop Modules](MODULES.md) for detailed information, including sample code and queries, from the modules leading up to Module 7 in the [Agentic AI with Strands (Agents) SDK and (Amazon Bedrock AgentCore)](https://catalog.workshops.aws/strands/en-US) workshop.  These published workshop modules will teach you how to use Strands Agents SDK to build and deploy agentic AI systems.

## Development Workflow

1. **Always activate the virtual environment first:**
   ```bash
   # Linux/macOS:
   source .venv/bin/activate
   # Windows (Git Bash):
   source .venv/Scripts/activate
   ```

2. **All sample code in this directory shares the same virtual environment**

3. **Use Git Bash on Windows for consistent Linux-like commands**

## Troubleshooting

### Common Issues

- **Python not found**: Ensure Python 3.12+ is installed and in PATH
- **Git Bash issues**: Install Git for Windows with Git Bash option
- **Package conflicts**: Try creating a fresh virtual environment

### Getting Help

- Check the troubleshooting section in the workshop materials
- Verify all prerequisites are installed
- Ensure you're using Git Bash on Windows for consistent behavior

## Next Steps

Once your environment is set up, you can proceed with the workshop exercises. Each track (Bedrock and SageMaker) provides equivalent learning outcomes with different implementation approaches.

## Current Workshop Contents

### Environment Setup

- `requirements.txt` - OS-independent Python dependencies
- `setup-environment.sh` - Cross-platform environment setup script
- This README with setup and usage instructions

### Planned Additions

- Bedrock implementation examples
- SageMaker implementation examples
- Comparison materials and documentation
- Hands-on exercises and validation scripts
