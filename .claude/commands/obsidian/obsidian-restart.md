---
name: obsidian-restart
description: |
  Restart VPS Docker service(s) with pre-flight checks and post-restart verification.

  Usage: /obsidian-restart <service-name(s)>

  Examples:
  /obsidian-restart "obsidian-brain"              — Restart a single service
  /obsidian-restart "obsidian-agent obsidian-brain" — Restart multiple services
  /obsidian-restart "all"                          — Restart entire stack (careful!)

  Best for: Applying config changes, recovering stuck services
  See also: /obsidian-status (check before), /obsidian-health (verify after), /obsidian-logs (monitor after)
argument-hint: "<service-name(s)|all>"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health, obsidian/obsidian-logs]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Service Restart

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for service inventory, dependency chain, and integration patterns.

## Step 1: Pre-Flight Check

Identify which service(s) to restart from `$ARGUMENTS`. If no argument provided, ask the user which service to restart.

Check current status of the target service(s):
```bash
ssh hostinger-vps 'cd /root/stack && docker compose ps <service>'
```

**Dependency awareness**: Using the dependency chain from `obsidian-context`, warn if:
- Restarting `postgres-vector` will affect 7 downstream services
- Restarting `minio` will affect 6 downstream services
- Restarting `redis` or `clickhouse` will affect Langfuse
- Restarting `ollama` will affect open-webui, n8n, flowise

If "all" was requested, list all 16 services and the expected downtime.

## Step 2: Confirm with User

Present the restart plan:

```
## Restart Plan

**Target**: [service name(s)]
**Current status**: [running/unhealthy/stopped]
**Downstream impact**: [list affected services, or "none" for leaf services]
**Estimated downtime**: [seconds for single service, minutes for "all"]

Proceed with restart? (yes/no)
```

**Wait for user confirmation before proceeding.** Do NOT restart without explicit approval.

## Step 3: Execute Restart

For single service:
```bash
ssh hostinger-vps 'cd /root/stack && docker compose restart <service>'
```

For "all" (full stack):
```bash
ssh hostinger-vps 'cd /root/stack && docker compose down && docker compose up -d'
```

For multiple named services:
```bash
ssh hostinger-vps 'cd /root/stack && docker compose restart <service1> <service2>'
```

## Step 4: Post-Restart Verification

Wait a few seconds, then verify the restarted service(s) are healthy:

```bash
# Check service status
ssh hostinger-vps 'cd /root/stack && docker compose ps <service>'

# Check logs for startup errors (last 30 lines)
ssh hostinger-vps 'cd /root/stack && docker compose logs --tail=30 <service>'
```

If the service has an HTTP health endpoint (from `obsidian-context` service inventory), test it:
```bash
ssh hostinger-vps 'curl -sf http://localhost:<port>/<health-path> && echo "Health: OK"'
```

## Step 5: Present Results

```
## Restart Results

| Service | Before | After | Health Endpoint |
|---------|--------|-------|-----------------|
| obsidian-brain | Up (unhealthy) | Up (healthy) | /health OK |

### Post-Restart Logs (last 10 lines)
[relevant log output]

### Status
- [Success: all services healthy]
- [or: Warning — service still unhealthy, check /obsidian-logs for details]
```

If any service failed to restart healthily, suggest running `/obsidian-logs <service>` and `/obsidian-health <service>` for diagnosis.
