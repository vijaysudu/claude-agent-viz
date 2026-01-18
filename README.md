# Claude Agent Visualizer

A terminal UI for visualizing and interacting with Claude Code agent sessions.

## Features

- **Session Browser**: View all Claude sessions from `~/.claude/projects`
- **Tool Inspector**: See every tool use (Read, Write, Edit, Bash, etc.) with full input/output
- **Active Session Detection**: Highlights sessions with running Claude processes
- **Spawn New Sessions**: Start Claude in embedded terminal or external window
- **Resume Sessions**: Continue existing sessions with `claude --resume`
- **Kill Sessions**: Terminate running Claude processes

## Installation

```bash
# Install from source
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Run with real sessions from ~/.claude/projects
claude-viz

# Run with demo data
claude-viz --demo

# Specify a custom sessions directory
claude-viz -d /path/to/sessions

# Show version
claude-viz --version
```

## Keybindings

| Key | Action |
|-----|--------|
| `n` | New session (uses current spawn mode) |
| `c` | Resume selected session in embedded terminal |
| `k` | Kill selected session |
| `t` | Toggle spawn mode (embedded/external) |
| `r` | Refresh sessions |
| `ESC` | Back to session view (from tool detail) |
| `q` | Quit |
| `?` | Show help |

## Spawn Modes

- **External** (default): Opens Claude in a new terminal window
- **Embedded**: Runs Claude inside the visualizer's TUI

Toggle between modes with `t`.

## Terminal Controls (Embedded Mode)

When running Claude in embedded mode:

| Key | Action |
|-----|--------|
| `ESC` | Graceful exit (sends `/exit` to Claude) |
| `Ctrl+C` x2 | Force kill session |
| `Ctrl+Q` | Immediate force quit |

## Layout

```
+------------------+----------------------------------------+
| Sessions         | Detail Panel                           |
|  > session-1     |  (Session info or tool output)         |
|    session-2     |                                        |
|                  |                                        |
+------------------+                                        |
| Tools            |                                        |
|  > Read: file.py |                                        |
|    Edit: app.py  |                                        |
|    Bash: npm run |                                        |
+------------------+----------------------------------------+
| Status: External | Active Sessions: 2                     |
+------------------+----------------------------------------+
```

## Requirements

- Python 3.10+
- Textual >= 0.50.0
- Rich >= 13.0.0
- watchdog >= 4.0.0

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/

# Run type checking
mypy src/

# Run tests
pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.
