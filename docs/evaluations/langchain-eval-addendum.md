# Addendum: The Self-Improving Agent Mesh

**Date:** 2026-02-12
**Context:** Incorporating OpenClaw deep dive + Claude Agent SDK + Google ADK + LangGraph

---

## The Insight We're Missing

The original evaluation treated this as "extract patterns from LangChain." But we have **four untapped weapons** sitting right here:

1. **OpenClaw's memory system** — the most architecturally innovative persistent memory we've seen, with a pre-compaction flush pattern, hybrid search, auto-capture, and a v2 vision (Retain/Recall/Reflect) that maps perfectly to Claude Code hooks
2. **Claude Agent SDK** (`/new-sdk-app` plugin) — can build **persistent deployed agents as services**, not just ephemeral Claude Code sessions
3. **Google ADK** — multi-agent orchestration with evaluation framework, 100+ GCP connectors, and Vertex AI managed deployment
4. **LangGraph** (just added as submodule) — the reflection/self-critique pattern that research says gives 15-30% improvement

We've been thinking about this as a **development tool improvement**. The real play is an **always-on agent mesh** — persistent agents deployed as services that continuously improve the development environment.

---

## Architecture: The Agent Mesh

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   TIER 1: DEVELOPMENT SESSIONS (Ephemeral — Claude Code)                │
│   ═══════════════════════════════════════════════════════                │
│                                                                         │
│   You sit here. Claude Code (Opus 4.6) + 22 agents + fork-terminal     │
│   + slash commands. Human-in-the-loop. Sessions last 1-2 hours.        │
│                                                                         │
│   NEW: OpenClaw-style hooks                                             │
│   • PreCompact flush → save durable memories before context lost        │
│   • Stop hook → auto-capture decisions/preferences/entities             │
│   • SessionStart → inject recent memory + auto-recall                   │
│   • PostToolUse → structured traces to postgres-vector                  │
│                                                                         │
│   Every session generates: traces, decisions, patterns, skills          │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ traces + memory writes
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   TIER 2: PERSISTENT AGENTS (Always-On — Agent SDK + Google ADK)        │
│   ══════════════════════════════════════════════════════════════         │
│                                                                         │
│   These run 24/7 on the VPS (148.230.95.154) as Docker services.       │
│   Built with /new-sdk-app (Claude Agent SDK) or Google ADK.             │
│   They NEVER sleep. They're the autonomous improvement engine.          │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │  SESSION ANALYZER (Claude Agent SDK — Python)                 │     │
│   │  • Watches session_traces table in postgres                   │     │
│   │  • Nightly: analyzes tool call patterns, success/failure      │     │
│   │  • Generates structured improvement proposals                 │     │
│   │  • Uses LangGraph REFLECTION: generate → critique → revise    │     │
│   │  • Outputs: improvements.json with confidence scores          │     │
│   │  Deployed: Docker container, connects to postgres-vector      │     │
│   └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │  MEMORY CURATOR (Claude Agent SDK — Python)                   │     │
│   │  • Implements OpenClaw's Retain/Recall/Reflect loop           │     │
│   │  • Daily: normalizes session logs → typed facts               │     │
│   │    W (world facts), B (biographical), O(c=0.95) (opinions)    │     │
│   │  • Weekly: consolidates → updates entity pages, prunes stale  │     │
│   │  • Monthly: meta-consolidation (summaries of summaries)       │     │
│   │  • Manages bank/ directory:                                   │     │
│   │    bank/world.md, bank/experience.md, bank/opinions.md        │     │
│   │    bank/entities/Mike.md, bank/entities/openclaw.md           │     │
│   │  Deployed: Docker container, full memory write access          │     │
│   └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │  RAG OPTIMIZER (Google ADK — Gemini 2.5 Pro)                  │     │
│   │  • Uses Gemini's 1M context to ingest full Obsidian vault     │     │
│   │  • Evaluates retrieval quality: did the RAG return the right  │     │
│   │    docs for recent queries? (from session traces)             │     │
│   │  • Tunes: chunk sizes, overlap, embedding model, weights      │     │
│   │  • Proposes retriever config changes with A/B test results    │     │
│   │  • ADK evaluation framework scores each config variant        │     │
│   │  Deployed: Cloud Run or Docker, calls Gemini API              │     │
│   └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
│   ┌───────────────────────────────────────────────────────────────┐     │
│   │  SKILL GENERATOR (Claude Agent SDK — TypeScript)              │     │
│   │  • Watches for recurring successful tool sequences in traces  │     │
│   │  • Identifies patterns: "when user asks X, these 5 tools      │     │
│   │    are always called in this order with 90%+ success"         │     │
│   │  • Generates new SKILL.md files from these patterns           │     │
│   │  • Voyager-inspired: skill library grows over time            │     │
│   │  • Creates PR with new skill + test cases                     │     │
│   │  Deployed: Docker container, git write access                  │     │
│   └───────────────────────────────────────────────────────────────┘     │
│                                                                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ reads + writes
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   TIER 3: SHARED STATE (postgres-vector + obsidian-brain + git)         │
│   ═════════════════════════════════════════════════════════════          │
│                                                                         │
│   postgres-vector @ 148.230.95.154                                      │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │ session_traces    — every tool call from every session       │       │
│   │ agent_metrics     — aggregated performance by agent/date     │       │
│   │ skill_library     — Voyager-style reusable patterns         │       │
│   │ memory_bank       — typed facts (W/B/O) with embeddings     │       │
│   │ improvement_log   — what was proposed, applied, rolled back  │       │
│   │ retrieval_evals   — RAG quality scores over time             │       │
│   └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│   ~/projects/claude-memory/   — git-tracked markdown (source of truth)  │
│   ├── MEMORY.md               — curated long-term memory               │
│   ├── bank/                   — OpenClaw v2 typed memory (NEW)         │
│   │   ├── world.md            — objective facts                        │
│   │   ├── experience.md       — what we've done (first-person)         │
│   │   ├── opinions.md         — preferences with confidence scores     │
│   │   └── entities/           — per-entity knowledge pages             │
│   ├── sessions/               — daily logs                             │
│   └── projects/               — per-project context                    │
│                                                                         │
│   obsidian-brain — knowledge management (vault sync with MinIO S3)      │
│   n8n — orchestration (triggers, webhooks, scheduled workflows)         │
│   git — version control for all memory + agent configs                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Heartbeat: Keeping the Mesh Alive

The mesh isn't useful if agents silently die at 3am. Inspired by OpenClaw's maintenance timers (tick ~10s, health ~60s, cleanup ~60s), every Tier 2 agent gets a heartbeat — and there's a dedicated daemon that orchestrates them all.

### Heartbeat Daemon

A single lightweight Python asyncio service (~200 LOC, ~20MB RAM) that runs alongside the Tier 2 agents:

```python
# heartbeat.py — the mesh's nervous system
import asyncio, httpx, docker
from datetime import datetime, timedelta

INTERVALS = {
    "tick":    10,    # keep-alive ping to all agents
    "health":  60,    # deep probe: endpoint + postgres + memory bank
    "pulse":  300,    # flush aggregated metrics to postgres
    "rhythm": 3600,   # trigger memory consolidation check
}

AGENTS = {
    "session-analyzer": {"port": 8081, "health": "/health"},
    "memory-curator":   {"port": 8082, "health": "/health"},
    "rag-optimizer":    {"port": 8083, "health": "/health"},
    "skill-generator":  {"port": 8084, "health": "/health"},
}

async def tick():
    """Keep-alive: lightweight ping, track last-seen timestamp."""
    async with httpx.AsyncClient() as client:
        for name, cfg in AGENTS.items():
            try:
                r = await client.get(f"http://{name}:{cfg['port']}/ping", timeout=5)
                await update_heartbeat(name, "alive", r.elapsed.total_seconds())
            except Exception:
                await update_heartbeat(name, "unreachable", None)

async def health():
    """Deep probe: agent health + postgres + memory bank integrity."""
    results = {}
    # Agent endpoints
    async with httpx.AsyncClient() as client:
        for name, cfg in AGENTS.items():
            try:
                r = await client.get(
                    f"http://{name}:{cfg['port']}{cfg['health']}", timeout=10
                )
                results[name] = r.json()
            except Exception as e:
                results[name] = {"status": "down", "error": str(e)}
                await auto_restart(name)  # Docker API restart

    # Postgres connectivity
    results["postgres"] = await check_postgres()

    # Memory bank file integrity
    results["memory_bank"] = await check_memory_bank()

    # Alert on anomalies
    down = [k for k, v in results.items() if v.get("status") == "down"]
    if down:
        await alert_n8n(f"Agents down: {', '.join(down)}")

    return results

async def pulse():
    """Flush: aggregate agent_metrics from in-memory counters to postgres."""
    for name in AGENTS:
        metrics = await collect_agent_metrics(name)
        await flush_to_postgres("agent_metrics", metrics)

async def rhythm():
    """Consolidation trigger: check if memory needs weekly/monthly rollup."""
    last_consolidation = await get_last_consolidation()
    if datetime.now() - last_consolidation > timedelta(days=7):
        await trigger_memory_curator("weekly_consolidation")
    if datetime.now().day == 1:  # First of month
        await trigger_memory_curator("monthly_meta_consolidation")

async def auto_restart(agent_name: str):
    """Restart dead agent via Docker API, max 3 restarts per hour."""
    client = docker.from_env()
    container = client.containers.get(f"mesh-{agent_name}")
    container.restart(timeout=30)
    await alert_n8n(f"Auto-restarted {agent_name}")

# /status endpoint — Tier 1 reads this on SessionStart
async def status_handler(request):
    """Returns mesh health for injection into Claude Code sessions."""
    return {
        "agents": {name: await get_last_heartbeat(name) for name in AGENTS},
        "postgres": await check_postgres(),
        "last_improvement": await get_last_improvement(),
        "skills_count": await count_skills(),
        "memory_last_consolidated": await get_last_consolidation(),
    }
```

### The Four Rhythms

| Rhythm | Interval | What it does | Failure action |
|--------|----------|-------------|----------------|
| **tick** | ~10s | Ping all agents, update last-seen | Log miss, alert after 3 consecutive |
| **health** | ~60s | Deep probe endpoints + postgres + memory bank | Auto-restart dead agents, n8n alert |
| **pulse** | ~5min | Flush in-memory metrics to postgres | Buffer locally, retry next pulse |
| **rhythm** | ~1hr | Check if memory consolidation is due | Queue for next cycle |

### Tier 1 Integration

When a Claude Code session starts, the `SessionStart` hook hits the heartbeat's `/status` endpoint:

```json
{
  "hooks": [{
    "event": "SessionStart",
    "type": "prompt",
    "prompt": "Check mesh status at http://148.230.95.154:8080/status. Report any agents that are down. Inject the latest improvement proposal and skills count into your working context."
  }]
}
```

This means every session starts **knowing the state of the entire mesh** — which agents are healthy, what was last improved, how many skills exist. The development environment is self-aware.

### Docker Compose Addition

```yaml
# Added to existing VPS docker-compose.yml
mesh-heartbeat:
  build: ./heartbeat
  restart: unless-stopped
  ports:
    - "8080:8080"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock  # for auto-restart
  environment:
    - POSTGRES_URL=postgresql://mesh:${MESH_DB_PASS}@postgres:5432/mesh
    - N8N_WEBHOOK_URL=http://n8n:5678/webhook/mesh-alert
  depends_on:
    - postgres
    - session-analyzer
    - memory-curator
    - rag-optimizer
    - skill-generator
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/ping"]
    interval: 30s
    timeout: 5s
    retries: 3
```

---

## Why This is Different

### Before (Current State)
- Claude Code sessions are ephemeral — improvements happen manually
- Memory is flat markdown files — no structured recall
- No persistent agents — everything stops when you close the terminal
- ADK plugins sit unused — `/new-sdk-app` has never been called
- OpenClaw's best patterns are documented but not implemented
- **No visibility into agent health** — if something breaks, you don't know until it matters

### After (Agent Mesh + Heartbeat)
- **4 persistent agents** run 24/7, analyzing and improving autonomously
- **Heartbeat daemon** keeps everything alive — auto-restarts, health probes, alerting
- **OpenClaw's memory v2** gives structured memory with types, confidence, entities
- **Every session feeds the mesh** — traces become training data for improvement
- **Every session starts self-aware** — SessionStart injects mesh health + latest improvements
- **Skills grow automatically** — Voyager pattern generates new SKILL.md files
- **RAG improves itself** — Google ADK agent tunes retrieval based on actual query results
- **LangGraph reflection** makes improvement proposals higher quality (multi-pass critique)
- **Nothing silently dies** — heartbeat detects failures in <60s, auto-restarts, alerts via n8n

---

## What OpenClaw Adds (Previously Missing)

The original LangChain evaluation missed these critical OpenClaw patterns:

### 1. Pre-Compaction Memory Flush (HIGHEST VALUE)

OpenClaw's most innovative pattern. From our deep dive (Part VII, §7.3):

> Before context compaction occurs, a silent agentic turn triggers that prompts the model to save durable knowledge. If nothing to save, responds with NO_REPLY. User never sees this.

**Implementation for Claude Code** (from OpenClaw's adoption guide):
```json
{
  "hooks": [{
    "event": "PreCompact",
    "type": "prompt",
    "prompt": "Session context is about to be compacted. Review the conversation for important decisions, preferences, facts, or context that should persist. Write anything worth remembering to ~/projects/claude-memory/sessions/$(date +%Y-%m-%d).md. If nothing needs saving, do nothing."
  }]
}
```

This is a **zero-code, immediate win**. Add it to hooks.json today.

### 2. Auto-Capture with Regex Triggers

From OpenClaw's memory-lancedb plugin:
```
/remember|prefer|decided|always|never|important/i → capture
```

Categories: `[DECISION]`, `[PREFERENCE]`, `[FACT]`, `[ENTITY]`
Max 3 captures per conversation. 10-500 chars. Skip system-generated content.

### 3. Retain/Recall/Reflect Loop (Memory v2)

OpenClaw's roadmap for structured memory:
- **Retain**: End of day, normalize daily logs into typed facts (W/B/O prefixes)
- **Recall**: Queries supporting lexical + entity + temporal + opinion search
- **Reflect**: Scheduled job updates entity pages, adjusts opinion confidence

This is what the **Memory Curator** persistent agent implements.

### 4. Hybrid Search Algorithm

OpenClaw's proven configuration:
- Vector weight: 0.7, BM25 weight: 0.3
- Min score: 0.35, max results: 6
- Chunk size: 400 tokens, overlap: 80 tokens
- FTS5 query: AND-joined quoted terms

This replaces the "extract ensemble retriever from LangChain" recommendation with a **proven configuration from a production system we've already analyzed deeply**.

---

## What the ADKs Add (Previously Unused)

### Claude Agent SDK — The Deployment Vehicle

We have `/new-sdk-app` installed. We've never used it. Here's what it unlocks:

```bash
# Create the Session Analyzer agent
/new-sdk-app session-analyzer

# → Language: Python
# → Agent type: Data analysis agent (trace analysis)
# → Starting point: Basic agent with common features
# → Generates: session-analyzer/ with main.py, requirements.txt, .env
```

Then customize `main.py`:
```python
from claude_agent_sdk import Agent, Tool

analyzer = Agent(
    model="claude-sonnet-4-5",  # Sonnet for cost efficiency
    system_prompt="""You analyze Claude Code session traces stored in
    postgres-vector. Identify patterns, failures, and improvement
    opportunities. Use the reflection pattern: generate analysis,
    critique it, revise, output final recommendations.""",
    tools=[
        Tool(name="query_traces", fn=query_postgres_traces),
        Tool(name="write_improvement", fn=write_improvement_proposal),
        Tool(name="create_pr", fn=create_github_pr),
    ],
    permissions={"allow": ["query_traces", "write_improvement", "create_pr"]},
)
```

Deploy as Docker service on VPS alongside the other 16 containers.

### Google ADK — The Evaluation Engine

Google ADK's killer feature for us: **built-in evaluation framework**.

```python
from google.adk import LlmAgent, AgentEvaluator

rag_optimizer = LlmAgent(
    model="gemini-2.5-pro",
    instruction="""Evaluate RAG retrieval quality. For each query-result
    pair, score relevance 0-1. Suggest parameter adjustments.""",
    tools=[google_search, query_postgres],
)

# Evaluate with test dataset
results = AgentEvaluator.evaluate(
    agent=rag_optimizer,
    test_data="rag_eval_dataset.json",  # Generated from session traces
)
# → Scores each retrieval, identifies worst-performing queries
# → Proposes chunk_size, overlap, weight adjustments
```

ADK also gives us: hierarchical agent transfers (agent-to-agent handoff), parallel execution pipelines, and 100+ GCP connectors if we ever want BigQuery/AlloyDB integration.

---

## Revised Implementation Plan

### Phase 0: Immediate Wins (Today — 2 hours)

**Zero-code hooks from OpenClaw adoption guide:**

```json
// Add to ~/.claude/hooks.json
{
  "hooks": [
    {
      "event": "PreCompact",
      "type": "prompt",
      "prompt": "Session context is about to be compacted. Save any important decisions, preferences, facts, or context to ~/projects/claude-memory/sessions/$(date +%Y-%m-%d).md. If nothing needs saving, do nothing."
    },
    {
      "event": "Stop",
      "type": "prompt",
      "prompt": "Review this session for decisions ([DECISION]), preferences ([PREFERENCE]), facts ([FACT]), or entities ([ENTITY]) worth remembering. Append to ~/projects/claude-memory/sessions/$(date +%Y-%m-%d).md."
    }
  ]
}
```

Also: Set up `bank/` directory structure in claude-memory:
```
~/projects/claude-memory/bank/
├── world.md
├── experience.md
├── opinions.md
└── entities/
```

### Phase 1: Observability (Week 1 — 16h)

1. **Create session_traces table** in postgres-vector on VPS
2. **Implement SessionTracer** hook (PostToolUse → postgres)
3. **Extract OpenClaw's hybrid search** config (not LangChain's — OpenClaw's is proven and documented)
4. **Extract RecursiveCharacterTextSplitter** from LangChain (still best-in-class for chunking)

### Phase 2: First Persistent Agent + Heartbeat (Week 2 — 16h)

1. **Run `/new-sdk-app session-analyzer`** — create our first deployed agent
2. Customize with postgres connector + improvement proposal output
3. Add LangGraph reflection loop (clone from `references/langgraph/examples/reflection/`)
4. **Build heartbeat daemon** (~200 LOC asyncio service, 4h)
   - `/ping` and `/health` on each agent
   - `/status` endpoint for Tier 1 SessionStart hook
   - Auto-restart via Docker socket
   - n8n webhook for anomaly alerts
5. **Deploy both as Docker services** on VPS alongside existing containers
6. Wire n8n to trigger session-analyzer nightly + receive heartbeat alerts

### Phase 3: Memory Curator (Week 3 — 16h)

1. **Run `/new-sdk-app memory-curator`** — second deployed agent
2. Implement OpenClaw's Retain/Recall/Reflect loop:
   - Retain: Parse daily session logs → typed facts (W/B/O)
   - Recall: Hybrid search over bank/ directory
   - Reflect: Update entity pages, adjust opinion confidence
3. Deploy on VPS, trigger weekly via n8n

### Phase 4: RAG Optimizer + Skill Generator (Week 4 — 16h)

1. **Build RAG optimizer with Google ADK** — uses Gemini 2.5 Pro + ADK evaluation framework
2. **Build skill generator with Agent SDK** — Voyager-inspired, generates SKILL.md from trace patterns
3. Deploy both on VPS
4. Set up safety: max 3 auto-applies/day, confidence > 0.8, human PR review

### Phase 5: Close the Loop (Week 5 — 8h)

1. All 4 persistent agents + heartbeat daemon running on VPS
2. n8n orchestrates nightly/weekly/monthly cycles
3. Heartbeat rhythm triggers memory consolidation automatically
4. Auto-PRs flow to GitHub for review
5. Baseline comparison agent (frozen "control" config) validates improvements
6. SessionStart hook injects mesh health → every session is self-aware

---

## The Numbers

| Investment | Hours | Cost |
|-----------|-------|------|
| Phase 0 (hooks) | 2h | $0 |
| Phase 1 (observability) | 16h | ~$5/mo postgres storage |
| Phase 2 (session analyzer + heartbeat) | 16h | ~$10/mo Sonnet API for nightly runs |
| Phase 3 (memory curator) | 16h | ~$5/mo Sonnet API for weekly runs |
| Phase 4 (RAG + skill gen) | 16h | ~$15/mo Gemini API + Sonnet |
| Phase 5 (integration) | 8h | $0 (n8n already running) |
| **Total** | **74h** | **~$35/mo ongoing** |

Heartbeat daemon cost: effectively $0 — runs on existing VPS, ~20MB RAM, no API calls. It's pure infrastructure.

| Expected Return | Timeline |
|----------------|----------|
| Memory never lost (PreCompact flush) | Immediate |
| Mesh self-healing (heartbeat auto-restart) | Week 2 |
| Self-aware sessions (mesh status on start) | Week 2 |
| Structured memory (bank/ + entities) | Week 3 |
| Auto-generated skills | Month 2 |
| +15-30% agent success rate | Month 3 |
| Self-tuning RAG | Month 3 |
| Compound improvements | Month 4+ |

---

## What We're Actually Building

Not "extracting patterns from LangChain." We're building a **living development environment** — an agent mesh where:

1. **You code** (Tier 1 — Claude Code sessions)
2. **The heartbeat keeps everything alive** — 10s ticks, 60s health probes, auto-restart, n8n alerts
3. **Persistent agents analyze** what you did (Tier 2 — Agent SDK services)
4. **Shared state evolves** from raw logs to structured knowledge (Tier 3 — postgres + memory bank)
5. **Next session is better** than the last — and it *knows* it is, because SessionStart reads mesh status

The key realization: **the Agent SDK plugin and Google ADK aren't just for building user-facing apps**. They're for building the **autonomous improvement infrastructure** that wraps around your development sessions.

OpenClaw already proved these memory patterns work in production (22+ channels, 50+ skills, thousands of users). LangChain provides the RAG primitives. LangGraph provides the reflection loop. The Agent SDKs provide the deployment vehicle. And the heartbeat keeps it all breathing — no silent failures, no dead agents, no mystery downtime. Every session starts knowing the mesh is alive.

We have ALL the pieces. We just need to connect them.
