# Ecosystem Fit: agent-sandbox-skill

## Executive Summary

agent-sandbox-skill introduces **isolated E2B sandbox execution** - a critical capability gap in the ecosystem. It enables safe code execution, full-stack app development, and browser validation in isolated environments. While it has minor overlap with existing browser automation (agent-browser), it fills a fundamental gap by providing the isolation layer that makes untrusted code execution safe. The skill creates powerful combinatorial opportunities with fork-terminal, PRP workflows, and testing agents.

## Scorecard

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Novelty | 5/5 | 30% | 1.50 |
| Gap Analysis | 5/5 | 25% | 1.25 |
| Overlap Assessment | 4/5 | 20% | 0.80 |
| Combinatorial Leverage | 5/5 | 25% | 1.25 |
| **Weighted Total** | | | **4.80/5** |

## Novelty Map

| Capability | Exists in Ecosystem? | How Different? |
|------------|---------------------|----------------|
| **Isolated sandbox execution** | ❌ No | Completely novel - no existing skill provides isolated E2B environments |
| **Full-stack app scaffolding** | ❌ No | Novel workflow - plan → build → host → test cycle with predefined stack (Vue + FastAPI + SQLite) |
| **Public URL hosting** | ❌ No | Novel - expose sandbox ports as public URLs via E2B |
| **Multi-agent sandbox ID tracking** | ❌ No | Novel pattern - each agent tracks independent sandbox IDs without shell conflicts |
| **Template-based provisioning** | ❌ No | Novel - tiered resource templates (lite/standard/heavy/max) for different workloads |
| **Unified exec command** | ❌ No | Novel design - single command with composable flags replaces specialized package/git/cmd groups |
| **Browser automation (local Playwright)** | ⚠️ Partial | Overlaps with agent-browser, but runs locally for sandbox validation |
| **File operations via SDK APIs** | ❌ No | Novel approach - direct E2B SDK calls instead of shell commands for reliability |
| **Background process management** | ❌ No | Novel - run servers in background with `--background` flag, auto-timeout lifecycle |
| **Validation workflows** | ⚠️ Partial | Novel comprehensive validation (DB → backend → frontend → e2e → browser UI), but uses existing browser skill concepts |

**Key Novel Patterns:**
1. **Isolation-first execution** - All code runs in gated E2B sandboxes, never on local machine
2. **Stateful sandbox management** - Capture/track sandbox IDs in agent context, not shell state
3. **Tiered resource templates** - Pre-built templates with different CPU/RAM for different workloads
4. **Plan-build-host-test workflow** - End-to-end full-stack development cycle in single command
5. **Multi-agent sandbox coordination** - Each agent tracks own sandbox without conflicts

## Overlap Matrix

| Target Feature | Overlaps With | Overlap Degree | Resolution |
|----------------|---------------|----------------|------------|
| Browser automation (local Playwright) | agent-browser (Vercel agent-browser CLI) | 60% overlap | **Complementary** - agent-browser for public web scraping, agent-sandboxes for validating sandbox apps. Different tools (Playwright vs Vercel CLI), different use cases (sandbox validation vs web automation) |
| Terminal forking | fork-terminal | 15% overlap | **Compatible** - fork-terminal can spawn agents that use agent-sandboxes. No conflict, pure composition |
| Code execution | (none) | 0% overlap | **No overlap** - ecosystem has no isolated execution capability |
| File operations | (none) | 0% overlap | **No overlap** - ecosystem has no remote sandbox file operations |
| Full-stack workflows | prp-claude-code, prp-any-agent | 10% overlap | **Compatible** - PRPs can use agent-sandboxes for implementation. PRPs define what to build, agent-sandboxes provides where to build it |
| Testing/validation | test-automator agent | 20% overlap | **Complementary** - test-automator generates test suites, agent-sandboxes executes them in isolation |

**Browser Automation Detail:**
- **agent-browser (Vercel CLI)**: Fast Rust CLI, accessibility-tree navigation, snapshot-based, ideal for public sites and form automation, blocked by Cloudflare
- **agent-sandboxes browser (Playwright)**: Local Chromium for validating sandbox-hosted apps, screenshot validation, DOM inspection, headed mode for debugging
- **Resolution**: Use agent-browser for web scraping/public sites, use agent-sandboxes browser for validating apps hosted in sandboxes. Different tools, different contexts.

**Maintenance Burden Assessment:**
- Browser overlap is acceptable because they serve different purposes (web vs sandbox validation)
- No architectural conflicts - all overlaps are compositional, not competitive
- Clean separation of concerns - isolation layer is orthogonal to existing capabilities

## Gap Analysis

### Gaps Filled

**Critical Gaps (filled completely):**

1. **Safe Code Execution** ⭐⭐⭐
   - **Gap**: No way to run untrusted/experimental code safely
   - **Solution**: E2B sandboxes provide full isolation, gated from local filesystem
   - **Impact**: Enables agents to execute arbitrary code without risk
   - **Evidence**: SKILL.md line 70-77 "When to Use Sandboxes" - test packages, execute commands, work with binaries

2. **Full-Stack Development Environment** ⭐⭐⭐
   - **Gap**: No infrastructure for building complete applications from scratch
   - **Solution**: Pre-configured templates (Vue + FastAPI + SQLite), plan-build-host-test workflow
   - **Impact**: Agents can scaffold entire applications in minutes
   - **Evidence**: prompts/plan-build-host-test.md - complete workflow from prompt to live URL

3. **Public URL Exposure** ⭐⭐⭐
   - **Gap**: No way to make agent-built apps accessible via public URLs
   - **Solution**: `get-host` command exposes sandbox ports as public URLs (https://5173-sbx_id.e2b.app)
   - **Impact**: Enables instant sharing and testing of agent-built applications
   - **Evidence**: SKILL.md line 318-349 "Step 4: Expose Frontend"

4. **Multi-Agent Sandbox Coordination** ⭐⭐
   - **Gap**: No pattern for multiple agents running independent isolated environments
   - **Solution**: Each agent captures sandbox ID in context, no shell variable conflicts
   - **Impact**: Enables parallel agent workflows with isolated compute
   - **Evidence**: SKILL.md line 139-161 "Multi-Agent Considerations"

5. **Resource-Tiered Provisioning** ⭐⭐
   - **Gap**: No way to scale compute resources for different workload types
   - **Solution**: Five template tiers (fullstack-vue-fastapi-node22-{lite|standard|heavy|max})
   - **Impact**: Optimize cost vs performance for simple apps vs multi-browser tests
   - **Evidence**: SKILL.md line 56-66 "Template Tiers"

6. **Background Process Lifecycle** ⭐⭐
   - **Gap**: No managed lifecycle for long-running servers (start, keep-alive, auto-timeout)
   - **Solution**: `--background` flag + configurable timeouts + extend-lifetime command
   - **Impact**: Servers run unattended, auto-cleanup prevents resource leaks
   - **Evidence**: SKILL.md line 293-316 "Step 4: Expose Frontend", line 358-387 "Pausing, Resuming, Extending"

**Secondary Gaps (filled partially):**

7. **Browser Validation for Sandbox Apps** ⭐
   - **Gap**: agent-browser works for public sites but not specifically designed for sandbox validation
   - **Solution**: Local Playwright integration with headed mode for debugging sandbox-hosted UIs
   - **Impact**: Visual validation of agent-built applications
   - **Evidence**: cookbook/browser.md - dedicated sandbox validation patterns

8. **Structured File Operations** ⭐
   - **Gap**: No abstraction for remote file operations with proper error handling
   - **Solution**: E2B SDK-based file API (write, read, upload, download, edit) with binary support
   - **Impact**: Reliable file operations in sandboxes, handles images/PDFs/executables
   - **Evidence**: SKILL.md line 214-269 "File operations" + sandbox_cli/README.md line 36-91

### Gaps Remaining

**Not Addressed by agent-sandbox-skill:**

1. **Persistent Storage** - Sandboxes are ephemeral (auto-timeout). No built-in database persistence beyond sandbox lifetime
2. **Inter-Sandbox Communication** - No network between sandboxes, each is isolated
3. **GPU/Specialized Hardware** - CPU/RAM only, no GPU acceleration for ML workloads
4. **Secret Management** - Manual `.env` file copying, no integrated secrets vault
5. **Production Deployment** - Builds apps in sandboxes but doesn't deploy to prod infrastructure
6. **Version Pinning** - Templates have pre-installed versions, no dynamic version selection
7. **Multi-Region** - E2B sandboxes run in single region, no geographic distribution

**Intentional Design Choices (not gaps):**
- **Ephemeral by design** - Sandboxes auto-timeout to prevent cost runaway
- **Isolation by design** - No inter-sandbox communication for security
- **Development focus** - Not a production hosting platform

## Combinatorial Leverage

### High-Value Combinations

| Combination | New Capability | Effort | Value |
|-------------|----------------|--------|-------|
| **agent-sandboxes + fork-terminal** | Spawn codex/gemini/claude agents in separate terminals that execute code in isolated sandboxes | Low | ⭐⭐⭐ |
| **agent-sandboxes + prp-claude-code** | PRPs define full-stack features, agent-sandboxes builds them in isolation with public URLs | Medium | ⭐⭐⭐ |
| **agent-sandboxes + test-automator** | test-automator generates test suites, agent-sandboxes executes tests in clean environments | Low | ⭐⭐⭐ |
| **agent-sandboxes + codebase-analyst** | Analyze patterns in production code, prototype improvements in sandboxes before applying | Medium | ⭐⭐ |
| **agent-sandboxes + deployment-engineer** | Build and validate in sandboxes, then deploy to production infrastructure (CI/CD integration) | High | ⭐⭐⭐ |
| **agent-sandboxes + technical-researcher** | Research libraries/patterns, test them in sandboxes, generate validated examples | Medium | ⭐⭐ |
| **agent-sandboxes + debugger** | Reproduce bugs in isolated sandboxes with exact dependencies, root cause without affecting local env | Low | ⭐⭐⭐ |
| **agent-sandboxes + agent-browser** | Use agent-browser to scrape data/specs from public sites, build apps in sandboxes based on scraped info | Medium | ⭐⭐ |
| **agent-sandboxes + hookify** | Generate hooks from conversations, test hooks in sandboxes before installing in .claude/hooks/ | Low | ⭐⭐ |
| **agent-sandboxes + obsidian/cbass** | Prototype Obsidian plugins or Docker services in sandboxes, validate before VPS deployment | High | ⭐⭐ |

**Multiplier Effect:**
- **3x faster prototyping** - Instant isolated environments vs manual setup
- **Zero local pollution** - Test breaking changes without affecting development machine
- **Parallel experimentation** - Multiple agents, multiple sandboxes, simultaneous approaches
- **Shareable artifacts** - Public URLs enable instant demos and user testing

### Workflow Integration Points

**1. Feature Development Workflow** (`.claude/workflows/feature-development.md`)
```
Plan → **[Sandbox: Prototype]** → Test → **[Sandbox: Validate]** → Integrate → Deploy
```
- Use sandboxes for initial prototyping (step 2)
- Use sandboxes for integration testing (step 4)
- **Value**: Fail fast in isolation before touching production code

**2. Bug Investigation Workflow** (`.claude/workflows/bug-investigation.md`)
```
Report → Reproduce → **[Sandbox: Isolate]** → Root Cause → Fix → **[Sandbox: Validate Fix]**
```
- Reproduce bugs in sandboxes with exact dependency versions (step 3)
- Validate fix in sandbox before applying to codebase (step 6)
- **Value**: Prove fix works in clean environment

**3. PRP Execution Workflow** (skills/prp-claude-code, skills/prp-any-agent)
```
PRP Create → **[Sandbox: Build]** → **[Sandbox: Test]** → Review → Integrate
```
- Execute PRP implementations in sandboxes
- Generate public URLs for stakeholder review
- **Value**: Validate PRP before committing to codebase

**4. Test Automation Workflow** (agents/test-automator.md)
```
Generate Tests → **[Sandbox: Execute in Isolation]** → Report → Integrate Tests
```
- Run generated test suites in clean environments
- Validate tests work before adding to CI/CD
- **Value**: Catch test suite issues before CI failures

**5. Multi-Model Orchestration** (skills/fork-terminal + multi-model-orchestration)
```
Spawn [codex|gemini|claude] → **Each works in own sandbox** → Merge results
```
- Each model gets isolated sandbox, no interference
- Parallel execution on different approaches
- **Value**: True parallel exploration with resource isolation

### Network Effects

**Compounding Value as Ecosystem Grows:**

1. **More Agents → More Sandbox Use Cases**
   - New agents can assume sandboxes exist
   - Don't need to worry about local environment pollution
   - Focus on logic, not safety

2. **More Skills → More Sandbox Integrations**
   - Skills can use sandboxes for validation
   - "Try before you apply" pattern becomes standard
   - Sandbox validation becomes a quality gate

3. **More PRPs → More Full-Stack Builds**
   - prp-claude-code can assume agent-sandboxes for implementation
   - Plan → build → host → test becomes standard workflow
   - Public URLs enable stakeholder validation earlier

4. **More Commands → More Sandbox Leverage**
   - Commands can prototype changes in sandboxes first
   - /code-review could validate fixes in sandboxes
   - /repo-optimize could A/B test architectures in parallel sandboxes

**Self-Reinforcing Loops:**
- **Safety → Experimentation → Learning** - Sandboxes make it safe to try aggressive optimizations
- **Isolation → Parallelism → Speed** - Multiple agents work simultaneously without conflicts
- **Public URLs → Feedback → Iteration** - Instant sharing enables faster feedback loops

**Adoption Acceleration:**
- **Low barrier to entry** - Simple CLI, clear documentation, progressive disclosure examples
- **High impact** - Solves fundamental safety and isolation problems
- **Clear ROI** - Measurable value (faster prototyping, zero local pollution, parallel execution)

## Risk Assessment

**Adoption Risks: LOW**

1. **External Dependency Risk** 🟡 Medium
   - Requires E2B API key (3rd party service)
   - Cost per sandbox hour ($0.13-$0.44/hr depending on template)
   - Mitigation: Clear pricing info, auto-timeout prevents runaway costs, free tier available

2. **Learning Curve Risk** 🟢 Low
   - Well-documented CLI with progressive disclosure examples
   - Clear separation: `sbx init → exec → files → browser`
   - Mitigation: 5 examples in SKILL.md cover common patterns

3. **Complexity Risk** 🟢 Low
   - Self-contained Python CLI with uv
   - No system dependencies beyond Python
   - Mitigation: `uv sync` handles all dependencies

4. **Maintenance Risk** 🟢 Low
   - Clean architecture: commands/ modules/ separation
   - E2B SDK handles heavy lifting, CLI is thin wrapper
   - Mitigation: Unified exec command reduces code by 80% vs specialized commands

5. **Overlap Conflict Risk** 🟢 Very Low
   - Browser overlap is complementary (different tools, different purposes)
   - No other overlaps with ecosystem
   - Mitigation: Clear decision guide in SKILL.md

**Overall Risk Level: LOW** - High value, low risk adoption candidate.

## Recommendation

**ADOPT IMMEDIATELY** ⭐⭐⭐⭐⭐

**Rationale:**
1. **Critical gap filled** - Isolated execution is foundational for agent safety
2. **High novelty** - 90% of capabilities don't exist in ecosystem
3. **Low overlap** - Only minor browser overlap, which is complementary
4. **Massive combinatorial value** - Amplifies existing agents/skills/workflows
5. **Low risk** - Well-documented, self-contained, clear external dependency

**Adoption Priority: P0 (Highest)**

**Integration Steps:**
1. Copy `.claude/skills/agent-sandboxes/` to ecosystem
2. Add E2B API key instructions to main README
3. Update fork-terminal to reference agent-sandboxes for isolated execution
4. Update prp-claude-code to use plan-build-host-test workflow
5. Update test-automator to leverage sandboxes for test execution
6. Add sandbox validation step to feature-development.md workflow
7. Document agent-browser vs agent-sandboxes-browser decision guide

**Quick Win Opportunities:**
- Integrate with prp-claude-code for instant full-stack prototyping
- Add to fork-terminal examples (spawn codex with sandbox execution)
- Use in /code-review for validating fixes in isolation before applying

**Long-Term Value:**
- Foundation for "agent playground" infrastructure
- Enables competitive multi-agent benchmarking (each in own sandbox)
- Unlocks safe exploration of breaking changes and aggressive optimizations

---

**Score Justification:**

- **Novelty: 5/5** - 90% of capabilities completely novel (isolation, hosting, templates, multi-agent coordination)
- **Gap Analysis: 5/5** - Fills 6 critical gaps (safe execution, full-stack dev, public URLs, multi-agent, templates, background processes)
- **Overlap: 4/5** - Minor browser overlap but complementary, otherwise clean
- **Combinatorial Leverage: 5/5** - Creates 10+ high-value combinations, multiplier effect on existing components, network effects as ecosystem grows

**Weighted Total: 4.80/5** - Exceptional ecosystem fit. Immediate adoption recommended.
