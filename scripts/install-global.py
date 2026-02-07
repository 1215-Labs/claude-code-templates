#!/usr/bin/env python3
"""
MANIFEST-driven installer for global Claude Code components.

Reads MANIFEST.json, filters deployment:"global" components, and creates
symlinks from ~/.claude/ to the template repository. Safe to re-run.

Usage:
    python3 scripts/install-global.py            # Install
    python3 scripts/install-global.py --dry-run   # Preview only
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TEMPLATES = REPO_ROOT / ".claude"
TARGET = Path.home() / ".claude"

# Category -> target subdirectory
CATEGORY_DIR = {
    "commands": "commands",
    "agents": "agents",
    "skills": "skills",
    "workflows": "workflows",
}

# Directories to always create
INSTALL_DIRS = ["commands", "agents", "skills", "workflows", "hooks", "rules"]


def load_manifest() -> dict:
    manifest_path = REPO_ROOT / "MANIFEST.json"
    with open(manifest_path) as f:
        return json.load(f)


def get_global_components(manifest: dict) -> list[dict]:
    """Return all components with deployment: global, tagged with their type."""
    result = []
    for comp_type in ["commands", "agents", "skills", "workflows"]:
        for comp in manifest.get("components", {}).get(comp_type, []):
            if comp.get("deployment") == "global":
                result.append({**comp, "_type": comp_type})
    return result


def get_global_hooks(manifest: dict) -> list[dict]:
    """Return hooks that have a path field (command-type hooks with scripts)."""
    hooks = []
    for hook in manifest.get("components", {}).get("hooks", []):
        if hook.get("deployment") == "global" and hook.get("path"):
            hooks.append(hook)
    return hooks


def clean_broken_symlinks(dry_run: bool) -> int:
    """Phase 1: Remove broken symlinks under ~/.claude/."""
    count = 0
    for subdir in INSTALL_DIRS:
        target_dir = TARGET / subdir
        if not target_dir.exists():
            continue
        for item in target_dir.iterdir():
            if item.is_symlink() and not item.resolve().exists():
                count += 1
                if dry_run:
                    print(f"  Would remove broken symlink: {item.name}")
                else:
                    item.unlink()
                    print(f"  Removed broken symlink: {item.name}")
    return count


def create_directories(dry_run: bool):
    """Phase 2: Ensure target directories exist."""
    for subdir in INSTALL_DIRS:
        target_dir = TARGET / subdir
        if not target_dir.exists():
            if dry_run:
                print(f"  Would create: {target_dir}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"  Created: {target_dir}")
        else:
            print(f"  Exists: {target_dir}")


def _is_directory_command(comp: dict) -> str | None:
    """If a command should be installed as a directory symlink, return the dir name.

    Commands under 'workflow/' are individual files (symlinked separately).
    Commands under other subdirs (e.g., prp-claude-code/) are grouped directory installs.
    Returns None for individual file installs.
    """
    path_parts = Path(comp["path"]).parts
    # .claude / commands / subdir / file.md -> 4 parts means it's in a subdirectory
    if len(path_parts) > 3:
        parent_dir_name = path_parts[2]
        if parent_dir_name != "workflow":
            return parent_dir_name
    return None


def install_component(comp: dict, dry_run: bool) -> bool:
    """Symlink a single component. Returns True if installed."""
    comp_type = comp["_type"]
    src = REPO_ROOT / comp["path"]
    target_subdir = CATEGORY_DIR[comp_type]
    dest_dir = TARGET / target_subdir

    if not src.exists():
        print(f"  SKIP (missing): {comp['path']}")
        return False

    # For commands in grouped subdirectories (prp-claude-code/, prp-any-agent/),
    # install the entire directory as a symlink
    dir_name = _is_directory_command(comp) if comp_type == "commands" else None
    if dir_name:
        src = REPO_ROOT / ".claude" / "commands" / dir_name
        link_name = dir_name
        dest = dest_dir / link_name
    else:
        # Individual file or directory component
        link_name = src.name
        dest = dest_dir / link_name

    if dry_run:
        print(f"  Would link: {link_name} -> {src}")
        return True

    # Remove existing
    if dest.is_symlink() or dest.exists():
        if dest.is_dir() and not dest.is_symlink():
            import shutil
            shutil.rmtree(dest)
        else:
            dest.unlink()

    dest.symlink_to(src)
    print(f"  {link_name}")
    return True


def install_hooks(manifest: dict, dry_run: bool) -> int:
    """Install hooks.json and hook scripts."""
    count = 0

    # Install hooks.json
    hooks_json_src = TEMPLATES / "hooks" / "hooks.json"
    hooks_json_dest = TARGET / "hooks" / "hooks.json"
    if hooks_json_src.exists():
        if dry_run:
            print(f"  Would link: hooks.json -> {hooks_json_src}")
        else:
            if hooks_json_dest.is_symlink() or hooks_json_dest.exists():
                hooks_json_dest.unlink()
            hooks_json_dest.symlink_to(hooks_json_src)
            print(f"  hooks.json")
        count += 1

    # Install hook scripts referenced in MANIFEST
    for hook in get_global_hooks(manifest):
        src = REPO_ROOT / hook["path"]
        if not src.exists():
            print(f"  SKIP (missing): {hook['path']}")
            continue
        dest = TARGET / "hooks" / src.name
        if dry_run:
            print(f"  Would link: {src.name} -> {src}")
        else:
            if dest.is_symlink() or dest.exists():
                dest.unlink()
            dest.symlink_to(src)
            print(f"  {src.name}")
        count += 1

    return count


def install_rules(dry_run: bool) -> int:
    """Install rules directory contents."""
    count = 0
    rules_src = TEMPLATES / "rules"
    rules_dest = TARGET / "rules"

    if not rules_src.exists():
        return 0

    for item in rules_src.iterdir():
        if item.name.startswith(("_", ".")):
            continue
        dest = rules_dest / item.name
        if dry_run:
            print(f"  Would link: {item.name} -> {item}")
        else:
            if dest.is_symlink() or dest.exists():
                dest.unlink()
            dest.symlink_to(item)
            print(f"  {item.name}")
        count += 1

    return count


def verify_installation() -> tuple[dict, int]:
    """Count installed components and broken symlinks."""
    counts = {}
    for subdir in INSTALL_DIRS:
        target_dir = TARGET / subdir
        if not target_dir.exists():
            counts[subdir] = 0
            continue
        count = 0
        for item in target_dir.iterdir():
            if item.name.startswith(("_", ".")):
                continue
            count += 1
        counts[subdir] = count

    # Count broken symlinks
    broken = 0
    for subdir in INSTALL_DIRS:
        target_dir = TARGET / subdir
        if not target_dir.exists():
            continue
        for item in target_dir.iterdir():
            if item.is_symlink() and not item.resolve().exists():
                broken += 1

    return counts, broken


def main():
    dry_run = "--dry-run" in sys.argv

    manifest = load_manifest()
    components = get_global_components(manifest)

    mode = "DRY RUN" if dry_run else "Installing"
    print(f"=== Claude Code Global Installation ({mode}) ===")
    print(f"Source: {TEMPLATES}")
    print(f"Target: {TARGET}")
    print(f"Global components: {len(components)}")
    print()

    # Phase 1: Clean broken symlinks
    print("Phase 1: Cleaning broken symlinks...")
    cleaned = clean_broken_symlinks(dry_run)
    if cleaned == 0:
        print("  None found.")
    print()

    # Phase 2: Create directories
    print("Phase 2: Creating directories...")
    create_directories(dry_run)
    print()

    # Phase 3-6: Install by category
    installed = {}
    seen_dirs = set()  # Track command directories already installed

    for comp_type, label, phase in [
        ("commands", "Commands", 3),
        ("agents", "Agents", 4),
        ("skills", "Skills", 5),
        ("workflows", "Workflows", 6),
    ]:
        type_comps = [c for c in components if c["_type"] == comp_type]
        print(f"Phase {phase}: Symlinking {label.lower()}...")
        count = 0
        for comp in type_comps:
            # Deduplicate grouped command directories (prp-claude-code/, etc.)
            dir_name = _is_directory_command(comp) if comp_type == "commands" else None
            if dir_name:
                if dir_name in seen_dirs:
                    continue
                seen_dirs.add(dir_name)

            if install_component(comp, dry_run):
                count += 1
        installed[comp_type] = count
        print()

    # Phase 7: Hooks and rules
    print("Phase 7: Symlinking hooks and rules...")
    hook_count = install_hooks(manifest, dry_run)
    rule_count = install_rules(dry_run)
    print()

    # Phase 8: Verification
    if not dry_run:
        print("=== Verification ===")
        counts, broken = verify_installation()
        if broken == 0:
            print("No broken symlinks found")
        else:
            print(f"WARNING: {broken} broken symlink(s) found")
        print()

        print("=== Installation Summary ===")
        for subdir in INSTALL_DIRS:
            print(f"  {subdir}: {counts.get(subdir, 0)}")
        print()
        print("Installation complete! Run this script again after template updates.")
    else:
        print("=== Dry Run Summary ===")
        for comp_type in ["commands", "agents", "skills", "workflows"]:
            print(f"  {comp_type}: {installed.get(comp_type, 0)}")
        print(f"  hooks: {hook_count}")
        print(f"  rules: {rule_count}")
        total = sum(installed.values()) + hook_count + rule_count
        print(f"  total: {total}")


if __name__ == "__main__":
    main()
