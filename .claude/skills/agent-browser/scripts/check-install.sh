#!/bin/bash
# Check if agent-browser is installed and ready to use

set -e

echo "Checking agent-browser installation..."

# Check if agent-browser command exists
if ! command -v agent-browser &> /dev/null; then
    echo "❌ agent-browser is NOT installed"
    echo ""
    echo "To install:"
    echo "  npm install -g agent-browser"
    echo "  agent-browser install"
    echo ""
    echo "On Linux, also run:"
    echo "  agent-browser install --with-deps"
    exit 1
fi

# Get version
VERSION=$(agent-browser --version 2>/dev/null || echo "unknown")
echo "✓ agent-browser is installed (version: $VERSION)"

# Check if Chromium is installed by attempting to verify
# Note: There's no direct command to check this, so we just note it
echo ""
echo "If browser commands fail, run:"
echo "  agent-browser install"
echo ""
echo "Ready to use agent-browser!"
