---
name: service-deployment
description: VPS service deployment workflow for the Obsidian Ecosystem Hub — from pre-flight checks through deployment verification
trigger: Docker Compose, Caddyfile, or .env changes to deploy
---

# Service Deployment Workflow

Complete workflow for deploying changes to the Obsidian Ecosystem Hub VPS (16 Docker services + Caddy reverse proxy).

Reference the `obsidian-context` skill for VPS paths, service inventory, and integration patterns.

## Workflow Sequence

```
1. /obsidian-status                  → Check current service states
         ↓
2. [Edit docker-compose.yml,         → Make changes
    Caddyfile, or .env]
         ↓
3. /obsidian-env-check               → Validate environment variables
         ↓
4. deployment-engineer agent          → Review changes for issues
         ↓
5. /obsidian-restart <service>        → Apply changes (with confirmation)
         ↓
6. /obsidian-health <service>         → Verify deployment health
         ↓
7. /obsidian-logs <service>           → Monitor for errors (30s)
         ↓
8. /devlog                            → Document changes
```

## Step Details

### Step 1: Pre-Flight Status Check
**Command**: `/obsidian-status`
- Verify all services are running before making changes
- Note any already-unhealthy services (don't confuse pre-existing issues with deployment problems)
- Check Caddy is active and routing correctly

### Step 2: Make Changes
**User action**: Edit the relevant configuration files.

Common change types:
| Change | Files to Edit | Services Affected |
|--------|---------------|-------------------|
| Add/modify Docker service | `stack/docker-compose.yml` | Target service + dependents |
| Change domain routing | `stack/Caddyfile` | Caddy + target service |
| Update environment variable | `stack/.env` | Services using that variable |
| Update Python service code | `stack/obsidian-ai-agent/` or `stack/obsidian-brain/` | Target service |
| Change deployment script | `stack/deploy.sh` | All (on next full deploy) |

### Step 3: Environment Validation
**Command**: `/obsidian-env-check`
- Verify all required env vars are set
- Check for empty or placeholder values
- Confirm new env vars (if added) are present

**Decision point**: If env check fails, fix the .env file before proceeding.

### Step 4: Change Review
**Agent**: `deployment-engineer`
- Review docker-compose.yml changes for: port conflicts, volume mount issues, dependency ordering, resource limits
- Review Caddyfile changes for: syntax, domain conflicts, reverse_proxy targets matching docker-compose ports
- Review .env changes for: security concerns, missing values referenced by services
- Flag any breaking changes or required service restart order

**Decision point**: If the agent finds issues, address them before restarting services.

### Step 5: Apply Changes
**Command**: `/obsidian-restart <service>`
- For Docker Compose changes: restart the changed service(s)
- For Caddyfile changes: use `/obsidian-caddy-reload` instead
- For .env changes: recreate the affected service(s) to pick up new env
- The command will ask for confirmation and show downstream impact

For a **full deployment** (syncing all changes to VPS):
```bash
rsync -avz stack/ hostinger-vps:/root/stack/
ssh hostinger-vps 'cd /root/stack && ./deploy.sh'
```

### Step 6: Health Verification
**Command**: `/obsidian-health <service>`
- Verify the restarted service is healthy (Docker + endpoint)
- Check dependent services weren't disrupted
- Verify SSL certificates are valid (if Caddy was changed)

**Decision point**: If health check fails:
1. Check logs immediately with `/obsidian-logs <service>`
2. If the service won't start, check dependencies with `/obsidian-health "databases"`
3. Consider rollback: `ssh hostinger-vps 'cd /root/stack && docker compose up -d <previous-image>'`

### Step 7: Log Monitoring
**Command**: `/obsidian-logs <service>`
- Watch logs for 30 seconds after deployment
- Look for startup errors, connection failures, or unexpected behavior
- Verify the service is handling requests correctly

**Decision point**: If errors are detected:
1. Analyze the error pattern (connection refused = dependency issue, crash loop = code issue)
2. Use `/rca "<error description>"` for systematic root cause analysis
3. If critical, rollback and investigate

### Step 8: Documentation
**Command**: `/devlog`
- Record what was changed and why
- Note any issues encountered during deployment
- Document the before/after service state
- Add any follow-up tasks

## Decision Points Summary

| After Step | Condition | Action |
|------------|-----------|--------|
| Step 3 | Env check fails | Fix .env, re-run check |
| Step 4 | Agent finds issues | Address issues, re-review |
| Step 5 | Restart fails | Check `/obsidian-logs`, investigate |
| Step 6 | Health check fails | Check logs, check dependencies, consider rollback |
| Step 7 | Errors in logs | `/rca`, fix, re-deploy |

## Rollback Procedure

If deployment fails and the service won't recover:

1. **Check the backup**: `ssh hostinger-vps 'ls -lt /root/backups/ | head -5'`
2. **Restore config**: `ssh hostinger-vps 'cp /root/backups/<latest>/docker-compose.yml /root/stack/'`
3. **Restart**: `ssh hostinger-vps 'cd /root/stack && docker compose up -d <service>'`
4. **Verify**: `/obsidian-health <service>`
5. **Document**: `/devlog` — record the rollback and why

## Related Components

- **Commands**: /obsidian-status, /obsidian-health, /obsidian-restart, /obsidian-logs, /obsidian-env-check, /obsidian-caddy-reload, /obsidian-vault-sync, /devlog
- **Agents**: deployment-engineer, debugger
- **Skills**: obsidian-context
- **Scripts**: stack/deploy.sh, stack/scripts/vault-sync.sh
