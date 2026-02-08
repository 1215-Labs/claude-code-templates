#!/usr/bin/env python3
"""
SessionStart hook: injects skill-router enforcement and repo-specific priorities.

Reads the skill-router SKILL.md and per-repo skill-priorities.md,
combines them into a systemMessage wrapped in <SKILL_ROUTER_ACTIVE> tags.

Graceful fallback when no skill-priorities.md exists.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging import get_logger, timed_hook

log = get_logger("skill-router-loader")

# Default fallback when no repo-specific priorities exist
FALLBACK_PRIORITIES = """# Skill Priorities (Default)

## Always (invoke proactively every session)
- `/catchup` - Resume session with briefing (run first thing)

## Available (use when relevant)
- `/quick-prime` - Fast project context
- `/all_skills` - Discover available skills

## Repo Context
- No repo-specific priorities configured. Run `/repo-equip` to generate them.
"""


def find_skill_router_md():
    """Find the skill-router SKILL.md, checking multiple locations."""
    candidates = []

    # 1. Relative to this hook file (same repo)
    hook_dir = Path(__file__).parent
    candidates.append(hook_dir.parent / "skills" / "skill-router" / "SKILL.md")

    # 2. CLAUDE_PLUGIN_ROOT if set
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        candidates.append(Path(plugin_root) / "skills" / "skill-router" / "SKILL.md")

    # 3. Global install location
    candidates.append(Path.home() / ".claude" / "skills" / "skill-router" / "SKILL.md")

    for path in candidates:
        if path.exists():
            return path

    return None


def find_skill_priorities():
    """Find repo-specific skill-priorities.md in the current working directory."""
    return Path.cwd() / ".claude" / "memory" / "skill-priorities.md"


def main():
    """Load skill-router enforcement and priorities, inject into session."""
    with timed_hook("skill-router-loader", decision="approve") as h:
        # Find and read the skill-router SKILL.md
        router_path = find_skill_router_md()
        if not router_path:
            log.warning("no_skill_router", message="skill-router SKILL.md not found, skipping")
            h.set(router_found=False)
            return 0

        router_content = router_path.read_text().strip()
        h.set(router_found=True, router_path=str(router_path))

        # Find and read repo-specific priorities
        priorities_path = find_skill_priorities()
        has_priorities = priorities_path.exists()
        h.set(has_priorities=has_priorities)

        if has_priorities:
            priorities_content = priorities_path.read_text().strip()
            h.set(priorities_tokens=len(priorities_content) // 4)
        else:
            priorities_content = FALLBACK_PRIORITIES.strip()
            log.info("using_fallback", message="No skill-priorities.md found, using defaults")

    # Build the combined injection
    combined = f"""<SKILL_ROUTER_ACTIVE>
{router_content}

---

{priorities_content}
</SKILL_ROUTER_ACTIVE>"""

    result = {
        "decision": "approve",
        "systemMessage": combined,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
