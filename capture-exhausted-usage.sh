#!/bin/bash
# Run this script when Claude usage is exhausted to capture the output format
# This will help update the parser to handle the "out of usage" state

OUTPUT_DIR="/home/lars/github/claudebar/exhausted-samples"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

echo "=== Capturing Claude usage output when exhausted ==="
echo "Timestamp: $(date)"
echo ""

# 1. Capture raw output using the tool's dump feature
echo ">>> Running: claude-usage --dump-raw"
claude-usage --dump-raw > "$OUTPUT_DIR/dump-raw_$TIMESTAMP.txt" 2>&1
echo "Saved to: $OUTPUT_DIR/dump-raw_$TIMESTAMP.txt"
echo ""

# 2. Capture parsed output
echo ">>> Running: claude-usage --dump-parsed"
claude-usage --dump-parsed > "$OUTPUT_DIR/dump-parsed_$TIMESTAMP.txt" 2>&1
echo "Saved to: $OUTPUT_DIR/dump-parsed_$TIMESTAMP.txt"
echo ""

# 3. Capture plain text output
echo ">>> Running: claude-usage --format plain"
claude-usage --format plain > "$OUTPUT_DIR/plain_$TIMESTAMP.txt" 2>&1
echo "Saved to: $OUTPUT_DIR/plain_$TIMESTAMP.txt"
echo ""

# 4. Capture JSON output
echo ">>> Running: claude-usage --format json"
claude-usage --format json > "$OUTPUT_DIR/json_$TIMESTAMP.txt" 2>&1
echo "Saved to: $OUTPUT_DIR/json_$TIMESTAMP.txt"
echo ""

# 5. Capture waybar output (default)
echo ">>> Running: claude-usage"
claude-usage > "$OUTPUT_DIR/waybar_$TIMESTAMP.txt" 2>&1
echo "Saved to: $OUTPUT_DIR/waybar_$TIMESTAMP.txt"
echo ""

echo "=== All captures complete ==="
echo "Files saved to: $OUTPUT_DIR/"
ls -la "$OUTPUT_DIR/"
echo ""
echo "Share the dump-raw_$TIMESTAMP.txt file - that has the actual CLI output I need to parse."
