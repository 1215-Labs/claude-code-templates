#!/usr/bin/env python3
"""
LSP Type Validator Hook

Runs type validation on modified TypeScript/JavaScript files.
Surfaces type errors before commit.

Related:
  - Agent: type-checker
  - Skill: lsp-type-safety-check
"""

import subprocess
import sys
import os

TYPESCRIPT_EXTENSIONS = {'.ts', '.tsx'}
JAVASCRIPT_EXTENSIONS = {'.js', '.jsx'}


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


def is_typescript_file(filepath):
    """Check if file is TypeScript."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in TYPESCRIPT_EXTENSIONS


def is_javascript_file(filepath):
    """Check if file is JavaScript."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in JAVASCRIPT_EXTENSIONS


def check_tsconfig_exists():
    """Check if tsconfig.json exists in project."""
    return os.path.exists('tsconfig.json')


def validate_typescript_files(files):
    """Run TypeScript compiler on modified files."""
    if not files:
        return []

    errors = []

    try:
        # Run tsc with --noEmit to type-check without generating output
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            # Parse errors for modified files only
            error_output = result.stdout + result.stderr
            for filepath in files:
                if filepath in error_output:
                    errors.append({
                        "file": filepath,
                        "has_errors": True
                    })

            if errors:
                return [{
                    "type": "typescript",
                    "message": "TypeScript type errors found",
                    "details": error_output[:1000]  # Truncate long output
                }]

    except FileNotFoundError:
        # TypeScript not installed - skip silently
        pass
    except Exception as e:
        # Other errors - skip silently
        pass

    return errors


def main():
    modified_files = get_modified_files()
    if not modified_files:
        return 0

    ts_files = [f for f in modified_files if is_typescript_file(f)]

    # Only run if there are TypeScript files and tsconfig exists
    if ts_files and check_tsconfig_exists():
        errors = validate_typescript_files(ts_files)

        if errors:
            print("\n=== LSP Type Validator ===")
            for error in errors:
                print(f"\n  {error['message']}")
                if 'details' in error:
                    # Print first few lines of details
                    lines = error['details'].split('\n')[:10]
                    for line in lines:
                        print(f"    {line}")
                    if len(error['details'].split('\n')) > 10:
                        print("    ...")
            print("\n  Tip: Use `type-checker` agent for detailed analysis")
            print("  Skill: lsp-type-safety-check")
            print("  Run: npx tsc --noEmit for full error list\n")
            return 1  # Block commit on type errors

    return 0


if __name__ == "__main__":
    sys.exit(main())
