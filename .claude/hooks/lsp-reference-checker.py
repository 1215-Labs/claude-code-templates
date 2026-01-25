#!/usr/bin/env python3
"""
LSP Reference Checker Hook

Warns if a symbol being changed has many references.
Encourages running LSP-based impact analysis on heavily used symbols.

Related:
  - Agent: dependency-analyzer
  - Skill: lsp-dependency-analysis
"""

import subprocess
import sys
import os

REFERENCE_THRESHOLD = 10  # Warn if symbol has more than this many references
SUPPORTED_EXTENSIONS = {'.py', '.ts', '.js', '.tsx', '.jsx', '.go', '.rs'}


def get_modified_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f]
    except subprocess.CalledProcessError:
        return []


def is_supported_file(filepath):
    """Check if file type is supported for analysis."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in SUPPORTED_EXTENSIONS


def check_file_impact(filepath):
    """Check if modified file is heavily imported."""
    warnings = []

    # Get files that import this one
    try:
        # Use git grep to find imports (basic heuristic)
        filename = os.path.basename(filepath)
        name_without_ext = os.path.splitext(filename)[0]

        result = subprocess.run(
            ["git", "grep", "-l", f"from.*{name_without_ext}|import.*{name_without_ext}"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            importers = [f for f in result.stdout.strip().split('\n') if f and f != filepath]
            if len(importers) >= REFERENCE_THRESHOLD:
                warnings.append({
                    "file": filepath,
                    "references": len(importers),
                    "message": f"High-impact file: {len(importers)} files import this module"
                })
    except Exception:
        pass  # Fail silently - this is advisory

    return warnings


def main():
    modified_files = get_modified_files()
    if not modified_files:
        return 0

    all_warnings = []

    for filepath in modified_files:
        if is_supported_file(filepath):
            warnings = check_file_impact(filepath)
            all_warnings.extend(warnings)

    if all_warnings:
        print("\n=== LSP Reference Checker ===")
        for warning in all_warnings:
            print(f"\n  {warning['file']}")
            print(f"    {warning['message']}")
        print("\n  Tip: Use `dependency-analyzer` agent for detailed impact analysis")
        print("  Skill: lsp-dependency-analysis\n")

    return 0  # Non-blocking - advisory only


if __name__ == "__main__":
    sys.exit(main())
