#!/bin/bash
#
# Install git hooks for claude-code-templates
#
# Usage: ./git-hooks/install.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Copy pre-commit hook (MANIFEST.json validation)
cp "$SCRIPT_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"
echo "  Installed: pre-commit (validates MANIFEST.json)"

# Copy post-commit hook
cp "$SCRIPT_DIR/post-commit" "$HOOKS_DIR/post-commit"
chmod +x "$HOOKS_DIR/post-commit"
echo "  Installed: post-commit (auto-updates CHANGELOG.md)"

# Copy pre-push hook (documentation validation)
cp "$SCRIPT_DIR/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"
echo "  Installed: pre-push (validates documentation alignment)"

echo "Done."
echo ""
echo "Hooks installed:"
echo "  - pre-commit: MANIFEST.json validation on each commit"
echo "  - post-commit: CHANGELOG.md auto-update"
echo "  - pre-push: Documentation alignment validation before push"
