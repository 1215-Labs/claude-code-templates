---
name: youtube-transcript
description: |
  Download YouTube video transcripts (3-method fallback) and transform into structured
  markdown via OpenRouter. Standalone skill with embedded tools — no external repo dependency.
  Integrates with skill-evaluator to enrich reference submodule evaluations with creator
  video context.
version: 1.0.0
category: research
user-invocable: true
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
related:
  skills: [skill-evaluator, reference-distill]
  commands: [workflow/youtube-transcript]
---

# YouTube Transcript Skill

Download YouTube video transcripts with a 3-method fallback chain (youtube-transcript-api,
pytube, yt-dlp) and optionally transform them into structured markdown using style guides
via OpenRouter LLM. All tools are self-contained PEP 723 UV scripts with inline dependencies.

## When to Use

- Research from YouTube tutorials, talks, or interviews
- Ingest video content into Claude context for analysis
- Extract technical knowledge from developer videos
- Build a transcript library for reference
- Enrich skill evaluations with creator video context (see Skill-Evaluator Integration)

## When NOT to Use

- Live streams with no transcript available
- Videos with no auto-captions or manual subtitles
- Private, age-restricted, or region-locked videos

## Prerequisites

- `uv` installed (`uv --version`)
- `yt-dlp` on PATH (for title fetching and fallback subtitle download)
- For transforms: `OPENROUTER_API_KEY` in environment or `.env` file

## Argument Routing

| Input | Action |
|-------|--------|
| `<url-or-id>` | Download transcript to `./transcripts/` |
| `<url-or-id> <style>` | Download + transform with style |
| `styles` | List available style guides |
| `transform <dir> <style>` | Re-transform an existing transcript |

## Tool Scripts

### `tools/yt_download.py` — Transcript Downloader

Standalone PEP 723 script. Downloads transcript with 3-method fallback chain.

```bash
uv run .claude/skills/youtube-transcript/tools/yt_download.py <url-or-id> [--output-dir DIR]
```

- Default output: `./transcripts/<safe_title>/`
- Creates: `<title>_formatted_transcript.txt` (timestamped) + `<title>_clean_text.txt` (plain)
- Prints JSON report to stdout: `{"title", "video_id", "output_dir", "files", "word_count"}`
- Dependencies: youtube-transcript-api, pytube, yt-dlp (all inline via PEP 723)

### `tools/yt_transform.py` — Transcript Transformer

Standalone PEP 723 script. Transforms clean text via OpenRouter LLM with a style guide.

```bash
uv run .claude/skills/youtube-transcript/tools/yt_transform.py <video-dir> <style> [--style-dir DIR]
```

- Styles resolved from `styles/` dir (sibling of `tools/`)
- Output: `<video-dir>/<title>_<style>.md` with YAML front-matter
- Prints output file path to stdout
- Dependencies: openai, python-dotenv (inline via PEP 723)

## Style Guide Reference

| Style | Optimized For | Key Sections |
|-------|---------------|--------------|
| `coding_agent` | Developer tutorials | Overview, Prerequisites, Key Concepts, Steps, Troubleshooting, Technical Reference |
| `knowledge_base` | Learning & reference | Summary, Key Concepts, Patterns, Tools, Quotes, Applications, Related Topics |
| `diy_project` | Maker/DIY projects | Project Summary, Materials/BOM, Tools, Safety, Instructions, Variations |
| `claude_context` | LLM context injection | TL;DR, Facts, Techniques, Code, Opinions, Gaps, Action Items |

The `claude_context` style produces dense, low-redundancy output (10-20% of transcript length)
designed for injection into Claude's context window.

## Skill-Evaluator Integration

Reference submodules often have associated YouTube videos where authors explain design intent,
usage patterns, and known limitations. This skill can enrich skill evaluations with that context.

### Convention: Declaring Associated Videos

Reference submodules can declare associated YouTube videos via a `VIDEOS.md` file in the
submodule root:

```markdown
# Associated Videos

- https://youtube.com/watch?v=abc123 "Building the plugin architecture"
- https://youtube.com/watch?v=def456 "Deep dive: hook system design"
```

Alternatively, pass URLs directly when invoking the skill-evaluator.

### Integration Workflow

During skill evaluation (Step 2b — Ecosystem Snapshot):

1. Check if the reference submodule has a `VIDEOS.md` file
2. If found (or if user provides URLs), download transcripts:
   ```bash
   uv run .claude/skills/youtube-transcript/tools/yt_download.py <url> \
     --output-dir /tmp/skill-eval-{name}-transcripts
   ```
3. Transform with `claude_context` style:
   ```bash
   uv run .claude/skills/youtube-transcript/tools/yt_transform.py \
     /tmp/skill-eval-{name}-transcripts/<title> claude_context
   ```
4. Append transformed content to the ecosystem snapshot under a
   `## Creator Video Context` section
5. This enriches the ecosystem-fit and risk-adoption agents with:
   - Author's design rationale and intent
   - Known limitations acknowledged in video
   - Maintenance philosophy and commitment signals
   - Hidden use cases or patterns not documented in code

### What This Enables

| Evaluation Agent | Benefit |
|-----------------|---------|
| Ecosystem Fit (Gemini Pro) | Richer novelty analysis — understands WHY the author built it, not just what |
| Risk & Adoption (Gemini Flash) | Maintenance signals from author's statements about future plans, commitment |
| Final Synthesis (Opus) | Creator intent context for resolving contradictions between agents |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No transcript available" | Video may not have captions; check manually on YouTube |
| yt-dlp not found | `uv tool install yt-dlp` or `pip install yt-dlp` |
| OPENROUTER_API_KEY not set | Create `.env` with `OPENROUTER_API_KEY=sk-or-...` |
| All 3 transcript methods fail | Video may be private, age-restricted, or region-locked |
| Transform returns empty | Check API key validity and model availability on OpenRouter |
| UV not found | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
