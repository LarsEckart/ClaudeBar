# Claude Usage Monitor for Waybar

A Python tool using `uv` that scrapes Claude CLI usage data and outputs Waybar-compatible JSON.

## Project Structure

```
claude-usage/
├── pyproject.toml
├── src/
│   └── claude_usage/
│       ├── __init__.py
│       ├── cli.py          # Entry point
│       ├── probe.py        # PTY interaction → raw text
│       ├── parser.py       # Raw text → structured data
│       ├── formatters.py   # Structured data → output
│       └── models.py       # Data classes
└── README.md
```

## Implementation Steps

### Step 1: Project Setup
- [x] Initialize project with `uv init claude-usage`
- [x] Add dependencies: `pexpect`
- [x] Create project structure

### Step 2: Models
- [x] Define `UsageSnapshot` dataclass with fields:
  - `session_percent: int | None`
  - `weekly_percent: int | None`
  - `opus_percent: int | None`
  - `session_reset: str | None`
  - `weekly_reset: str | None`
  - `account_email: str | None`
  - `raw_text: str`

### Step 3: Probe (PTY Interaction)
- [x] Implement `fetch_usage_raw(timeout: int = 15) -> str`
- [x] Spawn `claude` via `pexpect`
- [x] Send `/usage` command
- [x] Capture output until idle/timeout
- [x] Send `/exit` to terminate cleanly
- [x] Handle edge cases:
  - [x] Claude not installed
  - [ ] Not logged in
  - [x] Folder trust prompts (auto-accept)
  - [x] Timeout

### Step 4: Parser
Port regex patterns from CodexBar's `ClaudeStatusProbe.swift`:
- [x] `strip_ansi(text: str) -> str`
- [x] `extract_percent(text: str, label: str) -> int | None`
- [x] `extract_reset(text: str, label: str) -> str | None`
- [x] `extract_email(text: str) -> str | None`
- [x] `parse_usage(raw_text: str) -> UsageSnapshot`

Key patterns:
```python
PERCENT_PATTERN = r'(\d{1,3})\s*%\s*(used|left)'
EMAIL_PATTERN = r'(?i)Account:\s+(\S+@\S+)'
RESET_PATTERN = r'Resets?\s*[:\s]*(.*?)(?:\n|$)'
```

### Step 5: Formatters
- [x] `format_waybar(snapshot: UsageSnapshot) -> dict`
  - Output: `{"text": "85%", "tooltip": "...", "percentage": 85, "class": "good"}`
- [x] `format_plain(snapshot: UsageSnapshot) -> str`
- [x] `format_json(snapshot: UsageSnapshot) -> dict` (full data)

CSS class thresholds:
- `good`: >50%
- `warning`: 20-50%
- `critical`: <20%

### Step 6: CLI Interface
- [x] Implemented with argparse
```
claude-usage [OPTIONS]

Options:
  --format      waybar|json|plain (default: waybar)
  --timeout     Seconds to wait for Claude CLI (default: 15)
  --dump-raw    Output raw CLI text (for debugging)
  --dump-parsed Output parsed data before formatting (for debugging)
```

### Step 7: Error Handling
- [x] Claude binary not found → helpful error message
- [ ] Not logged in → prompt to run `claude login`
- [x] Parse failure → return `{"text": "?", "class": "error"}`
- [x] Timeout → graceful degradation

### Step 8: Documentation
- [x] README with installation instructions
- [x] Waybar config example
- [x] CSS snippet for styling

## Waybar Integration

Config (`~/.config/waybar/config`):
```json
{
  "custom/claude": {
    "exec": "uvx claude-usage",
    "return-type": "json",
    "interval": 300
  }
}
```

CSS (`~/.config/waybar/style.css`):
```css
#custom-claude.critical { color: #f38ba8; }
#custom-claude.warning { color: #f9e2af; }
#custom-claude.good { color: #a6e3a1; }
```

## Testing Workflow

1. Implement probe → run it → show raw output ✅
2. Verify raw output looks correct ✅
3. Implement parser → show structured data ✅
4. Implement formatters → show Waybar JSON ✅
5. Manual test in Waybar → iterate if needed

## Debug Commands

```bash
# See raw CLI output
claude-usage --dump-raw

# See parsed data
claude-usage --dump-parsed

# Final waybar output
claude-usage
```
