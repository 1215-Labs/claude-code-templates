# Codex PRP Execution Methodology

Definitive guide for executing PRPs (Prompt Request Protocol) via Codex forked terminals.
Covers when to use, how to execute, how to troubleshoot, and best practices.

## Prerequisites

| Requirement | Minimum | Check Command |
|-------------|---------|---------------|
| Codex CLI | v0.98.0+ | `codex --version` |
| Python | 3.10+ | `python3 --version` |
| UV | any | `uv --version` |
| xterm (WSL2) | any | `which xterm` |
| OPENAI_API_KEY | set | `echo $OPENAI_API_KEY \| head -c 8` |

**Install Codex CLI**: `npm install -g @openai/codex`

## When to Use Codex PRP vs Alternatives

| Method | Best For | Effort Range |
|--------|----------|-------------|
| **Codex PRP** (this doc) | Convention-convert, full-rewrite PRPs with clear specs | 4-8 points |
| **Claude Code PRP** (`/prp-claude-code-execute`) | PRPs needing deep codebase context or LSP | 3-8 points |
| **Manual execution** | Simple PRPs (1-3 points), or when debugging | 1-3 points |
| **Parallel Codex PRPs** | Multiple independent PRPs | 4+ points each |

**Use Codex PRP when:**
- PRP has complete source code included (Codex doesn't need to search the repo)
- Adaptation is well-specified (clear before/after requirements)
- Tests are self-contained (can run with stdin JSON, no external dependencies)
- You want autonomous execution with structured validation

**Don't use Codex PRP when:**
- PRP requires understanding complex cross-file dependencies
- Tests need LSP or IDE integration
- The task is exploratory (no clear spec yet)

## Architecture

```
Claude Code (Opus) — Orchestrator
  │
  ├─ 1. Fork ────→ codex_prp_executor.py (new terminal window)
  │                  │
  │                  ├── Writes prompt to /tmp/codex-prp-{name}-prompt.txt
  │                  ├── Writes scoped AGENTS.md to target directory
  │                  ├── Runs: codex exec --full-auto -m gpt-5.3-codex ...
  │                  │         (user watches live in terminal)
  │                  ├── Codex implements PRP, runs tests
  │                  ├── Codex outputs structured JSON (--output-schema)
  │                  ├── Runs codex_prp_validator.py (independent verification)
  │                  ├── Writes combined report
  │                  └── Writes done flag
  │
  ├─ 2. Monitor ─→ Poll /tmp/codex-prp-{name}-done.json
  │                 tail -f /tmp/codex-prp-{name}-output.log
  │
  ├─ 3. Validate → Read report, verify files, run tests independently
  │
  └─ 4. Register → Update MANIFEST, REGISTRY, adoptions.md
```

**Key design principle**: Codex handles code implementation. Claude Code handles
cross-cutting registry updates and adoption tracking.

## Step-by-Step Runbook

### Step 1: Dry Run

Always dry-run first to verify the command is correct.

```bash
uv run .claude/skills/fork-terminal/tools/codex_prp_executor.py PRPs/distill-foo.md --dry-run
```

Check:
- Prompt file size is reasonable (5-15KB typical)
- Scoped AGENTS.md targets the correct directory
- No flag errors in the generated command

### Step 2: Fork Execution

```bash
python3 .claude/skills/fork-terminal/tools/fork_terminal.py \
  --log --tool codex-prp \
  "uv run .claude/skills/fork-terminal/tools/codex_prp_executor.py PRPs/distill-foo.md"
```

This opens a new terminal window where you can watch Codex work in real time.

### Step 3: Monitor

**Poll for completion** (from Claude Code or another terminal):

```bash
# Quick check
cat /tmp/codex-prp-{name}-done.json 2>/dev/null

# Live output
tail -f /tmp/fork_codex-prp_*.log

# Detailed Codex output
tail -f /tmp/codex-prp-{name}-output.log
```

**Typical durations**: 150-200 seconds for 4-5 point PRPs.

### Step 4: Verify Results

```bash
# Check completion
cat /tmp/codex-prp-{name}-done.json

# Check Codex self-report
cat /tmp/codex-prp-{name}-result.json | python3 -m json.tool

# Check independent validation
cat /tmp/codex-prp-{name}-report.json | python3 -m json.tool
```

**Quick summary script:**
```bash
cat /tmp/codex-prp-{name}-result.json | python3 -c "
import sys,json
r=json.load(sys.stdin)
print(f'Status: {r[\"status\"]}')
print(f'Tests: {sum(1 for t in r[\"test_results\"] if t[\"passed\"])}/{len(r[\"test_results\"])}')
print(f'Criteria: {sum(1 for c in r[\"acceptance_criteria\"] if c[\"met\"])}/{len(r[\"acceptance_criteria\"])}')
print(f'Errors: {r[\"errors\"]}')
"
```

### Step 5: Independent Verification

Don't trust Codex's self-report blindly. Verify key outcomes:

```bash
# Does the file exist?
ls -la <destination_file>

# Does it run?
echo '<test_json>' | python3 <destination_file>; echo "Exit: $?"

# Does validate-docs.py still pass?
python3 scripts/validate-docs.py
```

### Step 6: Register & Track

After verification, Claude Code handles:
- Update `MANIFEST.json` (if Codex didn't already)
- Update `REGISTRY.md` (if Codex didn't already)
- Update `.claude/memory/adoptions.md` (status: `deferred-to-prp` → `adopted`)
- Update `.claude/memory/tasks.md` (mark PRP task as completed)
- Commit and push

## Model Selection Strategy

| Model | Strengths | When to Use | Typical Duration |
|-------|-----------|-------------|------------------|
| `gpt-5.3-codex` | Highest SWE-bench, best code quality | Default — start here | 150-200s |
| `gpt-5.2-codex` | Reliable, well-tested | Fallback if 5.3 fails | 120-180s |
| `gpt-5.1-codex-max` | Extended context, good for large PRPs | Large PRPs (>10KB), last resort | 180-240s |
| `gpt-5.1-codex-mini` | Fast, cheap | NOT recommended for PRPs | N/A |

**Fallback chain**: The executor automatically tries models in order:
`gpt-5.3-codex` → `gpt-5.2-codex` → `gpt-5.1-codex-max`

**Override**: Use `--model` / `-m` to force a specific model:
```bash
uv run codex_prp_executor.py PRPs/foo.md -m gpt-5.2-codex
```

**Timeout**: Default 600s (10 min). Adjust with `-t`:
```bash
uv run codex_prp_executor.py PRPs/foo.md -t 300  # 5 minutes
```

## Codex CLI Flags Reference

### Flags Used by the Executor

| Flag | Purpose | Required |
|------|---------|----------|
| `--full-auto` | Auto-approve + workspace-write sandbox | Yes |
| `--skip-git-repo-check` | Avoid "not trusted directory" errors | Yes |
| `-m MODEL` | Select model | Yes |
| `-o FILE` | Write final message to file | Yes |
| `--output-schema FILE` | Force structured JSON output | Yes |
| `-C DIR` | Set working directory to repo root | Yes |
| `--add-dir /tmp` | Allow writing temp files outside repo | Yes |

### Flags NOT Available (Common Mistakes)

| Flag | Status | Alternative |
|------|--------|-------------|
| `--ephemeral` | Does NOT exist in v0.98.0 | Not needed — use `exec` subcommand |
| `--json` | Exists but outputs JSONL events | Don't use — breaks human-readable terminal output |
| `--dangerously-bypass-approvals-and-sandbox` | Deprecated | Use `--full-auto` |

### Prompt Passing

The executor passes prompts via **stdin** (not shell argument) to avoid quoting issues:

```bash
codex exec [flags] - < /tmp/codex-prp-{name}-prompt.txt
```

The `-` tells Codex to read the prompt from stdin. This is essential for large PRPs
(8-15KB prompts would break shell argument limits).

## Output Schema Design

OpenAI's structured output API requires strict schemas:

**Rule**: Every `"type": "object"` MUST have `"additionalProperties": false` and
all properties in `"required"`.

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "passed": {"type": "boolean"}
  },
  "required": ["name", "passed"],
  "additionalProperties": false
}
```

**If you violate this**, Codex returns:
```
Invalid schema for response_format: 'additionalProperties' is required
to be supplied and to be false.
```

The current schema at `templates/codex-prp-output-schema.json` is correct.
If you modify it, ensure every nested object follows this pattern.

## PRP Design for Codex Success

### What Makes a Good Codex PRP

1. **Include full source code** — Codex works best when it can see the code to adapt,
   not when it has to search the repo for it
2. **Specify exact destination paths** — `**File**: \`.claude/hooks/foo.py\`` not
   "somewhere in the hooks directory"
3. **Include a reference exemplar** — "Match the style of `security-check.py`" gives
   Codex a concrete target
4. **Write testable acceptance criteria** — each criterion should be verifiable with
   a single command
5. **Provide stdin-based tests** — `echo '{"json":"input"}' | python3 hook.py` works
   in Codex's sandbox; tests requiring external services don't

### What Makes a Bad Codex PRP

- Vague requirements: "improve the error handling" (improve how?)
- External dependencies: "connect to the database and verify" (Codex can't)
- Cross-repo changes: "update 3 repos" (Codex works in one repo)
- Exploratory tasks: "figure out the best approach" (use Claude Code instead)

### PRP Structure Checklist

- [ ] Source code included (not just a file reference)
- [ ] Destination path is exact
- [ ] Adaptation requirements are numbered and specific
- [ ] Each acceptance criterion maps to a test
- [ ] Test plan uses stdin JSON (no external deps)
- [ ] hooks.json entry pattern shown (if applicable)
- [ ] Exemplar file referenced for style matching

## AGENTS.md Context Injection

Codex auto-reads `AGENTS.md` from the repo root on every invocation. This provides
free, persistent context for conventions without consuming prompt tokens.

Our `AGENTS.md` documents:
- Python hook conventions (UV shebang, PEP 723, exit codes)
- hooks.json format (matchers, `${CLAUDE_PLUGIN_ROOT}`, `uv run`)
- Component registration requirements (MANIFEST, REGISTRY)
- Testing pipeline (validate-docs.py, install-global.py)

**Scoped AGENTS.md**: The executor also writes a temporary `AGENTS.md` to the
destination directory with PRP-specific context (source file, destination, adaptation
type). This is cleaned up after execution.

## Validation Interpretation

The validator returns one of three statuses:

| Status | Meaning | Action |
|--------|---------|--------|
| `pass` | All checks passed | Proceed to registration |
| `partial` | Some checks failed (< 1/3) | Review failures, may need manual fixes |
| `fail` | Most checks failed (> 1/3) | Codex output likely needs redo |

### Validator Checks

| Check | What It Verifies |
|-------|-----------------|
| `file_exists` | Created files actually exist on disk |
| `uv_shebang` | Python files start with `#!/usr/bin/env -S uv run --script` |
| `pep723_block` | Python files have `# /// script` metadata block |
| `provenance_header` | Files contain `Adapted from:` provenance |
| `hooks_json_valid` | hooks.json is valid JSON with expected entry |
| `test: *` | Each PRP test plan command runs successfully |
| `validate_docs` | `python3 scripts/validate-docs.py` passes |

**Important**: The validator checks exit codes `0` and `2` as valid for hook tests
(0 = allow, 2 = block). But a "file not found" error also returns exit code 2 on
some systems. Always cross-check test output, not just exit codes.

## Error Recovery

### Model Failure

If Codex fails with one model, the executor automatically falls back to the next:

```
gpt-5.3-codex (failed) → gpt-5.2-codex (retry) → gpt-5.1-codex-max (last resort)
```

If ALL models fail:
1. Check `OPENAI_API_KEY` is valid: `codex exec --full-auto -m gpt-5.2-codex "echo hello"`
2. Check rate limits: wait 60s and retry
3. Try with a longer timeout: `-t 900`
4. Fall back to Claude Code: `/prp-claude-code-execute "PRPs/foo.md"`

### Schema Rejection

If you see `Invalid schema for response_format`:
1. Open `codex-prp-output-schema.json`
2. Find every `"type": "object"` block
3. Ensure each has `"additionalProperties": false`
4. Ensure each has ALL properties listed in `"required"`
5. Remove any `"$schema"` top-level key (OpenAI doesn't accept it)

### Validation Partial/Fail

If validation returns `partial` or `fail`:
1. Read the report: `cat /tmp/codex-prp-{name}-report.json`
2. Check `issues` array for specific failures
3. Common fixes:
   - Missing UV shebang → add `#!/usr/bin/env -S uv run --script` as first line
   - Missing PEP 723 → add `# /// script` block after shebang
   - Missing provenance → add `# Adapted from: <source> on <date>` comment
   - hooks.json not updated → manually add the entry
4. After fixing, re-run tests manually to confirm

### File Not Created

If the destination file doesn't exist after execution:
1. Check the Codex log: `cat /tmp/codex-prp-{name}-output.log`
2. Look for errors near the end of the log
3. Common causes:
   - Flag errors (Codex didn't start) → check flag compatibility
   - Sandbox restrictions (Codex couldn't write) → ensure path is under repo root
   - Timeout (Codex didn't finish) → increase with `-t`

## Troubleshooting

### Known Issues & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `unexpected argument '--ephemeral'` | Flag doesn't exist in v0.98.0 | Remove `--ephemeral` from command |
| `'additionalProperties' is required to be supplied and to be false` | OpenAI strict schema requirement | Add `"additionalProperties": false` to all objects in schema |
| `Warning: no last agent message; wrote empty content` | Codex failed before producing output | Check log for API errors; verify API key |
| `codex: command not found` | Codex CLI not installed | `npm install -g @openai/codex` |
| `Not inside trusted directory` | Missing `--skip-git-repo-check` | Add the flag (executor includes it) |
| Duration 0.2s with exit 0 | Codex started but failed immediately | Check output.log for API/schema errors |
| All tests show "No such file" | Destination file wasn't created | See "File Not Created" above |

### Diagnostic Commands

```bash
# Is Codex working at all?
echo "print hello" | codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex -

# Check all output files
ls -la /tmp/codex-prp-{name}-*

# Read the full Codex conversation
cat /tmp/codex-prp-{name}-output.log

# Check what the executor sent
cat /tmp/codex-prp-{name}-prompt.txt | head -50

# Clean up before retry
rm -f /tmp/codex-prp-{name}-*.{json,log,txt}
```

## Worked Example

Executing `PRPs/distill-dangerous-command-blocker.md` (4 points, convention-convert):

**1. Dry run:**
```bash
$ uv run .claude/skills/fork-terminal/tools/codex_prp_executor.py \
    PRPs/distill-dangerous-command-blocker.md --dry-run

Prompt written to /tmp/codex-prp-dangerous-command-blocker-prompt.txt (8710 chars)
Scoped AGENTS.md written to .claude/hooks/AGENTS.md

Codex command:
  codex exec --full-auto --skip-git-repo-check -m gpt-5.3-codex \
    -o /tmp/codex-prp-dangerous-command-blocker-result.json \
    --output-schema .../codex-prp-output-schema.json \
    -C /home/user/projects/claude-code-templates \
    --add-dir /tmp \
    - < /tmp/codex-prp-dangerous-command-blocker-prompt.txt

[DRY RUN] Exiting without executing.
```

**2. Fork:**
```bash
$ python3 .claude/skills/fork-terminal/tools/fork_terminal.py \
    --log --tool codex-prp \
    "uv run .claude/skills/fork-terminal/tools/codex_prp_executor.py \
     PRPs/distill-dangerous-command-blocker.md"

Linux terminal launched (xterm)
log_file: /tmp/fork_codex-prp_20260209_091518.log
```

**3. Monitor (poll every 10s):**
```bash
$ cat /tmp/codex-prp-dangerous-command-blocker-done.json
{
  "exit_code": 0,
  "model_used": "gpt-5.3-codex",
  "duration_seconds": 169.2
}
```

**4. Verify results:**
```
Status: success
Files created: [".claude/hooks/dangerous-command-blocker.py"]
Files modified: [".claude/hooks/hooks.json", "MANIFEST.json", ".claude/REGISTRY.md"]
Tests: 8/8 passed
Criteria: 8/8 met
Errors: []
```

**5. Independent verification:**
```bash
$ python3 -c "
import subprocess
tests = [
    ('rm -rf block', '{...rm -rf /...}', 2),
    ('.env block', '{...file_path:.env...}', 2),
    ('.env.sample allow', '{...file_path:.env.sample...}', 0),
    ('normal cmd', '{...ls -la...}', 0),
]
for name, inp, expected in tests:
    r = subprocess.run(['python3', '.claude/hooks/dangerous-command-blocker.py'],
                       input=inp, capture_output=True, text=True)
    print(f'{'PASS' if r.returncode == expected else 'FAIL'}: {name}')
"
PASS: rm -rf block
PASS: .env block
PASS: .env.sample allow
PASS: normal cmd
```

**6. Register:**
- Update adoptions.md: `deferred-to-prp` → `adopted`
- Commit and push

## Output Files Reference

All files under `/tmp/codex-prp-{name}-*`:

| File | When Written | Purpose |
|------|-------------|---------|
| `-prompt.txt` | Before Codex runs | Full prompt sent to Codex (8-15KB) |
| `-result.json` | After Codex finishes | Structured self-report (via `--output-schema`) |
| `-output.log` | During execution | Full terminal output (via `tee`) |
| `-report.json` | After validation | Combined executor + validator report |
| `-done.json` | Last | Completion flag with exit code, model, duration |

**Cleanup**: These files persist in `/tmp/` until system reboot. To clean up:
```bash
rm -f /tmp/codex-prp-{name}-*.{json,log,txt}
```

## Parallel PRP Execution

For multiple independent PRPs, fork them in parallel:

```bash
# Fork all 4 PRPs simultaneously
for prp in PRPs/distill-*.md; do
  python3 .claude/skills/fork-terminal/tools/fork_terminal.py \
    --log --tool codex-prp \
    "uv run .claude/skills/fork-terminal/tools/codex_prp_executor.py $prp"
  sleep 2  # Stagger to avoid API rate limits
done
```

**Warning**: Parallel execution may hit OpenAI rate limits. If you see failures,
switch to sequential execution or increase the stagger interval.

**Monitor all:**
```bash
ls /tmp/codex-prp-*-done.json 2>/dev/null | wc -l  # Count completed
```
