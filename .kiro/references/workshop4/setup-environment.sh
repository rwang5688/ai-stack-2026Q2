#!/bin/bash

# Workshop 4 Environment Setup Script
# Cross-platform setup for Agentic AI with Strands Agents SDK
# Works on Linux and Windows (via Git Bash)

set -e  # Exit on any error

echo "🚀 Setting up Workshop 4 environment..."

# Check if Python 3.12+ is available
echo "📋 Checking Python version..."

# Try different Python command variations
PYTHON_CMD=""
for cmd in python python3; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python not found. Please install Python 3.12.x or 3.13.x."
    echo "   Tried: python, python3"
    echo "   Recommended: Python 3.12.x (stable) or 3.13.x (latest)"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
MAJOR_MINOR=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Check for supported Python versions (3.12 or above)
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info[:2] >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Python $PYTHON_VERSION found with '$PYTHON_CMD'."
    echo "   Supported versions: Python 3.12.x or 3.13.x"
    echo "   Recommended: Python 3.12.x (stable) or 3.13.x (latest)"
    echo "   Note: Ensure Visual Studio Build Tools are installed on Windows."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found using '$PYTHON_CMD'"

# Try to install UV if not available
if ! command -v uv &> /dev/null; then
    echo "📦 UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the shell configuration to make uv available
    if [ -f "$HOME/.bashrc" ]; then
        source "$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        source "$HOME/.bash_profile"
    fi
    
    # Check if uv is now available
    if ! command -v uv &> /dev/null; then
        echo "⚠️  UV installation completed but not immediately available."
        echo "   Please restart your terminal or run: source ~/.bashrc"
        echo "   Then run this script again."
        exit 1
    fi
fi

echo "✅ UV package manager available"

# Create virtual environment with UV
echo "🔧 Creating virtual environment..."
uv venv venv --python "$PYTHON_CMD" --allow-existing

# Determine the correct activation script path
if [ -f "venv/bin/activate" ]; then
    ACTIVATE_PATH="venv/bin/activate"
    PLATFORM="Linux/macOS"
elif [ -f "venv/Scripts/activate" ]; then
    ACTIVATE_PATH="venv/Scripts/activate"
    PLATFORM="Windows"
else
    echo "❌ Could not find virtual environment activation script"
    exit 1
fi

echo "✅ Virtual environment ready for $PLATFORM"

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source "$ACTIVATE_PATH"

# Try to install dependencies, with fallback for compilation issues
echo "🔧 Attempting to install all dependencies..."
if ! uv pip install -r requirements.txt; then
    echo "⚠️  Some packages failed to compile. Trying alternative approach..."
    echo "📦 Installing packages that don't require compilation first..."
    
    # Install packages that typically don't require compilation
    uv pip install boto3 litellm pandas streamlit tqdm retrying opensearch-py
    uv pip install strands-agents "strands-agents-tools[mem0_memory]"
    uv pip install aws-opentelemetry-distro
    uv pip install "mcp[cli]"
    uv pip install nova-act
    
    # Try bedrock packages with pre-compiled wheels
    echo "🔧 Attempting bedrock packages with pre-compiled wheels..."
    if ! uv pip install bedrock-agentcore bedrock-agentcore-starter-toolkit --only-binary=all; then
        echo "⚠️  Bedrock packages require compilation. Installing core bedrock-agentcore only..."
        uv pip install bedrock-agentcore --only-binary=all || echo "❌ bedrock-agentcore also failed"
    fi
fi

echo "🧪 Verifying installation..."
if $PYTHON_CMD -c "from strands import Agent; print('✅ Strands Agents SDK installed successfully')" 2>/dev/null; then
    echo "✅ Core dependencies installed successfully"
    
    # Check for optional bedrock components
    if $PYTHON_CMD -c "import bedrock_agentcore; print('✅ Bedrock AgentCore available')" 2>/dev/null; then
        echo "✅ Bedrock AgentCore toolkit available"
    else
        echo "⚠️  Bedrock AgentCore toolkit not available (compilation issues)"
        echo "   You can still use most workshop features without it"
    fi
else
    echo "❌ Core installation verification failed"
    exit 1
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment in future sessions:"
echo "  source $ACTIVATE_PATH"
echo ""
echo "Useful commands after activation:"
echo "  uv pip list                 # List all installed packages"
echo "  uv pip list | grep strands  # Show only strands packages"
echo "  uv pip show strands-agents  # Show details about strands-agents"
echo "  python -c \"from strands import Agent; print('Ready!')\"  # Test import"
echo ""
echo "You're ready to start the workshop exercises!"
