---
name: obsidian-logs
description: |
  Tail VPS service logs with error filtering and highlighting.

  Usage: /obsidian-logs <service-name> [line-count]

  Examples:
  /obsidian-logs "obsidian-brain"          — Last 100 lines of obsidian-brain logs
  /obsidian-logs "obsidian-agent 500"      — Last 500 lines
  /obsidian-logs "langfuse-web errors"     — Only error-level messages
  /obsidian-logs "minio 200"              — Last 200 lines of MinIO logs

  Best for: Investigating service issues, monitoring after restart, finding error patterns
  See also: /obsidian-health (health checks), /obsidian-status (overview), /rca (root cause analysis)
argument-hint: "<service-name> [line-count|errors]"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health, obsidian/obsidian-restart]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Service Logs

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for service inventory and domain glossary.

## Step 1: Parse Arguments

From `$ARGUMENTS`, extract:
- **Service name** (required) — must match a container name from the service inventory
- **Line count** (optional, default 100) — number of lines to fetch
- **Filter mode** (optional) — if "errors" specified, filter to error/warning lines only

If no service name provided, ask the user which service to inspect. Suggest using `/obsidian-status` first to identify which service needs attention.

## Step 2: Fetch Logs

```bash
# Standard log fetch
ssh hostinger-vps 'cd /root/stack && docker compose logs --tail=<line-count> --no-color <service>'
```

For Caddy (system service, not Docker):
```bash
ssh hostinger-vps 'journalctl -u caddy --no-pager -n <line-count>'
```

## Step 3: Analyze and Filter

Scan the logs for:
- **Errors**: Lines containing `ERROR`, `FATAL`, `CRITICAL`, `Exception`, `Traceback`, HTTP 5xx status codes
- **Warnings**: Lines containing `WARN`, `WARNING`, HTTP 4xx status codes
- **Connection issues**: `connection refused`, `timeout`, `ECONNREFUSED`, `could not connect`
- **Resource issues**: `out of memory`, `disk full`, `no space left`

If "errors" filter was requested, show only error and warning lines.

## Step 4: Present Results

```
## Logs: <service-name> (last <N> lines)

### Error Summary
- X errors found, Y warnings
- [brief pattern description, e.g., "Repeated Neo4j connection timeout (5 occurrences)"]
- [or "No errors found in last N lines"]

### Error Lines
[highlighted error lines with timestamps]

### Recent Activity
[last 20 lines of log output for context]

### Recommendations
- [if connection errors: suggest checking dependency service with /obsidian-health]
- [if repeated crashes: suggest checking resource usage with /obsidian-health]
- [if no errors: "Logs look healthy"]
```

Use the dependency chain from `obsidian-context` to suggest which upstream service to check if connection errors are found (e.g., if obsidian-brain has Neo4j connection errors, suggest checking Neo4j).
