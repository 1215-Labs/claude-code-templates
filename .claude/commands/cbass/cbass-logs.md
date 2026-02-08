---
name: cbass-logs
description: |
  View and analyze cbass service logs with AI-powered error interpretation

  Usage: /cbass-logs "<service>" ["context"]

  Examples:
  /cbass-logs "n8n"
  /cbass-logs "ollama" "model loading stuck"
  /cbass-logs "db" "connection refused errors"
  /cbass-logs "caddy" "TLS certificate"

  Best for: Diagnosing service errors, understanding failures, correlating issues
  See also: /cbass-status (service overview), /rca (deep root cause analysis)
argument-hint: "<service name>" ["optional context"]
user-invocable: true
related:
  commands: [cbass/cbass-status, cbass/cbass-deploy]
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

# cbass Log Analysis

**Target**: $ARGUMENTS

Reference the `cbass-context` skill for service inventory, known issues, and integration patterns.

## Step 1: Parse Arguments

Extract:
- **Service name** (required): The Docker Compose service to inspect
- **Context** (optional): What the user is looking for or what went wrong

Validate the service name against the `cbass-context` service inventory. If not recognized, list valid service names and suggest the closest match.

## Step 2: Fetch Logs

Pull recent logs for the target service:

```bash
docker compose -p localai logs --tail=100 <service> 2>&1
```

If the user context mentions a specific timeframe or the log output is very large, adjust `--tail` accordingly (50 for quick scan, 200 for deeper investigation).

Also check the service state:
```bash
docker compose -p localai ps <service> 2>&1
```

## Step 3: Analyze Logs

Scan the log output for:

### Errors & Exceptions
- Stack traces, error messages, panic/fatal entries
- HTTP error codes (4xx, 5xx)
- Connection refused / timeout patterns
- OOM (out of memory) signals

### Warnings
- Deprecation notices
- Retry attempts
- Slow query warnings
- Resource pressure signals

### Patterns
- Repeated error cycles (crash loop)
- Correlation with other services (e.g., "connection to db refused" = db is down)
- Timing patterns (errors started at specific time)

## Step 4: Cross-Reference

Using the `cbass-context` dependency chain:
- If errors mention another service (db, redis, ollama), check if that dependency is healthy
- If errors match a known issue from `cbass-context`, reference the documented workaround
- If errors involve credentials, note the `.env` configuration needed

## Step 5: Present Analysis

For each issue found, provide:

1. **What happened** — plain language summary of the error
2. **Why it happened** — root cause based on log patterns and service dependencies
3. **How to fix it** — exact command or configuration change
4. **Confidence** — how certain you are (based on log clarity)

### Common Remediation Commands
```bash
# Restart a service
docker compose -p localai restart <service>

# Restart with fresh container
docker compose -p localai up -d --force-recreate <service>

# Check dependency health
docker compose -p localai ps db redis ollama

# View more log history
docker compose -p localai logs --tail=500 <service>
```

## Step 6: Suggest Next Steps

- If root cause is in a dependency: suggest `/cbass-logs "<dependency>"`
- If issue is complex: suggest `/rca "<summary of issue>"`
- If issue is resolved after restart: suggest `/cbass-status` to verify
- If credentials/config issue: point to specific `.env` variable
