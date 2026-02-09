# PRP: Obsidian Ecosystem Hub Health Monitoring

**Date**: 2026-02-09
**Status**: Draft
**Complexity**: High (score 6+)
**Target Repo**: obsidian-ecosystem-hub

## Summary

Implement a health monitoring and alerting stack for the obsidian-ecosystem-hub VPS using Prometheus for metrics collection, Grafana for dashboards, and Alertmanager for notifications. This covers all 16 Docker services, the Caddy reverse proxy, MinIO storage, PostgreSQL (pgvector), Neo4j, and system-level metrics (CPU, memory, disk). Alerts route to Slack (existing integration) and optionally email.

## Why This Is Complex

- **16 services to instrument**: Each has different health check patterns (HTTP endpoints, TCP ports, process health)
- **Multiple metric types**: Docker container metrics, application-level metrics (FastAPI), database metrics (PostgreSQL, Neo4j), storage metrics (MinIO), system metrics
- **Dashboard design**: Need multiple dashboards for different audiences (overview, per-service, storage, AI/LLM costs)
- **Alert tuning**: Too many alerts cause fatigue; too few miss incidents. Need careful threshold selection
- **Integration with existing stack**: Must fit into existing docker-compose.yml without disrupting running services
- **Persistent state**: Prometheus TSDB and Grafana dashboards need persistent volumes and backup
- **MinIO single point of failure**: Monitoring must detect MinIO issues before data loss

## Context

### Current State
- **Monitoring**: None. Manual `docker compose ps` and `docker compose logs` only
- **Health checks**: Some Docker HEALTHCHECK directives in docker-compose.yml, but no collection or alerting
- **Alerting**: None. Service failures go unnoticed until manual check or user report
- **Metrics**: Langfuse tracks LLM costs but no infrastructure metrics
- **Observability stack**: Langfuse + ClickHouse already in docker-compose.yml (for LLM tracing, not infra monitoring)

### Pain Points (from needs analysis)
- No health monitoring/alerting (rated High impact)
- MinIO single point of failure — no way to detect storage issues
- Manual health checks only — problems discovered late
- No disk usage monitoring — risk of disk exhaustion from Docker logs and MinIO data
- Unknown OpenAI API costs for 133K vector embeddings

### VPS Infrastructure
| Property | Value |
|----------|-------|
| Host | hostinger-vps (148.230.95.154) |
| Stack path | /root/stack/ |
| Docker services | 16 containers |
| Caddy | System service (not Docker) |
| Public domains | obsidian.1215group.com, openwebui.1215group.com, n8n.1215group.com, flowise.1215group.com, langfuse.1215group.com, search.1215group.com, minio.1215group.com, s3.1215group.com |

### Existing Docker Services (all 16)
| Service | Type | Health Check Pattern |
|---------|------|---------------------|
| obsidian-agent | FastAPI | HTTP GET /health |
| obsidian-brain | FastAPI | HTTP GET /health |
| rag-pipeline | Background worker | Process alive + queue depth |
| postgres-vector | PostgreSQL + pgvector | pg_isready |
| neo4j | Graph database | HTTP GET :7474 |
| minio | Object storage | HTTP GET /minio/health/live |
| redis | Cache (Valkey) | valkey-cli ping |
| ollama | LLM runtime | HTTP GET /api/tags |
| open-webui | Web UI | HTTP GET / |
| n8n | Workflow engine | HTTP GET /healthz |
| n8n-mcp | MCP server | Process alive |
| flowise | LLM orchestrator | HTTP GET / |
| langfuse-web | Observability UI | HTTP GET / |
| langfuse-worker | Background worker | Process alive |
| clickhouse | Analytics DB | HTTP GET :8123/ping |
| searxng | Search engine | HTTP GET / |

### Docker Compose File
- Location: `stack/docker-compose.yml`
- Network: Default bridge network (services communicate by container name)
- Volumes: Named volumes for persistent data (postgres_data, neo4j_data, minio_data, etc.)

## Proposed Architecture

### New Services (added to docker-compose.yml)

```
prometheus:
  image: prom/prometheus:latest
  ports: 9090
  volumes:
    - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus

grafana:
  image: grafana/grafana:latest
  ports: 3001
  volumes:
    - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
    - grafana_data:/var/lib/grafana
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}

alertmanager:
  image: prom/alertmanager:latest
  ports: 9093
  volumes:
    - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml

node-exporter:
  image: prom/node-exporter:latest
  # System-level metrics (CPU, memory, disk, network)

cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  # Docker container metrics (CPU, memory, network per container)

postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  # PostgreSQL metrics (connections, query performance, pgvector stats)

minio-exporter:
  # MinIO has built-in Prometheus metrics at /minio/v2/metrics/cluster
  # No separate exporter needed — configure Prometheus to scrape MinIO directly
```

### Caddy Configuration
Add reverse proxy entries for monitoring UIs:
```
grafana.1215group.com {
    reverse_proxy grafana:3001
}
```

### Metrics Collection Architecture

```
                    ┌─────────────┐
                    │  Prometheus  │
                    │   (scrape)   │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐     ┌─────▼──────┐
   │ Node    │      │ cAdvisor  │     │ App Metrics │
   │Exporter │      │ (Docker)  │     │ (FastAPI)   │
   └─────────┘      └───────────┘     └────────────┘
   System metrics   Container metrics  /metrics endpoints
   CPU, RAM, Disk   Per-container      Request rate, latency
                    CPU, Memory        Error rate, queue depth
```

## Implementation Tasks

### Task 1: Create Monitoring Directory Structure
```
stack/monitoring/
├── prometheus.yml              # Prometheus config (scrape targets)
├── alert-rules.yml             # Prometheus alerting rules
├── alertmanager.yml            # Alertmanager config (Slack webhook)
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── prometheus.yml  # Auto-provision Prometheus datasource
    │   └── dashboards/
    │       └── dashboard.yml   # Auto-provision dashboard JSON
    └── dashboards/
        ├── overview.json       # Main overview dashboard
        ├── docker.json         # Per-container metrics
        ├── postgres.json       # PostgreSQL metrics
        ├── minio.json          # MinIO storage metrics
        └── fastapi.json        # FastAPI service metrics
```

### Task 2: Prometheus Configuration
**File**: `stack/monitoring/prometheus.yml`

Scrape targets:
1. `node-exporter:9100` — System metrics (CPU, memory, disk, network)
2. `cadvisor:8080` — Docker container metrics
3. `postgres-exporter:9187` — PostgreSQL metrics
4. `minio:9000/minio/v2/metrics/cluster` — MinIO built-in metrics
5. `obsidian-agent:8000/metrics` — FastAPI metrics (requires prometheus-fastapi-instrumentator)
6. `obsidian-brain:8000/metrics` — FastAPI metrics
7. `neo4j:2004/metrics` — Neo4j metrics endpoint

Scrape interval: 15s for infrastructure, 30s for application metrics

### Task 3: Instrument FastAPI Services
**Files**: `stack/obsidian-ai-agent/app/main.py`, `stack/obsidian-brain/app/main.py`

Add `prometheus-fastapi-instrumentator` to each service:
```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

This exposes `/metrics` endpoint with:
- Request count by method, path, status
- Request duration histogram
- Request size and response size
- In-progress requests

Add custom metrics:
- `rag_pipeline_queue_depth` — Number of pending documents to process
- `minio_vault_size_bytes` — Total vault storage usage
- `embedding_requests_total` — OpenAI API call count
- `embedding_cost_dollars` — Estimated embedding costs

### Task 4: Alert Rules
**File**: `stack/monitoring/alert-rules.yml`

Critical alerts (immediate notification):
| Alert | Condition | For |
|-------|-----------|-----|
| ServiceDown | Any container unhealthy | 2m |
| MinIODown | MinIO not responding | 1m |
| PostgresDown | PostgreSQL not accepting connections | 1m |
| DiskSpaceCritical | Disk usage > 90% | 5m |
| HighMemoryUsage | Memory usage > 90% | 5m |

Warning alerts (batched notification):
| Alert | Condition | For |
|-------|-----------|-----|
| HighErrorRate | 5xx rate > 5% for any service | 5m |
| SlowResponses | p95 latency > 5s | 10m |
| DiskSpaceWarning | Disk usage > 75% | 15m |
| PostgresConnectionsHigh | Active connections > 80% of max | 10m |
| MinIOStorageHigh | Bucket usage > 80% of quota | 30m |
| CertificateExpiringSoon | SSL cert expires in < 14 days | 1h |
| ContainerRestarting | Container restart count > 3 in 15m | 1m |

### Task 5: Alertmanager Configuration
**File**: `stack/monitoring/alertmanager.yml`

Routes:
- Critical alerts → Slack channel `#obsidian-alerts` (immediate)
- Warning alerts → Slack channel `#obsidian-alerts` (grouped, 15m batch)
- Resolved notifications → Same channel (so you know it recovered)

Slack integration:
- Use existing Slack app (obsidian-agent already has Slack integration)
- Create `SLACK_WEBHOOK_URL` secret for Alertmanager
- Rich message formatting with service name, alert severity, dashboard link

### Task 6: Grafana Dashboards

**Dashboard 1: Overview** (`overview.json`)
- Service health grid (all 16 services, green/red)
- System resources (CPU, memory, disk gauges)
- Request rate across all FastAPI services
- Error rate across all services
- Active alerts panel

**Dashboard 2: Docker Containers** (`docker.json`)
- CPU usage per container (time series)
- Memory usage per container (time series)
- Network I/O per container
- Container restart count
- Container uptime

**Dashboard 3: PostgreSQL** (`postgres.json`)
- Active connections vs max
- Query duration histogram
- Transaction rate
- pgvector index size and search latency
- Table sizes (top 10)
- Dead tuples and vacuum status

**Dashboard 4: MinIO Storage** (`minio.json`)
- Total storage used vs available
- Bucket sizes (vault, backups)
- Object count
- Read/write IOPS
- Network throughput
- Error rate

**Dashboard 5: FastAPI Services** (`fastapi.json`)
- Request rate by endpoint
- Response time p50/p95/p99
- Error rate by endpoint
- Request/response size
- In-progress requests

### Task 7: Update docker-compose.yml
Add monitoring services to existing `stack/docker-compose.yml`:
- prometheus, grafana, alertmanager, node-exporter, cadvisor, postgres-exporter
- Named volumes for persistence
- Network configuration (same network as existing services)
- Resource limits to prevent monitoring from consuming too many resources

### Task 8: Update Caddyfile
Add Grafana reverse proxy entry:
```
grafana.1215group.com {
    reverse_proxy grafana:3001
}
```

Consider: Should Prometheus and Alertmanager UIs be exposed publicly? Probably not — access via SSH tunnel or VPN only.

### Task 9: Update deploy.sh
Add monitoring service deployment:
1. Generate `GRAFANA_ADMIN_PASSWORD` if not set
2. Create monitoring directory structure
3. Start monitoring services after main stack
4. Verify Prometheus is scraping all targets
5. Verify Grafana dashboards are provisioned

### Task 10: Create `/obsidian-metrics` Command (optional)
A Claude Code command that SSHs to VPS and queries Prometheus API for quick metrics:
- Current service health summary
- Disk usage
- Error rates in last hour
- Active alerts

## Dependencies

- Docker Compose v2 (already available on VPS)
- Slack webhook URL for alerts
- DNS record for grafana.1215group.com (if exposing Grafana)
- `prometheus-fastapi-instrumentator` Python package added to obsidian-ai-agent and obsidian-brain
- Available disk space for Prometheus TSDB (~500MB-1GB for 15-day retention)
- Available memory for monitoring stack (~512MB total for all monitoring containers)

## Estimated Effort

| Task | Effort |
|------|--------|
| Monitoring directory structure | 30 min |
| Prometheus configuration | 1-2 hours |
| Instrument FastAPI services | 1-2 hours |
| Alert rules | 2-3 hours |
| Alertmanager configuration | 1 hour |
| Grafana dashboards (5 dashboards) | 4-6 hours |
| Update docker-compose.yml | 1 hour |
| Update Caddyfile and deploy.sh | 1 hour |
| Testing and iteration | 3-4 hours |
| **Total** | **~15-22 hours** |

## Acceptance Criteria

- [ ] Prometheus scrapes all 16 services + system metrics every 15-30s
- [ ] Grafana overview dashboard shows all service health at a glance
- [ ] Per-service dashboards show CPU, memory, network for each container
- [ ] PostgreSQL dashboard shows connections, query performance, pgvector stats
- [ ] MinIO dashboard shows storage usage, IOPS, errors
- [ ] FastAPI dashboard shows request rate, latency, error rate per endpoint
- [ ] Critical alerts fire to Slack within 2 minutes of service failure
- [ ] Warning alerts batch and fire to Slack within 15 minutes
- [ ] Resolved notifications appear in Slack when issues recover
- [ ] Prometheus data persists across container restarts (named volume)
- [ ] Grafana dashboards auto-provision on fresh deployment
- [ ] Monitoring stack uses < 512MB RAM and < 1GB disk
- [ ] deploy.sh handles monitoring service lifecycle

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Monitoring stack consumes too many VPS resources | Set resource limits in docker-compose.yml; use 15-day retention; compact TSDB |
| Alert fatigue from too many notifications | Start with critical alerts only; tune warning thresholds over 2 weeks |
| Prometheus scrape targets change when services restart | Use Docker service discovery (docker_sd_configs) instead of static targets |
| MinIO metrics endpoint requires authentication | Use MinIO admin credentials from existing .env |
| Grafana dashboards drift from provisioned JSON | Use provisioning mode that prevents manual edits, or accept drift |
| Neo4j metrics endpoint not available in Community edition | Fall back to container-level metrics from cAdvisor |
| FastAPI instrumentation adds latency | prometheus-fastapi-instrumentator adds < 1ms per request; negligible |

## References

- [Prometheus configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [MinIO Prometheus metrics](https://min.io/docs/minio/linux/operations/monitoring/collect-minio-metrics-using-prometheus.html)
- [PostgreSQL exporter](https://github.com/prometheus-community/postgres_exporter)
- [cAdvisor for Docker monitoring](https://github.com/google/cadvisor)
- [Node Exporter for system metrics](https://github.com/prometheus/node_exporter)
