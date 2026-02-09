---
name: obsidian-status
description: |
  Show all Docker service statuses and Caddy reverse proxy status on the VPS.

  Usage: /obsidian-status [service-name]

  Examples:
  /obsidian-status                  — Full status of all 16 services + Caddy
  /obsidian-status "obsidian-brain" — Status of a specific service
  /obsidian-status "langfuse"       — Status of Langfuse services

  Best for: Quick overview of VPS service health at the start of a session
  See also: /obsidian-health (deep health checks), /obsidian-logs (service logs)
argument-hint: "[service-name]"
user-invocable: true
related:
  commands: [obsidian/obsidian-health, obsidian/obsidian-logs, obsidian/obsidian-restart]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Service Status

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for paths, service inventory, and domain glossary.

## Step 1: Gather Service Status

SSH to the VPS and collect Docker Compose status:

```bash
ssh hostinger-vps 'cd /root/stack && docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"'
```

If a specific service name was provided in `$ARGUMENTS`, filter the output to only that service (or services matching the name, e.g., "langfuse" matches both langfuse-web and langfuse-worker).

Also collect Caddy status:
```bash
ssh hostinger-vps 'systemctl is-active caddy && systemctl status caddy --no-pager -l | head -15'
```

## Step 2: Parse and Enrich

Using the service inventory from `obsidian-context`, enrich each service with:
- Its **role** (e.g., "GraphRAG semantic search", "S3-compatible storage")
- Its **subdomain** if web-facing (e.g., obsidian.1215group.com)
- Its **dependency tier** (postgres-vector and minio are Tier 1 — if they are down, many others will fail)

Flag any services that are:
- **Unhealthy** or **Restarting** — highlight as critical
- **Exited** — highlight as stopped
- **Missing** — expected service not in output

## Step 3: Present Results

Display a formatted status table:

```
## VPS Service Status (hostinger-vps)

| Service | Status | Role | Domain |
|---------|--------|------|--------|
| postgres-vector | ✓ Up (healthy) | PostgreSQL + pgvector | internal |
| minio | ✓ Up (healthy) | S3 storage | minio.1215group.com |
| ...

### Caddy Reverse Proxy
Status: active (running)
Domains: 8 sites with auto-HTTPS

### Issues Found
- [list any unhealthy/stopped/missing services]
- [or "All services healthy"]
```

If any Tier 1 dependencies (postgres-vector, minio) are down, add a warning explaining which downstream services are affected using the dependency chain from `obsidian-context`.
