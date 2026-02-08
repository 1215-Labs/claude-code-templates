---
name: cbass-context
description: Shared knowledge base for cbass slash commands — Docker Compose services, profiles, domains, glossary, and integration patterns
version: 1.0.0
category: infrastructure
user-invocable: false
related:
  commands: [cbass/cbass-status, cbass/cbass-logs, cbass/cbass-deploy]
  workflows: [bug-investigation]
---

# cbass Context

Shared context referenced by all `/cbass-*` commands. Do NOT invoke directly.

## Paths & Constants

| Variable | Value |
|----------|-------|
| `CBASS_DIR` | `/Users/mike/projects/cbass` |
| `COMPOSE_PROJECT` | `localai` |
| `ENTRY_POINT` | `start_services.py` |
| `DOMAIN` | `cbass.space` |
| `ENV_FILE` | `.env` (gitignored, copy from `env.example`) |
| `N8N_WORKFLOWS` | `n8n-tool-workflows/` |
| `N8N_BACKUP` | `n8n/backup/` |
| `FLOWISE_CHATFLOWS` | `flowise/` |
| `DOCS_DIR` | `docs/` |
| `DASHBOARD_DIR` | `dashboard/` |

## CLI Commands

```
# Orchestration
python start_services.py --profile <PROFILE> --environment <ENV>
  Profiles:  cpu | gpu-nvidia | gpu-amd | none
  Environments: private (all ports exposed) | public (80/443 only via Caddy)

# Docker Compose (project name: localai)
docker compose -p localai ps                         # Service status
docker compose -p localai logs -f <service>          # Follow logs
docker compose -p localai logs --tail=50 <service>   # Recent logs
docker compose -p localai restart <service>          # Restart one
docker compose -p localai up -d <service>            # Start one
docker compose -p localai down                       # Stop all
docker compose -p localai pull                       # Pull images

# Webhook-based container update
curl "https://update.cbass.space/hooks/update-container?token=cbass-update-secret-2026&container=<service>"
  Valid containers: open-webui, n8n, flowise, langfuse-web
```

## Service Inventory

| Service | Port(s) | Subdomain | Role | Healthcheck |
|---------|---------|-----------|------|-------------|
| **dashboard** | 3000 | dashboard.cbass.space | Next.js landing + auth | HTTP |
| **n8n** | 5678 | n8n.cbass.space | Workflow automation | HTTP |
| **open-webui** | 8080 | chat.cbass.space | ChatGPT-style LLM UI | HTTP |
| **flowise** | 3001 | flowise.cbass.space | No-code AI agent builder | HTTP |
| **ollama** | 11434 | — | Local LLM inference | HTTP |
| **kong** (Supabase) | 8000 | supabase.cbass.space | API gateway | — |
| **db** (Postgres) | 5432 | — | Primary DB + pgvector | pg_isready |
| **qdrant** | 6333/6334 | qdrant.cbass.space | Vector DB (HTTP+gRPC) | HTTP |
| **neo4j** | 7474/7687 | neo4j.cbass.space | Graph DB (HTTP+Bolt) | HTTP |
| **langfuse-web** | 3000 | langfuse.cbass.space | LLM observability UI | HTTP |
| **langfuse-worker** | 3030 | — | Background processing | — |
| **clickhouse** | 8123/9000 | — | Analytics DB | HTTP |
| **minio** | 9000/9001 | — | S3-compatible storage | — |
| **redis** | 6379 | — | Cache (Valkey 8) | redis-cli ping |
| **searxng** | 8080 | search.cbass.space | Meta search engine | HTTP |
| **caddy** | 80/443 | — | Reverse proxy + auto-TLS | — |
| **kali** | 6901 | kali.cbass.space | Security desktop (KasmWeb) | — |
| **updater** | 9000 | update.cbass.space | Webhook → container update | — |

Init services (run once on startup):
- `n8n-import` — imports workflows + credentials from `n8n/backup/`
- `ollama-pull-*` — pulls `qwen2.5:7b-instruct-q4_K_M` and `nomic-embed-text`

## Deployment Profiles

| Profile | Ollama Image | GPU Support | Use When |
|---------|-------------|-------------|----------|
| `cpu` | `ollama/ollama` | None | No GPU available |
| `gpu-nvidia` | `ollama/ollama` | NVIDIA CUDA | NVIDIA GPU (default) |
| `gpu-amd` | `ollama/ollama:rocm` | AMD ROCm | AMD GPU (Linux only) |
| `none` | — | — | External LLM API only |

| Environment | Ports Exposed | TLS | Use When |
|-------------|--------------|-----|----------|
| `private` | All service ports | No | Local development |
| `public` | 80, 443 only | Auto (Let's Encrypt) | Production/VPS |

## Subdomain Routing (Production)

All subdomains resolve to the same VPS IP. Caddy routes by hostname:

```
chat.cbass.space      → open-webui:8080
n8n.cbass.space       → n8n:5678
flowise.cbass.space   → flowise:3001
supabase.cbass.space  → kong:8000
dashboard.cbass.space → dashboard:3000
langfuse.cbass.space  → langfuse-web:3000
neo4j.cbass.space     → neo4j:7474
qdrant.cbass.space    → qdrant:6333
search.cbass.space    → searxng:8080
kali.cbass.space      → kali:6901
update.cbass.space    → updater:9000
```

## Domain Glossary

### AI/ML Terms
| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-Augmented Generation — query docs before generating answers |
| **Vector Store** | Database optimized for similarity search (Qdrant, pgvector) |
| **Embeddings** | Numerical representations of text for semantic search |
| **LLM** | Large Language Model — served locally via Ollama |
| **Agent** | Autonomous AI with tool access (built in n8n or Flowise) |
| **Chatflow** | Flowise visual workflow for AI agent chains |
| **Pipe** | Open WebUI custom function (see `n8n_pipe.py`) |

### Infrastructure Terms
| Term | Meaning |
|------|---------|
| **Profile** | Docker Compose variant selecting GPU support |
| **Environment** | Deployment mode: `private` (dev) or `public` (prod) |
| **Sparse Checkout** | Git optimization — downloads only `docker/` from Supabase repo |
| **Named Volume** | Docker-managed volume (not bind-mounted from host) |
| **Init Service** | Container that runs once on startup then exits |
| **Kong** | Supabase API gateway (not the penetration testing tool) |

### Data Terms
| Term | Meaning |
|------|---------|
| **pgvector** | PostgreSQL extension for vector similarity search |
| **Qdrant** | Dedicated vector database (HTTP port 6333, gRPC port 6334) |
| **Neo4j** | Graph database for relationship modeling (Bolt port 7687) |
| **ClickHouse** | Column-oriented analytics database (Langfuse backend) |
| **MinIO** | S3-compatible object storage (Langfuse blob store) |

## Known Issues & Workarounds

| Issue | Workaround |
|-------|------------|
| n8n MCP returns non-existent node types | Use n8n API directly, don't trust MCP node type info |
| Flowise upload failures | Uses named Docker volume; check `FLOWISE_FILE_SIZE_LIMIT` env var |
| Supabase pooler restarts | Known issue (GitHub #30210); restart `supabase-pooler` container |
| `.env` password cannot contain `@` | Use URL-encoded `%40` or avoid `@` in passwords |
| SearXNG first-run permissions | Script auto-handles `cap_drop` workaround |
| Supabase analytics won't start after password change | Delete `db-config` volume: `docker volume rm localai_db-config` |

## Integration Patterns

### With `/rca`
When a service is down or unhealthy:
```
/rca "n8n returning 502 — container restarting in loop"
/rca "Qdrant not responding on port 6333"
```

### With `debugger` Agent
For investigating service connectivity issues, delegate to debugger with Docker context.

### With `deployment-engineer` Agent
For Docker Compose changes, CI/CD workflow updates, or Caddy routing modifications.

### Service Dependency Chain
```
db (Postgres) ← n8n, kong, langfuse-web, langfuse-worker
redis ← n8n, langfuse-web, langfuse-worker
ollama ← open-webui, n8n (via webhook), flowise
clickhouse ← langfuse-web, langfuse-worker
minio ← langfuse-web, langfuse-worker
caddy ← all web-facing services (in public mode)
```

### Health Check Priority
When diagnosing issues, check in dependency order:
1. `db` (Postgres) — most services depend on it
2. `redis` — n8n and Langfuse depend on it
3. `ollama` — LLM services depend on it
4. Individual service that's failing
