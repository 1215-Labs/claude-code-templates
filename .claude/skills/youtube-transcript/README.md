# YouTube Transcript Skill

Download and transform YouTube video transcripts for use in Claude Code sessions.
Standalone — all tools are self-contained PEP 723 UV scripts with inline dependencies.

## Quick Start

```bash
# Download transcript
/youtube-transcript "https://youtube.com/watch?v=abc123"

# Download + transform with Claude-optimized style
/youtube-transcript "abc123" "claude_context"

# List available styles
/youtube-transcript "styles"

# Re-transform with a different style
/youtube-transcript "transform" "./transcripts/My_Video" "knowledge_base"
```

## Prerequisites

- `uv` — Python package runner ([install](https://docs.astral.sh/uv/getting-started/installation/))
- `yt-dlp` — YouTube downloader (`uv tool install yt-dlp`)
- For transforms: `OPENROUTER_API_KEY` in environment or `.env` file

## Styles

| Style | Best For |
|-------|----------|
| `coding_agent` | Developer tutorials — step-by-step instructions |
| `knowledge_base` | Learning & reference — concepts, patterns, tools |
| `diy_project` | Maker/DIY projects — materials, steps, safety |
| `claude_context` | LLM context injection — dense, structured, zero filler |

## Direct Tool Usage

```bash
# Download only
uv run .claude/skills/youtube-transcript/tools/yt_download.py "VIDEO_URL" --output-dir ./transcripts

# Transform existing transcript
uv run .claude/skills/youtube-transcript/tools/yt_transform.py "./transcripts/Video_Title" "claude_context"
```

## Skill-Evaluator Integration

When evaluating reference submodules, add a `VIDEOS.md` to the submodule root with author
YouTube URLs. The skill-evaluator can then include creator video context in evaluations.

See `SKILL.md` for full integration details.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Full skill definition with argument routing and eval integration |
| `tools/yt_download.py` | Standalone transcript downloader (PEP 723) |
| `tools/yt_transform.py` | Standalone transcript transformer (PEP 723) |
| `styles/*.md` | Style guide templates for transformation |
