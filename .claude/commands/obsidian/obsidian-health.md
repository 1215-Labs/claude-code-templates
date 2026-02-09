---
name: obsidian-health
description: |
  Deep health check for VPS services — beyond Docker status to actual endpoint testing.

  Usage: /obsidian-health [service-name|"all"]

  Examples:
  /obsidian-health                      — Deep check all services
  /obsidian-health "obsidian-brain"     — Deep check obsidian-brain only
  /obsidian-health "databases"          — Check postgres-vector, neo4j, redis, clickhouse

  Best for: Diagnosing why a service appears up but isn't working correctly
  See also: /obsidian-status (quick overview), /obsidian-logs (log inspection), /rca (root cause analysis)
argument-hint: "[service-name|all]"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-logs, obsidian/obsidian-restart]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Deep Health Check

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for service inventory, health check endpoints, and dependency chain.

## Step 1: Docker-Level Health

SSH to VPS and collect per-container diagnostics:

```bash
# Container status + health + restart count
ssh hostinger-vps 'cd /root/stack && docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"'

# Memory and CPU usage per container
ssh hostinger-vps 'docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"'

# Recent restart counts (containers that restarted indicate instability)
ssh hostinger-vps 'docker inspect --format "{{.Name}} restarts={{.RestartCount}}" $(docker ps -aq) 2>/dev/null | sort'
```

If `$ARGUMENTS` specifies a service, filter to that service only. If "databases" is specified, check postgres-vector, neo4j, redis, clickhouse.

## Step 2: Endpoint-Level Health

Follow the health check priority from `obsidian-context` (check dependencies first):

**Tier 1 — Core Dependencies:**
```bash
# PostgreSQL
ssh hostinger-vps 'docker exec postgres-vector pg_isready -U postgres'

# MinIO
ssh hostinger-vps 'curl -sf http://localhost:9000/minio/health/live && echo "MinIO: OK"'

# Redis
ssh hostinger-vps 'docker exec redis valkey-cli -a "$REDIS_PASSWORD" ping'

# ClickHouse
ssh hostinger-vps 'curl -sf http://localhost:8123/ping && echo "ClickHouse: OK"'
```

**Tier 2 — Databases:**
```bash
# Neo4j
ssh hostinger-vps 'curl -sf http://localhost:7474 && echo "Neo4j: OK"'
```

**Tier 3 — Application Services:**
```bash
# obsidian-brain
ssh hostinger-vps 'curl -sf http://localhost:8123/health && echo "obsidian-brain: OK"'

# obsidian-agent
ssh hostinger-vps 'curl -sf http://localhost:8124/agent/health && echo "obsidian-agent: OK"'

# n8n
ssh hostinger-vps 'curl -sf http://localhost:5678/healthz && echo "n8n: OK"'

# Open WebUI
ssh hostinger-vps 'curl -sf http://localhost:3000/health && echo "open-webui: OK"'

# Langfuse
ssh hostinger-vps 'curl -sf http://localhost:3002 -o /dev/null && echo "langfuse-web: OK"'

# SearXNG
ssh hostinger-vps 'curl -sf http://localhost:8081/healthz && echo "searxng: OK"'
```

**Tier 4 — External Access (Caddy):**
```bash
# Verify Caddy is routing correctly
ssh hostinger-vps 'systemctl is-active caddy'

# Check SSL certificate expiry for each domain
ssh hostinger-vps 'for domain in obsidian openwebui n8n flowise langfuse search minio s3; do echo -n "${domain}.1215group.com: "; echo | openssl s_client -connect ${domain}.1215group.com:443 -servername ${domain}.1215group.com 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null || echo "CERT ERROR"; done'
```

## Step 3: Disk and Storage Health

```bash
# System disk usage
ssh hostinger-vps 'df -h / /root'

# Docker disk usage
ssh hostinger-vps 'docker system df'

# MinIO storage (if mc is available)
ssh hostinger-vps 'mc du vps/vault 2>/dev/null || echo "mc not configured"'
```

## Step 4: Present Results

Display a formatted health report:

```
## VPS Deep Health Report

### Service Health Matrix
| Service | Docker | Endpoint | CPU | Memory | Restarts |
|---------|--------|----------|-----|--------|----------|
| postgres-vector | Up | pg_isready OK | 2.1% | 256M/512M | 0 |
| minio | Up | /health/live OK | 1.5% | 180M/256M | 0 |
| ... |

### SSL Certificates
| Domain | Expiry |
|--------|--------|
| obsidian.1215group.com | 2026-04-15 |
| ... |

### Storage
- System disk: 42% used (18G/42G)
- Docker: 8.5G images, 2.1G containers, 12G volumes
- MinIO vault: 84MB (5,654 files)

### Issues Found
- [any failing health checks with diagnosis]
- [any high restart counts with log excerpt]
- [any disk warnings > 75% usage]
- [any SSL certs expiring within 14 days]
- [or "All health checks passed"]

### Recommendations
- [if issues found, suggest specific /obsidian-* commands to remediate]
```
