"""
Persistent memory utilities for Claude Code sessions.

Zero dependencies - stdlib only for fast imports.

Two-tier memory:
    Global:  ~/.claude/memory/     (cross-project, follows user)
    Project: .claude/memory/       (per-repo, git-tracked)

Usage:
    from utils.memory import load_memory_bundle, append_memory, contains_secrets
    bundle = load_memory_bundle()
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# --- Constants ---

DEFAULT_GLOBAL_DIR = Path.home() / ".claude" / "memory"
DEFAULT_PROJECT_DIR = Path(".claude") / "memory"
DEFAULT_BUDGET = 2000  # tokens

# Priority tiers for memory loading
# P0: always loaded, P1: if budget remains, P2: fill remaining space
MEMORY_PRIORITIES = {
    # (directory_key, filename): (priority, max_tokens)
    ("project", "project-context.md"): (0, 600),
    ("global", "user-profile.md"): (0, 400),
    ("project", "tasks.md"): (0, 400),
    ("project", "decisions.md"): (1, 400),
    ("project_session", "latest"): (1, 300),
    ("global", "voice.md"): (2, 200),
    ("global", "tool-environment.md"): (2, 200),
}

# Secret patterns to detect before writing
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),            # OpenAI / Stripe secret keys
    re.compile(r"sk-ant-[a-zA-Z0-9-]{20,}"),        # Anthropic keys
    re.compile(r"ghp_[a-zA-Z0-9]{36,}"),             # GitHub PATs
    re.compile(r"gho_[a-zA-Z0-9]{36,}"),             # GitHub OAuth
    re.compile(r"github_pat_[a-zA-Z0-9_]{20,}"),     # GitHub fine-grained PATs
    re.compile(r"AKIA[0-9A-Z]{16}"),                  # AWS access key IDs
    re.compile(r"xoxb-[0-9a-zA-Z-]{20,}"),           # Slack bot tokens
    re.compile(r"xoxp-[0-9a-zA-Z-]{20,}"),           # Slack user tokens
    re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"),  # Private keys
    re.compile(r"password\s*[:=]\s*[\"'][^\"']{8,}[\"']", re.IGNORECASE),  # Passwords
    re.compile(r"(?:api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*[\"'][^\"']{8,}[\"']", re.IGNORECASE),
    re.compile(r"mongodb\+srv://[^\s]+"),             # MongoDB connection strings
    re.compile(r"postgres(?:ql)?://[^\s]+:[^\s]+@"),  # Postgres connection strings
]


def estimate_tokens(text: str) -> int:
    """Approximate token count. ~4 chars per token for English text."""
    return len(text) // 4


def contains_secrets(text: str) -> list[str]:
    """
    Scan text for common secret patterns.

    Returns list of matched pattern descriptions (empty if clean).
    """
    findings = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(pattern.pattern[:60])
    return findings


def ensure_memory_dirs(
    global_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
) -> tuple[Path, Path]:
    """Create memory directories if they don't exist. Returns (global_dir, project_dir)."""
    gd = global_dir or DEFAULT_GLOBAL_DIR
    pd = project_dir or DEFAULT_PROJECT_DIR

    gd.mkdir(parents=True, exist_ok=True)
    pd.mkdir(parents=True, exist_ok=True)
    (pd / "sessions").mkdir(exist_ok=True)

    return gd, pd


def read_memory_file(path: Path, max_tokens: int = 0) -> str:
    """
    Read a single memory file with optional token-based truncation.

    Args:
        path: File path to read
        max_tokens: Max tokens to return (0 = no limit)

    Returns:
        File contents, possibly truncated with "[...truncated]" marker
    """
    if not path.exists() or not path.is_file():
        return ""

    try:
        content = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return ""

    if not content:
        return ""

    if max_tokens > 0 and estimate_tokens(content) > max_tokens:
        # Truncate to approximate token limit (tokens * 4 chars)
        char_limit = max_tokens * 4
        content = content[:char_limit] + "\n[...truncated]"

    return content


def _get_latest_session(sessions_dir: Path) -> Optional[Path]:
    """Find the most recent session log file."""
    if not sessions_dir.exists():
        return None

    session_files = sorted(sessions_dir.glob("*.md"), reverse=True)
    for f in session_files:
        if f.name == ".gitkeep":
            continue
        if f.stat().st_size > 0:
            return f
    return None


def load_memory_bundle(
    global_dir: Optional[Path] = None,
    project_dir: Optional[Path] = None,
    budget: int = DEFAULT_BUDGET,
) -> str:
    """
    Load all memory files within a token budget, ordered by priority.

    Priority loading:
        P0 (always): user-profile, project-context, tasks
        P1 (if room): decisions, latest session
        P2 (if room): voice, tool-environment

    Args:
        global_dir: Global memory directory (default: ~/.claude/memory/)
        project_dir: Project memory directory (default: .claude/memory/)
        budget: Maximum tokens to load

    Returns:
        Combined markdown string ready for injection as systemMessage
    """
    gd = global_dir or DEFAULT_GLOBAL_DIR
    pd = project_dir or DEFAULT_PROJECT_DIR

    sections: list[str] = []
    tokens_used = 0

    # Build ordered list of (priority, max_tokens, path, label)
    load_order: list[tuple[int, int, Path, str]] = []

    for (dir_key, filename), (priority, max_tok) in MEMORY_PRIORITIES.items():
        if dir_key == "global":
            path = gd / filename
            label = f"Global: {filename}"
        elif dir_key == "project":
            path = pd / filename
            label = f"Project: {filename}"
        elif dir_key == "project_session" and filename == "latest":
            path = _get_latest_session(pd / "sessions")
            if path is None:
                continue
            label = f"Last Session: {path.name}"
        else:
            continue

        load_order.append((priority, max_tok, path, label))

    # Sort by priority (P0 first)
    load_order.sort(key=lambda x: x[0])

    for priority, max_tok, path, label in load_order:
        remaining = budget - tokens_used
        if remaining <= 50:
            break

        effective_max = min(max_tok, remaining)
        content = read_memory_file(path, max_tokens=effective_max)
        if not content:
            continue

        content_tokens = estimate_tokens(content)
        sections.append(f"### {label}\n{content}")
        tokens_used += content_tokens

    if not sections:
        return ""

    header = "=== PERSISTENT MEMORY ==="
    footer = f"=== END MEMORY ({tokens_used} tokens) ==="

    return f"{header}\n\n" + "\n\n".join(sections) + f"\n\n{footer}"


def append_memory(
    path: Path,
    section: str,
    content: str,
    check_secrets: bool = True,
) -> Optional[str]:
    """
    Append content to a specific markdown section in a memory file.

    If the section (## heading) exists, content is appended under it.
    If not, a new section is created at the end.

    Args:
        path: Memory file path
        section: Section heading (without ##)
        content: Content to append
        check_secrets: Whether to scan for secrets first

    Returns:
        None on success, error message string on failure
    """
    if check_secrets:
        findings = contains_secrets(content)
        if findings:
            return f"Secret detected - refusing to write. Patterns: {', '.join(findings)}"

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing content or start fresh
    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            existing = ""
    else:
        existing = f"# {path.stem.replace('-', ' ').title()}\n"

    section_header = f"## {section}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entry = f"- [{timestamp}] {content}"

    if section_header in existing:
        # Append under the existing section (before next ## or end of file)
        lines = existing.split("\n")
        insert_idx = None
        in_section = False

        for i, line in enumerate(lines):
            if line.strip() == section_header:
                in_section = True
                continue
            if in_section:
                # Find the end of this section (next heading or end)
                if line.startswith("## "):
                    insert_idx = i
                    break

        if insert_idx is None:
            # Section is at the end - just append
            if not existing.endswith("\n"):
                existing += "\n"
            existing += f"{entry}\n"
        else:
            lines.insert(insert_idx, entry)
            existing = "\n".join(lines)
    else:
        # Add new section at end
        if not existing.endswith("\n"):
            existing += "\n"
        existing += f"\n{section_header}\n\n{entry}\n"

    try:
        path.write_text(existing, encoding="utf-8")
    except OSError as e:
        return f"Failed to write: {e}"

    return None


def classify_memory(text: str) -> tuple[str, str, str]:
    """
    Auto-classify a memory entry.

    Returns:
        (tier, filename, section) where:
        - tier: "global" or "project"
        - filename: target filename
        - section: section heading to append under
    """
    lower = text.lower()

    # Decisions (ADR-style) - check early, before tool/pref keywords
    decision_keywords = [
        "decided", "decision", "chose", "chosen", "went with",
        "adr", "trade-off", "tradeoff", "because we",
    ]
    if any(kw in lower for kw in decision_keywords):
        return ("project", "decisions.md", "Decisions")

    # Tasks / TODOs
    task_keywords = [
        "todo", "to-do", "task", "next time", "remember to",
        "don't forget", "pending", "blocked on",
    ]
    if any(kw in lower for kw in task_keywords):
        return ("project", "tasks.md", "Active")

    # User preferences / identity
    # Use word-boundary-aware matching to avoid "uses" matching "i use"
    pref_patterns = [
        r"\bi prefer\b", r"\bi like\b", r"\bi always\b", r"\bi never\b",
        r"\bi want\b", r"\bi use\b", r"\bmy name\b", r"\bmy email\b",
        r"\bmy role\b", r"\bcall me\b", r"\bi am a\b",
        r"\bdon't call\b", r"\balways use\b", r"\bnever use\b",
    ]
    if any(re.search(p, lower) for p in pref_patterns):
        return ("global", "user-profile.md", "Preferences")

    # Voice / communication style
    voice_keywords = [
        "tone", "style", "verbose", "concise", "formal", "casual",
        "emoji", "no emoji", "brief", "detailed",
    ]
    if any(kw in lower for kw in voice_keywords):
        return ("global", "voice.md", "Style")

    # Tool / environment
    tool_keywords = [
        "tool", "editor", "ide", "terminal", "shell", "os ", "macos",
        "linux", "windows", "docker", "node version", "python version",
        "bun", "npm", "yarn", "pnpm",
    ]
    if any(kw in lower for kw in tool_keywords):
        return ("global", "tool-environment.md", "Tools")

    # Default: project context
    return ("project", "project-context.md", "Notes")
