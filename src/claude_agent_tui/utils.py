"""Utility functions for Claude Agent TUI.

This module contains shared utility functions used across the application.
"""

from __future__ import annotations

from datetime import datetime


def format_relative_time(timestamp: str) -> str:
    """Format a timestamp as relative time.

    Args:
        timestamp: ISO format timestamp string.

    Returns:
        Relative time string like '2h ago', 'just now', '5d ago'.
        Returns empty string if parsing fails.
    """
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = now - dt

        seconds = delta.total_seconds()
        if seconds < 0:
            return "in the future"
        elif seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    except (ValueError, AttributeError, TypeError):
        return ""
