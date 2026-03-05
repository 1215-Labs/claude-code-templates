#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Memory search sidecar using SQLite FTS5.

Indexes all .md files from global (~/.claude/memory/) and project (.claude/memory/)
directories, then runs a ranked keyword search.

Based on OpenClaw Section 8.2 — Memory Search Sidecar.

Usage:
    uv run memory-search.py "query string"
    uv run memory-search.py --reindex          # force reindex without searching
"""

import sqlite3
import sys
from pathlib import Path

# Memory directories to index
MEMORY_DIRS = [
    ("global", Path.home() / ".claude" / "memory"),
    ("project", Path(".claude") / "memory"),
]

# DB lives alongside project memory (not tracked by git)
DB_PATH = Path(".claude") / "memory" / ".memory-search.db"

MAX_RESULTS = 8
SNIPPET_TOKENS = 64


def ensure_db(conn: sqlite3.Connection) -> None:
    """Create FTS5 table if it doesn't exist."""
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts "
        "USING fts5(tier, path, content, tokenize='porter unicode61')"
    )


def reindex(conn: sqlite3.Connection) -> int:
    """Re-index all markdown files. Returns count of files indexed."""
    conn.execute("DELETE FROM memory_fts")
    count = 0
    for tier, mem_dir in MEMORY_DIRS:
        if not mem_dir.exists():
            continue
        for md_file in mem_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not content.strip():
                continue
            rel_path = str(md_file)
            conn.execute(
                "INSERT INTO memory_fts(tier, path, content) VALUES (?, ?, ?)",
                (tier, rel_path, content),
            )
            count += 1
    conn.commit()
    return count


def search(conn: sqlite3.Connection, query: str) -> list[tuple[str, str, str]]:
    """Search indexed memory files. Returns list of (tier, path, snippet)."""
    # FTS5 query: wrap bare words in quotes for safety
    fts_query = query.strip()
    if not fts_query:
        return []

    try:
        results = conn.execute(
            "SELECT tier, path, snippet(memory_fts, 2, '>>> ', ' <<<', '...', ?) "
            "FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (SNIPPET_TOKENS, fts_query, MAX_RESULTS),
        ).fetchall()
    except sqlite3.OperationalError:
        # If query has special chars that break FTS5, try quoting it
        safe_query = '"' + fts_query.replace('"', '""') + '"'
        results = conn.execute(
            "SELECT tier, path, snippet(memory_fts, 2, '>>> ', ' <<<', '...', ?) "
            "FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (SNIPPET_TOKENS, safe_query, MAX_RESULTS),
        ).fetchall()

    return results


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print("Usage: memory-search.py <query>", file=sys.stderr)
        print("       memory-search.py --reindex", file=sys.stderr)
        return 1

    # Ensure DB directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    ensure_db(conn)

    if args[0] == "--reindex":
        count = reindex(conn)
        print(f"Indexed {count} files into {DB_PATH}")
        conn.close()
        return 0

    # Always reindex before search (memory dirs are small, sub-second)
    reindex(conn)

    query = " ".join(args)
    results = search(conn, query)
    conn.close()

    if not results:
        print(f"No results for: {query}")
        return 0

    for tier, path, snippet in results:
        print(f"### [{tier}] {path}")
        print(snippet)
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
