# Code-to-Deploy Alignment Audit

Use this template when forking Gemini for code-to-deploy verification during `/repo-audit` Phase 1. This fork only launches when deploy configuration is detected.

## Variables

- `{REPO_PATH}` - Absolute path to the target repository
- `{REPO_NAME}` - Directory basename
- `{RUN_DIR}` - Run output directory
- `{DEPLOY_CONFIGS}` - List of deploy config files detected (e.g., "Dockerfile, docker-compose.yml, .github/workflows/deploy.yml")

## Prompt Template

```
Audit deployment alignment for the repository at {REPO_PATH}.

## Context

- Repository: {REPO_NAME}
- Path: {REPO_PATH}
- Deploy configs detected: {DEPLOY_CONFIGS}

## Your Task

Verify that deployment configuration accurately reflects the codebase's requirements. Check that what gets deployed matches what the code expects — ports, dependencies, environment variables, build artifacts, and service configurations.

First, determine the **authoritative deployment mechanism**. A repo may have multiple deploy configs (Docker for local, CI for prod). Identify which is primary and note any conflicts between them.

## Checks

### 1. Dockerfile Alignment (if present)

- **Base image version**: Does it match the project's runtime version? (e.g., `node:20` when package.json engines says `>=18`)
- **System dependencies**: Are all required system packages installed? (e.g., native modules need build tools)
- **Build command**: Does the Dockerfile's build step match package.json scripts?
- **Exposed ports**: Do EXPOSE directives match the application's configured port?
- **COPY/ADD paths**: Do all referenced source paths exist in the repo?
- **Multi-stage outputs**: Does the final stage copy the correct build artifacts?
- **Working directory**: Does WORKDIR match where the code expects to run?
- **CMD/ENTRYPOINT**: Does the start command match what the code expects?
- **Build args**: Are all ARG values documented or have defaults?

### 2. Docker Compose Alignment (if present)

- **Service names**: Match what the code expects (e.g., database connection strings)
- **Port mappings**: External:internal ports are consistent with app config
- **Volume mounts**: Mounted paths exist in the repo
- **Environment variables**: All required env vars are either set or have defaults
- **Depends_on**: Service dependencies match actual runtime dependencies
- **Network configuration**: Services that need to communicate share a network
- **Health checks**: Health check commands reference valid endpoints

### 3. CI/CD Pipeline (if present)

- **Build steps**: Use correct commands and match project's build system
- **Test steps**: Match the project's test framework and commands
- **Node/Python/Go version**: Matches what the project requires
- **Deploy target**: Artifact pushed to the right location
- **Environment secrets**: All referenced secrets are documented
- **Conditional logic**: Branch/tag filters make sense for the project
- **Cache configuration**: Cache paths match the package manager's cache location

### 4. Reverse Proxy / Server Config (if present — Caddyfile, nginx.conf, etc.)

- **Upstream addresses**: Match application host:port
- **Route paths**: Match application route definitions
- **SSL/TLS configuration**: Cert paths exist or are properly managed
- **Static file paths**: Match build output directory
- **Headers**: Security headers match what the app expects (CORS, CSP)
- **Timeouts**: Reasonable for the application type

### 5. Environment Variables

- **Code references**: All `process.env.X`, `os.environ["X"]`, `env::var("X")` etc. are documented
- **No hardcoded secrets**: No API keys, passwords, tokens, or connection strings in source
- **.env.example completeness**: Every env var used in code has an entry in .env.example (or equivalent)
- **Default values**: Env vars without defaults that could cause crashes are flagged
- **Naming consistency**: Env var names follow a consistent pattern (e.g., `DB_HOST` vs `DATABASE_HOST`)

### 6. Build Artifacts

- **Output directory**: Build output goes where deploy expects to find it
- **Asset paths**: Static assets served from the correct location
- **Source maps**: Generated if expected, excluded if not wanted in production
- **Entry point**: The deployed entry point file actually gets built

## Scoring

Apply the Code-to-Deploy rubric (100 points):

| Criterion | Points | Check |
|-----------|--------|-------|
| Dockerfile installs all deps | +20 | Build stage covers all required packages |
| CI builds what deploy expects | +20 | Build output matches deploy target |
| Env vars documented and used | +15 | Every referenced env var is in .env.example |
| Port/host configs consistent | +10 | App ports match Docker/proxy config |
| Build artifacts match deploy | +15 | Output dir matches what deploy copies |
| Health check endpoints exist | +10 | If deploy expects health check, code has it |
| Secrets not hardcoded | +10 | No credentials in source files |

Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)

## Gating Issues

These cap the overall audit grade at C:
- Secrets/credentials hardcoded in source
- Deploy config references files that don't exist
- Port mismatch between app and deploy config (app won't be reachable)

## Output Requirements

Write your output as structured JSON to stdout. Use exactly this schema:

{
  "layer": "code-to-deploy",
  "executive_summary": "2-3 sentences summarizing deployment alignment",
  "score": 78,
  "grade": "C",
  "total_issues": 5,
  "by_severity": {"HIGH": 1, "MEDIUM": 2, "LOW": 2},
  "gating_issues": [
    {
      "issue": "API key hardcoded in src/config/stripe.ts line 12",
      "evidence": "const STRIPE_KEY = 'sk_live_abc123...'"
    }
  ],
  "findings": [
    {
      "severity": "HIGH",
      "category": "deploy-mismatch",
      "description": "Dockerfile exposes port 3000 but app listens on port 8080",
      "source_path": "Dockerfile",
      "source_line": 28,
      "claim": "EXPOSE 3000",
      "reality": "src/index.ts sets port to process.env.PORT || 8080",
      "status": "MISMATCH",
      "fix_suggestion": "Change Dockerfile EXPOSE to 8080 or update app default port"
    }
  ],
  "evidence_index": ["Dockerfile", "docker-compose.yml", ".github/workflows/deploy.yml", "src/index.ts", ".env.example"],
  "scoring_breakdown": [
    {
      "criterion": "Dockerfile installs all deps",
      "points_possible": 20,
      "points_awarded": 20,
      "notes": "All system deps covered, multi-stage build correct"
    }
  ]
}
```

## Tips

1. **Identify the authoritative deploy** — don't assume Docker is canonical; the repo might primarily deploy via Vercel/CI
2. **Check port chains** — trace port from app config -> Dockerfile EXPOSE -> docker-compose ports -> reverse proxy upstream
3. **Env vars are critical** — a missing env var can crash production silently
4. **Hardcoded secrets are always HIGH** — even in example/test files, flag them
5. **Health checks matter** — if deploy has a health check but the endpoint doesn't exist, deploys will fail
6. **Be conservative with scoring** — deployment issues are production issues
7. **Note which deploy mechanism is authoritative** — helps the engineer prioritize fixes
