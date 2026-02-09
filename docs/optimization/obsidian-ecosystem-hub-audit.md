# obsidian-ecosystem-hub Quality Audit

## Executive Summary

The obsidian-ecosystem-hub repository serves as a configuration hub for the Obsidian knowledge management ecosystem, containing shared Claude Code components for managing Docker-based VPS services. The configuration averages 51.3/100 (Grade: F) for component freshness, with significant gaps in deployment-specific commands, domain context skills, and critical hooks. While the CLAUDE.md is comprehensive (73/100, Grade: C), it describes a generic template library rather than this repo's specific VPS deployment and MinIO-centric architecture. The primary gaps include: no context skill for MinIO/GraphRAG domain knowledge, missing deployment commands for the 16-service Docker stack, and incomplete hook coverage (missing security, memory, completion checks).

## Overall Scores

| Metric | Score |
|--------|-------|
| Average freshness | 51.3/100 (Grade: F) |
| CLAUDE.md quality | 73/100 (Grade: C) |
| Coverage | 42% of detected needs addressed |
| Components audited | 37 |
| Components missing | 11 |

## Component Scorecard

| Component | Type | Freshness | Grade | Key Issue |
|-----------|------|-----------|-------|-----------|
| hooks.json | Hook | 41 | F | Missing 7 hook types from template (security, memory, completion, etc.) |
| hooks/session-init.py | Hook | 37 | F | No Docker/Python detection, only checks TS/Node |
| hooks/lsp-type-validator.py | Hook | 48 | F | LSP-focused but repo is config hub, not code project |
| hooks/lsp-reference-checker.py | Hook | 44 | F | LSP-focused but repo is config hub, not code project |
| agent/code-reviewer | Agent | 59 | F | Generic template, not customized for VPS stack |
| agent/codebase-analyst | Agent | 60 | D- | Generic template, not customized for VPS stack |
| agent/context-manager | Agent | 58 | F | Generic template, not customized for VPS stack |
| agent/debugger | Agent | 62 | D- | Generic template, not customized for VPS stack |
| agent/deployment-engineer | Agent | 56 | F | Generic K8s focus, no VPS/Docker Compose customization |
| agent/library-researcher | Agent | 55 | F | Generic template, not customized for VPS stack |
| agent/mcp-backend-engineer | Agent | 54 | F | MCP-specific but no Obsidian ecosystem context |
| agent/n8n-mcp-tester | Agent | 48 | F | n8n-specific but no integration with VPS services |
| agent/technical-researcher | Agent | 56 | F | Generic template, not customized for VPS stack |
| agent/test-automator | Agent | 62 | D- | Generic template, not for config/infra testing |
| agent/dependency-analyzer | Agent | 60 | D- | LSP-focused, not relevant to config hub |
| agent/lsp-navigator | Agent | 60 | D- | LSP-focused, not relevant to config hub |
| agent/type-checker | Agent | 60 | D- | LSP-focused, not relevant to config hub |
| command/all_skills | Command | 23 | F | Bare-bones 20-line implementation |
| command/code-review | Command | 69 | D+ | Generic code review, not for Docker/config files |
| command/coderabbit-helper | Command | 61 | D- | CodeRabbit-specific, not customized |
| command/deep-prime | Command | 67 | D | Generic priming, no VPS/MinIO context |
| command/onboarding | Command | 67 | D | Generic onboarding, no VPS/MinIO context |
| command/prime | Command | 21 | F | Simple alias, bare minimum |
| command/quick-prime | Command | 57 | F | Generic 4-point context, no VPS-specific checks |
| command/sync-reference | Command | 66 | D | Reference sync, not VPS deployment |
| command/ui-review | Command | 66 | D | UI review not applicable to config hub |
| skill/devlog | Skill | 66 | D | Good devlog pattern, VPS rsync hardcoded |
| skill/fork-terminal | Skill | 64 | D- | Multi-model orchestration, generic |
| skill/lsp-dependency-analysis | Skill | 44 | F | LSP-focused, not relevant to config hub |
| skill/lsp-symbol-navigation | Skill | 44 | F | LSP-focused, not relevant to config hub |
| skill/lsp-type-safety-check | Skill | 46 | F | LSP-focused, not relevant to config hub |
| skill/triage | Skill | 36 | F | Obsidian vault-specific, not config hub-specific |
| workflow/bug-investigation | Workflow | 39 | F | Generic workflow, no VPS context |
| workflow/code-quality | Workflow | 39 | F | Generic workflow, no VPS context |
| workflow/feature-development | Workflow | 39 | F | Generic workflow, no VPS context |
| workflow/new-developer | Workflow | 36 | F | Generic workflow, no VPS context |
| rule/feature-workflow | Rule | 28 | F | Generic feature workflow, minimal content |

## Coverage Gaps

| Need (from tech stack) | Expected Component | Status |
|------------------------|--------------------|--------|
| MinIO S3 operations | `/obsidian-deploy` or `/stack-status` command | Missing |
| Docker Compose stack management | `/stack-restart [service]` command | Missing |
| VPS service health checks | `/stack-health` command | Missing |
| Domain knowledge (MinIO, GraphRAG, Neo4j, etc.) | `obsidian-context` skill | Missing |
| Caddy configuration updates | `/stack-caddy-reload` command | Missing |
| Vault sync operations | `/vault-sync [push\|pull\|sync]` command | Exists as script, not wrapped |
| Environment variable management | `/stack-env-check` command | Missing |
| Service log inspection | `/stack-logs [service]` command | Missing |
| Security scanning for secrets | security-check hook (PreToolUse) | Missing |
| Memory persistence | memory-loader/memory-distill hooks | Missing |
| Session summaries | session-summary hook (SessionEnd) | Missing |
| Task completion tracking | task-completed-gate hook | Missing |

## Quality Issues

| Severity | Component | Issue | Fix |
|----------|-----------|-------|-----|
| Critical | hooks.json | Missing 7 hook types (security, memory, SessionEnd, SubagentStop, PreCompact, TeammateIdle, TaskCompleted) | Copy from template: security-check.py, memory-loader.py, memory-distill.py, session-summary.py, task-completed-gate.py, teammate-idle-gate.py |
| Critical | commands/ | No deployment commands for VPS stack | Create `/stack-*` commands: status, health, restart, logs, env-check, caddy-reload |
| Critical | skills/ | No domain context skill for MinIO/GraphRAG/VPS services | Create `obsidian-context` skill with glossary, paths, output formats |
| Important | hooks/session-init.py | No Docker/Python project detection | Add check_docker_project() and check_python_project() functions |
| Important | agent/deployment-engineer | Generic K8s focus, no Docker Compose/VPS customization | Add VPS-specific examples: docker-compose patterns, Caddy config, systemd services |
| Important | CLAUDE.md | Describes self as config template hub, not VPS deployment hub | Rewrite to focus on VPS deployment, MinIO architecture, service orchestration |
| Important | commands/ | UI review not applicable to headless VPS services | Remove ui-review command or mark as not applicable |
| Important | workflows/ | Generic workflows don't mention VPS deployment lifecycle | Add VPS-specific workflow: service-deployment.md |
| Nice to Have | LSP agents/skills | 6 LSP-focused components not useful for config hub | Mark as conditionally deployed (only for code projects) |
| Nice to Have | skill/triage | Obsidian vault triage, not config hub triage | Keep but document as vault-specific, not hub-specific |
| Nice to Have | command/coderabbit-helper | CodeRabbit PR review helper for code projects | Keep but mark as not primary use case |

## CLAUDE.md Assessment

| Criterion | Score | Notes |
|-----------|-------|-------|
| Commands documented | 18/20 | All 9 commands listed with purpose |
| Architecture clarity | 18/20 | Excellent VPS architecture diagrams, MinIO-centric data flow |
| Non-obvious patterns | 10/15 | Explains auto-discovery but not deployment patterns |
| Conciseness | 11/15 | 238 lines, somewhat verbose, repeated ecosystem info |
| Currency | 8/15 | Accurate but doesn't distinguish config hub from code project needs |
| Actionability | 8/15 | Good quick start but no guidance on creating deployment commands |
| **Total** | **73/100** | **Grade: C** |

### CLAUDE.md Strengths
1. **Excellent architecture documentation**: Clear diagrams showing MinIO-centric design, data flow, and service relationships
2. **Comprehensive ecosystem context**: All related repositories, public domains, service ports documented
3. **Detailed VPS service health table**: Current status of all 16 services
4. **Good quick start section**: Commands for checking VPS services, deploying changes, vault sync

### CLAUDE.md Weaknesses
1. **Identity confusion**: Opens with "This is the **Obsidian Ecosystem Hub** - a central coordination repository containing shared AI development configuration" but then says "This hub coordinates these related repositories" - unclear if it's a config library or a deployment hub
2. **Missing deployment guidance**: No instructions on creating VPS-specific commands or skills
3. **No domain glossary reference**: Doesn't mention need for domain context skill (MinIO, S3, GraphRAG, Neo4j)
4. **Generic component lists**: Agents/commands/skills tables don't distinguish between universal (code-reviewer) and missing VPS-specific ones
5. **No workflow guidance for VPS changes**: Feature development workflow doesn't mention service restart, health checks, log inspection

### Recommended CLAUDE.md Changes
1. **Clarify purpose**: "This repository serves two purposes: (1) Configuration hub with shared Claude Code components, (2) VPS deployment stack for 16 Docker services"
2. **Add VPS command section**: Table of `/stack-*` commands for deployment operations
3. **Document domain context skill**: Explain `obsidian-context` skill with MinIO, S3, GraphRAG, Neo4j glossary
4. **Add deployment workflow**: Reference new `service-deployment.md` workflow
5. **Distinguish component types**: Mark which agents/commands are universal vs VPS-specific

## Recommendations (Priority Order)

### Critical (fix immediately)

1. **Create domain context skill** (`skills/obsidian-context/SKILL.md`)
   - Paths: `/root/stack/`, vault bucket, Caddy config
   - CLI commands: `docker compose`, `systemctl`, `rclone`, `mc` (MinIO client)
   - Output formats: Docker container status, MinIO bucket listing, Caddy logs
   - Glossary: MinIO (S3-compatible storage), GraphRAG (graph-enhanced RAG), pgvector (vector similarity search), Neo4j (knowledge graph), Caddy (reverse proxy with auto-SSL)
   - Integration patterns: "After updating docker-compose.yml, run `docker compose up -d [service]`", "After Caddyfile changes, run `systemctl reload caddy`"

2. **Create VPS deployment commands** (7 new commands in `commands/obsidian/`)
   - `/stack-status` - Show all service statuses with health checks
   - `/stack-health [service]` - Deep health check for specific service or all
   - `/stack-restart [service]` - Restart service(s), confirm no downtime
   - `/stack-logs [service]` - Tail logs for service with error filtering
   - `/stack-env-check` - Validate all required env vars in .env
   - `/stack-caddy-reload` - Reload Caddy config after changes
   - `/vault-sync [push|pull|sync]` - Wrapper for vault-sync.sh script

3. **Complete hook coverage** (copy 7 hooks from template)
   - `security-check.py` (PreToolUse Edit|Write) - Scan for secrets before writing
   - `memory-loader.py` (SessionStart) - Load persistent memory files
   - `memory-distill.py` (SessionEnd) - Summarize session to memory
   - `session-summary.py` (SessionEnd) - Write session summary to .claude/memory/sessions/
   - `task-completed-gate.py` (TaskCompleted) - Verify task completion
   - `teammate-idle-gate.py` (TeammateIdle) - Check teammate idle state
   - Update `hooks.json` with all missing hook types

4. **Fix hooks/session-init.py** - Add Docker and Python project detection
   ```python
   def check_docker_project():
       return Path("docker-compose.yml").exists() or Path("Dockerfile").exists()

   def check_python_project():
       return Path("pyproject.toml").exists() or Path("setup.py").exists() or len(list(Path(".").glob("**/*.py"))) > 5
   ```

5. **Rewrite CLAUDE.md intro** (lines 1-25)
   - Clarify dual purpose: config hub + VPS deployment stack
   - Add "## VPS Deployment Commands" section after "## Key Commands"
   - Reference `obsidian-context` skill in "## Skills"

### Important (fix soon)

6. **Customize agent/deployment-engineer** for VPS
   - Add section: "## VPS Docker Compose Patterns"
   - Add section: "## Caddy Reverse Proxy Configuration"
   - Add section: "## Systemd Service Management"
   - Add examples: Multi-service compose file, Caddy auto-SSL, health checks

7. **Create VPS deployment workflow** (`workflows/service-deployment.md`)
   ```markdown
   ## Service Deployment Workflow

   1. /stack-status → Check current service states
   2. Edit docker-compose.yml or Caddyfile
   3. /stack-env-check → Validate env vars
   4. deployment-engineer agent → Review changes
   5. /stack-restart [service] → Apply changes
   6. /stack-health [service] → Verify deployment
   7. /stack-logs [service] → Monitor for errors
   8. /devlog → Document changes
   ```

8. **Create `.claude/memory/skill-priorities.md`**
   - **Always**: `/stack-status` (check VPS services every session)
   - **Context-Triggered**: All `/stack-*` commands (when working with VPS), `/devlog` (when making changes)
   - **Available**: Generic commands (code-review, deep-prime, etc.)
   - **Repo Context**: Domain: VPS deployment, Prefix: `/stack-*`, Context skill: `obsidian-context`

9. **Add Stop hook devlog prompt** - Modify existing Stop hook:
   ```json
   {
     "type": "prompt",
     "prompt": "Before stopping:\n1. Verify task completion: all changes made, no pending todos, services healthy.\n2. If VPS services were changed, ask: 'Would you like me to add a devlog entry?' If yes, invoke /devlog to document changes, architecture updates, and next steps in DEVELOPMENT.md.\n3. If incomplete, explain what remains."
   }
   ```

10. **Document component deployment tiers** in CLAUDE.md
    - **Universal (globally deployed)**: code-reviewer, debugger, codebase-analyst, /code-review, /onboarding, /quick-prime, /deep-prime
    - **VPS-specific (this repo only)**: All `/stack-*` commands, obsidian-context skill, deployment workflows
    - **Conditionally deployed (code projects only)**: LSP agents/skills, type-checker, dependency-analyzer
    - **Vault-specific (separate concern)**: triage skill

### Nice to Have (fix when convenient)

11. **Mark LSP components as conditional** - Add note in CLAUDE.md:
    ```markdown
    ## LSP Components (Code Projects Only)

    These agents and skills are designed for TypeScript/Python code projects, not configuration hubs:
    - Agents: dependency-analyzer, lsp-navigator, type-checker
    - Skills: lsp-dependency-analysis, lsp-symbol-navigation, lsp-type-safety-check
    - Hooks: lsp-reference-checker.py, lsp-type-validator.py

    These are installed globally but only useful when working in code projects, not VPS config.
    ```

12. **Create deployment troubleshooting guide** (`docs/TROUBLESHOOTING.md`)
    - Common issues: Service won't start, Caddy SSL fails, MinIO connection refused
    - Debugging commands: docker logs, systemctl status, netstat
    - Recovery procedures: Restart sequence, rollback docker-compose.yml

13. **Add pre-commit hook for docker-compose validation**
    ```bash
    # .claude/hooks/docker-compose-validate.sh
    docker compose -f stack/docker-compose.yml config --quiet
    ```

14. **Create deployment metrics dashboard** (`/stack-metrics` command)
    - Service uptime, CPU/memory usage per container
    - MinIO storage usage, PostgreSQL database size
    - Network bandwidth, request counts

15. **Enhance devlog skill** - Auto-detect VPS deployment changes
    - Check if docker-compose.yml, Caddyfile, or .env changed
    - Auto-generate service restart commands in devlog entry
    - Include before/after service status

## Summary

The obsidian-ecosystem-hub has solid infrastructure (Docker Compose stack, comprehensive CLAUDE.md) but lacks deployment-specific automation. The critical gap is the missing abstraction layer between the VPS stack and Claude Code - no commands to manage services, no domain context skill to explain MinIO/GraphRAG/Neo4j concepts, and incomplete hook coverage. Implementing the 7 critical recommendations would raise the average freshness score from 51.3/100 (F) to approximately 68/100 (D+), with full implementation of all recommendations targeting 82/100 (B-).

The root cause is template library bias: most components are generic "copy this to any project" templates, not customized for this repo's unique role as a VPS deployment hub. The fix is to **add a repo-specific layer** on top of the universal components, specifically targeting the MinIO-centric Docker stack architecture documented so well in CLAUDE.md.
