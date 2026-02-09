---
name: obsidian-caddy-reload
description: |
  Validate and reload the Caddy reverse proxy configuration on the VPS.

  Usage: /obsidian-caddy-reload

  Examples:
  /obsidian-caddy-reload            — Validate Caddyfile, sync to VPS, reload Caddy
  /obsidian-caddy-reload "validate" — Only validate, don't reload
  /obsidian-caddy-reload "diff"     — Show diff between local and VPS Caddyfile

  Best for: After editing the Caddyfile to add/change domain routing
  See also: /obsidian-status (verify services are routable), /obsidian-health (check SSL certs)
argument-hint: "[validate|diff]"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Bash(caddy*)
  - Read
  - Grep
  - Glob
---

# Obsidian Caddy Reload

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for Caddyfile path, public domains, and integration patterns.

## Step 1: Read Current Caddyfile

Read the local Caddyfile:
```bash
cat stack/Caddyfile
```

Read the VPS Caddyfile for comparison:
```bash
ssh hostinger-vps 'cat /etc/caddy/Caddyfile'
```

## Step 2: Validate Syntax

If Caddy is available locally, validate:
```bash
caddy validate --config stack/Caddyfile 2>&1 || echo "Local caddy not available, skip local validation"
```

Check for common issues:
- All expected domains present (from `obsidian-context` public domains list)
- Each domain block has a `reverse_proxy` directive
- No duplicate domain blocks
- Port numbers match the service inventory from `obsidian-context`

## Step 3: Show Diff (if "diff" mode or before reload)

Compare local vs VPS Caddyfile:
```bash
ssh hostinger-vps 'cat /etc/caddy/Caddyfile' > /tmp/vps-caddyfile
diff stack/Caddyfile /tmp/vps-caddyfile || echo "Files differ"
```

Present the diff with context:
- Added domains (new routing)
- Changed reverse_proxy targets (port changes)
- Removed domains (breaking change warning)

If `$ARGUMENTS` is "validate" or "diff", stop here and present findings without reloading.

## Step 4: Sync and Reload

Copy the updated Caddyfile to the VPS and reload:
```bash
# Sync Caddyfile to VPS
rsync stack/Caddyfile hostinger-vps:/root/stack/Caddyfile

# Copy to Caddy's config location and reload
ssh hostinger-vps 'sudo cp /root/stack/Caddyfile /etc/caddy/Caddyfile && systemctl reload caddy'
```

## Step 5: Verify

After reload, check:
```bash
# Caddy service status
ssh hostinger-vps 'systemctl is-active caddy && echo "Caddy: active"'

# Recent Caddy logs (check for reload errors)
ssh hostinger-vps 'journalctl -u caddy --no-pager -n 10 --since "1 minute ago"'

# Verify SSL for each domain
ssh hostinger-vps 'for domain in obsidian openwebui n8n flowise langfuse search minio s3; do echo -n "${domain}.1215group.com: "; curl -sI https://${domain}.1215group.com 2>/dev/null | head -1 || echo "UNREACHABLE"; done'
```

## Step 6: Present Results

```
## Caddy Reload Results

### Changes Applied
[diff summary — added/changed/removed domains]

### Verification
| Domain | HTTPS Status | Backend |
|--------|-------------|---------|
| obsidian.1215group.com | 200 OK | obsidian-brain:8123 |
| openwebui.1215group.com | 200 OK | open-webui:3000 |
| ...

### Caddy Logs (post-reload)
[last few log lines]

### Status
- [Success: Caddy reloaded, all domains responding]
- [or: Warning — some domains not responding, check /obsidian-logs for backend issues]
```
