"""Centralized constants for Claude Agent TUI.

This module contains all shared constants including icons, status mappings,
magic numbers, and configuration values used across the application.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .store.models import ToolStatus


# =============================================================================
# Magic Numbers / Configuration Values
# =============================================================================

# Maximum number of history lines to read when finding active sessions
MAX_HISTORY_LINES = 100

# Maximum number of recent session files to check when matching processes
MAX_RECENT_SESSION_FILES = 10

# Threshold in seconds for considering a session as active based on file modification
ACTIVE_SESSION_THRESHOLD_SECONDS = 30

# Default subprocess timeout in seconds
DEFAULT_SUBPROCESS_TIMEOUT = 5


# =============================================================================
# Tool Icons
# =============================================================================

TOOL_ICONS: dict[str, str] = {
    "Read": "",
    "Edit": "",
    "Write": "",
    "Bash": "",
    "Grep": "",
    "Glob": "",
    "Task": "",
    "WebFetch": "",
    "AskUserQuestion": "",
}

# Default icon for unknown tools
DEFAULT_TOOL_ICON = ""


def get_tool_icon(tool_name: str) -> str:
    """Get the icon for a tool name.

    Args:
        tool_name: Name of the tool.

    Returns:
        Icon string for the tool.
    """
    return TOOL_ICONS.get(tool_name, DEFAULT_TOOL_ICON)


# =============================================================================
# Status Icons and Colors
# =============================================================================

# Status icons with their colors (icon, color) - used in tool_list.py
# Import ToolStatus at runtime to avoid circular imports
def get_status_icons() -> dict["ToolStatus", tuple[str, str]]:
    """Get status icons mapping.

    Returns lazily to avoid circular import with ToolStatus enum.
    """
    from .store.models import ToolStatus

    return {
        ToolStatus.PENDING: ("", "yellow"),
        ToolStatus.RUNNING: ("", "blue"),
        ToolStatus.COMPLETED: ("", "green"),
        ToolStatus.ERROR: ("", "red"),
    }


# Status display for detail panel (icon + text, color)
def get_status_display() -> dict["ToolStatus", tuple[str, str]]:
    """Get status display mapping for detail panel.

    Returns lazily to avoid circular import with ToolStatus enum.
    """
    from .store.models import ToolStatus

    return {
        ToolStatus.PENDING: (" Pending", "yellow"),
        ToolStatus.RUNNING: (" Running", "blue"),
        ToolStatus.COMPLETED: (" Completed", "green"),
        ToolStatus.ERROR: (" Error", "red"),
    }


# =============================================================================
# File Type to Language Mapping (for syntax highlighting)
# =============================================================================

FILE_EXTENSION_LANGUAGES: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
    ".sh": "bash",
    ".rs": "rust",
    ".go": "go",
}

DEFAULT_LANGUAGE = "text"


def get_language_from_path(file_path: str) -> str:
    """Determine the language/lexer from a file path.

    Args:
        file_path: Path to the file.

    Returns:
        Language identifier for syntax highlighting.
    """
    from pathlib import Path

    path = Path(file_path)
    return FILE_EXTENSION_LANGUAGES.get(path.suffix.lower(), DEFAULT_LANGUAGE)


# =============================================================================
# Tool Parameter Field Mappings
# =============================================================================

# Maps tool names to their file path parameter field
TOOL_FILE_PATH_PARAMS: dict[str, str] = {
    "Read": "file_path",
    "Edit": "file_path",
    "Write": "file_path",
    "Grep": "path",
    "Glob": "path",
}


def get_tool_file_path(tool_name: str, input_params: dict) -> str | None:
    """Get the file path from tool parameters.

    Args:
        tool_name: Name of the tool.
        input_params: Tool input parameters.

    Returns:
        File path if found, None otherwise.
    """
    param_name = TOOL_FILE_PATH_PARAMS.get(tool_name)
    if param_name:
        return input_params.get(param_name)
    return None


def generate_tool_preview(tool_name: str, input_params: dict, max_length: int = 80) -> str:
    """Generate a preview string for a tool invocation.

    Args:
        tool_name: Name of the tool.
        input_params: Tool input parameters.
        max_length: Maximum length of the preview (default 80).

    Returns:
        Preview string suitable for display.
    """
    def truncate(s: str, length: int = max_length) -> str:
        return s[:length - 3] + "..." if len(s) > length else s

    if tool_name == "Read":
        return truncate(input_params.get("file_path", ""))
    elif tool_name == "Edit":
        path = input_params.get("file_path", "")
        return truncate(f"{path} (edit)")
    elif tool_name == "Write":
        path = input_params.get("file_path", "")
        return truncate(f"{path} (write)")
    elif tool_name == "Bash":
        return truncate(input_params.get("command", ""))
    elif tool_name == "Grep":
        pattern = input_params.get("pattern", "")
        path = input_params.get("path", ".")
        return truncate(f"{pattern} in {path}")
    elif tool_name == "Glob":
        return truncate(input_params.get("pattern", ""))
    elif tool_name == "Task":
        return truncate(input_params.get("description", ""))
    else:
        # Generic preview - use first parameter value
        if input_params:
            first_val = str(list(input_params.values())[0])
            return truncate(first_val)
        return ""


def generate_tool_display_name(tool_name: str, input_params: dict, max_length: int = 30) -> str:
    """Generate a display-friendly name for a tool use.

    Args:
        tool_name: Name of the tool.
        input_params: Tool input parameters.
        max_length: Maximum length for parameter portion (default 30).

    Returns:
        Display name like "Read: file.py" or "Bash: pytest".
    """
    from pathlib import Path

    def truncate(s: str, length: int = max_length) -> str:
        return s[:length - 3] + "..." if len(s) > length else s

    if tool_name == "Read":
        path = input_params.get("file_path", "")
        name = Path(path).name if path else "file"
        return f"Read: {truncate(name)}"
    elif tool_name == "Edit":
        path = input_params.get("file_path", "")
        name = Path(path).name if path else "file"
        return f"Edit: {truncate(name)}"
    elif tool_name == "Write":
        path = input_params.get("file_path", "")
        name = Path(path).name if path else "file"
        return f"Write: {truncate(name)}"
    elif tool_name == "Bash":
        cmd = input_params.get("command", "")
        parts = cmd.split() if cmd else []
        short_cmd = parts[0] if parts else "command"
        return f"Bash: {truncate(short_cmd)}"
    elif tool_name == "Grep":
        pattern = input_params.get("pattern", "")
        return f"Grep: {truncate(pattern, 20)}"
    elif tool_name == "Glob":
        pattern = input_params.get("pattern", "")
        return f"Glob: {truncate(pattern, 20)}"
    elif tool_name == "Task":
        desc = input_params.get("description", "")
        return f"Task: {truncate(desc, 20)}"
    return tool_name


# =============================================================================
# Config Item Icons
# =============================================================================

CONFIG_ICONS: dict[str, str] = {
    "skill": "",
    "skill_plugin": "",
    "hook": "",
    "command": "",
    "agent": "",
    "agent_plugin": "",
    "mcp_server": "",
}


def get_config_icon(config_type: str, is_from_plugin: bool = False) -> str:
    """Get the icon for a config item type.

    Args:
        config_type: Type of config item (skill, hook, command, agent, mcp_server).
        is_from_plugin: Whether the item is from a plugin.

    Returns:
        Icon string for the config type.
    """
    if is_from_plugin and config_type in ("skill", "agent"):
        return CONFIG_ICONS.get(f"{config_type}_plugin", "")
    return CONFIG_ICONS.get(config_type, "")


# =============================================================================
# Agent Color Mapping
# =============================================================================

# Maps informal color names to valid Rich color names
AGENT_COLOR_MAP: dict[str, str] = {
    "orange": "bright_red",
    "purple": "magenta",
    "pink": "bright_magenta",
    "gray": "bright_black",
    "grey": "bright_black",
    "lime": "bright_green",
    "aqua": "bright_cyan",
    "navy": "blue",
    "maroon": "red",
    "olive": "yellow",
    "teal": "cyan",
    "silver": "white",
}

VALID_RICH_COLORS = {
    "red", "green", "blue", "cyan", "magenta", "yellow", "white", "black",
    "bright_red", "bright_green", "bright_blue", "bright_cyan",
    "bright_magenta", "bright_yellow", "bright_white", "bright_black",
}


def get_valid_color(color: str | None) -> str | None:
    """Convert a color name to a valid Rich color.

    Args:
        color: Color name to convert.

    Returns:
        Valid Rich color name or None.
    """
    if not color:
        return None

    color_lower = color.lower()

    # Check if already valid
    if color_lower in VALID_RICH_COLORS:
        return color_lower

    # Check mapping
    return AGENT_COLOR_MAP.get(color_lower)
