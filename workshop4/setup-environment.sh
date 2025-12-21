#!/bin/bash

# Workshop 4 Environment Setup Script
# Cross-platform setup for Agentic AI with Strands Agents SDK
# Works on Linux and Windows (via Git Bash)

set -e  # Exit on any error

echo "🚀 Setting up Workshop 4 environment..."

# Check if Python 3.12+ is available
echo "📋 Checking Python version..."
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.12"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>/dev/null; then
    echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

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
uv venv

# Determine the correct activation script path
if [ -f ".venv/bin/activate" ]; then
    ACTIVATE_PATH=".venv/bin/activate"
    PLATFORM="Linux/macOS"
elif [ -f ".venv/Scripts/activate" ]; then
    ACTIVATE_PATH=".venv/Scripts/activate"
    PLATFORM="Windows"
else
    echo "❌ Could not find virtual environment activation script"
    exit 1
fi

echo "✅ Virtual environment created for $PLATFORM"

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source "$ACTIVATE_PATH"
uv pip install -r requirements.txt

echo "🧪 Verifying installation..."
if python -c "import strands_agents; print('✅ Strands Agents SDK installed successfully')" 2>/dev/null; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Installation verification failed"
    exit 1
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment in future sessions:"
echo "  source $ACTIVATE_PATH"
echo ""
echo "To verify the installation:"
echo "  python -c \"import strands_agents; print('Strands Agents SDK ready!')\""
echo ""
echo "You're ready to start the workshop exercises!"