---
name: cbass-status
description: |
  Check status of all cbass services with AI-powered health interpretation

  Usage: /cbass-status [focus]

  Examples:
  /cbass-status
  /cbass-status "n8n"
  /cbass-status "databases"
  /cbass-status "after deploy"

  Best for: Quick overview of which services are up, down, or unhealthy
  See also: /cbass-logs (log analysis), /cbass-deploy (start services)
argument-hint: "[optional focus like 'databases' or 'after deploy']"
user-invocable: true
related:
  commands: [cbass/cbass-logs, cbass/cbass-deploy]
  skills: [cbass-context]
  workflows: [bug-investigation]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# cbass Service Status

**User context**: $ARGUMENTS

Reference the `cbass-context` skill for service inventory, ports, dependency chains, and glossary.

## Step 1: Gather Service Status

Run Docker Compose status for the `localai` project:

```bash
docker compose -p localai ps -a 2>&1
```

Capture the full output. If Docker is not running or the project doesn't exist, report that clearly.

## Step 2: Check Key Health Endpoints

For critical services, attempt lightweight health probes:

```bash
# Database
docker compose -p localai exec -T db pg_isready -U postgres 2>&1 || echo "DB: unreachable"

# Redis
docker compose -p localai exec -T redis redis-cli ping 2>&1 || echo "Redis: unreachable"

# Ollama
curl -sf http://localhost:11434/api/version 2>&1 || echo "Ollama: unreachable"
```

If user context focuses on specific services, add targeted checks for those.

## Step 3: Categorize and Interpret

For each service from the `cbass-context` inventory, categorize as:

### Healthy
- Container running, healthcheck passing (if applicable)
- Expected ports exposed

### Warning
- Container running but healthcheck failing
- Container restarting (restart count > 0)
- Init service that hasn't completed

### Down
- Container exited (non-zero exit code)
- Container not found (not started)
- Service unreachable on expected port

### Expected Stopped
- Init services that completed successfully (exit 0)
- Profile-specific services not in current profile (e.g., `ollama-gpu` when running `cpu`)

## Step 4: Present Results

Show a categorized status report:

1. **Summary line**: "X/Y services healthy, Z warnings, W down"
2. **Warnings first** — services needing attention with diagnosis
3. **Down services** — with likely cause and fix command
4. **Healthy services** — brief confirmation table
5. **Expected stopped** — init services, profile variants

For each issue found, provide:
- What the service does (from `cbass-context` glossary)
- Likely cause based on dependency chain
- Exact fix command (restart, check logs, check dependency)

## Step 5: Suggest Next Steps

Based on findings:
- If services are down: suggest `/cbass-logs "<service>"` for the failing service
- If everything is healthy: report clean status, note uptime
- If Docker isn't running: suggest starting Docker Desktop
- If project doesn't exist: suggest `/cbass-deploy` to start services
- If dependency is down causing cascading failures: identify the root service
