---
name: obsidian-deploy
description: |
  Guided VPS deployment with pre-flight checks, rsync, deploy.sh execution, and health verification.

  Usage: /obsidian-deploy [scope]

  Examples:
  /obsidian-deploy                        — Full deployment (rsync + deploy.sh + health check)
  /obsidian-deploy "obsidian-agent"       — Deploy only a specific service (rebuild + restart)
  /obsidian-deploy "caddy"               — Deploy Caddy config changes only

  Best for: After editing docker-compose.yml, Caddyfile, .env, or service code
  See also: /obsidian-status (check before), /obsidian-health (verify after), /obsidian-env-check (pre-flight)
argument-hint: "[scope: service-name|caddy|all]"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health, obsidian/obsidian-env-check, obsidian/obsidian-logs]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Bash(rsync*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Deployment

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for paths, service inventory, CLI commands, and integration patterns.

## Step 1: Determine Deployment Scope

Parse `$ARGUMENTS` to determine what's being deployed:

- **No argument or "all"** → Full stack deployment (rsync everything, run deploy.sh)
- **Service name** (e.g., "obsidian-agent") → Single service rebuild + restart
- **"caddy"** → Caddy config reload only

If no argument, check what's changed locally to suggest scope:
```bash
cd ~/projects/obsidian-ecosystem-hub && git diff --name-only HEAD
```

## Step 2: Pre-Flight Checks

Run these checks before deploying. Stop if any fail.

### 2a. Environment validation
```bash
ssh hostinger-vps 'test -f /root/stack/.env && echo "ENV_OK" || echo "ENV_MISSING"'
```

### 2b. Current service status (snapshot for comparison)
```bash
ssh hostinger-vps 'cd /root/stack && docker compose ps --format "table {{.Name}}\t{{.Status}}"'
```

### 2c. VPS disk space
```bash
ssh hostinger-vps 'df -h /root | tail -1'
```

### 2d. For Caddy deployments, validate config syntax
```bash
ssh hostinger-vps 'caddy validate --config /root/stack/Caddyfile 2>&1 || echo "CADDY_INVALID"'
```

Present pre-flight summary and **wait for user confirmation before proceeding**.

## Step 3: Execute Deployment

### Full deployment (no scope or "all")
```bash
# Sync local stack to VPS
rsync -avz --exclude '.env' --exclude '__pycache__' --exclude '.git' \
  ~/projects/obsidian-ecosystem-hub/stack/ hostinger-vps:/root/stack/

# Run deploy script
ssh hostinger-vps 'cd /root/stack && ./deploy.sh'
```

### Single service deployment
```bash
# Sync only the service directory
rsync -avz --exclude '__pycache__' --exclude '.git' \
  ~/projects/obsidian-ecosystem-hub/stack/<service>/ hostinger-vps:/root/stack/<service>/

# Rebuild and restart just that service
ssh hostinger-vps 'cd /root/stack && docker compose build <service> && docker compose up -d <service>'
```

### Caddy-only deployment
```bash
# Sync Caddyfile
rsync -avz ~/projects/obsidian-ecosystem-hub/stack/Caddyfile hostinger-vps:/root/stack/Caddyfile

# Copy to system location and reload
ssh hostinger-vps 'sudo cp /root/stack/Caddyfile /etc/caddy/Caddyfile && systemctl reload caddy'
```

## Step 4: Post-Deployment Verification

Wait 10 seconds for services to stabilize, then verify.

### Check service status
```bash
ssh hostinger-vps 'cd /root/stack && docker compose ps --format "table {{.Name}}\t{{.Status}}"'
```

### Check health endpoints for affected services
Using health endpoints from `obsidian-context` service inventory, test each affected service:
```bash
ssh hostinger-vps 'curl -sf http://localhost:<port>/<health-path> && echo "OK" || echo "FAIL"'
```

### Check for startup errors in logs
```bash
ssh hostinger-vps 'cd /root/stack && docker compose logs --tail=20 <service> 2>&1 | grep -iE "error|exception|fatal|traceback" || echo "No errors"'
```

## Step 5: Present Results

```
## Deployment Results

**Scope**: [full / service-name / caddy]
**Duration**: [time taken]

| Service | Before | After | Health |
|---------|--------|-------|--------|
| ... | Up (healthy) | Up (healthy) | /health OK |

### Changes Deployed
[List what was synced based on scope]

### Errors
[Any errors found in logs, or "None"]

### Next Steps
- Run `/obsidian-health` for deep endpoint testing
- Run `/obsidian-logs <service>` if any warnings appeared
```

If any service is unhealthy after deployment, suggest rollback steps:
```bash
# Rollback: restore from backup created by deploy.sh
ssh hostinger-vps 'ls -lt /root/backups/ | head -5'
```
