#!/usr/bin/env python3
"""
Validate documentation alignment across the repository.

Runs 4 checks:
  1. MANIFEST <-> Filesystem sync (critical)
  2. install-global.sh coverage (critical)
  3. Documentation counts & coverage (advisory)
  4. CHANGELOG freshness (advisory)

Exit codes:
  0 - All clear
  1 - Critical errors only
  2 - Advisory warnings only
  3 - Both critical and advisory
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def check_manifest_sync() -> list[str]:
    """Check 1: MANIFEST paths exist on disk and vice versa."""
    errors = []
    manifest_path = REPO_ROOT / "MANIFEST.json"

    if not manifest_path.exists():
        errors.append("MANIFEST.json not found")
        return errors

    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})

    # Check all MANIFEST paths exist on disk
    for comp_type in ["skills", "agents", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            path = REPO_ROOT / comp["path"]
            if not path.exists():
                errors.append(f"MANIFEST entry missing on disk: {comp['path']}")

    # Check all disk components have MANIFEST entries
    manifest_paths = set()
    for comp_type in ["skills", "agents", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            manifest_paths.add(comp["path"])

    # Skills on disk
    for skill_dir in _find_skill_dirs():
        rel = str(skill_dir.relative_to(REPO_ROOT))
        if rel not in manifest_paths:
            errors.append(f"Unregistered skill on disk: {rel}")

    # Agents on disk
    agents_dir = REPO_ROOT / ".claude" / "agents"
    if agents_dir.exists():
        for item in agents_dir.iterdir():
            if item.name.startswith("_") or item.name.startswith("."):
                continue
            if item.name in ("README.md",):
                continue
            rel = str(item.relative_to(REPO_ROOT))
            if rel not in manifest_paths:
                errors.append(f"Unregistered agent on disk: {rel}")

    # Commands on disk
    for cmd_file in _find_command_files():
        rel = str(cmd_file.relative_to(REPO_ROOT))
        if rel not in manifest_paths:
            errors.append(f"Unregistered command on disk: {rel}")

    # Workflows on disk
    workflows_dir = REPO_ROOT / ".claude" / "workflows"
    if workflows_dir.exists():
        for item in workflows_dir.iterdir():
            if item.is_file() and item.suffix == ".md" and not item.name.startswith("_"):
                rel = str(item.relative_to(REPO_ROOT))
                if rel not in manifest_paths:
                    errors.append(f"Unregistered workflow on disk: {rel}")

    return errors


def check_install_global_coverage() -> list[str]:
    """Check 2: Every global component has an install-global.sh entry."""
    errors = []
    manifest_path = REPO_ROOT / "MANIFEST.json"
    install_script = REPO_ROOT / "scripts" / "install-global.sh"

    if not manifest_path.exists() or not install_script.exists():
        errors.append("MANIFEST.json or install-global.sh not found")
        return errors

    with open(manifest_path) as f:
        manifest = json.load(f)

    script_content = install_script.read_text()

    components = manifest.get("components", {})

    for comp_type in ["skills", "agents", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            if comp.get("deployment") != "global":
                continue

            name = comp["name"]
            path = comp["path"]

            # Check if the component's filename or parent directory appears in install script
            # Commands in subdirectories (e.g., prp-claude-code/prp-claude-code-create.md)
            # are installed as directory symlinks, so check the parent dir name too
            p = Path(path)
            basename = p.name
            parent_name = p.parent.name if p.parent.name != "commands" else None

            found = basename in script_content
            if not found and parent_name:
                found = parent_name in script_content

            if not found:
                errors.append(
                    f"Global {comp_type[:-1]} '{name}' ({basename}) "
                    f"missing from install-global.sh"
                )

    return errors


def check_doc_counts() -> list[str]:
    """Check 3: Documentation counts match filesystem."""
    warnings = []
    manifest_path = REPO_ROOT / "MANIFEST.json"

    if not manifest_path.exists():
        return warnings

    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})
    actual_agents = len(components.get("agents", []))
    actual_commands = len(components.get("commands", []))
    actual_skills = len(components.get("skills", []))
    actual_workflows = len(components.get("workflows", []))

    # Check REGISTRY.md counts
    registry_path = REPO_ROOT / ".claude" / "REGISTRY.md"
    if registry_path.exists():
        registry_content = registry_path.read_text()

        # Look for "| Agents | N |" pattern
        agent_match = re.search(r"\| Agents \| (\d+)", registry_content)
        if agent_match:
            reg_agents = int(agent_match.group(1))
            if reg_agents != actual_agents:
                warnings.append(
                    f"REGISTRY.md agent count ({reg_agents}) != "
                    f"actual ({actual_agents})"
                )

    # Check USER_GUIDE.md has all agents listed
    user_guide = REPO_ROOT / ".claude" / "USER_GUIDE.md"
    if user_guide.exists():
        ug_content = user_guide.read_text()
        for comp in components.get("agents", []):
            agent_name = comp["name"]
            if agent_name not in ug_content:
                warnings.append(f"USER_GUIDE.md missing agent: {agent_name}")

        for comp in components.get("skills", []):
            skill_name = comp["name"]
            # n8n skills can be referenced as n8n-*
            if skill_name.startswith("n8n-") and "n8n-*" in ug_content:
                continue
            if skill_name not in ug_content:
                warnings.append(f"USER_GUIDE.md missing skill: {skill_name}")

    return warnings


def check_changelog_freshness() -> list[str]:
    """Check 4: HEAD commit has CHANGELOG entry."""
    warnings = []

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        if result.returncode != 0:
            return warnings

        head_hash = result.stdout.strip()
        changelog = REPO_ROOT / "CHANGELOG.md"

        if changelog.exists():
            content = changelog.read_text()
            if head_hash not in content:
                warnings.append(
                    f"CHANGELOG.md missing entry for HEAD commit ({head_hash})"
                )
    except Exception:
        pass

    return warnings


def _find_skill_dirs() -> list[Path]:
    """Find all skill directories with SKILL.md."""
    skills = []

    # Global skills
    claude_skills = REPO_ROOT / ".claude" / "skills"
    if claude_skills.exists():
        for item in claude_skills.iterdir():
            if item.is_dir() and not item.name.startswith(("_", ".")):
                if (item / "SKILL.md").exists():
                    skills.append(item)

    # Template skills
    templates = REPO_ROOT / "templates"
    if templates.exists():
        for tpl in templates.iterdir():
            if tpl.is_dir():
                tpl_skills = tpl / "skills"
                if tpl_skills.exists():
                    for item in tpl_skills.iterdir():
                        if item.is_dir() and not item.name.startswith(("_", ".")):
                            if (item / "SKILL.md").exists():
                                skills.append(item)

    return skills


def _find_command_files() -> list[Path]:
    """Find all command .md files recursively."""
    commands = []

    def scan(cmd_dir: Path):
        if not cmd_dir.exists():
            return
        for item in cmd_dir.iterdir():
            if item.name.startswith(("_", ".")) or item.name == "README.md":
                continue
            if item.is_dir():
                scan(item)
            elif item.is_file() and item.suffix == ".md":
                commands.append(item)

    scan(REPO_ROOT / ".claude" / "commands")
    return commands


def main():
    critical_errors = []
    advisory_warnings = []

    # Check 1: MANIFEST <-> Filesystem (critical)
    print("Check 1: MANIFEST <-> Filesystem sync...")
    errs = check_manifest_sync()
    if errs:
        critical_errors.extend(errs)
        for e in errs:
            print(f"  CRITICAL: {e}")
    else:
        print("  OK")

    # Check 2: install-global.sh coverage (critical)
    print("Check 2: install-global.sh coverage...")
    errs = check_install_global_coverage()
    if errs:
        critical_errors.extend(errs)
        for e in errs:
            print(f"  CRITICAL: {e}")
    else:
        print("  OK")

    # Check 3: Documentation counts (advisory)
    print("Check 3: Documentation counts & coverage...")
    warns = check_doc_counts()
    if warns:
        advisory_warnings.extend(warns)
        for w in warns:
            print(f"  WARNING: {w}")
    else:
        print("  OK")

    # Check 4: CHANGELOG freshness (advisory)
    print("Check 4: CHANGELOG freshness...")
    warns = check_changelog_freshness()
    if warns:
        advisory_warnings.extend(warns)
        for w in warns:
            print(f"  WARNING: {w}")
    else:
        print("  OK")

    # Summary
    print()
    if not critical_errors and not advisory_warnings:
        print("All checks passed.")
        return 0

    if critical_errors:
        print(f"{len(critical_errors)} critical error(s) found.")
    if advisory_warnings:
        print(f"{len(advisory_warnings)} advisory warning(s) found.")

    exit_code = 0
    if critical_errors:
        exit_code |= 1
    if advisory_warnings:
        exit_code |= 2
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
