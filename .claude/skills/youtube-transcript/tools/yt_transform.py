#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Standalone YouTube transcript transformer via OpenRouter.

Takes a downloaded transcript directory and a style guide, then transforms
the clean text into structured markdown using an LLM via OpenRouter.

Usage:
    yt_transform.py <video-dir> <style-name> [--style-dir DIR]

Requires OPENROUTER_API_KEY in environment or .env in current directory.
"""

import os
import sys
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
    # Also check for .env in home directory
    home_env = Path.home() / ".env"
    if home_env.is_file():
        load_dotenv(home_env)
except ImportError:
    pass

from openai import APIError, OpenAI


OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-3-flash-preview"


def get_api_key() -> str | None:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key or not key.strip():
        return None
    return key.strip()


def find_clean_text(video_dir: Path) -> Path | None:
    for f in video_dir.iterdir():
        if f.is_file() and f.name.endswith("_clean_text.txt"):
            return f
    return None


def transform_with_openrouter(style_content: str, transcript_content: str, api_key: str) -> str:
    user_content = (
        f"{style_content}\n\n---\n\n# Transcript to Transform\n\n{transcript_content}\n\n"
        "Transform the above transcript according to the style guide. "
        "Output ONLY the transformed document, no commentary or meta-discussion."
    )
    client = OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_content}],
        extra_body={"reasoning": {"enabled": True}},
    )
    message = response.choices[0].message
    content = (message.content or "").strip()
    if not content:
        raise ValueError(
            "OpenRouter returned empty content. Check model availability and response."
        )
    return content


def resolve_style_dir() -> Path:
    """Resolve the default styles directory (sibling of tools/)."""
    return Path(__file__).resolve().parent.parent / "styles"


def main() -> int:
    args = sys.argv[1:]

    if not args or len(args) < 2 or args[0] in ('-h', '--help'):
        default_styles = resolve_style_dir()
        print("Usage: yt_transform.py <video-dir> <style-name> [--style-dir DIR]")
        print()
        print("Transforms a downloaded transcript using a style guide via OpenRouter.")
        print(f"Default styles directory: {default_styles}")
        if default_styles.is_dir():
            print("\nAvailable styles:")
            for f in sorted(default_styles.glob("*.md")):
                print(f"  {f.stem}")
        return 0 if args and args[0] in ('-h', '--help') else 1

    video_dir = Path(args[0]).resolve()
    style_name = args[1]
    style_dir = resolve_style_dir()

    # Parse optional flags
    i = 2
    while i < len(args):
        if args[i] == '--style-dir' and i + 1 < len(args):
            style_dir = Path(args[i + 1]).resolve()
            i += 2
        else:
            i += 1

    style_file = style_dir / f"{style_name}.md"

    if not video_dir.is_dir():
        print(f"Error: Directory not found: {video_dir}", file=sys.stderr)
        return 1

    if not style_file.is_file():
        print(f"Error: Style guide not found: {style_file}", file=sys.stderr)
        if style_dir.is_dir():
            print("Available styles:", file=sys.stderr)
            for f in sorted(style_dir.glob("*.md")):
                print(f"  {f.stem}", file=sys.stderr)
        return 1

    clean_text_path = find_clean_text(video_dir)
    if not clean_text_path:
        print(f"Error: No *_clean_text.txt found in {video_dir}", file=sys.stderr)
        return 1

    api_key = get_api_key()
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set.", file=sys.stderr)
        print(
            "Set it in your environment, or create a .env file with:",
            file=sys.stderr,
        )
        print("  OPENROUTER_API_KEY=your_key_here", file=sys.stderr)
        return 1

    title = clean_text_path.stem.replace("_clean_text", "")
    output_file = video_dir / f"{title}_{style_name}.md"
    today = date.today().isoformat()

    style_content = style_file.read_text(encoding="utf-8")
    transcript_content = clean_text_path.read_text(encoding="utf-8")

    print(f"Transforming transcript...", file=sys.stderr)
    print(f"  Input: {clean_text_path}", file=sys.stderr)
    print(f"  Style: {style_name}", file=sys.stderr)
    print(f"  Output: {output_file}", file=sys.stderr)

    try:
        body = transform_with_openrouter(style_content, transcript_content, api_key)
    except (ValueError, APIError) as e:
        print(f"Error: OpenRouter request failed: {e}", file=sys.stderr)
        return 1

    front_matter = f"""---
type: tutorial
category: development
domain:
  - youtube-transcript
  - {style_name}
source: youtube-transcript-transform
created: {today}
status: inbox-triage
tags:
  - tutorial
  - {style_name}
  - transformed-transcript
summary: Transformed YouTube transcript using {style_name} style guide.
enriched_at: ""
---

"""

    output_file.write_text(front_matter + body, encoding="utf-8")
    print(f"\nCreated: {output_file}", file=sys.stderr)

    # Print result path to stdout for programmatic use
    print(str(output_file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
