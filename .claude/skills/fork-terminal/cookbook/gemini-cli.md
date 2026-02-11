# Purpose

Create a new Gemini CLI agent to execute the command.

## Variables

DEFAULT_MODEL: gemini-3-pro-preview
HEAVY_MODEL: gemini-3-pro-preview
BASE_MODEL: gemini-3-pro-preview
FAST_MODEL: gemini-2.5-flash
AUTO_MODEL: auto

## Gemini Strengths

- 1M token context window (massive codebase understanding)
- 78% SWE-bench with Flash model
- Best for: Codebase exploration, architecture analysis, pattern discovery
- Use Pro for: Complex multi-step reasoning, architecture decisions
- Built-in auto-routing: `auto` model picks Pro or Flash based on task complexity

## Model Selection

| Task | Model | Alias |
|------|-------|-------|
| Quick exploration | gemini-2.5-flash | `flash` |
| Auto-routed (default) | auto | `auto` |
| Codebase analysis | gemini-3-flash-preview | `flash` (preview) |
| Complex reasoning | gemini-3-pro-preview | `pro` |
| Architecture review | gemini-3-pro-preview | `pro` |
| Cheapest / simple | gemini-2.5-flash-lite | `flash-lite` |

### Model Aliases

Gemini CLI supports short aliases for model selection:

| Alias | Resolves To | Best For |
|-------|------------|---------|
| `auto` | Routes between Pro/Flash | Default — let Gemini decide |
| `pro` | gemini-3-pro-preview | Complex reasoning, architecture |
| `flash` | gemini-3-flash-preview | Quick analysis, file discovery |
| `flash-lite` | gemini-2.5-flash-lite | Cheapest, simple tasks |

## Fallback Chain

Gemini CLI has **built-in model fallback** with error classification (quota, auth, transient). Models fall back automatically.

Manual fallback order:
1. gemini-3-pro-preview (default)
2. gemini-3-flash-preview (fallback)
3. gemini-2.5-flash (emergency fallback)

## Instructions

- Always use `--approval-mode yolo` for automatic tool approvals (more explicit than `-y`)
- For the --model argument, use DEFAULT_MODEL if not specified. If 'fast' is requested, use FAST_MODEL. If 'heavy' is requested, use HEAVY_MODEL.

## Mode: Non-Interactive (Default)

Use the `-p` flag (prompt mode) for autonomous execution.

### Command Template

```bash
gemini -p "PROMPT" --model MODEL --approval-mode yolo
```

### Examples

**Basic execution:**
```bash
gemini -p "analyze this codebase and summarize the architecture" --model gemini-3-pro-preview --approval-mode yolo
```

**With explicit API key propagation (for forked terminals):**
```bash
export GEMINI_API_KEY="${GEMINI_API_KEY}" && gemini -p "PROMPT" --model gemini-3-pro-preview --approval-mode yolo
```

**With output logging:**
```bash
gemini -p "PROMPT" --model gemini-3-pro-preview --approval-mode yolo 2>&1 | tee /tmp/fork_gemini_$(date +%s).log
```

**Fast model for quick tasks:**
```bash
gemini -p "PROMPT" --model gemini-2.5-flash --approval-mode yolo
```

**Auto-routed model:**
```bash
gemini -p "PROMPT" --model auto --approval-mode yolo
```

## Mode: Interactive

Use the `-i` flag for an interactive session.

### Command Template

```bash
export GEMINI_API_KEY="${GEMINI_API_KEY}" && gemini -i --model MODEL --approval-mode yolo
```

### Examples

**Interactive session:**
```bash
export GEMINI_API_KEY="${GEMINI_API_KEY}" && gemini -i --model gemini-3-pro-preview --approval-mode yolo
```

**Interactive session with flash:**
```bash
export GEMINI_API_KEY="${GEMINI_API_KEY}" && gemini -i --model gemini-2.5-flash --approval-mode yolo
```

## Structured JSON Output

### JSON Mode (Single Response)

Use `--output-format json` for structured, parseable output:

```bash
gemini -p "PROMPT" --model MODEL --approval-mode yolo --output-format json
```

**Response schema:**
```json
{
  "response": "The model's text response...",
  "stats": {
    "models": {
      "gemini-3-pro-preview": {
        "api": { "totalRequests": 5, "totalErrors": 0, "totalLatencyMs": 12000 },
        "tokens": { "prompt": 5000, "candidates": 2000, "total": 7000, "cached": 0, "thoughts": 500, "tool": 200 }
      }
    },
    "tools": {
      "totalCalls": 8, "totalSuccess": 8, "totalFail": 0,
      "totalDurationMs": 3000
    },
    "files": { "totalLinesAdded": 0, "totalLinesRemoved": 0 }
  },
  "error": null
}
```

### Stream JSON Mode (Real-Time Events)

Use `--output-format stream-json` for newline-delimited JSON events:

```bash
gemini -p "PROMPT" --model MODEL --approval-mode yolo --output-format stream-json
```

**Event types:** `init`, `message`, `tool_use`, `tool_result`, `error`, `result`

### Piping and Processing

```bash
# Extract just the response text
gemini -p "Query" --output-format json | jq -r '.response'

# Save structured output
gemini -p "Query" --output-format json > output.json

# Monitor events in real-time
gemini -p "Long task" --output-format stream-json | while read line; do
  echo "$line" | jq -r '.type'
done
```

## Multi-Directory Exploration

Use `--include-directories` to add additional directories to Gemini's analysis scope:

```bash
gemini -p "PROMPT" --model auto --approval-mode yolo --include-directories src/,lib/,tests/
```

Useful for monorepo exploration or cross-project analysis.

## Gemini Skills System

Gemini has a built-in skills system using `.gemini/skills/SKILL.md` files.

### Skill Management

```bash
# List all discovered skills
gemini skills list

# Install from git repository
gemini skills install https://github.com/user/repo.git

# Link local skills directory
gemini skills link /path/to/skills --scope workspace

# Enable/disable skills
gemini skills enable <name>
gemini skills disable <name>
```

### Skill Locations (Discovery Order)

1. **Workspace**: `.gemini/skills/` (highest precedence)
2. **User**: `~/.gemini/skills/`
3. **Extension**: Bundled in npm packages

### Creating Skills

Each skill is a directory with a `SKILL.md` file:
```
.gemini/skills/my-skill/
├── SKILL.md           # Instructions and workflow
└── resources/         # Optional bundled files
```

Skills are activated automatically by the model based on task context. The `activate_skill` tool loads the SKILL.md into the context on demand (progressive disclosure).

## GEMINI.md Context Files

Gemini auto-loads context from hierarchical instruction files:

| Level | Path | Precedence |
|-------|------|-----------|
| Global | `~/.gemini/GEMINI.md` | Lowest |
| Project | `.gemini/GEMINI.md` | Higher |
| Subdirectory | `subdir/.gemini/GEMINI.md` | Highest |

### Features

- **File imports**: `@./components/instructions.md` to include other files
- **Convention injection**: Add project coding standards, patterns, preferences
- **Configurable**: Change context file names via `context.fileName` in settings.json:
  ```json
  { "context": { "fileName": ["AGENTS.md", "CONTEXT.md", "GEMINI.md"] } }
  ```

### Managing Context

```
/memory show              # Display loaded context files
/memory refresh           # Re-scan GEMINI.md files
/memory add <text>        # Append to ~/.gemini/GEMINI.md
```

## Session Resume

Resume a previous Gemini session to continue interrupted work:

```bash
gemini --resume latest          # Resume most recent session
gemini --list-sessions          # View available sessions
gemini --delete-session 5       # Clean up old sessions
```

## Restricting Tools

Pre-approve or restrict specific tools for safer exploration:

```bash
# Pre-approve read-only tools
gemini -p "PROMPT" --allowed-tools grep,read_file,ls,glob --approval-mode yolo

# Fully autonomous (all tools approved)
gemini -p "PROMPT" --approval-mode yolo
```

## Authentication

Gemini CLI supports three authentication methods, each routing to a different endpoint with separate quota pools.

### 1. OAuth (Default — Google Account)
If `~/.gemini/settings.json` has `security.auth.selectedType: "oauth-personal"` and cached tokens exist in `~/.gemini/oauth_creds.json`, OAuth is used automatically.

- **Endpoint**: `cloudcode-pa.googleapis.com`
- **Quota**: 60 RPM / 1,000 RPD (free tier)
- **Note**: OAuth takes precedence over API key when cached tokens exist

```bash
gemini -p "PROMPT" --model MODEL --approval-mode yolo
```

### 2. API Key (GEMINI_API_KEY)
Routes to AI Studio endpoint with separate quota. Only works when **no cached OAuth tokens** exist (e.g., in E2B sandboxes) OR when OAuth creds are cleared.

- **Endpoint**: `generativelanguage.googleapis.com`
- **Quota**: 10 RPM / 250 RPD (free tier), higher with paid tier
- **Models**: Flash only on free tier

```bash
export GEMINI_API_KEY="your-key-here" && gemini -p "PROMPT" --model gemini-2.5-flash --approval-mode yolo
```

### 3. Vertex AI
Routes to Google Cloud Vertex AI. Overrides both OAuth and API key when `GOOGLE_GENAI_USE_VERTEXAI=true` is set.

- **Endpoint**: `{region}-aiplatform.googleapis.com`
- **Quota**: Dynamic shared (highest ceiling)
- **Setup**: Requires GCP project with Vertex AI API enabled

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_API_KEY="your-vertex-api-key"
gemini -p "PROMPT" --model gemini-2.5-flash --approval-mode yolo
```

### Credential Precedence
1. `GOOGLE_GENAI_USE_VERTEXAI=true` → Vertex AI (always wins)
2. Cached OAuth in `~/.gemini/oauth_creds.json` → OAuth endpoint
3. `GEMINI_API_KEY` → AI Studio endpoint (only if no OAuth cache)

### Per-Project Auth via `.gemini/.env`
Gemini CLI auto-loads env vars from `.gemini/.env` (searches up from cwd, then `~/.gemini/.env`):
```
# .gemini/.env
GEMINI_API_KEY=your-key-here
```

## Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "hasSeenIdeIntegrationNudge" prompt | Use `-p` (prompt mode) NOT `-i` (interactive mode) |
| "GEMINI_API_KEY not set" | Export the key explicitly OR ensure OAuth is configured |
| OAuth tokens expired | Re-authenticate with `gemini` interactively |
| Rate limiting errors | Switch to gemini-2.5-flash or wait |
| Command hangs | Check if auth is valid, use timeout |
| Model not available | Fall back to next model in chain (automatic with built-in fallback) |
| JSON mixed with other output | Parse backwards from end of output for `{"response":` block |
| Large prompt shell escaping | Use `$(cat /tmp/prompt.txt)` with `-p` instead of inline strings |

## Deprecated Patterns

Do NOT use these deprecated patterns:
- `-y` flag alone - Use `--approval-mode yolo` for clarity
- Omitting `--output-format json` for automated tasks - Always use it for parseable output
- Running 5+ parallel forks - Max 2 concurrent, stagger by 30-60s
- Assuming `GEMINI_API_KEY` overrides OAuth - It does NOT when cached tokens exist
