# obsidian-ecosystem-hub Needs Analysis

## Executive Summary

The obsidian-ecosystem-hub is a centralized configuration repository for Claude Code/OpenCode AI development, providing reusable agents, commands, skills, and workflows. It doubles as a VPS deployment stack for a production Obsidian knowledge management system with 16 Docker services (AI services, databases, storage, observability). The repository is well-structured with comprehensive documentation, but has gaps in testing infrastructure, scattered Python service documentation, and hardcoded local paths throughout.

## Quick Reference
| Aspect | Details |
|--------|---------|
| Primary language | Python (FastAPI services) + Markdown (config) + Shell (deployment) |
| Framework | FastAPI + SQLAlchemy + Alembic + Pydantic |
| Build command | `docker compose build` (services) / N/A (config files) |
| Test command | `pytest` (Python services) / N/A (config validation) |
| Entry point | Docker Compose stack + Claude Code auto-discovery |
| Package manager | uv (Python) / Docker (services) |
| CI/CD | None detected (manual deployment via rsync/SSH) |
| Has CLI | Yes (shell scripts: deploy.sh, vault-sync.sh) |

## Architecture Overview

The repository has a dual-purpose architecture:

**1. Claude Code Configuration Library** (root level)
```
.claude/hooks/          # Auto-discovered lifecycle hooks (LSP validation, session init)
agents/                 # 13 AI sub-agents (code-reviewer, debugger, LSP specialists)
commands/workflow/      # 9 slash commands (/prime, /code-review, /onboarding)
skills/                 # 6 reusable skills (fork-terminal, LSP navigation, devlog)
workflows/              # 4 workflow chains (feature-development, bug-investigation)
rules/                  # 1 context-specific rule (feature-workflow)
```

**2. VPS Production Stack** (stack/ directory)
```
stack/
├── docker-compose.yml          # 16 services orchestration
├── Caddyfile                   # Reverse proxy + auto-HTTPS
├── deploy.sh                   # VPS deployment automation
├── obsidian-ai-agent/          # Slack/GPT capture service (FastAPI)
├── obsidian-brain/             # GraphRAG + Neo4j service (FastAPI)
└── scripts/vault-sync.sh       # rclone bidirectional vault sync
```

**Service Relationships:**
- MinIO S3 storage (central vault storage)
- obsidian-agent captures notes from Slack/ChatGPT → MinIO
- rag-pipeline watches MinIO, embeddings → PostgreSQL (133K vectors)
- obsidian-brain queries pgvector + Neo4j knowledge graph
- Langfuse observability for all AI calls
- Local vault ↔ MinIO sync via rclone

## Tech Stack Details

| Category | Technology | Config Location |
|----------|-----------|-----------------|
| **Python Services** | FastAPI 0.120+ | stack/obsidian-ai-agent/pyproject.toml |
| **Python Runtime** | 3.12+ | .python-version |
| **Package Manager** | uv (lockfile: uv.lock) | pyproject.toml |
| **ORM** | SQLAlchemy 2.0 + asyncpg | pyproject.toml dependencies |
| **Migrations** | Alembic 1.17+ | alembic.ini, alembic/ |
| **AI Framework** | pydantic-ai-slim[anthropic] | pyproject.toml |
| **Vector DB** | PostgreSQL + pgvector | docker-compose.yml (postgres-vector) |
| **Graph DB** | Neo4j 5 Community | docker-compose.yml (neo4j) |
| **Object Storage** | MinIO | docker-compose.yml (minio) |
| **Reverse Proxy** | Caddy v2.10+ | stack/Caddyfile |
| **LLM Platform** | Ollama + Open WebUI | docker-compose.yml |
| **Workflow Engine** | n8n + n8n-mcp | docker-compose.yml |
| **Observability** | Langfuse + ClickHouse | docker-compose.yml |
| **Search** | SearXNG | docker-compose.yml |
| **Type Checking** | mypy + pyright (strict) | pyproject.toml [tool.mypy] |
| **Linting** | Ruff | pyproject.toml [tool.ruff] |
| **Testing** | pytest + pytest-asyncio | pyproject.toml [tool.pytest] |
| **Vault Sync** | rclone | stack/scripts/vault-sync.sh |

## Workflow Discovery

### Build
**VPS Stack:**
```bash
# Build all services
cd stack && docker compose build

# Build specific service
docker compose build obsidian-agent

# Pull pre-built images
docker compose pull
```

**No build needed for Claude Code config** (Markdown files auto-discovered)

### Test
**Python Services:**
```bash
cd stack/obsidian-ai-agent
pytest                    # Run all tests
pytest -m integration     # Integration tests only
pytest --cov              # With coverage
```

**Type Checking:**
```bash
mypy app/
pyright
```

**Linting:**
```bash
ruff check .
ruff format .
```

**No automated tests for Claude Code config** (manual validation)

### Deploy
**VPS Deployment:**
```bash
# 1. Sync stack to VPS
rsync -avz stack/ hostinger-vps:/root/stack/

# 2. SSH and deploy
ssh hostinger-vps
cd /root/stack
./deploy.sh

# 3. Verify Caddy
systemctl status caddy
systemctl reload caddy

# 4. Check services
docker compose ps
docker compose logs -f
```

**Claude Code Config:**
```bash
# Option 1: Symlink to ~/.claude/ for global access
ln -s /path/to/obsidian-ecosystem-hub/agents/* ~/.claude/agents/
ln -s /path/to/obsidian-ecosystem-hub/skills/* ~/.claude/skills/

# Option 2: Work from repo (hooks auto-register from .claude/)
cd /path/to/obsidian-ecosystem-hub
# Commands/agents available via global symlinks
```

### Debug
**Service Logs:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f obsidian-agent

# Last N lines
docker compose logs --tail 100 langfuse-web
```

**Database Access:**
```bash
# PostgreSQL
docker exec postgres-vector psql -U postgres -d obsidian_agent

# Neo4j
docker exec neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD

# Redis
docker exec redis valkey-cli -a $REDIS_PASSWORD
```

**Health Checks:**
```bash
docker compose ps
docker inspect obsidian-agent --format='{{.State.Health.Status}}'
```

**Python Service Debug:**
```bash
# Local development
cd stack/obsidian-ai-agent
uv run uvicorn app.main:app --reload --log-level debug
```

## Domain Glossary

| Term | Meaning |
|------|---------|
| **Obsidian Vault** | Local markdown-based knowledge base (5,654 files, 84MB) synced to MinIO |
| **GraphRAG** | Graph + Retrieval-Augmented Generation (vector search + knowledge graph) |
| **obsidian-agent** | FastAPI service capturing notes from Slack Events API + ChatGPT GPT Actions |
| **obsidian-brain** | FastAPI service providing semantic search via pgvector + Neo4j queries |
| **rag-pipeline** | Background service watching vault files, generating embeddings, storing vectors |
| **MinIO S3** | Self-hosted S3-compatible object storage (central vault bucket) |
| **Caddy** | Reverse proxy with automatic HTTPS via Let's Encrypt |
| **n8n-mcp** | Model Context Protocol server for n8n workflow integration |
| **Langfuse** | LLM observability platform (traces, costs, evaluations) |
| **LSP Hooks** | Language Server Protocol-based code validation (pre/post edit checks) |
| **Sub-agent** | Claude Code agent spawned via Task tool for specialized work |
| **Skill** | Reusable Claude Code pattern invoked via /skill-name |
| **Command** | Quick workflow invoked via /command-name |
| **Workflow** | Multi-step sequence combining commands, agents, decision points |
| **Rule** | Context-specific instructions triggered by file globs |
| **Hook** | Automated check running on lifecycle events (SessionStart, PreToolUse, etc.) |

## Pain Points

| Category | Finding | Location | Impact |
|----------|---------|----------|--------|
| **Critical** | Hardcoded `/home/hammer/` paths throughout docs | CLAUDE.md, skills/devlog/SKILL.md, README | Breaks for other users (currently `/home/mdc159/`) |
| **Critical** | No automated tests for Claude Code config | agents/, commands/, skills/ | Risk of broken config, regression |
| **Critical** | Security: Recent credential leaks committed | DEVELOPMENT.md 2026-02-09 | Fixed but needs git history scrub |
| **High** | No CI/CD pipeline | Entire repo | Manual deployment, no validation gate |
| **High** | Missing test coverage for Python services | stack/obsidian-ai-agent/, stack/obsidian-brain/ | Unknow test coverage, risk |
| **High** | No health monitoring/alerting | VPS services | Manual checks only |
| **High** | Documentation drift | CLAUDE.md vs actual components | README lists 5 commands (9 exist), missing skills table |
| **Medium** | Duplicate hooks/ directory | .claude/hooks/ and root hooks/ (deleted 2026-02-09) | Maintenance confusion (now fixed) |
| **Medium** | No rollback mechanism | deploy.sh | Failed deployments require manual recovery |
| **Medium** | MinIO single point of failure | All services depend on MinIO | No backup/replication documented |
| **Medium** | Hardcoded VPS IP address | README, deployment scripts | Breaks if VPS changes |
| **Medium** | Python services lack proper logging config | obsidian-agent, obsidian-brain | Uses structlog but no rotation/retention |
| **Medium** | No integration tests for Slack/GPT capture | obsidian-agent | Only unit tests exist |
| **Low** | Missing /rca command | Referenced in docs but not implemented | Broken reference |
| **Low** | No agent-browser skill | Advertised in CLAUDE.md but missing | Broken reference |
| **Low** | Feature-workflow rule targets wrong repo | rules/feature-workflow.md (fixed 2026-02-09) | Was targeting oh-my-opencode paths |
| **Low** | No vault backup automation | rclone sync is manual | Risk of data loss |
| **Low** | No cost tracking for OpenAI API | Embeddings for 133K vectors | Unknown monthly costs |

## CLI Surface

### Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `deploy.sh` | Full VPS deployment (stop old, secrets, pull, migrate, start) | stack/deploy.sh |
| `vault-sync.sh` | rclone bidirectional vault sync (push/pull/sync/watch) | stack/scripts/vault-sync.sh |
| `deploy-to-vps.sh` | Legacy obsidian-agent deployment | stack/obsidian-ai-agent/deploy-to-vps.sh |

**deploy.sh workflow:**
1. Backup existing configs to /root/backups/YYYYMMDD_HHMMSS/
2. Stop systemd services (obsidian-agent, obsidian-brain)
3. Stop old docker compose stacks
4. Clean up old installations
5. Generate missing secrets (CLICKHOUSE_PASSWORD, MINIO_ROOT_PASSWORD, etc.)
6. Pull Docker images
7. Start services with `docker compose up -d`
8. Run Alembic migrations
9. Health check via `docker compose ps`

**vault-sync.sh modes:**
- `push` - Local → MinIO (one-way)
- `pull` - MinIO → Local (one-way)
- `sync` - Bidirectional (rclone bisync, newer wins)
- `watch` - Continuous push on inotify events

### Commands (Claude Code)

| Command | Purpose | Location |
|---------|---------|----------|
| `/prime` | Quick context (alias for /quick-prime) | commands/workflow/prime.md |
| `/quick-prime` | 4-point priming (docs, structure, stack, entry points) | commands/workflow/quick-prime.md |
| `/deep-prime "area" "focus"` | Deep dive into specific codebase area | commands/workflow/deep-prime.md |
| `/onboarding` | Full interactive new developer setup | commands/workflow/onboarding.md |
| `/code-review [scope]` | Parallel sub-agent code review + report | commands/workflow/code-review.md |
| `/coderabbit-helper` | CodeRabbit PR review helper | commands/workflow/coderabbit-helper.md |
| `/sync-reference` | Sync reference documentation | commands/workflow/sync-reference.md |
| `/ui-review` | UI/UX review workflow | commands/workflow/ui-review.md |
| `/all_skills` | List all available skills | commands/workflow/all_skills.md |

### Agents (Claude Code Sub-agents)

| Agent | Model | Purpose | Category |
|-------|-------|---------|----------|
| `code-reviewer` | inherit | Quality/security review after code changes | quality |
| `codebase-analyst` | sonnet | Pattern discovery, conventions, architecture | analysis |
| `context-manager` | sonnet | Session context for large projects | coordination |
| `debugger` | sonnet | Root cause analysis with parallel investigation | debugging |
| `deployment-engineer` | sonnet | CI/CD, containers, infrastructure | infrastructure |
| `library-researcher` | sonnet | Library docs and usage patterns | research |
| `technical-researcher` | sonnet | Deep technical research | research |
| `test-automator` | sonnet | Create/update test suites | quality |
| `mcp-backend-engineer` | sonnet | MCP server development (TypeScript SDK) | infrastructure |
| `n8n-mcp-tester` | sonnet | n8n MCP integration testing | quality |
| `dependency-analyzer` | haiku | Map module dependencies via LSP | analysis |
| `lsp-navigator` | haiku | Navigate code via LSP (go-to-def, references) | navigation |
| `type-checker` | haiku | Verify type safety via LSP | quality |

### Skills (Claude Code)

| Skill | Purpose | Category |
|-------|---------|----------|
| `fork-terminal` | Fork terminal to new window (Claude/Codex/Gemini) | productivity |
| `lsp-symbol-navigation` | Go-to-definition, hover, find-references via LSP | navigation |
| `lsp-dependency-analysis` | Map incoming/outgoing module dependencies | analysis |
| `lsp-type-safety-check` | Type validation after code changes | quality |
| `devlog` | Add structured entry to DEVELOPMENT.md + sync to VPS | documentation |
| `triage` | Issue triage and prioritization | productivity |

### Hooks (Claude Code)

| Hook Event | Trigger | Action | Timeout |
|------------|---------|--------|---------|
| SessionStart | Once per session | `session-init.py` - Check CLAUDE.md exists | 10s |
| PreToolUse (Edit) | Before each edit | `lsp-reference-checker.py` - Validate references | 30s |
| PostToolUse (Edit) | After each edit | `lsp-type-validator.py` - Type checking | 60s |
| Stop | Before stopping | Prompt: Verify completion, offer devlog entry | N/A |

## Recommendations

### High Priority

1. **Replace hardcoded paths with environment variables**
   - Add `OBSIDIAN_HUB_PATH` env var
   - Update CLAUDE.md, skills/devlog, README
   - Impact: Makes repo portable

2. **Add CI/CD pipeline**
   - GitHub Actions: lint, type-check, test on PR
   - Build Docker images on merge to main
   - Tag releases for deployment tracking
   - Impact: Catches issues before deployment

3. **Create config validation tests**
   - Test agent YAML frontmatter parsing
   - Test command argument handling
   - Test skill allowed-tools vs actual usage
   - Test hook timeouts and commands exist
   - Impact: Prevents broken Claude Code config

4. **Add Python test coverage tracking**
   - pytest-cov in CI
   - Require 80% coverage for new code
   - Integration tests for Slack/GPT capture
   - Impact: Reduces production bugs

5. **Implement health monitoring**
   - Prometheus + Grafana for metrics
   - Alerting for service failures
   - MinIO backup validation
   - Impact: Faster incident detection

6. **Document cost tracking**
   - OpenAI API usage for embeddings
   - Langfuse cost analysis
   - Set budget alerts
   - Impact: Prevents surprise bills

### Medium Priority

7. **Add rollback mechanism**
   - Tag Docker images by deploy date
   - Keep last 3 backups
   - `deploy.sh --rollback` command
   - Impact: Faster recovery from bad deploys

8. **Create MinIO backup automation**
   - Daily snapshots to external S3
   - Vault backup retention policy
   - Disaster recovery runbook
   - Impact: Prevents data loss

9. **Extract VPS IP to config**
   - Single .env file with VPS_HOST
   - Update all scripts
   - Impact: Easier VPS migration

10. **Add log rotation**
    - Docker log driver with max size
    - structlog file handlers with rotation
    - Impact: Prevents disk exhaustion

11. **Create integration test suite**
    - Test full capture pipeline (Slack → MinIO → RAG → pgvector)
    - Test GraphRAG queries
    - Test vault sync
    - Impact: Confidence in system behavior

12. **Fix missing references**
    - Implement /rca command (referenced by docs)
    - Add agent-browser skill (advertised in CLAUDE.md)
    - Update CLAUDE.md component tables (9 commands, 6 skills, 13 agents)
    - Impact: Removes broken references

### Low Priority

13. **Add cost optimization**
    - Cache OpenAI embeddings
    - Incremental RAG updates (not full reindex)
    - Impact: Reduces API costs

14. **Create local development guide**
    - Docker Compose for local stack
    - Mock Slack/GPT webhooks
    - Impact: Easier contributor onboarding

15. **Add schema migration tests**
    - Alembic upgrade/downgrade testing
    - Migration data integrity checks
    - Impact: Safer database changes

16. **Document secret rotation process**
    - How to rotate API keys
    - How to update VPS secrets
    - Impact: Security best practices

17. **Add API documentation**
    - FastAPI OpenAPI docs
    - Authentication flow diagrams
    - Impact: Easier third-party integration

## Raw Findings

### Repository Structure Analysis
- **Total files:** 489
- **Repository size:** 6.0MB
- **Documentation:** 1,290 lines across README.md (294), CLAUDE.md (237), DEVELOPMENT.md (759)
- **Recent activity:** Security audit 2026-02-09 removed committed credentials
- **Python services:** FastAPI + SQLAlchemy + Pydantic AI
- **Docker services:** 16 containers (AI, databases, storage, observability)
- **Configuration library:** 13 agents, 9 commands, 6 skills, 4 workflows, 1 rule, 4 hooks

### Code Quality Configuration
- **Type checking:** mypy strict mode + pyright strict mode
- **Linting:** Ruff with security checks (S), annotations (ANN), modernization (UP)
- **Testing:** pytest with asyncio mode, integration markers
- **Python version:** 3.12+ required
- **Package manager:** uv with lockfile

### Service Architecture
- **Public domains:** 8 services on *.1215group.com (Caddy auto-HTTPS)
- **Internal services:** 8 backend services
- **Storage:** MinIO S3 (vault bucket), PostgreSQL (133K vectors), Neo4j (knowledge graph)
- **Observability:** Langfuse + ClickHouse + Redis
- **AI:** Ollama + Open WebUI, n8n + n8n-mcp, Flowise

### Security Posture
- **Recent fixes:** Removed committed Google OAuth tokens, Slack secrets, DB passwords (2026-02-09)
- **Needs action:** Git history scrub, secret rotation
- **Good practices:** Docker secrets, .env templates, openssl random generation
- **Missing:** Secret rotation documentation, credential scanning in CI

### Testing Gaps
- No automated config validation (agents, commands, skills)
- No integration tests for capture pipeline
- No test coverage reporting
- No CI/CD validation gate

### Documentation Quality
- Comprehensive DEVELOPMENT.md with mermaid diagrams
- Detailed architecture documentation
- Some drift (component counts off)
- Hardcoded paths break portability

### Deployment Maturity
- Automated deploy.sh with backup/rollback prep
- No CI/CD (manual rsync + SSH)
- No health monitoring beyond manual checks
- No rollback automation

### Operational Concerns
- MinIO single point of failure (no documented backup)
- Unknown OpenAI API costs (133K vectors)
- Manual vault sync (no automation)
- No log rotation policy
