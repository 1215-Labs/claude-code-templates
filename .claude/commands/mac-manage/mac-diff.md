---
name: mac-diff
description: |
  Compare mac-manage snapshots with AI-powered change interpretation

  Usage: /mac-diff [snapshot-args]

  Examples:
  /mac-diff
  /mac-diff "snapshots/20260201-120000 snapshots/20260207-120000"

  Best for: Understanding what changed between snapshots
  See also: /mac-health (system health), /mac-status (snapshot management)
argument-hint: "[optional: 'old-snapshot new-snapshot']"
user-invocable: true
related:
  commands: [mac-manage/mac-health, mac-manage/mac-status, mac-manage/mac-restore]
  skills: [mac-manage-context]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# Snapshot Diff Interpretation

**User args**: $ARGUMENTS

Reference the `mac-manage-context` skill for paths, output formats, and glossaries.

## Step 1: Run Diff

Run the mac-manage diff command:

```bash
# If user provided snapshot paths, pass them through
# Otherwise, defaults to latest two snapshots
/Users/mike/mac-manage/mac-manage.sh diff $ARGUMENTS 2>&1
```

Capture the raw diff output.

## Step 2: Identify the Snapshots

Determine which two snapshots are being compared. If no args provided:

```bash
ls -1d /Users/mike/mac-manage/snapshots/[0-9]* 2>/dev/null | sort -r | head -2
```

Calculate the time span between them (parse the YYYYMMDD-HHMMSS directory names).

## Step 3: Read Full Snapshot Files

For deeper context beyond the unified diff, read the actual snapshot files. Focus on files that showed changes in the diff output. Read from both snapshots to understand full state, not just the delta.

Key files to compare:
- `brew-formulae.txt` — software packages
- `brew-casks.txt` — GUI applications via Homebrew
- `mas-apps.txt` — Mac App Store apps
- `applications.txt` — everything in /Applications
- `dotfiles/*` — shell config, git config, etc.
- `defaults/*.txt` — macOS preference domains
- `security-status.txt` — security settings

## Step 4: Categorize Changes

Organize all changes into these categories:

### Software Changes
- **Added**: New packages/apps installed
- **Removed**: Packages/apps uninstalled
- **Upgraded**: Version changes (extract old→new version numbers)

### Dotfile Changes
- Show what actually changed in each dotfile
- Explain the impact (e.g., "Added alias for `ll`", "Changed default Python version")
- Flag any PATH changes or environment variable modifications

### Preference Changes
- Translate plist keys to human language using the defaults glossary from `mac-manage-context`
- Examples:
  - `autohide = 1` → "Dock auto-hide was enabled"
  - `AppleInterfaceStyle = Dark` → "Dark mode was enabled"
  - `tilesize = 48` → "Dock icon size changed to 48px"
- For unknown keys, show the raw key=value with domain context

### Security Changes
- Compare `security-status.txt` between snapshots
- Flag any regressions (was enabled, now disabled) as **Security Regression**
- Flag any improvements (was disabled, now enabled) as **Security Improvement**

## Step 5: Flag Concerns

Highlight anything that warrants attention:

- **Security regressions** — any security setting that went from enabled to disabled
- **Untracked apps** — apps in `applications.txt` that aren't in brew casks, mas, or `baseline/apps-manual.list`
- **Suspicious changes** — dotfile modifications the user may not have made intentionally
- **Large version jumps** — major version upgrades that might break things

## Step 6: Present Summary

Format the output as:

1. **Overview** — time span, total changes count
2. **Software** — added/removed/upgraded in a clean table
3. **Configuration** — dotfile and preference changes in plain language
4. **Security** — any changes to security posture
5. **Attention Items** — flagged concerns from Step 5
6. **Recommendations**:
   - If many untracked apps: suggest `/mac-discover`
   - If security regressions: suggest `/mac-health` for full audit
   - If significant changes accumulated: suggest updating baseline files
   - If snapshots are far apart: suggest more frequent snapshots via `/mac-status "snapshot"`
