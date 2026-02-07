#!/usr/bin/env python3
"""
SessionStart hook: loads persistent memory into Claude's context.

Reads global (~/.claude/memory/) and project (.claude/memory/) files,
applies a ~2000 token budget with priority loading, and injects as
a systemMessage.

Gracefully handles missing directories (first run).
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging import get_logger, timed_hook
from utils.memory import DEFAULT_BUDGET, DEFAULT_GLOBAL_DIR, DEFAULT_PROJECT_DIR, load_memory_bundle

log = get_logger("memory-loader")


def main():
    """Load memory and inject into session context."""
    with timed_hook("memory-loader", decision="approve") as h:
        global_dir = DEFAULT_GLOBAL_DIR
        project_dir = DEFAULT_PROJECT_DIR

        # Check which directories exist
        has_global = global_dir.exists()
        has_project = project_dir.exists()

        h.set(has_global=has_global, has_project=has_project)

        if not has_global and not has_project:
            log.info("no_memory_dirs", message="No memory directories found, skipping")
            return 0

        bundle = load_memory_bundle(
            global_dir=global_dir,
            project_dir=project_dir,
            budget=DEFAULT_BUDGET,
        )

        if not bundle:
            log.info("empty_bundle", message="No memory files with content found")
            return 0

        h.set(bundle_tokens=len(bundle) // 4)

    result = {
        "decision": "approve",
        "systemMessage": bundle,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
