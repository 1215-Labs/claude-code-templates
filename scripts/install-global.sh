#!/bin/bash
# install-global.sh - Thin wrapper around install-global.py
# Kept for backwards compatibility. All logic is in install-global.py.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "$SCRIPT_DIR/install-global.py" "$@"
