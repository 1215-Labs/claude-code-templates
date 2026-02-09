#!/usr/bin/env python3
"""
Validate documentation alignment across the repository.

Runs 6 checks:
  1. MANIFEST <-> Filesystem sync, including hooks/examples (critical)
  2. install-global.py dry-run validation (critical)
  3. Documentation counts & coverage (critical)
  4. CHANGELOG freshness (advisory)
  5. YAML frontmatter validation (advisory)
  6. Cross-reference validation (advisory)

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


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from a markdown file. Returns None if no frontmatter."""
    try:
        text = filepath.read_text()
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    yaml_text = text[3:end].strip()

    # Simple YAML parser for flat keys + basic structures
    # Avoids requiring PyYAML as a dependency
    result = {}
    current_key = None
    current_value_lines = []

    for line in yaml_text.split("\n"):
        # Skip comment lines
        if line.strip().startswith("#"):
            continue

        # Check for key: value
        match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", line)
        if match:
            # Save previous key
            if current_key is not None:
                val = "\n".join(current_value_lines).strip()
                result[current_key] = val if val else True
            current_key = match.group(1)
            current_value_lines = [match.group(2).strip()]
        elif current_key is not None and (line.startswith("  ") or line.startswith("\t")):
            current_value_lines.append(line.strip())
        elif line.strip() == "":
            if current_key is not None:
                current_value_lines.append("")

    # Save last key
    if current_key is not None:
        val = "\n".join(current_value_lines).strip()
        result[current_key] = val if val else True

    # Clean up values
    for k, v in result.items():
        if isinstance(v, str):
            # Remove leading | for multiline strings
            if v.startswith("|"):
                v = v[1:].strip()
            result[k] = v

    return result


def check_manifest_sync() -> list[str]:
    """Check 1: MANIFEST paths exist on disk and vice versa (including hooks/examples)."""
    errors = []
    manifest_path = REPO_ROOT / "MANIFEST.json"

    if not manifest_path.exists():
        errors.append("MANIFEST.json not found")
        return errors

    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})

    # Check all MANIFEST paths exist on disk (skills, agents, commands, workflows)
    for comp_type in ["skills", "agents", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            path = REPO_ROOT / comp["path"]
            if not path.exists():
                errors.append(f"MANIFEST entry missing on disk: {comp['path']}")

    # Check hook paths exist on disk
    for hook in components.get("hooks", []):
        if hook.get("path"):
            path = REPO_ROOT / hook["path"]
            if not path.exists():
                errors.append(f"MANIFEST hook missing on disk: {hook['path']}")

    # Check example paths exist on disk
    for example in components.get("examples", []):
        if example.get("path"):
            path = REPO_ROOT / example["path"]
            if not path.exists():
                errors.append(f"MANIFEST example missing on disk: {example['path']}")

    # Reverse checks: disk components have MANIFEST entries
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

    # Reverse check: hook scripts on disk are in MANIFEST
    hook_manifest_paths = set()
    for hook in components.get("hooks", []):
        if hook.get("path"):
            hook_manifest_paths.add(hook["path"])

    hooks_dir = REPO_ROOT / ".claude" / "hooks"
    if hooks_dir.exists():
        for item in hooks_dir.iterdir():
            if item.name.startswith(("_", ".")) or item.name == "hooks.json":
                continue
            if item.is_file() and item.suffix in (".py", ".sh"):
                rel = str(item.relative_to(REPO_ROOT))
                if rel not in hook_manifest_paths:
                    errors.append(f"Unregistered hook script on disk: {rel}")

    return errors


def check_install_global_coverage() -> list[str]:
    """Check 2: install-global.py can parse MANIFEST and plan all global installs."""
    errors = []
    manifest_path = REPO_ROOT / "MANIFEST.json"
    install_script = REPO_ROOT / "scripts" / "install-global.py"

    if not manifest_path.exists():
        errors.append("MANIFEST.json not found")
        return errors

    if not install_script.exists():
        errors.append("scripts/install-global.py not found")
        return errors

    # Run --dry-run and check it succeeds
    try:
        result = subprocess.run(
            [sys.executable, str(install_script), "--dry-run"],
            capture_output=True, text=True, timeout=15,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            errors.append(
                f"install-global.py --dry-run failed (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )
            return errors
    except Exception as e:
        errors.append(f"install-global.py --dry-run error: {e}")
        return errors

    # Parse the dry-run total from output and compare to MANIFEST global count
    output = result.stdout
    total_match = re.search(r"total:\s*(\d+)", output)
    if not total_match:
        errors.append("Could not parse total from install-global.py --dry-run output")
        return errors

    dry_run_total = int(total_match.group(1))

    # Count expected globals from MANIFEST
    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})

    # Count unique global install units
    expected = 0
    seen_cmd_dirs = set()
    for comp_type in ["commands", "agents", "skills", "workflows"]:
        for comp in components.get(comp_type, []):
            if comp.get("deployment") != "global":
                continue
            # Deduplicate grouped command directories (prp-*, not workflow/)
            if comp_type == "commands":
                parts = Path(comp["path"]).parts
                if len(parts) > 3 and parts[2] != "workflow":
                    parent = parts[2]
                    if parent in seen_cmd_dirs:
                        continue
                    seen_cmd_dirs.add(parent)
            expected += 1

    # Add hooks with paths + hooks.json + rules
    hooks_json = REPO_ROOT / ".claude" / "hooks" / "hooks.json"
    if hooks_json.exists():
        expected += 1
    for hook in components.get("hooks", []):
        if hook.get("deployment") == "global" and hook.get("path"):
            expected += 1

    # Rules
    rules_dir = REPO_ROOT / ".claude" / "rules"
    if rules_dir.exists():
        for item in rules_dir.iterdir():
            if not item.name.startswith(("_", ".")):
                expected += 1

    if dry_run_total != expected:
        errors.append(
            f"install-global.py plans {dry_run_total} installs, "
            f"but MANIFEST has {expected} global install units"
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
    """Check 4: CHANGELOG reflects recent work.

    Passes if ANY of these are true:
    - HEAD commit hash appears in CHANGELOG.md
    - CHANGELOG.md was modified in the HEAD commit (handles the circular
      hash problem: amending to add the hash changes the hash)
    """
    warnings = []

    try:
        changelog = REPO_ROOT / "CHANGELOG.md"
        if not changelog.exists():
            warnings.append("CHANGELOG.md not found")
            return warnings

        # Check 1: HEAD hash in CHANGELOG
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        if result.returncode != 0:
            return warnings

        head_hash = result.stdout.strip()
        content = changelog.read_text()
        if head_hash in content:
            return warnings  # Pass: hash found

        # Check 2: CHANGELOG modified in HEAD commit
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=REPO_ROOT
        )
        if result.returncode == 0 and "CHANGELOG.md" in result.stdout:
            return warnings  # Pass: CHANGELOG was updated in this commit

        warnings.append(
            f"CHANGELOG.md missing entry for HEAD commit ({head_hash})"
        )
    except Exception:
        pass

    return warnings


def check_frontmatter() -> list[str]:
    """Check 5: YAML frontmatter has required fields (advisory)."""
    warnings = []
    manifest_path = REPO_ROOT / "MANIFEST.json"

    if not manifest_path.exists():
        return warnings

    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})

    # Required fields per component type
    required_fields = {
        "agents": ["name", "description"],
        "skills": ["name", "description", "version"],
        "commands": ["name", "description"],
        "workflows": ["name", "description"],
    }

    for comp_type in ["agents", "skills", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            path = REPO_ROOT / comp["path"]

            # Find the markdown file to parse
            if path.is_dir():
                # Directory agents have AGENT.md, skills have SKILL.md
                if comp_type == "agents":
                    md_file = path / "AGENT.md"
                elif comp_type == "skills":
                    md_file = path / "SKILL.md"
                else:
                    continue
            elif path.is_file() and path.suffix == ".md":
                md_file = path
            else:
                continue

            if not md_file.exists():
                warnings.append(f"No markdown file for {comp_type[:-1]} '{comp['name']}': {md_file}")
                continue

            fm = _parse_frontmatter(md_file)
            if fm is None:
                warnings.append(f"No frontmatter in {comp_type[:-1]} '{comp['name']}': {md_file.relative_to(REPO_ROOT)}")
                continue

            # Check required fields
            for field in required_fields.get(comp_type, []):
                if field not in fm:
                    warnings.append(
                        f"{comp_type[:-1]} '{comp['name']}' missing frontmatter field: {field}"
                    )

            # Validate model value if present
            if "model" in fm:
                valid_models = {"sonnet", "opus", "haiku", "inherit"}
                model_val = fm["model"].strip().lower() if isinstance(fm["model"], str) else ""
                if model_val not in valid_models:
                    warnings.append(
                        f"{comp_type[:-1]} '{comp['name']}' has invalid model: '{fm['model']}' "
                        f"(expected one of: {', '.join(sorted(valid_models))})"
                    )

            # Validate tools is a JSON array if present
            if "tools" in fm:
                tools_val = fm["tools"]
                if isinstance(tools_val, str):
                    tools_str = tools_val.strip()
                    if not (tools_str.startswith("[") and tools_str.endswith("]")):
                        warnings.append(
                            f"{comp_type[:-1]} '{comp['name']}' tools should be a JSON array, got: {tools_str[:50]}"
                        )

            # Validate version follows semver if present
            if "version" in fm and comp_type == "skills":
                version_val = fm["version"].strip() if isinstance(fm["version"], str) else ""
                if not re.match(r"^\d+\.\d+\.\d+$", version_val):
                    warnings.append(
                        f"skill '{comp['name']}' version should be semver (X.Y.Z), got: '{version_val}'"
                    )

    return warnings


def check_cross_references() -> list[str]:
    """Check 6: related field references exist in MANIFEST (advisory)."""
    warnings = []
    manifest_path = REPO_ROOT / "MANIFEST.json"

    if not manifest_path.exists():
        return warnings

    with open(manifest_path) as f:
        manifest = json.load(f)

    components = manifest.get("components", {})

    # Build set of known component names by type
    # Also build a short-name lookup for commands (e.g., "remember" -> "workflow/remember")
    known = {}
    cmd_short_names = {}  # short_name -> full MANIFEST name
    for comp_type in ["agents", "skills", "commands", "workflows"]:
        known[comp_type] = set()
        for comp in components.get(comp_type, []):
            known[comp_type].add(comp["name"])
            if comp_type == "commands":
                # Map the last part of the name for short lookups
                short = comp["name"].rsplit("/", 1)[-1]
                cmd_short_names[short] = comp["name"]

    # Check each component's related field
    for comp_type in ["agents", "skills", "commands", "workflows"]:
        for comp in components.get(comp_type, []):
            path = REPO_ROOT / comp["path"]

            # Find markdown file
            if path.is_dir():
                if comp_type == "agents":
                    md_file = path / "AGENT.md"
                elif comp_type == "skills":
                    md_file = path / "SKILL.md"
                else:
                    continue
            elif path.is_file() and path.suffix == ".md":
                md_file = path
            else:
                continue

            if not md_file.exists():
                continue

            fm = _parse_frontmatter(md_file)
            if fm is None or "related" not in fm:
                continue

            # Parse related references from the raw text
            # The related field structure varies, so parse from the raw YAML block
            try:
                text = md_file.read_text()
                end = text.find("---", 3)
                yaml_block = text[3:end]
            except Exception:
                continue

            # Find related section and extract references
            in_related = False
            for line in yaml_block.split("\n"):
                stripped = line.strip()
                if stripped.startswith("related:"):
                    in_related = True
                    continue
                if in_related:
                    # New top-level key ends related block
                    if re.match(r"^\w[\w-]*\s*:", line) and not line.startswith(" "):
                        break

                    # Parse "agents: [a, b, c]" or "agents:" / "  - a"
                    ref_match = re.match(r"\s+(agents|skills|commands|workflows)\s*:\s*(.*)", line)
                    if ref_match:
                        ref_type = ref_match.group(1)
                        ref_val = ref_match.group(2).strip()
                        if ref_val.startswith("[") and ref_val.endswith("]"):
                            # Inline array
                            refs = [r.strip().strip("'\"") for r in ref_val[1:-1].split(",")]
                            for ref in refs:
                                ref = ref.strip()
                                if not ref:
                                    continue
                                # Strip leading / from command references
                                if ref.startswith("/"):
                                    ref = ref[1:]
                                # Resolve short command names via lookup
                                if ref_type == "commands" and ref not in known["commands"]:
                                    ref = cmd_short_names.get(ref, ref)
                                if ref not in known.get(ref_type, set()):
                                    warnings.append(
                                        f"{comp_type[:-1]} '{comp['name']}' references "
                                        f"unknown {ref_type[:-1]}: '{ref}'"
                                    )

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

    # Check 2: install-global.py coverage (critical)
    print("Check 2: install-global.py dry-run validation...")
    errs = check_install_global_coverage()
    if errs:
        critical_errors.extend(errs)
        for e in errs:
            print(f"  CRITICAL: {e}")
    else:
        print("  OK")

    # Check 3: Documentation counts & coverage (critical)
    print("Check 3: Documentation counts & coverage...")
    warns = check_doc_counts()
    if warns:
        critical_errors.extend(warns)
        for w in warns:
            print(f"  CRITICAL: {w}")
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

    # Check 5: YAML frontmatter validation (advisory)
    print("Check 5: YAML frontmatter validation...")
    warns = check_frontmatter()
    if warns:
        advisory_warnings.extend(warns)
        for w in warns:
            print(f"  WARNING: {w}")
    else:
        print("  OK")

    # Check 6: Cross-reference validation (advisory)
    print("Check 6: Cross-reference validation...")
    warns = check_cross_references()
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
