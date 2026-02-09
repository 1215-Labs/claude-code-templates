---
name: obsidian-env-check
description: |
  Validate all required environment variables for the VPS stack.

  Usage: /obsidian-env-check

  Examples:
  /obsidian-env-check            — Compare .env.template vs .env, flag missing/empty vars
  /obsidian-env-check "local"    — Check local stack/.env file
  /obsidian-env-check "vps"      — Check VPS /root/stack/.env file via SSH

  Best for: Pre-deployment validation, debugging "service won't start" issues
  See also: /obsidian-status (service status), /obsidian-restart (apply env changes)
argument-hint: "[local|vps]"
user-invocable: true
related:
  commands: [obsidian/obsidian-status, obsidian/obsidian-restart]
  skills: [obsidian-context]
  workflows: [service-deployment]
thinking: auto
allowed-tools:
  - Bash(ssh hostinger-vps*)
  - Read
  - Grep
  - Glob
---

# Obsidian VPS Environment Variable Check

**User context**: $ARGUMENTS

Reference the `obsidian-context` skill for paths and service inventory.

## Step 1: Determine Check Target

If `$ARGUMENTS` specifies "vps", check on VPS via SSH.
If `$ARGUMENTS` specifies "local" or is empty, check the local repository's `stack/.env`.

## Step 2: Gather Environment Files

**Local check:**
```bash
# Read template (defines required variables)
cat stack/.env.example 2>/dev/null || cat stack/.env.template 2>/dev/null || echo "No template found"

# Read actual env file
cat stack/.env 2>/dev/null || echo "No .env file found"
```

**VPS check:**
```bash
# Read VPS env file (show variable names only, NOT values for security)
ssh hostinger-vps 'cd /root/stack && cat .env 2>/dev/null | grep -v "^#" | grep "=" | cut -d= -f1 | sort'

# Also check if template exists on VPS
ssh hostinger-vps 'ls /root/stack/.env.example /root/stack/.env.template 2>/dev/null'
```

## Step 3: Validate

For each variable found in the template:

1. **Present**: Variable exists in .env
2. **Empty**: Variable exists but has no value (e.g., `VAR=` or `VAR=""`)
3. **Missing**: Variable in template but not in .env
4. **Placeholder**: Variable still has placeholder value (e.g., `changeme`, `your-key-here`, `xxx`)

Additionally check for:
- **Sensitive variables without values**: Any var containing `PASSWORD`, `SECRET`, `KEY`, `TOKEN` that is empty
- **Hardcoded defaults that should be unique**: Variables that `deploy.sh` auto-generates with `openssl rand`
- **Extra variables**: Variables in .env not in template (may be obsolete)

**IMPORTANT**: Do NOT display actual secret values. Only show variable names and whether they are set/empty/missing.

## Step 4: Service-Variable Mapping

Using the service inventory from `obsidian-context`, map which services need which env vars:

| Variable | Required By |
|----------|-------------|
| `POSTGRES_PASSWORD` | postgres-vector, all DB consumers |
| `MINIO_ROOT_PASSWORD` | minio, obsidian-agent, obsidian-brain, rag-pipeline |
| `NEO4J_PASSWORD` | neo4j, obsidian-brain |
| `REDIS_PASSWORD` | redis, langfuse |
| `OPENAI_API_KEY` | obsidian-agent, rag-pipeline |
| `SLACK_*` | obsidian-agent |
| `LANGFUSE_*` | langfuse-web, langfuse-worker |

## Step 5: Present Results

```
## Environment Variable Check

### Target: [local|VPS]

### Status Summary
- Total variables: N
- Set: N
- Empty: N
- Missing: N
- Placeholder: N

### Issues Found
| Variable | Status | Required By | Impact |
|----------|--------|-------------|--------|
| OPENAI_API_KEY | MISSING | obsidian-agent, rag-pipeline | Embeddings will fail |
| NEO4J_PASSWORD | EMPTY | neo4j, obsidian-brain | Auth will fail |

### All Variables
| Variable | Status |
|----------|--------|
| POSTGRES_PASSWORD | Set |
| MINIO_ROOT_PASSWORD | Set |
| ...

### Recommendations
- [if missing vars: "Set these before deploying"]
- [if placeholder vars: "Replace placeholder values"]
- [if all set: "All environment variables configured correctly"]
```
