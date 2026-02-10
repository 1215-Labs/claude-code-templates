#!/usr/bin/env bash
set -euo pipefail

# Sandbox Isolation Test Orchestrator
# Creates an E2B sandbox, uploads test subjects + fixtures, runs tests, downloads results

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SBX_CLI="$REPO_ROOT/references/agent-sandbox-skill/.claude/skills/agent-sandboxes/sandbox_cli"
RESULTS_DIR="$SCRIPT_DIR/results"

# Ensure sbx CLI deps are installed
echo "=== Installing sbx CLI dependencies ==="
(cd "$SBX_CLI" && uv sync --quiet)

# Phase 1: Create sandbox
echo "=== Phase 1: Creating sandbox (1hr timeout) ==="
SBX_OUTPUT=$(cd "$SBX_CLI" && uv run sbx init --timeout 3600 2>&1)
echo "$SBX_OUTPUT"

# Extract sandbox ID (format varies — try common patterns)
SBX_ID=$(echo "$SBX_OUTPUT" | grep -oP 'sbx_[a-zA-Z0-9]+' | head -1)
if [ -z "$SBX_ID" ]; then
    # Fallback: look for any sandbox ID-like string
    SBX_ID=$(echo "$SBX_OUTPUT" | grep -oP '[a-z0-9]{20,}' | head -1)
fi

if [ -z "$SBX_ID" ]; then
    echo "ERROR: Could not extract sandbox ID from output"
    echo "Full output: $SBX_OUTPUT"
    exit 1
fi
echo "Sandbox ID: $SBX_ID"

# Helper function to run sbx commands
sbx() {
    (cd "$SBX_CLI" && uv run sbx "$@")
}

# Phase 2: Install dependencies in sandbox
echo "=== Phase 2: Installing sandbox dependencies ==="

# Ensure uvx is on PATH
sbx exec "$SBX_ID" "which uvx || (which uv && ln -sf \$(which uv | sed 's/uv$/uvx/') /usr/local/bin/uvx 2>/dev/null || true)" --timeout 30 || true

# Install pyyaml for frontmatter parsing
sbx exec "$SBX_ID" "pip install pyyaml 2>/dev/null || pip3 install pyyaml 2>/dev/null || uv pip install --system pyyaml 2>/dev/null || true" --timeout 60

# Warm ruff and ty caches (first run downloads them)
echo "Warming ruff cache..."
sbx exec "$SBX_ID" "uvx ruff --version" --timeout 120 || echo "WARNING: ruff not available"
echo "Warming ty cache..."
sbx exec "$SBX_ID" "uvx ty --version" --timeout 120 || echo "WARNING: ty not available"

# Phase 3: Create directories and upload files
echo "=== Phase 3: Uploading test files ==="
sbx exec "$SBX_ID" "mkdir -p /home/user/tests/fixtures /home/user/tests/hooks /home/user/tests/agents /home/user/tests/results" --timeout 10

# Upload hooks under test
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/hooks/ruff-validator.py" /home/user/tests/hooks/ruff-validator.py
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/hooks/ty-validator.py" /home/user/tests/hooks/ty-validator.py
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/hooks/hooks.json" /home/user/tests/hooks/hooks.json

# Upload agents under test
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/agents/meta-agent.md" /home/user/tests/agents/meta-agent.md
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/agents/team-builder.md" /home/user/tests/agents/team-builder.md
sbx files upload "$SBX_ID" "$REPO_ROOT/.claude/agents/team-validator.md" /home/user/tests/agents/team-validator.md

# Upload fixtures
for f in "$SCRIPT_DIR/fixtures/"*; do
    sbx files upload "$SBX_ID" "$f" "/home/user/tests/fixtures/$(basename "$f")"
done

# Upload test runner
sbx files upload "$SBX_ID" "$SCRIPT_DIR/test_runner.py" /home/user/tests/test_runner.py

# Phase 4: Run tests
echo "=== Phase 4: Running tests ==="
sbx exec "$SBX_ID" "cd /home/user/tests && python3 test_runner.py" --timeout 300 || true

# Phase 5: Download results
echo "=== Phase 5: Downloading results ==="
mkdir -p "$RESULTS_DIR"
sbx files download "$SBX_ID" /home/user/tests/results/report.json "$RESULTS_DIR/report.json" 2>/dev/null || echo "WARNING: Could not download report.json"
sbx files download "$SBX_ID" /home/user/tests/results/report.md "$RESULTS_DIR/report.md" 2>/dev/null || echo "WARNING: Could not download report.md"

# Also grab log files for debugging
sbx files read "$SBX_ID" /home/user/tests/hooks/ruff_validator.log 2>/dev/null || true
sbx files read "$SBX_ID" /home/user/tests/hooks/ty_validator.log 2>/dev/null || true

# Phase 6: Cleanup
echo "=== Phase 6: Killing sandbox ==="
sbx sandbox kill "$SBX_ID"

# Show results
echo ""
echo "=== DONE ==="
if [ -f "$RESULTS_DIR/report.md" ]; then
    cat "$RESULTS_DIR/report.md"
else
    echo "No report generated — check sandbox output above for errors"
fi
