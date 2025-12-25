# ClaudeBar

A Python tool that monitors your Claude Pro/Max subscription usage and displays it in Waybar.

Claude Pro and Max subscribers get usage limits that reset periodically (session limits reset every few hours, weekly limits reset weekly). This tool scrapes your current usage from [Claude Code](https://github.com/anthropics/claude-code) and displays it in Waybar so you always know how much capacity you have left.

This project is a port of [CodexBar](https://github.com/steipete/CodexBar) by [Peter Steinberger](https://github.com/steipete), adapted for Waybar. Thanks Peter for the original idea and implementation!

## Installation

```bash
# Using uvx (recommended for Waybar)
uvx claude-usage

# Or install globally
uv tool install claude-usage
```

## Usage

```bash
# Waybar JSON output (default)
claude-usage

# Human-readable output
claude-usage --format plain

# Full JSON data
claude-usage --format json

# Debug: show raw CLI output
claude-usage --dump-raw

# Debug: show parsed data
claude-usage --dump-parsed
```

## Waybar Integration

Add to your Waybar config (`~/.config/waybar/config`):

```json
{
  "custom/claude": {
    "exec": "uvx claude-usage",
    "return-type": "json",
    "interval": 300
  }
}
```

Add styling (`~/.config/waybar/style.css`):

```css
#custom-claude.critical { color: #f38ba8; }
#custom-claude.warning { color: #f9e2af; }
#custom-claude.good { color: #a6e3a1; }
#custom-claude.error { color: #f38ba8; }
#custom-claude.unknown { color: #6c7086; }
```

## Output Format

Waybar output includes:
- `text`: Usage percentage remaining (e.g., "85%")
- `tooltip`: Account tier, session and weekly usage with reset times
- `percentage`: Numeric percentage (0-100)
- `class`: CSS class ("good", "warning", "critical", "error", "unknown")

## Requirements

- Python 3.12+
- Claude Code installed and authenticated (`claude login`)
- A Claude Pro or Max subscription
