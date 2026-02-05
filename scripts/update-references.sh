#!/bin/bash
# Update all reference submodules to their latest remote versions
# Usage: ./scripts/update-references.sh [--status-only]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REFERENCES_DIR="$REPO_ROOT/references"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

status_only=false
if [[ "$1" == "--status-only" ]]; then
    status_only=true
fi

echo -e "${BLUE}Reference Submodules${NC}"
echo "===================="
echo ""

# Initialize submodules if needed
if ! git -C "$REPO_ROOT" submodule status | grep -q "^[^-]"; then
    echo -e "${YELLOW}Initializing submodules...${NC}"
    git -C "$REPO_ROOT" submodule update --init --recursive
fi

# Get list of submodules in references/
submodules=$(git -C "$REPO_ROOT" config --file .gitmodules --get-regexp path | grep "references/" | awk '{print $2}')

for submodule in $submodules; do
    name=$(basename "$submodule")
    path="$REPO_ROOT/$submodule"

    if [[ ! -d "$path" ]]; then
        echo -e "${YELLOW}$name${NC}: Not initialized"
        continue
    fi

    # Get current and remote commits
    current=$(git -C "$path" rev-parse HEAD 2>/dev/null || echo "unknown")
    current_short="${current:0:7}"

    # Fetch remote
    git -C "$path" fetch origin --quiet 2>/dev/null || true

    # Get default branch
    default_branch=$(git -C "$path" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

    remote=$(git -C "$path" rev-parse "origin/$default_branch" 2>/dev/null || echo "unknown")
    remote_short="${remote:0:7}"

    # Count commits behind
    if [[ "$current" != "unknown" && "$remote" != "unknown" ]]; then
        behind=$(git -C "$path" rev-list HEAD..origin/$default_branch --count 2>/dev/null || echo "?")
    else
        behind="?"
    fi

    if [[ "$behind" == "0" ]]; then
        echo -e "${GREEN}$name${NC}: Up to date ($current_short)"
    else
        echo -e "${YELLOW}$name${NC}: $behind commits behind ($current_short → $remote_short)"

        if [[ "$status_only" == false ]]; then
            echo -e "  ${BLUE}Updating...${NC}"
            git -C "$REPO_ROOT" submodule update --remote "$submodule"
            echo -e "  ${GREEN}Updated${NC}"
        fi
    fi
done

echo ""

if [[ "$status_only" == true ]]; then
    echo -e "${BLUE}Run without --status-only to update all submodules${NC}"
else
    # Check if there are changes to commit
    if git -C "$REPO_ROOT" status --porcelain | grep -q "references/"; then
        echo -e "${YELLOW}Submodules updated. Run 'git add references/ && git commit' to save changes.${NC}"
    else
        echo -e "${GREEN}All references up to date.${NC}"
    fi
fi
