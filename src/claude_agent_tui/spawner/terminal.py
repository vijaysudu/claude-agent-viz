"""Terminal spawner for Claude sessions."""

from __future__ import annotations

import os
import pty
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable


@dataclass
class SpawnResult:
    """Result of spawning a Claude session."""

    success: bool
    pid: int | None = None
    error: str | None = None
    master_fd: int | None = None
    slave_fd: int | None = None


# Type alias for terminal spawn functions
TerminalSpawnFunc = Callable[[str, str], None]


def _spawn_warp(cwd: str, command: str) -> None:
    """Spawn in Warp terminal using AppleScript."""
    script = f'''
    tell application "Warp"
        activate
        tell application "System Events" to tell process "Warp"
            keystroke "t" using command down
            delay 0.3
            keystroke "cd {cwd} && {command}"
            keystroke return
        end tell
    end tell
    '''
    subprocess.Popen(["osascript", "-e", script])


def _spawn_terminal_app(cwd: str, command: str) -> None:
    """Spawn in macOS Terminal.app using AppleScript."""
    script = f'tell application "Terminal" to do script "cd {cwd} && {command}"'
    subprocess.Popen(["osascript", "-e", script])


def _spawn_iterm2(cwd: str, command: str) -> None:
    """Spawn in iTerm2 using AppleScript."""
    script = f'''
    tell application "iTerm"
        create window with default profile
        tell current session of current window
            write text "cd {cwd} && {command}"
        end tell
    end tell
    '''
    subprocess.Popen(["osascript", "-e", script])


def _spawn_wezterm(cwd: str, command: str) -> None:
    """Spawn in WezTerm terminal."""
    if command == "claude":
        subprocess.Popen(["wezterm", "start", "--cwd", cwd, "--", "claude"])
    else:
        subprocess.Popen(["wezterm", "start", "--cwd", cwd, "--", "sh", "-c", command])


def _spawn_kitty(cwd: str, command: str) -> None:
    """Spawn in Kitty terminal."""
    if command == "claude":
        subprocess.Popen(["kitty", "--directory", cwd, "claude"])
    else:
        subprocess.Popen(["kitty", "--directory", cwd, "sh", "-c", command])


def _spawn_alacritty(cwd: str, command: str) -> None:
    """Spawn in Alacritty terminal."""
    if command == "claude":
        subprocess.Popen(["alacritty", "--working-directory", cwd, "-e", "claude"])
    else:
        subprocess.Popen(["alacritty", "--working-directory", cwd, "-e", "sh", "-c", command])


def _spawn_gnome_terminal(cwd: str, command: str) -> None:
    """Spawn in GNOME Terminal."""
    if command == "claude":
        subprocess.Popen(["gnome-terminal", f"--working-directory={cwd}", "--", "claude"])
    else:
        subprocess.Popen(["gnome-terminal", f"--working-directory={cwd}", "--", "sh", "-c", command])


def _spawn_konsole(cwd: str, command: str) -> None:
    """Spawn in KDE Konsole."""
    if command == "claude":
        subprocess.Popen(["konsole", "--workdir", cwd, "-e", "claude"])
    else:
        subprocess.Popen(["konsole", "--workdir", cwd, "-e", "sh", "-c", command])


def _spawn_xterm(cwd: str, command: str) -> None:
    """Spawn in xterm."""
    subprocess.Popen(["xterm", "-e", f"cd {cwd} && {command}"])


# Terminal spawner registry
TERMINAL_SPAWNERS: dict[str, TerminalSpawnFunc] = {
    "Warp.app": _spawn_warp,
    "Terminal.app": _spawn_terminal_app,
    "iterm2": _spawn_iterm2,
    "wezterm": _spawn_wezterm,
    "kitty": _spawn_kitty,
    "alacritty": _spawn_alacritty,
    "gnome-terminal": _spawn_gnome_terminal,
    "konsole": _spawn_konsole,
    "xterm": _spawn_xterm,
}


def get_available_terminals() -> list[str]:
    """Get list of available terminal emulators.

    Returns:
        List of available terminal command names, ordered by preference.
    """
    # Check for Warp first (preferred on macOS)
    available = []
    if sys.platform == "darwin" and os.path.exists("/Applications/Warp.app"):
        available.append("Warp.app")

    # Other terminals in preference order
    terminals = [
        "wezterm",
        "kitty",
        "alacritty",
        "iterm2",
        "gnome-terminal",
        "konsole",
        "xterm",
    ]

    for term in terminals:
        if shutil.which(term):
            available.append(term)

    # Check for macOS Terminal.app as fallback
    if sys.platform == "darwin" and os.path.exists("/System/Applications/Utilities/Terminal.app"):
        available.append("Terminal.app")

    return available


def _spawn_in_terminal(cwd: str, command: str, terminal: str | None = None) -> SpawnResult:
    """Spawn a command in an external terminal.

    Args:
        cwd: Working directory for the session.
        command: Command to execute (e.g., "claude" or "claude --resume <id>").
        terminal: Terminal emulator to use (auto-detect if None).

    Returns:
        SpawnResult indicating success or failure.
    """
    # Find claude executable
    claude_path = shutil.which("claude")
    if not claude_path:
        return SpawnResult(
            success=False,
            error="'claude' command not found in PATH",
        )

    # Auto-detect terminal if not specified
    if terminal is None:
        available = get_available_terminals()
        if not available:
            return SpawnResult(
                success=False,
                error="No supported terminal emulator found",
            )
        terminal = available[0]

    # Get the spawner function for this terminal
    spawner = TERMINAL_SPAWNERS.get(terminal)
    if spawner is None:
        return SpawnResult(
            success=False,
            error=f"Unsupported terminal: {terminal}",
        )

    try:
        spawner(cwd, command)
        return SpawnResult(success=True)
    except Exception as e:
        return SpawnResult(
            success=False,
            error=str(e),
        )


def spawn_session(cwd: str, terminal: str | None = None) -> SpawnResult:
    """Spawn a new Claude session in an external terminal.

    Args:
        cwd: Working directory for the session.
        terminal: Terminal emulator to use (auto-detect if None).

    Returns:
        SpawnResult indicating success or failure.
    """
    return _spawn_in_terminal(cwd, "claude", terminal)


def spawn_resume_session(
    cwd: str,
    session_id: str,
    terminal: str | None = None,
) -> SpawnResult:
    """Spawn a Claude resume session in an external terminal.

    Args:
        cwd: Working directory for the session.
        session_id: The session ID to resume.
        terminal: Terminal emulator to use (auto-detect if None).

    Returns:
        SpawnResult indicating success or failure.
    """
    return _spawn_in_terminal(cwd, f"claude --resume {session_id}", terminal)


def spawn_embedded(cwd: str) -> SpawnResult:
    """Spawn a Claude session for embedded terminal use.

    This creates a PTY pair that can be used for an embedded terminal.

    Args:
        cwd: Working directory for the session.

    Returns:
        SpawnResult with PTY file descriptors.
    """
    # Find claude executable
    claude_path = shutil.which("claude")
    if not claude_path:
        return SpawnResult(
            success=False,
            error="'claude' command not found in PATH",
        )

    try:
        # Create pseudo-terminal
        master_fd, slave_fd = pty.openpty()

        # Fork the process
        pid = os.fork()

        if pid == 0:
            # Child process
            os.close(master_fd)
            os.setsid()

            # Set up slave as controlling terminal
            os.dup2(slave_fd, 0)  # stdin
            os.dup2(slave_fd, 1)  # stdout
            os.dup2(slave_fd, 2)  # stderr

            if slave_fd > 2:
                os.close(slave_fd)

            # Change to working directory
            os.chdir(cwd)

            # Set environment
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"

            # Execute claude
            os.execvpe(claude_path, [claude_path], env)

        else:
            # Parent process
            os.close(slave_fd)

            return SpawnResult(
                success=True,
                pid=pid,
                master_fd=master_fd,
            )

    except Exception as e:
        return SpawnResult(
            success=False,
            error=str(e),
        )
