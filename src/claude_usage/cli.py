"""Command-line interface for claude-usage."""

import argparse
import json
import sys

from .probe import fetch_usage_raw
from .parser import parse_usage
from .formatters import format_waybar, format_plain, format_json
from .models import UsageSnapshot


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Monitor Claude CLI usage for Waybar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude-usage                    # Output Waybar JSON
  claude-usage --format plain     # Human-readable output
  claude-usage --dump-raw         # Debug: show raw CLI output
  claude-usage --dump-parsed      # Debug: show parsed data
        """,
    )
    parser.add_argument(
        "--format",
        choices=["waybar", "json", "plain"],
        default="waybar",
        help="Output format (default: waybar)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Seconds to wait for Claude CLI (default: 15)",
    )
    parser.add_argument(
        "--dump-raw",
        action="store_true",
        help="Output raw CLI text (for debugging)",
    )
    parser.add_argument(
        "--dump-parsed",
        action="store_true",
        help="Output parsed data before formatting (for debugging)",
    )
    
    args = parser.parse_args()
    
    try:
        # Fetch raw usage data
        raw_text = fetch_usage_raw(timeout=args.timeout)
        
        if args.dump_raw:
            print(raw_text)
            return 0
        
        # Parse the raw text
        snapshot = parse_usage(raw_text)
        
        if args.dump_parsed:
            print(json.dumps(format_json(snapshot), indent=2))
            return 0
        
        # Format output
        if args.format == "waybar":
            output = format_waybar(snapshot)
            print(json.dumps(output))
        elif args.format == "json":
            output = format_json(snapshot)
            print(json.dumps(output, indent=2))
        elif args.format == "plain":
            print(format_plain(snapshot))
        
        return 0
        
    except FileNotFoundError as e:
        # Claude not installed
        error_snapshot = UsageSnapshot(error=str(e))
        if args.format == "waybar":
            print(json.dumps(format_waybar(error_snapshot)))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1
        
    except RuntimeError as e:
        # Interaction failed
        error_snapshot = UsageSnapshot(error=str(e))
        if args.format == "waybar":
            print(json.dumps(format_waybar(error_snapshot)))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        # Unexpected error
        error_snapshot = UsageSnapshot(error=f"Unexpected error: {e}")
        if args.format == "waybar":
            print(json.dumps(format_waybar(error_snapshot)))
        else:
            print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
