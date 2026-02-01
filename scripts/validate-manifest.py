#!/usr/bin/env python3
"""
Validate MANIFEST.json against actual filesystem contents.

Ensures no components exist on disk without being registered in the manifest.
This is the single source of truth enforcement.

Exit codes:
  0 - All components registered
  1 - Unregistered components found
  2 - Missing components (in manifest but not on disk)
  3 - Both unregistered and missing
"""

import json
import sys
from pathlib import Path

# Files/patterns to ignore
IGNORE_NAMES = {
    "README.md",
    "README",
    ".gitkeep",
}


def should_ignore(name: str) -> bool:
    """Check if a file/dir should be ignored."""
    if name.startswith("_"):
        return True
    if name.startswith("."):
        return True
    return name in IGNORE_NAMES


def find_skills_on_disk(repo_root: Path) -> set[str]:
    """Find all skill directories (contain SKILL.md)."""
    skills = set()

    # Global skills
    global_skills = repo_root / "global" / "skills"
    if global_skills.exists():
        for item in global_skills.iterdir():
            if item.is_dir() and not should_ignore(item.name):
                if (item / "SKILL.md").exists():
                    skills.add(str(item.relative_to(repo_root)))

    # Template skills
    templates = repo_root / "templates"
    if templates.exists():
        for template_dir in templates.iterdir():
            if template_dir.is_dir():
                template_skills = template_dir / "skills"
                if template_skills.exists():
                    for item in template_skills.iterdir():
                        if item.is_dir() and not should_ignore(item.name):
                            if (item / "SKILL.md").exists():
                                skills.add(str(item.relative_to(repo_root)))

    # Dev/staging skills
    staging_skills = repo_root / "dev" / "staging" / "skills"
    if staging_skills.exists():
        for item in staging_skills.iterdir():
            if item.is_dir() and not should_ignore(item.name):
                if (item / "SKILL.md").exists():
                    skills.add(str(item.relative_to(repo_root)))

    return skills


def find_agents_on_disk(repo_root: Path) -> set[str]:
    """Find all agent files/directories."""
    agents = set()

    # Global agents
    global_agents = repo_root / "global" / "agents"
    if global_agents.exists():
        for item in global_agents.iterdir():
            if should_ignore(item.name):
                continue
            if item.is_dir():
                # Directory-based agent (has AGENT.md or is a known agent dir)
                agents.add(str(item.relative_to(repo_root)))
            elif item.is_file() and item.suffix == ".md":
                agents.add(str(item.relative_to(repo_root)))

    # Dev/staging agents
    staging_agents = repo_root / "dev" / "staging" / "agents"
    if staging_agents.exists():
        for item in staging_agents.iterdir():
            if should_ignore(item.name):
                continue
            if item.is_dir() or (item.is_file() and item.suffix == ".md"):
                agents.add(str(item.relative_to(repo_root)))

    return agents


def find_commands_on_disk(repo_root: Path) -> set[str]:
    """Find all command .md files (recursively in command directories)."""
    commands = set()

    def scan_command_dir(cmd_dir: Path):
        if not cmd_dir.exists():
            return
        for item in cmd_dir.iterdir():
            if should_ignore(item.name):
                continue
            if item.is_dir():
                # Recurse into subdirectories (like workflow/, dev/, prp-claude-code/)
                scan_command_dir(item)
            elif item.is_file() and item.suffix == ".md":
                commands.add(str(item.relative_to(repo_root)))

    # Global commands
    scan_command_dir(repo_root / "global" / "commands")

    # Template commands
    templates = repo_root / "templates"
    if templates.exists():
        for template_dir in templates.iterdir():
            if template_dir.is_dir():
                scan_command_dir(template_dir / "commands")

    # Dev/staging commands
    scan_command_dir(repo_root / "dev" / "staging" / "commands")

    return commands


def find_workflows_on_disk(repo_root: Path) -> set[str]:
    """Find all workflow .md files."""
    workflows = set()

    # Global workflows
    global_workflows = repo_root / "global" / "workflows"
    if global_workflows.exists():
        for item in global_workflows.iterdir():
            if item.is_file() and item.suffix == ".md" and not should_ignore(item.name):
                workflows.add(str(item.relative_to(repo_root)))

    # Dev/staging workflows
    staging_workflows = repo_root / "dev" / "staging" / "workflows"
    if staging_workflows.exists():
        for item in staging_workflows.iterdir():
            if item.is_file() and item.suffix == ".md" and not should_ignore(item.name):
                workflows.add(str(item.relative_to(repo_root)))

    return workflows


def get_manifest_paths(manifest: dict) -> dict[str, set[str]]:
    """Extract all component paths from manifest."""
    paths = {
        "skills": set(),
        "agents": set(),
        "commands": set(),
        "workflows": set(),
    }

    for component_type in paths.keys():
        for component in manifest.get("components", {}).get(component_type, []):
            paths[component_type].add(component["path"])

    return paths


def main():
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / "MANIFEST.json"

    if not manifest_path.exists():
        print("ERROR: MANIFEST.json not found at repo root")
        sys.exit(1)

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Find components on disk
    disk_components = {
        "skills": find_skills_on_disk(repo_root),
        "agents": find_agents_on_disk(repo_root),
        "commands": find_commands_on_disk(repo_root),
        "workflows": find_workflows_on_disk(repo_root),
    }

    manifest_components = get_manifest_paths(manifest)

    unregistered = {}
    missing = {}

    for component_type in disk_components:
        on_disk = disk_components[component_type]
        in_manifest = manifest_components[component_type]

        unreg = on_disk - in_manifest
        miss = in_manifest - on_disk

        if unreg:
            unregistered[component_type] = unreg
        if miss:
            missing[component_type] = miss

    exit_code = 0

    if unregistered:
        print("=" * 60)
        print("UNREGISTERED COMPONENTS (exist on disk, missing from MANIFEST.json)")
        print("=" * 60)
        for component_type, paths in unregistered.items():
            print(f"\n{component_type.upper()}:")
            for path in sorted(paths):
                print(f"  - {path}")
        print("\nAdd these to MANIFEST.json before committing.")
        exit_code |= 1

    if missing:
        print("=" * 60)
        print("MISSING COMPONENTS (in MANIFEST.json, not on disk)")
        print("=" * 60)
        for component_type, paths in missing.items():
            print(f"\n{component_type.upper()}:")
            for path in sorted(paths):
                print(f"  - {path}")
        print("\nRemove these from MANIFEST.json or restore the files.")
        exit_code |= 2

    if exit_code == 0:
        print("✓ MANIFEST.json is in sync with filesystem")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
