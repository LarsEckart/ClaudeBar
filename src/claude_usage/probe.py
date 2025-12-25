"""PTY interaction with Claude CLI to fetch usage data."""

import os
import shutil
import pexpect


def fetch_usage_raw(timeout: int = 15) -> str:
    """
    Spawn Claude CLI, send /usage command, and capture output.

    Args:
        timeout: Maximum seconds to wait for Claude CLI response

    Returns:
        Raw text output from the CLI

    Raises:
        FileNotFoundError: If claude binary is not found
        RuntimeError: If interaction fails
    """
    # Check if claude is installed
    claude_path = shutil.which("claude")
    if not claude_path:
        raise FileNotFoundError(
            "Claude CLI not found. Install it with: npm install -g @anthropic-ai/claude-code"
        )

    try:
        # Build environment - inherit current env but set TERM to reduce ANSI
        env = os.environ.copy()
        env["TERM"] = "dumb"

        # Spawn claude in a PTY using full path
        child = pexpect.spawn(
            claude_path,
            encoding="utf-8",
            timeout=timeout,
            env=env,
        )

        # Wait for Claude to be ready - look for the prompt character or help hint
        ready_patterns = [
            r"\? for shortcuts",  # Help hint at bottom of welcome screen
            r"[>›]",  # Prompt character
            r"trust this",  # Folder trust prompt
            r"Do you want",  # Various prompts
            pexpect.TIMEOUT,
            pexpect.EOF,
        ]

        index = child.expect(ready_patterns)

        if index == 2 or index == 3:
            # Handle trust prompt - send 'y' to accept
            child.sendline("y")
            child.expect(ready_patterns)
        elif index == 4:
            raise RuntimeError(
                f"Timeout waiting for Claude CLI to start (waited {timeout}s)"
            )
        elif index == 5:
            raise RuntimeError("Claude CLI exited unexpectedly")

        # Small delay to ensure prompt is fully rendered
        import time

        time.sleep(0.3)

        # Type /usage and press Enter twice
        # First Enter might just confirm autocomplete, second executes
        child.send("/usage\r")
        time.sleep(0.3)
        child.send("\r")  # Confirm the selection

        # Wait for usage output - look for percentage patterns
        usage_patterns = [
            r"\d+\s*%",  # Percentage in output
            r"remaining",  # "X% remaining"
            r"used",  # "X% used"
            r"\? for shortcuts",  # Back to prompt
            pexpect.TIMEOUT,
            pexpect.EOF,
        ]

        child.expect(usage_patterns, timeout=timeout)

        # Wait a bit more for full output
        time.sleep(1.0)

        # Read any remaining output
        try:
            child.expect(pexpect.TIMEOUT, timeout=0.5)
        except pexpect.ExceptionPexpect:
            pass

        # Capture Usage tab output
        usage_output = child.before or ""

        # Press Tab to switch to Status tab for account tier info
        child.send("\t")
        time.sleep(0.5)

        # Wait for Status tab content
        try:
            child.expect([r"Login method", r"Version", pexpect.TIMEOUT], timeout=3)
        except pexpect.ExceptionPexpect:
            pass

        # Read Status tab output
        try:
            child.expect(pexpect.TIMEOUT, timeout=0.5)
        except pexpect.ExceptionPexpect:
            pass

        status_output = child.before or ""

        # Combine both outputs
        output = usage_output + "\n" + status_output

        # Clean exit - send Escape first to close any menu, then /exit
        child.send("\x1b")  # Escape
        time.sleep(0.1)
        child.send("/exit\r")
        time.sleep(0.1)
        child.send("\r")  # Confirm exit
        try:
            child.expect(pexpect.EOF, timeout=5)
        except pexpect.ExceptionPexpect:
            pass
        child.close()

        return output

    except pexpect.ExceptionPexpect as e:
        raise RuntimeError(f"Failed to interact with Claude CLI: {e}")
