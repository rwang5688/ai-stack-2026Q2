"""
Cross-platform tool imports for Strands Agents.

This module handles platform-specific tool imports to ensure compatibility
across Windows, Linux, and macOS systems. It dynamically imports tools
based on the operating system and provides fallbacks for unsupported tools.
"""

import platform
import sys
from typing import List, Any

# Always available tools (cross-platform)
try:
    from strands_tools import calculator, http_request, file_read, file_write, editor
    CORE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core tools not available: {e}")
    CORE_TOOLS_AVAILABLE = False

# Platform-specific tools
PLATFORM_TOOLS_AVAILABLE = False
python_repl = None
shell = None

def get_platform_info():
    """Get detailed platform information."""
    return {
        'system': platform.system(),
        'platform': platform.platform(),
        'is_windows': platform.system().lower() == 'windows',
        'is_linux': platform.system().lower() == 'linux',
        'is_macos': platform.system().lower() == 'darwin'
    }

def import_platform_tools():
    """Import platform-specific tools with fallbacks."""
    global python_repl, shell, PLATFORM_TOOLS_AVAILABLE
    
    platform_info = get_platform_info()
    
    if platform_info['is_windows']:
        # Windows: Skip problematic tools that require Unix modules
        print("Detected Windows platform - using limited tool set (python_repl and shell not available)")
        python_repl = None
        shell = None
        PLATFORM_TOOLS_AVAILABLE = False
    else:
        # Linux/macOS: Try to import all tools
        try:
            from strands_tools import python_repl as _python_repl, shell as _shell
            python_repl = _python_repl
            shell = _shell
            PLATFORM_TOOLS_AVAILABLE = True
            print(f"Detected {platform_info['system']} platform - full tool set available")
        except ImportError as e:
            print(f"Warning: Platform-specific tools not available on {platform_info['system']}: {e}")
            python_repl = None
            shell = None
            PLATFORM_TOOLS_AVAILABLE = False

def get_math_tools() -> List[Any]:
    """Get tools available for Math Assistant."""
    tools = []
    if CORE_TOOLS_AVAILABLE:
        tools.append(calculator)
    return tools

def get_english_tools() -> List[Any]:
    """Get tools available for English Assistant."""
    tools = []
    if CORE_TOOLS_AVAILABLE:
        tools.extend([editor, file_read, file_write])
    return tools

def get_language_tools() -> List[Any]:
    """Get tools available for Language Assistant."""
    tools = []
    if CORE_TOOLS_AVAILABLE:
        tools.append(http_request)
    return tools

def get_computer_science_tools() -> List[Any]:
    """Get tools available for Computer Science Assistant."""
    tools = []
    if CORE_TOOLS_AVAILABLE:
        tools.extend([file_read, file_write, editor])
    
    # Add platform-specific tools if available
    if PLATFORM_TOOLS_AVAILABLE:
        if python_repl:
            tools.append(python_repl)
        if shell:
            tools.append(shell)
    
    return tools

def get_general_tools() -> List[Any]:
    """Get tools available for General Assistant (none by design)."""
    return []

def get_platform_capabilities() -> dict:
    """Get a summary of platform capabilities."""
    platform_info = get_platform_info()
    
    return {
        'platform': platform_info,
        'core_tools_available': CORE_TOOLS_AVAILABLE,
        'platform_tools_available': PLATFORM_TOOLS_AVAILABLE,
        'available_tools': {
            'calculator': CORE_TOOLS_AVAILABLE,
            'http_request': CORE_TOOLS_AVAILABLE,
            'file_read': CORE_TOOLS_AVAILABLE,
            'file_write': CORE_TOOLS_AVAILABLE,
            'editor': CORE_TOOLS_AVAILABLE,
            'python_repl': PLATFORM_TOOLS_AVAILABLE and python_repl is not None,
            'shell': PLATFORM_TOOLS_AVAILABLE and shell is not None,
        }
    }

# Initialize platform tools on import
import_platform_tools()

# Print platform info for debugging
if __name__ == "__main__":
    capabilities = get_platform_capabilities()
    print("Platform Capabilities:")
    print(f"  System: {capabilities['platform']['system']}")
    print(f"  Platform: {capabilities['platform']['platform']}")
    print(f"  Core tools available: {capabilities['core_tools_available']}")
    print(f"  Platform tools available: {capabilities['platform_tools_available']}")
    print("Available tools:")
    for tool, available in capabilities['available_tools'].items():
        status = "✓" if available else "✗"
        print(f"    {status} {tool}")