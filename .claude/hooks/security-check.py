#!/usr/bin/env python3
"""
Security pattern checker for Claude Code PreToolUse hooks.

Reads tool input from stdin JSON, checks for 9 security anti-patterns,
tracks shown warnings per session to avoid repetition, and exits with
code 2 (blocking) on first occurrence or 0 on repeat/no match.

Input: JSON on stdin with keys: session_id, tool_name, tool_input
Output: Warning message on stdout (if pattern detected)
Exit codes: 0 = allow, 2 = block (security issue found)
"""

import json
import os
import re
import sys

SECURITY_PATTERNS = [
    {
        "id": "eval",
        "pattern": re.compile(r'\beval\s*\('),
        "label": "eval() usage",
        "guidance": "eval() executes arbitrary code. Use JSON.parse() for data, or a safe expression parser.",
    },
    {
        "id": "new_function",
        "pattern": re.compile(r'\bnew\s+Function\s*\('),
        "label": "new Function() constructor",
        "guidance": "new Function() is equivalent to eval(). Use static functions or a safe template engine.",
    },
    {
        "id": "exec_child_process",
        "pattern": re.compile(r'\b(exec|execSync)\s*\('),
        "label": "exec()/execSync() — potential command injection",
        "guidance": "Use execFile()/execFileSync() with explicit argument arrays instead of shell strings.",
    },
    {
        "id": "os_system",
        "pattern": re.compile(r'\bos\.system\s*\('),
        "label": "os.system() — Python command injection",
        "guidance": "Use subprocess.run() with a list of arguments and shell=False.",
    },
    {
        "id": "dangerously_set_inner_html",
        "pattern": re.compile(r'dangerouslySetInnerHTML'),
        "label": "dangerouslySetInnerHTML — React XSS risk",
        "guidance": "Sanitize HTML with DOMPurify before rendering, or use safe markup components.",
    },
    {
        "id": "document_write",
        "pattern": re.compile(r'\bdocument\.write\s*\('),
        "label": "document.write() — XSS risk",
        "guidance": "Use DOM APIs (textContent, createElement) or a framework's safe rendering.",
    },
    {
        "id": "inner_html",
        "pattern": re.compile(r'\.innerHTML\s*='),
        "label": ".innerHTML assignment — XSS risk",
        "guidance": "Use .textContent for text, or sanitize with DOMPurify before assigning HTML.",
    },
    {
        "id": "pickle",
        "pattern": re.compile(r'\bpickle\.(load|loads)\s*\('),
        "label": "pickle deserialization — arbitrary code execution",
        "guidance": "Use json, msgpack, or protobuf for untrusted data. Only use pickle with trusted sources.",
    },
    {
        "id": "gha_injection",
        "pattern": re.compile(
            r'\$\{\{\s*github\.event\.(issue|pull_request|comment)\.'
        ),
        "label": "GitHub Actions workflow injection",
        "guidance": "Never interpolate user-controlled values in 'run:' blocks. Pass them as environment variables instead.",
    },
]


def get_state_path(session_id: str) -> str:
    return f"/tmp/claude-security-state-{session_id}.json"


def load_state(session_id: str) -> set:
    path = get_state_path(session_id)
    try:
        with open(path) as f:
            data = json.load(f)
            return set(data.get("warned", []))
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return set()


def save_state(session_id: str, warned: set) -> None:
    path = get_state_path(session_id)
    with open(path, "w") as f:
        json.dump({"warned": sorted(warned)}, f)


def extract_content(tool_name: str, tool_input: dict) -> str:
    """Extract the editable content from the tool input."""
    parts = []
    if tool_name == "Write":
        parts.append(tool_input.get("content", ""))
    elif tool_name == "Edit":
        parts.append(tool_input.get("new_string", ""))
    elif tool_name == "MultiEdit":
        for edit in tool_input.get("edits", []):
            parts.append(edit.get("new_string", ""))
    return "\n".join(parts)


def check_content(content: str) -> list:
    """Return list of matched pattern dicts."""
    if not content:
        return []
    matches = []
    for p in SECURITY_PATTERNS:
        if p["pattern"].search(content):
            matches.append(p)
    return matches


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    content = extract_content(tool_name, tool_input)
    matches = check_content(content)

    if not matches:
        sys.exit(0)

    warned = load_state(session_id)
    new_matches = [m for m in matches if m["id"] not in warned]

    if not new_matches:
        sys.exit(0)

    # Update state with newly warned patterns
    for m in new_matches:
        warned.add(m["id"])
    save_state(session_id, warned)

    # Build output message
    lines = ["SECURITY WARNING — potentially unsafe pattern(s) detected:\n"]
    for m in new_matches:
        lines.append(f"  * {m['label']}")
        lines.append(f"    -> {m['guidance']}\n")
    lines.append("Review and confirm this is intentional before proceeding.")
    print("\n".join(lines))
    sys.exit(2)


if __name__ == "__main__":
    main()
