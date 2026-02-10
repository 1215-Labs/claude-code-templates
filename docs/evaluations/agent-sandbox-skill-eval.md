# Skill Evaluation: agent-sandbox-skill

**Date:** 2026-02-09
**Evaluator:** Opus (synthesized from 3 parallel Sonnet agents + creator video transcript)
**Target:** `references/agent-sandbox-skill`
**Intended use:** Isolated sandbox execution for agent workflows, full-stack prototyping
**Evaluation depth:** full

## Executive Summary

agent-sandbox-skill is a well-engineered E2B sandbox CLI that fills a **critical gap** in the ecosystem: isolated code execution for AI agents. The architecture is clean (5/5), documentation is exceptional (5/5), and the skill introduces genuinely novel capabilities — sandbox isolation, public URL hosting, multi-agent coordination, and tiered resource templates. Creator video analysis confirms the skill works across Claude Code, Gemini CLI, and Codex CLI simultaneously (15 parallel sandboxes demonstrated), validating the "best of N" pattern and our fork-terminal integration hypothesis. However, it has **zero test coverage**, only 2 git commits, and requires an external paid service (E2B). The creator (IndyDevDan, 100K subs, weekly cadence) shows strong commitment signals despite the thin git history. **Extract the core sandbox CLI modules, skip browser automation (we already have agent-browser), and add tests before production use.**

> This is Opus's independent assessment — not a merge of agent summaries. Contradictions between agents have been resolved and noted below.

## At a Glance

| Dimension | Score | Agent |
|-----------|-------|-------|
| Structural Quality | 3.90/5 | Sonnet (structural) |
| Ecosystem Fit | 4.80/5 | Sonnet (ecosystem) |
| Risk Profile | 3.50/5 | Sonnet (risk) + video context + hands-on |
| **Overall** | **4.10/5** | **Opus (weighted)** |

**Verdict:** Extract Components

> Possible verdicts: **Adopt** | **Extract Components** | **Adapt Patterns** | **Skip**

## What's Genuinely New

The skill introduces capabilities that don't exist anywhere in our ecosystem:

| Capability | Novel? | Impact |
|------------|--------|--------|
| E2B sandbox isolation | Completely new | Agents execute arbitrary code without local risk |
| Public URL hosting (`get-host`) | Completely new | Instant shareable URLs for sandbox apps |
| Multi-agent sandbox coordination | Completely new | Each agent tracks own sandbox ID, no conflicts |
| Tiered resource templates (lite→max) | Completely new | Right-size compute for workload |
| Plan-build-host-test workflow | Completely new | End-to-end full-stack cycle in one command |
| Background process lifecycle | Completely new | Servers with auto-timeout, extend-lifetime |
| SDK-based file operations | Completely new | Reliable remote file ops (not shell commands) |
| Browser validation for sandboxes | Partially new | Overlaps agent-browser, different context |

**90% of capabilities are genuinely novel** — this isn't incremental, it's a new capability layer.

## What Gap It Fills

**Critical gaps filled:**

1. **Safe code execution** — No existing component can run untrusted code in isolation. This is foundational for agent safety.
2. **Full-stack prototyping** — No way to scaffold Vue + FastAPI + SQLite apps with public URLs in minutes.
3. **Parallel agent environments** — No pattern for multiple agents running independent isolated compute.

**Without this skill**, agents must execute code locally (unsafe), can't prototype full-stack apps (limited), and can't share live demos (no public URLs).

## Combinatorial Leverage

| Combination | New Capability | Effort | Value |
|-------------|---------------|--------|-------|
| agent-sandboxes + fork-terminal | Multi-model agents (codex/gemini/claude) each with isolated sandboxes | Low | High |
| agent-sandboxes + prp-claude-code | PRPs build full-stack apps in isolation with live URLs | Medium | High |
| agent-sandboxes + test-automator | Test suites execute in clean environments, zero local pollution | Low | High |
| agent-sandboxes + debugger | Reproduce bugs in isolation with exact dependencies | Low | High |
| agent-sandboxes + deployment-engineer | Build/validate in sandbox, then deploy to production | High | High |

**Multiplier effect:** Sandboxes make every other agent safer and more capable. The isolation layer is a force multiplier.

## Risk Profile

### Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| E2B vendor lock-in | HIGH | Extract patterns; document Docker fallback path |
| Zero test coverage | HIGH | Add pytest suite before production use |
| Single maintainer (IndyDevDan) | MEDIUM | Fork for stability; but 100K subs + weekly cadence = committed creator |
| 2-commit git history | LOW-MEDIUM | Young project; video context shows active development beyond git |
| E2B costs ($0.13-$0.44/hr) | MEDIUM | Set budget limits; auto-timeout prevents runaway |
| Shell command construction (`--shell` flag) | LOW | Commands execute in E2B sandbox (isolated) |

### Maintenance Health

| Signal | Status |
|--------|--------|
| Last activity | Recent (ac460ee) |
| Contributors | 1 (IndyDevDan) |
| Dependencies | 5 direct (e2b, click, python-dotenv, rich, playwright) |
| Tests | None |
| CI/CD | None |

## Adoption Strategies

### Strategy A: Adopt As-Is

Full integration — copy entire `.claude/skills/agent-sandboxes/` directory.

**Steps:**
1. Copy skill directory to ecosystem
2. Set up E2B account and API key
3. Install all dependencies including Playwright
4. Test all workflows end-to-end

| Effort | Risk | Value |
|--------|------|-------|
| High | High | High |

**When to choose:** You want all features including browser automation and full-stack generation, and accept E2B dependency + no tests.

### Strategy B: Extract Components (Recommended)

Cherry-pick core sandbox CLI, skip browser automation.

**Extract:**
- `sandbox_cli/src/modules/sandbox.py` -> Core sandbox CRUD
- `sandbox_cli/src/modules/commands.py` -> Command execution
- `sandbox_cli/src/modules/files.py` -> File operations
- `sandbox_cli/src/commands/{exec,files,sandbox}.py` -> CLI wrappers
- `sandbox_cli/src/main.py` -> Entry point (adapted)
- `SKILL.md` -> Adapted to extracted features
- `examples/01-04` -> Core usage examples
- `prompts/sandbox.md` -> Basic sandbox prompt

**Skip:**
- `browser.py` + browser commands (we have agent-browser)
- `build_template.py` (unless building custom E2B templates)
- `prompts/full_stack/` (40+ starter prompts — keep as reference only)
- `prompts/plan-build-host-test.md` (keep as reference for workflow patterns)
- `temp/` directory (test artifacts)

| Effort | Risk | Value |
|--------|------|-------|
| Medium | Medium | High |

**When to choose:** You want isolated code execution without browser complexity, and plan to add tests. This is the recommended path.

### Strategy C: Adapt Patterns

Learn from the approach, implement with Docker instead of E2B.

**Patterns to adopt:**
- CLI structure: commands/ modules/ separation with click + rich
- Agent-first design: prompts optimized for AI consumption
- Multi-agent coordination: sandbox ID tracking in agent context (not shell vars)
- Progressive disclosure: examples organized by complexity
- Background process lifecycle: start, keep-alive, auto-timeout

| Effort | Risk | Value |
|--------|------|-------|
| High (reimplementation) | Low | Medium |

**When to choose:** Can't use E2B (cost, compliance, air-gapped), but want the patterns for Docker-based sandboxing.

## Recommended Strategy

**Extract Components (Strategy B)**

The ecosystem fit is exceptional (4.80/5) — this skill fills critical gaps and creates powerful combinations. But the risk profile (3.25/5) — no tests, single maintainer, E2B lock-in — makes full adoption premature. Extract the core sandbox CLI, skip browser automation (redundant with agent-browser), add a test suite, and integrate with fork-terminal + PRP workflows.

**Concrete next steps:**
1. ~~Extract core modules (sandbox, commands, files) to `.claude/skills/agent-sandboxes/`~~ **Done** (2026-02-09)
2. ~~Adapt SKILL.md to extracted feature set~~ **Done** (2026-02-09)
3. Add pytest suite for extracted modules (use E2B mocks)
4. Set up E2B API key with budget limits
5. Integrate with fork-terminal for multi-model sandbox orchestration
6. Keep reference `prompts/full_stack/` as inspiration (don't install)

## Integration Checklist

If adopting (Strategy A or B):

- [ ] Add to `MANIFEST.json` (deployment: global, status: beta)
- [ ] Update `REGISTRY.md` (category: sandbox, quick lookup, relationships)
- [ ] Run `python3 scripts/validate-docs.py`
- [ ] Run `python3 scripts/install-global.py --dry-run` to verify installation
- [ ] Update component counts in REGISTRY
- [ ] Set up E2B API key provisioning
- [ ] Document E2B cost model for team

## Agent Reports

Raw agent reports for deep-dive:

- **Structural Quality:** [`docs/evaluations/agent-sandbox-skill-structural.md`](agent-sandbox-skill-structural.md)
- **Ecosystem Fit:** [`docs/evaluations/agent-sandbox-skill-ecosystem.md`](agent-sandbox-skill-ecosystem.md)
- **Risk & Adoption:** [`docs/evaluations/agent-sandbox-skill-risk.md`](agent-sandbox-skill-risk.md)

**Models used:** All 3 agents ran as Sonnet subagents (fallback from Codex/Gemini CLIs due to shell escaping complexity with long prompts).
- **Creator Video:** [I gave Gemini 3 Pro its own computer](https://www.youtube.com/watch?v=V5IhsHEHXOg) — transcript downloaded via youtube-transcript skill, manually synthesized (no OpenRouter key for LLM transform)

## Creator Video Context

**Source:** [I gave Gemini 3 Pro its own computer](https://www.youtube.com/watch?v=V5IhsHEHXOg) (IndyDevDan, ~5,747 words)
**Transcript:** `transcripts/I_gave_Gemini_3_Pro_its_own_computer_its_official_Claude_Code_has_COMPETITION/`

### Key Insights from Creator

**Design Philosophy — "Scale compute to scale impact":**
The creator's core thesis is that model intelligence is no longer the bottleneck — agent tooling is. He argues that giving agents their own isolated computers (E2B sandboxes) unlocks three capabilities: isolation (security), scale (parallel agents), and autonomy (agents do whatever they need). The "best of N" pattern — spin up many sandboxes, let agents attempt the same task, choose the best result — is central to the design.

**Multi-Model Validation (confirmed in video):**
The video demonstrates 15 simultaneous sandboxes across Claude Code (Sonnet 4.5), Gemini CLI (Gemini 3 Pro), and Codex CLI (GPT 5.1). All three models successfully built full-stack applications (Vue + FastAPI + SQLite) with working CRUD operations and data persistence. This validates our fork-terminal integration hypothesis — the skill is genuinely model-agnostic.

**Realistic Failure Tolerance:**
Not all sandboxes succeeded. Codex's image generation didn't work. Gemini got stuck at 40+ minutes on one task. The creator explicitly embraces this: "You can just fully expect that some versions will not work successfully." This is honest and architecturally sound — the "best of N" pattern assumes partial failure.

**"Reprogrammed Backslash" Pattern:**
The CLAUDE.md/AGENTS.md/GEMINI.md files redirect backslash commands to skill prompts — identical to our existing command routing pattern. The creator explicitly describes reprogramming agents to understand custom syntax via memory files. This is a validation of our own architecture, not a new pattern to learn.

**Chained Workflow Endorsement:**
The plan-build-host-test workflow is described as "a powerful agentic prompt that does a ton of work in a single prompt, a 170-line prompt." The creator walks through the workflow steps: read docs → init sandbox → plan → build → host → test. This maps directly to our PRP execution model.

### Impact on Evaluation Scores

| Dimension | Original | Adjusted | Reason |
|-----------|----------|----------|--------|
| Maintenance Signals | 2/5 | 2.5/5 | Creator has 100K YouTube subs, weekly content cadence, mentions "big prototypes" and 2026 plans. Active public commitment, though git history is still thin. |
| Ecosystem Fit (Novelty) | 5/5 | 5/5 | Confirmed — video demonstrates genuinely novel multi-model parallel sandbox execution at scale. |
| Adoption Cost | 3/5 | 3.5/5 | Video demonstrates working end-to-end flows across 3 CLI agents. Less integration risk than code-only analysis suggested. |

**Adjusted Risk Score:** 3.25 → 3.40/5 (marginal improvement from maintenance signals) → 3.50/5 (hands-on validation)
**Adjusted Overall:** 3.98 → 4.03/5 → 4.10/5 (hands-on validation)

### Quotes Worth Noting

> "The limitation is no longer the language model. The limitation is in the agent. The limitation is in what agentic systems you and I can or cannot build."

> "You can spin up dedicated environments for your agent to own end to end. This gives you isolation — and isolation gives you security. This gives you scale."

> "Every single release, [models] matter less... What truly matters is your benchmark and how they perform inside the agent."

### What This Changes for Our Strategy

The video **strengthens the case for extraction** (Strategy B):

1. **Multi-model support is real** — not just documented, but demonstrated across Claude/Gemini/Codex. Our fork-terminal integration is the highest-value combination.
2. **"Best of N" pattern** — this is a new workflow pattern we should adopt. Spin up N sandboxes with different models, compare results. Not currently possible in our ecosystem.
3. **Creator commitment** — 100K subs, weekly cadence, public roadmap signals. The 2-commit git history is misleading; this is an active, invested creator. Fork is still recommended for stability, but upstream abandonment risk is lower than code-only analysis suggested.
4. **Skip browser automation confirmed** — the video shows browser validation working but not as the core value prop. Sandbox execution + hosting is the main event.

## Hands-On Validation (2026-02-09)

Used the agent-sandbox-skill to test 5 extracted components (ruff-validator, ty-validator, meta-agent, team-builder, team-validator) in an E2B sandbox. 18/18 tests passed.

### What Worked

- **End-to-end workflow validated**: `init` → `exec` → `files upload/download` → `kill` lifecycle worked smoothly
- **Cost**: ~$0.05 for full test run (~15 min at $0.13/hr) — well within budget
- **E2B API key setup**: Straightforward — set `E2B_API_KEY` env var and go
- **Python 3.11**: Pre-installed in default sandbox template, no setup needed
- **File operations**: SDK-based `files.write` / `files.read` reliable for uploading test fixtures and downloading results
- **Rich CLI output**: Clear status messages made it easy to follow execution

### What the Evaluation Got Wrong

| Assumption | Reality | Impact |
|-----------|---------|--------|
| uv/uvx pre-installed | **NOT pre-installed** — requires `curl -LsSf https://astral.sh/uv/install.sh \| sh` + PATH symlinks | Medium — adds ~30s setup per sandbox |
| stderr visible on failures | `sbx exec` **swallows stderr on non-zero exit codes** — must redirect to file for debugging | High — silent failures until you learn the workaround |
| Compound commands work | `--shell` flag **required** for `&&`, pipes, redirections (not documented prominently) | Medium — easy fix once known |
| .env resolution works | 6-parent-dir traversal from `main.py` is **fragile** for non-standard nesting | Low — fixed in our extraction |

### Score Adjustments

| Dimension | Before | After | Reason |
|-----------|--------|-------|--------|
| Risk Profile | 3.40/5 | 3.50/5 | Validated workflow reduces adoption risk; quirks are documented and workaround-able |
| Overall | 4.03/5 | 4.10/5 | Hands-on confirmation of core value; known issues are minor |

### Verdict

No change — **Extract Components** confirmed as correct strategy. Hands-on use validates the skill works for real agent workflows but doesn't eliminate structural risks (no tests, single maintainer, E2B lock-in). Extraction is now in progress with specific modules identified.

## Contradictions & Resolutions

| Agent A Says | Agent B Says | Resolution |
|-------------|-------------|------------|
| Ecosystem: "ADOPT IMMEDIATELY (P0)" | Risk: "Extract Components (Strategy B)" | **Resolved: Extract Components.** The ecosystem fit is genuinely exceptional, but the risk agent correctly identifies that no tests + single maintainer + E2B lock-in = too risky for full adoption. Extract core modules, add tests, then expand. |
| Structural: Code quality 5/5 | Risk: Shell command construction MEDIUM severity | **Resolved: Both correct.** The code quality IS excellent (type hints, error handling, clean architecture). The shell command risk IS real, but mitigated by E2B isolation — commands execute in sandboxes, not locally. Low actual risk, good to document. |
| Ecosystem: Browser overlap "minor, complementary" | Risk: "Skip browser to reduce complexity 40%" | **Resolved: Skip browser.** Both are right — the overlap IS complementary (different tools, different purposes). But the risk agent's point about reducing scope is stronger. We already have agent-browser; extracting sandbox browser adds Playwright as a dependency for diminishing returns. |
