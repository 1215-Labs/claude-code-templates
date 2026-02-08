---
name: cbass-deploy
description: |
  Guided cbass deployment with pre-flight checks, profile selection, and post-deploy validation

  Usage: /cbass-deploy [profile] [environment]

  Examples:
  /cbass-deploy
  /cbass-deploy "gpu-nvidia"
  /cbass-deploy "cpu" "private"
  /cbass-deploy "gpu-nvidia" "public"

  Best for: Starting or restarting the cbass stack with validation
  See also: /cbass-status (check after deploy), /cbass-logs (troubleshoot failures)
argument-hint: "[profile: cpu|gpu-nvidia|gpu-amd|none]" "[environment: private|public]"
user-invocable: true
related:
  commands: [cbass/cbass-status, cbass/cbass-logs]
  skills: [cbass-context]
  workflows: [bug-investigation]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
  - AskUserQuestion
---

# cbass Deployment

**Arguments**: $ARGUMENTS

Reference the `cbass-context` skill for profiles, environments, service inventory, and known issues.

## Step 1: Parse Arguments

Extract from arguments:
- **Profile** (optional): `cpu`, `gpu-nvidia`, `gpu-amd`, or `none` — default to asking user
- **Environment** (optional): `private` or `public` — default to `private`

If no profile specified, use `AskUserQuestion` to let the user choose:
- `gpu-nvidia` — NVIDIA GPU available
- `cpu` — No GPU / CPU only
- `gpu-amd` — AMD GPU (Linux only)
- `none` — External LLM API only

## Step 2: Pre-Flight Checks

Run these validations before deploying:

### Docker Available
```bash
docker info > /dev/null 2>&1 && echo "Docker: OK" || echo "Docker: NOT RUNNING"
docker compose version 2>&1
```

### Environment File
```bash
test -f /Users/mike/projects/cbass/.env && echo ".env: EXISTS" || echo ".env: MISSING"
```

If `.env` is missing, warn the user and suggest:
```bash
cp /Users/mike/projects/cbass/env.example /Users/mike/projects/cbass/.env
# Then edit .env with actual values
```

### Disk Space
```bash
df -h / | tail -1
```
Warn if <10GB free (Docker images are large).

### Port Conflicts (private mode)
Check if key ports are already in use:
```bash
lsof -i :5432 -i :5678 -i :8080 -i :3000 -i :3001 2>/dev/null | grep LISTEN || echo "No port conflicts"
```

### Existing Stack
```bash
docker compose -p localai ps -q 2>/dev/null | head -1 && echo "STACK: ALREADY RUNNING" || echo "STACK: NOT RUNNING"
```

## Step 3: Present Pre-Flight Report

Show the user:
1. All checks passed/failed
2. Selected profile and environment
3. What will happen (which services start, estimated time)
4. If stack is already running: note that this will recreate containers

For `public` environment, additionally warn:
- DNS must point to this machine
- Caddy will request TLS certificates
- Ports 80/443 must be open

Use `AskUserQuestion` to confirm:
- "Deploy now" — proceed with deployment
- "Fix issues first" — abort so user can address pre-flight failures

**NEVER deploy without user confirmation.**

## Step 4: Deploy

Run the deployment:

```bash
cd /Users/mike/projects/cbass && python start_services.py --profile <PROFILE> --environment <ENVIRONMENT> 2>&1
```

Monitor the output for:
- Supabase clone progress (first run only)
- Service startup sequence
- Any errors during startup

## Step 5: Post-Deploy Validation

Wait a moment for services to initialize, then check:

```bash
# Wait for containers to stabilize
sleep 10

# Check overall status
docker compose -p localai ps -a 2>&1
```

Check critical services:
```bash
# Database
docker compose -p localai exec -T db pg_isready -U postgres 2>&1 || echo "DB: not ready"

# Redis
docker compose -p localai exec -T redis redis-cli ping 2>&1 || echo "Redis: not ready"
```

## Step 6: Present Results

Report deployment outcome:

### Success
- List all services with their status and access URLs
- For `private`: show `localhost:<port>` URLs
- For `public`: show `https://<subdomain>.cbass.space` URLs
- Note init services that are still running (model pulls, workflow imports)

### Partial Failure
- Identify which services failed and why
- Suggest `/cbass-logs "<failed-service>"` for each
- Check if it's a dependency issue (db not ready → downstream failures)

### Full Failure
- Show the error output
- Suggest checking Docker status, .env file, and disk space
- Recommend `/cbass-logs` for the first failing service

## Step 7: Suggest Next Steps

- If deployment succeeded: suggest visiting the dashboard URL
- If Ollama is pulling models: note it takes time, suggest `/cbass-status` later
- If n8n-import is running: note workflows will appear shortly
- For first-time setup: suggest checking CLAUDE.md for credential configuration
