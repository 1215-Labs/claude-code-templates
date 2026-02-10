---
name: youtube-transcript
description: |
  Download YouTube video transcripts and optionally transform them with style guides.

  Usage: /youtube-transcript "<url-or-id>" ["style"]

  Examples:
  /youtube-transcript "https://youtube.com/watch?v=abc123"
  /youtube-transcript "abc123" "coding_agent"
  /youtube-transcript "abc123" "claude_context"
  /youtube-transcript "styles"
  /youtube-transcript "transform" "Generated_Data/My_Video" "knowledge_base"

  Best for: Ingesting YouTube video content into your session context
argument-hint: "<url-or-id>" ["style"]
user-invocable: true
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
---

# YouTube Transcript

**Input**: $ARGUMENTS

Reference the `youtube-transcript` skill in `.claude/skills/youtube-transcript/SKILL.md`
for full argument routing, prerequisites, style guide reference, and troubleshooting.

## Variables

```
SKILL_DIR: .claude/skills/youtube-transcript
DOWNLOAD_TOOL: .claude/skills/youtube-transcript/tools/yt_download.py
TRANSFORM_TOOL: .claude/skills/youtube-transcript/tools/yt_transform.py
STYLES_DIR: .claude/skills/youtube-transcript/styles
```

## Phase 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **First arg**: YouTube URL, video ID, `styles`, or `transform`
- **Second arg** (optional): Style name (for download+transform) or video directory (for transform)
- **Third arg** (optional): Style name (for transform action)

Routing:
- If first arg is `styles` or `list-styles` → Phase 3a (list styles)
- If first arg is `transform` → Phase 3c (re-transform)
- If first arg looks like a URL or 11-char ID → Phase 2 then Phase 3b (download)

## Phase 2: Pre-flight

1. Verify `uv` is available: `uv --version`
2. If a style was requested AND it's not just a download:
   - Check `OPENROUTER_API_KEY` is set: `echo $OPENROUTER_API_KEY | head -c4`
   - If not set, check for `.env` file and warn the user with setup instructions
3. Verify the requested style exists in `STYLES_DIR` (if style was given)

## Phase 3: Execute

### 3a: List Styles
```bash
ls -1 .claude/skills/youtube-transcript/styles/*.md | xargs -I{} basename {} .md
```
Show each style name with a one-line description from the skill's style reference table.

### 3b: Download (+ optional transform)
```bash
# Download transcript
uv run .claude/skills/youtube-transcript/tools/yt_download.py "<url-or-id>" --output-dir ./transcripts

# If style was provided, also transform
uv run .claude/skills/youtube-transcript/tools/yt_transform.py "./transcripts/<title>" "<style>"
```

### 3c: Re-transform existing transcript
```bash
uv run .claude/skills/youtube-transcript/tools/yt_transform.py "<video-dir>" "<style>"
```

## Phase 4: Report & Offer

After successful execution:

1. **Report results**: Video title, output directory, files created, word count
2. **If download only** (no style): Ask the user:
   - "Would you like me to read the transcript and summarize it?"
   - "Or transform it with a style? Available: coding_agent, knowledge_base, diy_project, claude_context"
3. **If `claude_context` style was used**: Offer to read the output directly into context:
   - "The transcript has been formatted for context injection. Want me to read it now?"
4. **If any other style was used**: Show the output file path and offer to read it

## Error Handling

| Error | Recovery |
|-------|----------|
| uv not found | Show install command: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| API key missing | Show `.env` setup: `echo 'OPENROUTER_API_KEY=sk-or-...' > .env` |
| Download failed all 3 methods | Show which methods failed, suggest checking video accessibility |
| Style not found | List available styles from STYLES_DIR |
| Transform returned empty | Check OpenRouter API key validity, check model availability |
