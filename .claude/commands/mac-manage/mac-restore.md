---
name: mac-restore
description: |
  Safely restore dotfiles and macOS preferences from a mac-manage snapshot with validation

  Usage: /mac-restore "<snapshot>" [options]

  Examples:
  /mac-restore "latest"
  /mac-restore "latest" "--dry-run"
  /mac-restore "latest" "--dotfiles"
  /mac-restore "20260207-110950"
  /mac-restore "20260207-110950" "--defaults"

  IMPORTANT: Always runs --dry-run first for safety analysis before any restore.

  Best for: Restoring configuration after a clean install or reverting changes
  See also: /mac-health (verify after restore), /mac-diff (preview changes first)
argument-hint: "<snapshot-name-or-'latest'> [--dry-run | --dotfiles | --defaults]"
user-invocable: true
related:
  commands: [mac-manage/mac-health, mac-manage/mac-diff, mac-manage/mac-status]
  skills: [mac-manage-context]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# Safe Restore with Validation

**User args**: $ARGUMENTS

Reference the `mac-manage-context` skill for paths, output formats, and glossaries.

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **Snapshot identifier**: A specific directory name (e.g., `20260207-110950`) or `latest`
- **Options**: `--dry-run`, `--dotfiles`, `--defaults`

Resolve the snapshot path:

```bash
# If "latest", find the most recent snapshot
if [[ "$SNAPSHOT" == "latest" ]]; then
  SNAPSHOT_DIR=$(ls -1d /Users/mike/mac-manage/snapshots/[0-9]* 2>/dev/null | sort -r | head -1)
else
  SNAPSHOT_DIR="/Users/mike/mac-manage/snapshots/$SNAPSHOT"
fi
```

## Step 2: Validate Snapshot

Check that the snapshot exists and contains expected files:

```bash
# Check directory exists
[ -d "$SNAPSHOT_DIR" ] || echo "ERROR: Snapshot not found"

# Check expected contents
ls -la "$SNAPSHOT_DIR"/
ls -la "$SNAPSHOT_DIR/dotfiles/" 2>/dev/null
ls -la "$SNAPSHOT_DIR/defaults/" 2>/dev/null
```

Verify the snapshot contains:
- `dotfiles/` directory (if restoring dotfiles)
- `defaults/` directory with `.plist` files (if restoring defaults)
- `system-info.txt` (to check macOS version compatibility)

Read `system-info.txt` to check the macOS version the snapshot was taken on.

## Step 3: Always Run Dry-Run First

**Even if the user did NOT specify `--dry-run`, run it first for safety analysis.**

```bash
/Users/mike/mac-manage/mac-manage.sh restore "$SNAPSHOT_DIR" --dry-run 2>&1
```

Capture the dry-run output.

## Step 4: Diff Snapshot Against Current System

For each file that would be restored, compare snapshot version against current system:

### Dotfiles
```bash
# For each dotfile in the snapshot
for f in "$SNAPSHOT_DIR/dotfiles"/*; do
  name=$(basename "$f")
  diff "$HOME/$name" "$f" 2>/dev/null || true
done
```

### Defaults
```bash
# For each plist in the snapshot, compare against current defaults
for plist in "$SNAPSHOT_DIR/defaults"/*.txt; do
  domain=$(basename "$plist" .txt)
  # Current state
  defaults read "$domain" 2>/dev/null > /tmp/current-$domain.txt
  diff /tmp/current-$domain.txt "$plist" 2>/dev/null || true
done
```

## Step 5: Incompatibility Detection

Analyze the snapshot contents for potential issues:

### Stale PATH Entries
Read snapshot dotfiles (especially `.zshrc`, `.bash_profile`) and check for PATH entries pointing to directories that don't exist on the current system:

```bash
# Extract PATH additions from snapshot .zshrc
grep -E 'PATH|path' "$SNAPSHOT_DIR/dotfiles/.zshrc" 2>/dev/null
```

For each path component, verify it exists on the current system.

### Defaults for Uninstalled Apps
Check if defaults domains in the snapshot correspond to apps that are currently installed:

```bash
# For each domain being restored, check if the app exists
ls /Applications/ 2>/dev/null
```

### macOS Version Mismatch
Compare the macOS version from `system-info.txt` against the current system. Flag if major version differs.

## Step 6: Risk Assessment

Rate the overall restore risk:

### Safe
- Snapshot is recent (<7 days old)
- Same macOS version
- No incompatible PATH entries
- Only minor dotfile changes

### Caution
- Snapshot is 7-30 days old
- Minor macOS version difference
- Some PATH entries may be stale
- Moderate dotfile changes

### Warning
- Snapshot is >30 days old
- Major macOS version difference
- Multiple stale PATH entries
- Restoring defaults for uninstalled apps
- Large number of changes

## Step 7: Present Analysis

Show the user:

1. **Snapshot Info**: Name, date, age, macOS version, contents
2. **Changes Preview**: What would change (from dry-run + diff analysis)
3. **Incompatibilities Found**: Any issues from Step 5
4. **Risk Rating**: Safe / Caution / Warning with explanation
5. **What Will Be Backed Up**: List of files that will get `.bak` copies

## Step 8: Confirmation Gate

**If the user only asked for `--dry-run`**: Stop here. Present the analysis and suggest running without `--dry-run` when ready.

**If the user wants to proceed with actual restore**:

Present a clear confirmation prompt using AskUserQuestion:
- Show the risk rating
- List the specific files that will be modified
- Ask for explicit confirmation before proceeding

**NEVER execute the actual restore without user confirmation.**

## Step 9: Execute Restore (only after confirmation)

If confirmed:

```bash
/Users/mike/mac-manage/mac-manage.sh restore "$SNAPSHOT_DIR" [options] 2>&1
```

Pass through any `--dotfiles` or `--defaults` flags from the original arguments.

## Step 10: Post-Restore Guidance

After restore completes, advise the user:

1. **Reload shell config**: `source ~/.zshrc` (or relevant shell rc file)
2. **Verify health**: suggest running `/mac-health` to confirm system state
3. **Test applications**: suggest opening recently restored apps to verify preferences took effect
4. **Restart note**: Some macOS preference changes require logout/restart to take effect (Dock, Finder, WindowManager)
5. **Backup files**: Note that original files were backed up to `*.bak` and can be restored manually if needed

```
# If something went wrong, restore backups:
# mv ~/.zshrc.bak ~/.zshrc
# mv ~/.gitconfig.bak ~/.gitconfig
```
