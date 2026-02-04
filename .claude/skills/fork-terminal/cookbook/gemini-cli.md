# Purpose

Create a new Gemini CLI agent to execute the command in non-interactive prompt mode.

## Variables

DEFAULT_MODEL: gemini-3-pro-preview
HEAVY_MODEL: gemini-3-pro-preview
BASE_MODEL: gemini-3-pro-preview
FAST_MODEL: gemini-2.5-flash

## Fallback Chain

If the primary model fails, try models in this order:
1. gemini-3-pro-preview (default)
2. gemini-2.5-flash (fallback)
3. gemini-2.0-flash-exp (emergency fallback)

## Instructions

- Use the `-p` flag (prompt mode) for non-interactive execution, NOT `-i` (interactive mode)
- Always use `--approval-mode yolo` for automatic tool approvals (more explicit than `-y`)
- For the --model argument, use DEFAULT_MODEL if not specified. If 'fast' is requested, use FAST_MODEL. If 'heavy' is requested, use HEAVY_MODEL.
- IMPORTANT: Ensure GEMINI_API_KEY is exported before running the command

## Command Template

```bash
export GEMINI_API_KEY="${GEMINI_API_KEY}" && gemini -p "PROMPT" --model MODEL --approval-mode yolo
```

## Examples

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

## Authentication

Gemini CLI supports two authentication methods:

### 1. API Key (GEMINI_API_KEY)
```bash
export GEMINI_API_KEY="your-key-here" && gemini -p "PROMPT" --model MODEL --approval-mode yolo
```

### 2. OAuth (Google Account)
If using OAuth authentication, run `gemini` interactively first to complete the OAuth flow, then forked terminals will use the stored tokens.

Note: Check `~/.gemini/settings.json` for `security.auth.selectedType` to see which method is configured.

## Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "hasSeenIdeIntegrationNudge" prompt | Use `-p` (prompt mode) NOT `-i` (interactive mode) |
| "GEMINI_API_KEY not set" | Export the key explicitly OR ensure OAuth is configured |
| OAuth tokens expired | Re-authenticate with `gemini` interactively |
| Rate limiting errors | Switch to gemini-2.5-flash or wait |
| Command hangs | Check if auth is valid, use timeout |
| Model not available | Fall back to next model in chain |

## Deprecated Patterns

Do NOT use these deprecated patterns:
- `-i` flag for interactive mode - Always use `-p` for forked terminals
- `-y` flag alone - Use `--approval-mode yolo` for clarity
- Interactive prompt without explicit API key - Always export GEMINI_API_KEY
