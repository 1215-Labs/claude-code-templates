---
name: obsidian-context
description: Shared knowledge base for obsidian-ecosystem-hub slash commands — VPS paths, Docker services, domain glossary, CLI commands, and integration patterns
version: 1.0.0
category: infrastructure
user-invocable: false
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-health, obsidian/obsidian-restart, obsidian/obsidian-logs, obsidian/obsidian-env-check, obsidian/obsidian-caddy-reload, obsidian/obsidian-vault-sync]
  workflows: [bug-investigation]
---

# Obsidian Ecosystem Context

Shared context referenced by all `/obsidian-*` commands. Do NOT invoke directly.

## Paths & Constants

| Variable | Value |
|----------|-------|
| `OBSIDIAN_HUB_DIR` | `~/projects/obsidian-ecosystem-hub` |
| `VPS_STACK_DIR` | `/root/stack/` |
| `COMPOSE_FILE` | `/root/stack/docker-compose.yml` |
| `CADDYFILE` | `/etc/caddy/Caddyfile` |
| `ENV_FILE` | `/root/stack/.env` |
| `VAULT_PATH` | `/root/vault` |
| `VAULT_BUCKET` | `vault` (MinIO bucket) |
| `DEPLOY_SCRIPT` | `/root/stack/deploy.sh` |
| `VAULT_SYNC_SCRIPT` | `/root/stack/scripts/vault-sync.sh` |
| `VPS_HOST` | `hostinger-vps` (SSH alias) |
| `DOMAIN` | `1215group.com` |
| `BACKUP_DIR` | `/root/backups/` |

## CLI Commands

```
# SSH to VPS
ssh hostinger-vps

# Docker Compose (from /root/stack/)
docker compose up -d                        # Start all services
docker compose up -d <service>              # Start specific service
docker compose down                         # Stop all services
docker compose ps                           # Service status
docker compose logs -f <service>            # Follow logs
docker compose logs --tail=100 <service>    # Recent logs
docker compose restart <service>            # Restart service
docker compose build <service>              # Rebuild custom image
docker compose pull                         # Pull latest images

# Caddy (reverse proxy)
systemctl status caddy                      # Caddy status
systemctl reload caddy                      # Reload config (no downtime)
systemctl restart caddy                     # Full restart
journalctl -u caddy --no-pager -n 50       # Caddy logs

# MinIO client (mc)
mc alias set vps http://localhost:9000 admin $MINIO_ROOT_PASSWORD
mc ls vps/vault                             # List vault bucket
mc ls vps/langfuse                          # List Langfuse bucket
mc du vps/vault                             # Vault storage usage
mc stat vps/vault/<file>                    # File metadata

# rclone (vault sync)
rclone sync /root/vault minio:vault --progress    # Push local to MinIO
rclone sync minio:vault /root/vault --progress    # Pull MinIO to local
bash /root/stack/scripts/vault-sync.sh push        # One-way push
bash /root/stack/scripts/vault-sync.sh pull        # One-way pull
bash /root/stack/scripts/vault-sync.sh sync        # Bidirectional sync
bash /root/stack/scripts/vault-sync.sh watch       # Continuous push on change

# Database access
docker exec postgres-vector psql -U postgres -d obsidian_agent     # Agent DB
docker exec postgres-vector psql -U postgres -d obsidian_brain     # Brain DB
docker exec postgres-vector psql -U postgres -d langfuse           # Langfuse DB
docker exec postgres-vector psql -U postgres -d flowise            # Flowise DB
docker exec neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD         # Neo4j
docker exec redis valkey-cli -a $REDIS_PASSWORD                    # Redis

# Deployment
rsync -avz stack/ hostinger-vps:/root/stack/       # Sync to VPS
ssh hostinger-vps 'cd /root/stack && ./deploy.sh'  # Run deploy script

# Alembic migrations (obsidian-agent)
docker exec obsidian-agent alembic upgrade head
docker exec obsidian-agent alembic history
```

## Service Inventory

| Service | Container | Port(s) | Subdomain | Role | Healthcheck |
|---------|-----------|---------|-----------|------|-------------|
| **ollama** | ollama | 11434 (internal) | -- | Local LLM inference | `ollama list` |
| **open-webui** | open-webui | 3000:8080 | openwebui.1215group.com | ChatGPT-style LLM UI | HTTP /health |
| **n8n** | n8n | 5678:5678 | n8n.1215group.com | Workflow automation | HTTP /healthz |
| **n8n-mcp** | n8n-mcp | -- (stdio) | -- | MCP server for n8n API | JSON-RPC probe |
| **flowise** | flowise | 3001:3001 | flowise.1215group.com | No-code AI agent builder | HTTP / |
| **searxng** | searxng | 8081:8080 | search.1215group.com | Meta search engine | HTTP /healthz |
| **postgres-vector** | postgres-vector | 5432:5432 | -- | PostgreSQL + pgvector (133K vectors) | pg_isready |
| **neo4j** | neo4j | 7474,7687 | -- | Knowledge graph (APOC enabled) | HTTP :7474 |
| **clickhouse** | clickhouse | 8123,9000 (internal) | -- | Analytics DB (Langfuse backend) | HTTP /ping |
| **redis** | redis | 6379 (internal) | -- | Cache (Valkey 8) | valkey-cli ping |
| **minio** | minio | 9000,9001 | minio.1215group.com (console), s3.1215group.com (API) | S3-compatible storage | mc ready |
| **langfuse-web** | langfuse-web | 3002:3000 | langfuse.1215group.com | LLM observability UI | -- |
| **langfuse-worker** | langfuse-worker | 3030 (internal) | -- | Background trace processing | -- |
| **obsidian-agent** | obsidian-agent | 8124:8123 | obsidian.1215group.com/slack/*, /agent/health | Slack/GPT capture service (FastAPI) | HTTP /health |
| **obsidian-brain** | obsidian-brain | 8123:8123 | obsidian.1215group.com (default) | GraphRAG semantic search (FastAPI) | HTTP /health |
| **rag-pipeline** | rag-pipeline | -- (background) | -- | Continuous embedding pipeline | -- |

## Public Domains (Caddy auto-HTTPS)

```
obsidian.1215group.com     -> obsidian-brain:8123 (default) + obsidian-agent:8124 (/slack/*, /agent/health)
openwebui.1215group.com    -> open-webui:3000
n8n.1215group.com          -> n8n:5678
flowise.1215group.com      -> flowise:3001
langfuse.1215group.com     -> langfuse-web:3002
search.1215group.com       -> searxng:8081
minio.1215group.com        -> minio:9001 (console)
s3.1215group.com           -> minio:9000 (S3 API)
```

## MinIO Buckets

| Bucket | Purpose | Consumers |
|--------|---------|-----------|
| `vault` | Obsidian vault markdown files (primary storage) | obsidian-agent, obsidian-brain, rag-pipeline |
| `langfuse` | Langfuse event/media uploads | langfuse-web, langfuse-worker |
| `inbox` | n8n workflow input files | n8n |
| `processed` | n8n processed output | n8n |
| `backups` | Service backup snapshots | deploy.sh |
| `vault-snapshots` | Vault point-in-time snapshots | vault-sync.sh |
| `temp` | Temporary processing files | various |

## Domain Glossary

### Obsidian Ecosystem
| Term | Meaning |
|------|---------|
| **Obsidian Vault** | Local markdown-based knowledge base (5,654 files, 84MB) synced to MinIO |
| **obsidian-agent** | FastAPI service capturing notes from Slack Events API + ChatGPT GPT Actions |
| **obsidian-brain** | FastAPI service providing semantic search via pgvector + Neo4j knowledge graph |
| **rag-pipeline** | Background service watching vault files, generating embeddings, storing vectors |
| **GraphRAG** | Graph + Retrieval-Augmented Generation (vector search + knowledge graph combined) |

### Infrastructure
| Term | Meaning |
|------|---------|
| **MinIO** | Self-hosted S3-compatible object storage (central vault bucket + Langfuse blobs) |
| **pgvector** | PostgreSQL extension for vector similarity search (133K embeddings stored) |
| **Neo4j** | Graph database for knowledge graph relationships (APOC plugin enabled) |
| **Caddy** | Reverse proxy with automatic HTTPS via Let's Encrypt (replaces NGINX) |
| **Valkey** | Redis-compatible in-memory cache (fork of Redis, used by n8n + Langfuse) |
| **ClickHouse** | Column-oriented analytics database (Langfuse trace storage backend) |

### AI Services
| Term | Meaning |
|------|---------|
| **Ollama** | Local LLM inference server (8192 context, flash attention, q8_0 KV cache) |
| **Open WebUI** | ChatGPT-style web interface for Ollama and external LLMs |
| **n8n** | Workflow automation platform (webhook-driven, Slack + MinIO integration) |
| **n8n-mcp** | Model Context Protocol server bridging Claude/LLMs to n8n workflow API |
| **Flowise** | No-code AI agent builder using PostgreSQL backend (not SQLite) |
| **SearXNG** | Privacy-focused meta search engine (used by n8n for web search) |
| **Langfuse** | LLM observability platform — traces, costs, evaluations for all AI calls |

### Operations
| Term | Meaning |
|------|---------|
| **deploy.sh** | Full deployment script: backup, stop, secrets, pull, start, migrate, health check |
| **vault-sync.sh** | rclone-based vault synchronization: push, pull, bidirectional sync, watch modes |
| **rclone** | CLI tool for syncing files between local filesystem and MinIO S3 |
| **mc** | MinIO client CLI for bucket management, file listing, storage stats |

## Service Dependency Chain

```
postgres-vector <- n8n, flowise, langfuse-web, langfuse-worker, obsidian-agent, obsidian-brain, rag-pipeline
redis           <- langfuse-web, langfuse-worker
clickhouse      <- langfuse-web, langfuse-worker
minio           <- n8n, langfuse-web, langfuse-worker, obsidian-agent, obsidian-brain, rag-pipeline
neo4j           <- obsidian-brain
ollama          <- open-webui, n8n, flowise
caddy (systemd) <- all web-facing services (external access)
```

## Health Check Priority

When diagnosing issues, check in dependency order:
1. `postgres-vector` -- most services depend on it
2. `minio` -- storage layer for vault + Langfuse + n8n
3. `redis` + `clickhouse` -- Langfuse depends on both
4. `ollama` -- LLM services depend on it
5. `neo4j` -- obsidian-brain depends on it
6. Individual failing service

## Integration Patterns

### After editing docker-compose.yml
```bash
ssh hostinger-vps
cd /root/stack
docker compose up -d <changed-service>    # Restart only changed service
docker compose logs -f <changed-service>  # Verify it starts correctly
```

### After editing Caddyfile
```bash
ssh hostinger-vps
# Copy updated Caddyfile
sudo cp /root/stack/Caddyfile /etc/caddy/Caddyfile
systemctl reload caddy                    # Reload without downtime
journalctl -u caddy --no-pager -n 20     # Verify no errors
```

### After changing .env variables
```bash
ssh hostinger-vps
cd /root/stack
docker compose up -d <affected-service>   # Recreate with new env
docker compose logs --tail=20 <service>   # Verify env picked up
```

### Full deployment
```bash
# From local machine
rsync -avz stack/ hostinger-vps:/root/stack/
ssh hostinger-vps 'cd /root/stack && ./deploy.sh'
# deploy.sh: backup -> stop old -> generate secrets -> pull -> start -> migrate -> health check
```

### With `/rca`
When a service is down or unhealthy:
```
/rca "obsidian-brain returning 502 -- Neo4j connection refused"
/rca "rag-pipeline not generating new embeddings"
/rca "Langfuse traces not appearing -- ClickHouse timeout"
```

### With `debugger` Agent
For investigating service connectivity issues, delegate to debugger with Docker context.

### With `deployment-engineer` Agent
For Docker Compose changes, Caddy routing modifications, or systemd service management.

## Known Issues & Workarounds

| Issue | Workaround |
|-------|------------|
| obsidian-agent port conflict (8123 vs 8124) | Agent mapped to host 8124, brain to 8123. Caddy routes by path. |
| n8n MCP stdio mode | Container runs `tail -f /dev/null`; MCP invoked via `docker exec` |
| MinIO bucket creation on first start | Entrypoint `mkdir -p` creates all 7 buckets before server starts |
| Vault sync conflicts | Use `vault-sync.sh sync` (bidirectional) -- newer file wins |
| Neo4j APOC plugin | Requires `NEO4J_PLUGINS=["apoc"]` and unrestricted procedures config |
| Langfuse ClickHouse single-node | `CLICKHOUSE_CLUSTER_ENABLED=false` required (no replicas) |
