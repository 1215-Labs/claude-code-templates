# Optimization Plan for obsidian-ecosystem-hub

## Mode: audit

## Analysis Summary
- **Sonnet (Gemini fallback)** found: 17 needs across architecture, deployment, domain knowledge, testing, CI/CD, documentation
- **Sonnet (Codex fallback)** found: 48 issues, avg freshness score: 51.3/100
- **Models used**: Sonnet (Gemini fallback) + Sonnet (Codex fallback)

## Upgrade Tasks (9 total)

### config-upgrader (3 tasks, no blockers — starts immediately)

| # | Task | Impact | Effort |
|---|------|--------|--------|
| T1 | Create `obsidian-context` skill — domain glossary (MinIO, GraphRAG, Neo4j, pgvector, Caddy), VPS paths, CLI commands, service relationships, integration patterns | High | 3 |
| T2 | Complete hook coverage — add security-check, memory-loader, memory-distill, session-summary, uncommitted-check hooks; update hooks.json; fix session-init.py for Docker/Python detection | High | 2 |
| T3 | Register obsidian-ecosystem-hub in MANIFEST.json and REGISTRY.md | Low | 1 |

### command-builder (3 tasks, blocked by T1 context skill)

| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
| T4 | Create 7 VPS commands: `/obsidian-status`, `/obsidian-health`, `/obsidian-restart`, `/obsidian-logs`, `/obsidian-env-check`, `/obsidian-caddy-reload`, `/obsidian-vault-sync` | High | 3 | T1 |
| T5 | Create VPS deployment workflow: `service-deployment.md` chaining status → edit → env-check → restart → health → logs → devlog | Medium | 2 | T1 |
| T6 | Generate PRPs for CI/CD pipeline (GitHub Actions) and health monitoring (Prometheus+Grafana) | Medium | 2 | — |

### docs-finalizer (3 tasks, blocked by T4, T5)

| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
| T7 | Rewrite CLAUDE.md — clarify dual purpose (config hub + VPS stack), add VPS Commands section, reference obsidian-context skill, fix hardcoded paths | High | 2 | T4, T5 |
| T8 | Generate `skill-priorities.md` — always: `/obsidian-status`; context-triggered: `/obsidian-*`, `/devlog`; available: generic commands | Medium | 1 | T4, T5 |
| T9 | Validate all components: cross-references, MANIFEST consistency, symlink integrity, hook configuration | Low | 1 | T7, T8 |

### Deferred (PRPs — complex gaps for later)

| PRP | Why Complex | Effort Est |
|-----|-------------|------------|
| CI/CD pipeline (GitHub Actions) | Multi-environment workflow, Docker build, test matrix, deployment automation | 5+ |
| Health monitoring (Prometheus + Grafana) | Dashboard design, alert rules, service instrumentation, Docker integration | 6+ |

## Target Repository
- Path: /home/mdc159/projects/obsidian-ecosystem-hub
- Templates: /home/mdc159/projects/claude-code-templates

## Key Files
- Needs analysis: docs/optimization/obsidian-ecosystem-hub-needs.md
- Quality audit: docs/optimization/obsidian-ecosystem-hub-audit.md
