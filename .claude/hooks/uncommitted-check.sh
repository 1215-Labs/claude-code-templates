#!/bin/bash
# Stop hook: warn if there are uncommitted changes or unpushed commits

status=$(git status --porcelain 2>/dev/null)
unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null)

if [ -n "$status" ] || [ -n "$unpushed" ]; then
    echo "WARNING: You have unsynced work!"
    [ -n "$status" ] && echo "  Uncommitted changes: $(echo "$status" | wc -l | tr -d ' ') files"
    [ -n "$unpushed" ] && echo "  Unpushed commits: $(echo "$unpushed" | wc -l | tr -d ' ')"
    echo "  Remember to commit and push before switching machines."
    exit 0
fi
