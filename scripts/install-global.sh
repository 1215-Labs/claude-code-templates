#!/bin/bash
# install-global.sh - Install universal Claude Code components system-wide
# Run this script to set up symlinks from ~/.claude/ to the templates repo
# Safe to re-run - removes existing symlinks before creating new ones

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES="$SCRIPT_DIR/.claude"
TARGET="$HOME/.claude"

echo "=== Claude Code Global Installation ==="
echo "Source: $TEMPLATES"
echo "Target: $TARGET"
echo ""

# Phase 1: Clean up broken symlinks
echo "Phase 1: Cleaning up broken symlinks..."
find "$TARGET/commands" -maxdepth 1 -type l -exec test ! -e {} \; -delete 2>/dev/null || true
find "$TARGET/agents" -maxdepth 1 -type l -exec test ! -e {} \; -delete 2>/dev/null || true
find "$TARGET/skills" -maxdepth 1 -type l -exec test ! -e {} \; -delete 2>/dev/null || true
find "$TARGET/workflows" -maxdepth 1 -type l -exec test ! -e {} \; -delete 2>/dev/null || true
echo "  Done."

# Phase 2: Create directory structure
echo "Phase 2: Creating directories..."
mkdir -p "$TARGET/commands"
mkdir -p "$TARGET/agents"
mkdir -p "$TARGET/skills"
mkdir -p "$TARGET/workflows"
echo "  Done."

# Helper function to create symlinks (removes existing first)
link() {
    local src="$1"
    local dest="$2"
    local name=$(basename "$src")

    # Remove existing symlink or file
    rm -f "$dest/$name" 2>/dev/null || true

    # Create new symlink
    ln -s "$src" "$dest/$name"
    echo "  $name"
}

# Phase 3: Symlink Commands
echo "Phase 3: Symlinking commands..."

# Workflow commands (individual files)
link "$TEMPLATES/commands/workflow/prime.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/quick-prime.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/deep-prime.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/onboarding.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/code-review.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/rca.md" "$TARGET/commands"
link "$TEMPLATES/commands/workflow/all_skills.md" "$TARGET/commands"

# PRP command directories (link entire directories)
rm -rf "$TARGET/commands/prp-claude-code" 2>/dev/null || true
rm -rf "$TARGET/commands/prp-any-agent" 2>/dev/null || true
ln -s "$TEMPLATES/commands/prp-claude-code" "$TARGET/commands/prp-claude-code"
echo "  prp-claude-code/"
ln -s "$TEMPLATES/commands/prp-any-agent" "$TARGET/commands/prp-any-agent"
echo "  prp-any-agent/"

# Phase 4: Symlink Agents
echo "Phase 4: Symlinking agents..."

# Standard agents (individual files)
link "$TEMPLATES/agents/codebase-analyst.md" "$TARGET/agents"
link "$TEMPLATES/agents/code-reviewer.md" "$TARGET/agents"
link "$TEMPLATES/agents/debugger.md" "$TARGET/agents"
link "$TEMPLATES/agents/test-automator.md" "$TARGET/agents"
link "$TEMPLATES/agents/context-manager.md" "$TARGET/agents"
link "$TEMPLATES/agents/technical-researcher.md" "$TARGET/agents"
link "$TEMPLATES/agents/library-researcher.md" "$TARGET/agents"
link "$TEMPLATES/agents/deployment-engineer.md" "$TARGET/agents"

# LSP agents (link entire directories)
rm -rf "$TARGET/agents/dependency-analyzer" 2>/dev/null || true
rm -rf "$TARGET/agents/lsp-navigator" 2>/dev/null || true
rm -rf "$TARGET/agents/type-checker" 2>/dev/null || true
ln -s "$TEMPLATES/agents/dependency-analyzer" "$TARGET/agents/dependency-analyzer"
echo "  dependency-analyzer/"
ln -s "$TEMPLATES/agents/lsp-navigator" "$TARGET/agents/lsp-navigator"
echo "  lsp-navigator/"
ln -s "$TEMPLATES/agents/type-checker" "$TARGET/agents/type-checker"
echo "  type-checker/"

# Phase 5: Symlink Skills
echo "Phase 5: Symlinking skills..."

# Universal skills (link directories)
rm -rf "$TARGET/skills/lsp-symbol-navigation" 2>/dev/null || true
rm -rf "$TARGET/skills/lsp-dependency-analysis" 2>/dev/null || true
rm -rf "$TARGET/skills/lsp-type-safety-check" 2>/dev/null || true
rm -rf "$TARGET/skills/fork-terminal" 2>/dev/null || true
rm -rf "$TARGET/skills/agent-browser" 2>/dev/null || true

ln -s "$TEMPLATES/skills/lsp-symbol-navigation" "$TARGET/skills/lsp-symbol-navigation"
echo "  lsp-symbol-navigation/"
ln -s "$TEMPLATES/skills/lsp-dependency-analysis" "$TARGET/skills/lsp-dependency-analysis"
echo "  lsp-dependency-analysis/"
ln -s "$TEMPLATES/skills/lsp-type-safety-check" "$TARGET/skills/lsp-type-safety-check"
echo "  lsp-type-safety-check/"
ln -s "$TEMPLATES/skills/fork-terminal" "$TARGET/skills/fork-terminal"
echo "  fork-terminal/"
ln -s "$TEMPLATES/skills/agent-browser" "$TARGET/skills/agent-browser"
echo "  agent-browser/"

# Phase 6: Symlink Workflows
echo "Phase 6: Symlinking workflows..."

link "$TEMPLATES/workflows/feature-development.md" "$TARGET/workflows"
link "$TEMPLATES/workflows/bug-investigation.md" "$TARGET/workflows"
link "$TEMPLATES/workflows/code-quality.md" "$TARGET/workflows"
link "$TEMPLATES/workflows/new-developer.md" "$TARGET/workflows"

# Phase 7: Verification
echo ""
echo "=== Verification ==="

# Check for broken symlinks
BROKEN=$(find "$TARGET" -maxdepth 2 -type l -exec test ! -e {} \; -print 2>/dev/null | wc -l)
if [ "$BROKEN" -eq 0 ]; then
    echo "✓ No broken symlinks found"
else
    echo "✗ Found $BROKEN broken symlinks:"
    find "$TARGET" -maxdepth 2 -type l -exec test ! -e {} \; -print
fi

# Count installed components
CMD_COUNT=$(find "$TARGET/commands" -maxdepth 1 \( -type l -o -type f \) -name "*.md" 2>/dev/null | wc -l)
CMD_DIR_COUNT=$(find "$TARGET/commands" -maxdepth 1 -type l -exec test -d {} \; -print 2>/dev/null | wc -l)
AGENT_COUNT=$(find "$TARGET/agents" -maxdepth 1 \( -type l -o -type f \) -name "*.md" 2>/dev/null | wc -l)
AGENT_DIR_COUNT=$(find "$TARGET/agents" -maxdepth 1 -type l -exec test -d {} \; -print 2>/dev/null | wc -l)
SKILL_COUNT=$(find "$TARGET/skills" -maxdepth 1 -type l -exec test -d {} \; -print 2>/dev/null | wc -l)
WORKFLOW_COUNT=$(find "$TARGET/workflows" -maxdepth 1 \( -type l -o -type f \) -name "*.md" 2>/dev/null | wc -l)

echo ""
echo "=== Installation Summary ==="
echo "Commands:  $CMD_COUNT files + $CMD_DIR_COUNT directories"
echo "Agents:    $AGENT_COUNT files + $AGENT_DIR_COUNT directories"
echo "Skills:    $SKILL_COUNT directories"
echo "Workflows: $WORKFLOW_COUNT files"
echo ""
echo "Installation complete! Run this script again after template updates."
