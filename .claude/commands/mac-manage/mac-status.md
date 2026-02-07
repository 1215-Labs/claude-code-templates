---
name: mac-status
description: |
  Snapshot management, weekly reviews, and system status overview

  Usage: /mac-status [mode]

  Modes:
  /mac-status                  List snapshots with age and metadata
  /mac-status "snapshot"       Take new snapshot, auto-diff, summarize
  /mac-status "prune"          Suggest old snapshots to delete
  /mac-status "weekly"         Full weekly review (snapshot + diff + health + discover)

  Best for: Regular Mac maintenance and snapshot lifecycle management
  See also: /mac-health (health only), /mac-diff (diff only), /mac-discover (tracking gaps)
argument-hint: "[mode: snapshot | prune | weekly]"
user-invocable: true
related:
  commands: [mac-manage/mac-health, mac-manage/mac-diff, mac-manage/mac-discover, mac-manage/mac-restore]
  skills: [mac-manage-context]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# Mac Status & Snapshot Management

**Mode**: $ARGUMENTS

Reference the `mac-manage-context` skill for paths, output formats, and glossaries.

Parse the mode from `$ARGUMENTS`. If empty or unrecognized, default to **list** mode.

---

## Mode: List (default — no args)

### Step 1: List Snapshots

```bash
/Users/mike/mac-manage/mac-manage.sh list 2>&1
```

### Step 2: Enrich with Metadata

For each snapshot directory, gather:

```bash
# For each snapshot dir in /Users/mike/mac-manage/snapshots/[0-9]*
# Parse timestamp from directory name (YYYYMMDD-HHMMSS)
# Calculate age in days from today
# Get total size: du -sh <dir>
# Count files: find <dir> -type f | wc -l
# Check what's captured: ls <dir>/ to see which files exist
```

### Step 3: Present Table

Show a table with:
| Snapshot | Age | Size | Files | Contents |
|----------|-----|------|-------|----------|
| 20260207-110950 | 0 days | 45K | 12 | installs + config |
| 20260207-040808 | 0 days | 44K | 12 | installs + config |

Add status notes:
- Latest snapshot age assessment (Current / Stale / Very Stale)
- Recommendation for next snapshot if stale

---

## Mode: Snapshot

### Step 1: Take New Snapshot

```bash
/Users/mike/mac-manage/mac-manage.sh snapshot 2>&1
```

Capture the output and note the new snapshot directory name.

### Step 2: Auto-Diff Against Previous

If there was a previous snapshot, run diff between the previous latest and the new one:

```bash
/Users/mike/mac-manage/mac-manage.sh diff 2>&1
```

### Step 3: Summarize Changes

Apply the same interpretation logic as `/mac-diff`:
- Categorize changes (software, config, security)
- Translate plist keys to plain language
- Flag anything noteworthy

If no previous snapshot exists, just report the snapshot contents.

### Step 4: Present

Show:
1. Snapshot saved confirmation with directory name
2. Change summary (if diff was possible)
3. Any action items from the diff

---

## Mode: Prune

### Step 1: Inventory Snapshots

List all snapshots with their ages:

```bash
ls -1d /Users/mike/mac-manage/snapshots/[0-9]* 2>/dev/null | sort -r
```

Parse timestamps and calculate ages.

### Step 2: Apply Retention Policy

Retention rules:
- **Keep**: Latest 3 snapshots (always)
- **Keep**: 1 per week for the last month
- **Suggest delete**: Everything else

### Step 3: Present Pruning Plan

For each snapshot, show:
- Keep / Delete recommendation with reason
- Total space that would be freed

Provide ready-to-run `rm -rf` commands for the user to confirm, but **never execute them automatically**. Example:

```
# Suggested cleanup (review before running):
rm -rf /Users/mike/mac-manage/snapshots/20260115-080000
rm -rf /Users/mike/mac-manage/snapshots/20260110-080000
# Would free: ~150K
```

---

## Mode: Weekly

This is the comprehensive weekly review. Run all sub-checks in sequence.

### Step 1: Take Snapshot

```bash
/Users/mike/mac-manage/mac-manage.sh snapshot 2>&1
```

### Step 2: Diff Against Previous

```bash
/Users/mike/mac-manage/mac-manage.sh diff 2>&1
```

Interpret changes using `/mac-diff` logic — categorize, translate, flag.

### Step 3: Health Check

```bash
/Users/mike/mac-manage/mac-manage.sh health 2>&1
```

Interpret results using `/mac-health` logic — categorize as Critical/Important/Informational.

### Step 4: Abbreviated Discovery

Do a quick scan for untracked items (abbreviated version of `/mac-discover`):

```bash
# Quick dotfile scan
ls -a $HOME | grep '^\.' | head -30

# Quick app scan
ls /Applications/ 2>/dev/null
```

Compare against baseline files to identify the top 3-5 untracked items worth adding.

### Step 5: Weekly Summary Report

Present a consolidated report:

```
## Weekly Mac Review — [date]

### Snapshot
- New snapshot: YYYYMMDD-HHMMSS (N files)
- Total snapshots: N (suggest prune if >10)

### Changes Since Last Snapshot
- Software: N added, N removed, N upgraded
- Config: [brief summary]
- Security: [any changes]

### Health Status
- Critical: N issues
- Important: N issues
- All clear / Action needed

### Discovery Highlights
- [Top untracked items worth adding]

### Action Items
1. [Prioritized list of things to do]
```
