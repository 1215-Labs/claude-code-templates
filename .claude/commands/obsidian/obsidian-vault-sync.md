---
name: obsidian-vault-sync
description: |
  Wrapper for vault-sync.sh — sync the Obsidian vault between local filesystem and MinIO S3.

  Usage: /obsidian-vault-sync <push|pull|sync|watch|status>

  Examples:
  /obsidian-vault-sync "push"    — Push local vault to MinIO (one-way)
  /obsidian-vault-sync "pull"    — Pull MinIO vault to local (one-way)
  /obsidian-vault-sync "sync"    — Bidirectional sync (newer file wins)
  /obsidian-vault-sync "watch"   — Continuous push on local file changes
  /obsidian-vault-sync "status"  — Show sync status without transferring

  Best for: Keeping Obsidian vault in sync with VPS storage
  See also: /obsidian-status (check MinIO is running), /obsidian-health (verify MinIO health)
argument-hint: "<push|pull|sync|watch|status>"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Bash(rclone*)
  - Bash(bash*vault-sync*)
  - Read
  - Grep
  - Glob
---

# Obsidian Vault Sync

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for vault paths, MinIO buckets, and CLI commands.

## Step 1: Parse Sync Mode

Extract the sync mode from `$ARGUMENTS`. Valid modes:
- **push** — Local vault → MinIO (one-way, local is source of truth)
- **pull** — MinIO → Local vault (one-way, MinIO is source of truth)
- **sync** — Bidirectional (rclone bisync, newer file wins)
- **watch** — Continuous push on inotify file change events
- **status** — Show what would sync without transferring

If no mode specified, default to "status" (safe, read-only).

## Step 2: Pre-Sync Check

Verify MinIO is accessible:
```bash
ssh hostinger-vps 'curl -sf http://localhost:9000/minio/health/live && echo "MinIO: OK" || echo "MinIO: DOWN"'
```

If MinIO is down, stop and suggest running `/obsidian-health "minio"` first.

Show current vault stats:
```bash
# MinIO vault bucket size
ssh hostinger-vps 'mc du vps/vault 2>/dev/null || echo "mc not configured — check MinIO alias"'

# Local vault size (if running from VPS)
ssh hostinger-vps 'du -sh /root/vault 2>/dev/null || echo "No local vault at /root/vault"'
```

## Step 3: Execute Sync

For **status** mode (dry-run):
```bash
ssh hostinger-vps 'bash /root/stack/scripts/vault-sync.sh sync --dry-run 2>&1 | tail -20'
```

For **push/pull/sync** modes:
```bash
ssh hostinger-vps 'bash /root/stack/scripts/vault-sync.sh <mode>'
```

For **watch** mode:
Warn the user that watch mode runs continuously and will block the terminal. Suggest running it in a tmux/screen session:
```bash
ssh hostinger-vps 'tmux new-session -d -s vault-watch "bash /root/stack/scripts/vault-sync.sh watch"'
```

## Step 4: Present Results

```
## Vault Sync Results

### Mode: <push|pull|sync|status>
### MinIO Health: OK

### Transfer Summary
- Files transferred: N
- Files skipped (up to date): N
- Total size: XMB
- Duration: Xs

### Changes
[list of files transferred, if not too many]
[or "N files transferred — too many to list, see full log on VPS"]

### Vault Stats
| Location | Files | Size |
|----------|-------|------|
| MinIO (vault bucket) | 5,654 | 84MB |
| Local (/root/vault) | 5,654 | 84MB |

### Status
- [Success: Sync complete, vaults in sync]
- [or: Warning — N conflicts detected (both sides modified)]
- [or: Error — MinIO unreachable, check /obsidian-health]
```
