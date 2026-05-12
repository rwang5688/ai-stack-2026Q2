"""
Cross-platform tool imports for Strands Agents.

This module handles platform-specific tool imports to ensure compatibility
across Windows, Linux, and macOS systems. It provides math tools for the
Math Teaching Agent and platform capability reporting for debugging.
"""

import platform
from typing import Any, List


# Always available tools (cross-platform)
CORE_TOOLS_AVAILABLE = False
calculator = None

try:
    from strands_tools import calculator as _calculator

    calculator = _calculator
    CORE_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: strands_tools not available: {e}")


def get_platform_info() -> dict:
    """Get detailed platform information."""
    return {
        "system": platform.system(),
        "platform": platform.platform(),
        "is_windows": platform.system().lower() == "windows",
        "is_linux": platform.system().lower() == "linux",
        "is_macos": platform.system().lower() == "darwin",
    }


def get_math_tools() -> List[Any]:
    """
    Get tools available for the Math Teaching Agent.

    Returns:
        List containing the calculator tool if available, empty list otherwise.
    """
    tools = []
    if CORE_TOOLS_AVAILABLE and calculator is not None:
        tools.append(calculator)
    return tools


def get_platform_capabilities() -> dict:
    """
    Get a summary of platform capabilities for debugging.

    Returns:
        Dictionary with platform info and tool availability.
    """
    platform_info = get_platform_info()

    return {
        "platform": platform_info,
        "core_tools_available": CORE_TOOLS_AVAILABLE,
        "available_tools": {
            "calculator": CORE_TOOLS_AVAILABLE and calculator is not None,
        },
    }
