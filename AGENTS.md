# ClaudeBar Development Guide

ClaudeBar monitors Claude CLI usage and displays it in Waybar.

## Project Structure

```
claudebar/
├── src/claude_usage/
│   ├── cli.py          # Command-line interface
│   ├── formatters.py   # Output formatting (waybar, json, plain)
│   ├── models.py       # Data models (UsageSnapshot)
│   ├── parser.py       # Parse Claude CLI output
│   └── probe.py        # Interact with Claude CLI via pexpect
├── pyproject.toml      # Project configuration
└── plan.md             # Original design plan
```

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Python package manager

## Development Setup

```bash
cd /home/lars/github/claudebar

# Create venv and install dependencies
uv sync

# Run during development (without installing)
uv run claude-usage
uv run claude-usage --format plain
uv run claude-usage --dump-raw      # Debug: show raw CLI output
uv run claude-usage --dump-parsed   # Debug: show parsed data
```

## Installing/Updating

The tool is installed globally via `uv tool`. After making changes:

```bash
uv tool install --force /home/lars/github/claudebar
```

This installs the `claude-usage` executable to `~/.local/bin/`.

Then restart Waybar to pick up changes:

```bash
killall waybar && waybar &
```

## Running Tests

```bash
uv run pytest
```

## How It Works

1. **probe.py**: Spawns `claude` CLI with pexpect, sends `/usage` command, captures output
2. **parser.py**: Strips ANSI codes, extracts percentages and reset times via regex
3. **formatters.py**: Formats data for Waybar JSON output (or plain text/JSON)
4. **cli.py**: Entry point, handles arguments and orchestrates the pipeline

## Waybar Integration

The module is configured in `~/.config/waybar/config`:

```json
"custom/claude": {
  "exec": "claude-usage",
  "return-type": "json",
  "interval": 300
}
```

Styling in `~/.config/waybar/style.css` uses classes: `good`, `warning`, `critical`, `error`.

## Output Format

Waybar JSON output:
```json
{
  "text": "53%",
  "tooltip": "Weekly: 94% (resets Jan 1)\nSession: 53% (resets 4pm)",
  "percentage": 53,
  "class": "warning"
}
```

- **text**: Session usage remaining (primary display)
- **tooltip**: Both weekly and session with reset times
- **class**: `good` (>50%), `warning` (20-50%), `critical` (<20%)
