---
name: mac-health
description: |
  Run mac-manage health checks with AI-powered triage and remediation guidance

  Usage: /mac-health [context]

  Examples:
  /mac-health
  /mac-health "preparing for travel"
  /mac-health "setting up new machine"
  /mac-health "security audit"

  Best for: Quick system health assessment with prioritized remediation
  See also: /mac-status (full weekly review), /mac-diff (change analysis)
argument-hint: "[optional context like 'preparing for travel']"
user-invocable: true
related:
  commands: [mac-manage/mac-diff, mac-manage/mac-status, mac-manage/mac-restore]
  skills: [mac-manage-context]
  workflows: [bug-investigation]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# Mac Health Check Triage

**User context**: $ARGUMENTS

Reference the `mac-manage-context` skill for paths, output formats, and glossaries.

## Step 1: Run Health Check

Run the mac-manage health check and capture output:

```bash
/Users/mike/mac-manage/mac-manage.sh health 2>&1
```

Capture the full output for analysis.

## Step 2: Read Security Snapshot for Regression Detection

Read the latest snapshot's security status to detect regressions:

```bash
# Find the latest snapshot
LATEST=$(ls -1d /Users/mike/mac-manage/snapshots/[0-9]* 2>/dev/null | sort -r | head -1)
```

If a latest snapshot exists, read `$LATEST/security-status.txt` and compare against current health check results. Any PASS→FAIL transitions are regressions.

## Step 3: Categorize and Prioritize

Categorize every finding into one of three tiers:

### Critical (fix immediately)
- FileVault OFF
- SIP disabled
- Firewall OFF (especially if user context mentions travel/public networks)
- Disk >90% full
- Security regressions (was passing, now failing)

### Important (fix soon)
- Gatekeeper issues
- No Time Machine backup configured
- Disk 80-90% full
- macOS updates available
- Stale Time Machine backup (>7 days)

### Informational (awareness)
- Homebrew packages outdated
- `brew doctor` warnings
- Disk <80% (just report the number)
- All checks passing (celebrate!)

**Context-aware priority adjustments:**
- "travel" / "public" / "coffee shop" → elevate encryption + firewall to Critical
- "new machine" / "setup" → elevate all security to Critical, note missing backups
- "security audit" → treat all warnings as Important
- "development" → elevate Homebrew issues to Important

## Step 4: Present Results

For each finding, provide:

1. **Tier** (Critical / Important / Informational)
2. **What it means** in plain language
3. **How to fix it** — exact System Settings path OR terminal command
4. **Why it matters** — one sentence on the risk

Format as a prioritized list, Critical first.

### Remediation Reference

| Issue | Fix |
|-------|-----|
| FileVault OFF | System Settings > Privacy & Security > FileVault > Turn On |
| Firewall OFF | System Settings > Network > Firewall > Turn On |
| SIP disabled | Boot to Recovery (Cmd+R) > Terminal > `csrutil enable` > Restart |
| Gatekeeper issues | `sudo spctl --master-enable` |
| No Time Machine | System Settings > General > Time Machine > Add Backup Disk |
| Disk full | `brew cleanup`, empty Trash, check `~/Library/Caches`, use `du -sh ~/* \| sort -hr \| head -20` |
| macOS updates | `softwareupdate -ia` or System Settings > General > Software Update |
| Homebrew outdated | `brew upgrade` |
| brew doctor issues | `brew doctor` then follow suggestions |

## Step 5: Suggest Next Steps

Based on findings:
- If security regressions found: suggest `/rca "Security regression: [detail]"`
- If snapshot is stale (>14 days): suggest `/mac-status "snapshot"`
- If many changes: suggest `/mac-diff` to understand what changed
- If all clear: note the clean bill of health, suggest scheduling regular `/mac-status "weekly"` checks
