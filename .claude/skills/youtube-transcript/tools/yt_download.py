#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "youtube-transcript-api>=1.2.4",
#     "pytube>=15.0.0",
#     "yt-dlp>=2025.12.8",
# ]
# ///
"""Standalone YouTube transcript downloader with 3-method fallback.

Downloads video transcripts and saves timestamped + clean text versions.
No external project dependencies — all logic is embedded.

Usage:
    yt_download.py <youtube-url-or-id> [--output-dir DIR]

Output:
    Creates <output-dir>/<safe_title>/ with:
    - <title>_formatted_transcript.txt (timestamped: seconds|text)
    - <title>_clean_text.txt (plain text, deduplicated, paragraphed)
    Prints JSON report to stdout on success.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    if re.match(r'^[\w-]{11}$', url_or_id):
        return url_or_id

    parsed = urlparse(url_or_id)

    if parsed.netloc in ('youtu.be', 'www.youtu.be'):
        return parsed.path.lstrip('/')

    if parsed.netloc in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
        if parsed.path == '/watch':
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                return query_params['v'][0]
        if parsed.path.startswith(('/v/', '/embed/')):
            return parsed.path.split('/')[2]

    return url_or_id


def get_safe_title(video_id: str) -> str:
    """Fetch video title via yt-dlp and sanitize for filesystem use."""
    try:
        cmd = ["yt-dlp", "--get-title", f"https://www.youtube.com/watch?v={video_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        title = result.stdout.strip()
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        return safe_title
    except Exception as e:
        print(f"Warning: Could not fetch title for {video_id} using yt-dlp: {e}", file=sys.stderr)
        return video_id


def _parse_srt(srt_content: str) -> list[tuple[float, str]]:
    """Parse SRT format to [(timestamp_seconds, text), ...]."""
    entries = []
    blocks = re.split(r'\n\n+', srt_content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        timestamp_line = lines[1]
        text_lines = lines[2:]

        match = re.match(r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})', timestamp_line)
        if match:
            hours, minutes, seconds, millis = map(int, match.groups())
            start_seconds = hours * 3600 + minutes * 60 + seconds + millis / 1000
            text = ' '.join(text_lines).strip()
            if text:
                entries.append((start_seconds, text))

    return entries


def _parse_vtt(vtt_content: str) -> list[tuple[float, str]]:
    """Parse VTT format to [(timestamp_seconds, text), ...].

    Handles YouTube's auto-generated VTT with progressively building captions.
    """
    raw_entries = []
    lines = vtt_content.split('\n')

    i = 0
    while i < len(lines) and not re.match(r'^\d{2}:\d{2}', lines[i]):
        i += 1

    while i < len(lines):
        line = lines[i].strip()

        match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->', line)
        if not match:
            match = re.match(r'(\d{2}):(\d{2})\.(\d{3})\s*-->', line)
            if match:
                minutes, seconds, millis = map(int, match.groups())
                start_seconds = minutes * 60 + seconds + millis / 1000
            else:
                i += 1
                continue
        else:
            hours, minutes, seconds, millis = map(int, match.groups())
            start_seconds = hours * 3600 + minutes * 60 + seconds + millis / 1000

        i += 1
        text_lines = []
        while i < len(lines):
            text_line = lines[i].strip()
            if not text_line or re.match(r'^\d{2}:\d{2}', text_line):
                break
            text_line = re.sub(r'<[^>]+>', '', text_line)
            text_lines.append(text_line)
            i += 1

        text = ' '.join(text_lines).strip()
        if text:
            raw_entries.append((start_seconds, text))

    # Deduplicate progressive captions
    entries = []
    for i, (ts, text) in enumerate(raw_entries):
        if i + 1 < len(raw_entries):
            next_text = raw_entries[i + 1][1]
            if next_text.startswith(text):
                continue
        entries.append((ts, text))

    return entries


def _fetch_via_transcript_api(video_id: str) -> list[tuple[float, str]]:
    """Primary method: youtube-transcript-api."""
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    return [(entry.start, entry.text) for entry in transcript]


def _fetch_via_pytube(video_id: str) -> list[tuple[float, str]]:
    """Fallback 1: pytube captions."""
    from pytube import YouTube

    url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url)

    caption = None
    if 'en' in yt.captions:
        caption = yt.captions['en']
    elif 'a.en' in yt.captions:
        caption = yt.captions['a.en']
    elif yt.captions:
        caption = list(yt.captions.values())[0]

    if not caption:
        raise Exception("No captions available via pytube")

    srt_content = caption.generate_srt_captions()
    return _parse_srt(srt_content)


def _fetch_via_ytdlp(video_id: str) -> list[tuple[float, str]]:
    """Fallback 2: yt-dlp subtitle download."""
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(id)s.%(ext)s")

        cmd = [
            "yt-dlp",
            "--write-auto-sub",
            "--write-sub",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "-o", output_template,
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        vtt_files = [f for f in os.listdir(tmpdir) if f.endswith('.vtt')]

        if not vtt_files:
            raise Exception(f"yt-dlp did not produce subtitle file. stderr: {result.stderr}")

        vtt_path = os.path.join(tmpdir, vtt_files[0])
        with open(vtt_path, 'r', encoding='utf-8') as f:
            vtt_content = f.read()

        return _parse_vtt(vtt_content)


def fetch_transcript_with_fallbacks(video_id: str) -> list[tuple[float, str]] | None:
    """Try each method in sequence until one succeeds."""
    methods = [
        ("youtube-transcript-api", _fetch_via_transcript_api),
        ("pytube", _fetch_via_pytube),
        ("yt-dlp", _fetch_via_ytdlp),
    ]

    errors = []
    for name, method in methods:
        try:
            result = method(video_id)
            print(f"Success with {name}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"{name} failed: {e}", file=sys.stderr)
            errors.append((name, str(e)))
            continue

    print("All transcript methods failed:", file=sys.stderr)
    for name, error in errors:
        print(f"  - {name}: {error}", file=sys.stderr)
    return None


def _extract_unique_text(entries: list[tuple[float, str]]) -> str:
    """Extract unique text from entries, removing overlapping portions."""
    if not entries:
        return ""

    result_text = entries[0][1].strip()

    for i in range(1, len(entries)):
        current_text = entries[i][1].strip()

        overlap_len = 0
        for j in range(1, min(len(result_text), len(current_text)) + 1):
            if result_text[-j:] == current_text[:j]:
                overlap_len = j

        if overlap_len > 0:
            new_part = current_text[overlap_len:].strip()
            if new_part:
                result_text += " " + new_part
        else:
            result_text += " " + current_text

    return result_text


def _format_as_paragraphs(text: str) -> str:
    """Format text with paragraph breaks every ~3 sentences."""
    sentences = re.split(r'([.!?])\s+', text)

    full_sentences = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in '.!?':
            full_sentences.append(sentences[i] + sentences[i + 1])
            i += 2
        else:
            if sentences[i].strip():
                full_sentences.append(sentences[i])
            i += 1

    paragraphs = []
    for i in range(0, len(full_sentences), 3):
        paragraph = ' '.join(full_sentences[i:i + 3])
        paragraphs.append(paragraph)

    return '\n\n'.join(paragraphs)


def download_transcript(
    video_id: str, output_dir: str, title: str | None = None
) -> list[tuple[float, str]] | None:
    """Download transcript using fallback chain and save to files."""
    entries = fetch_transcript_with_fallbacks(video_id)

    if not entries:
        print(f"Error: Could not download transcript for {video_id}", file=sys.stderr)
        return None

    file_prefix = title if title else video_id

    raw_path = os.path.join(output_dir, f"{file_prefix}_formatted_transcript.txt")
    with open(raw_path, "w") as f:
        for start, text in entries:
            f.write(f"{start}|{text}\n")

    clean_path = os.path.join(output_dir, f"{file_prefix}_clean_text.txt")
    with open(clean_path, "w") as f:
        unique_text = _extract_unique_text(entries)
        formatted_text = _format_as_paragraphs(unique_text)
        f.write(formatted_text)

    return entries


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print("Usage: yt_download.py <youtube-url-or-id> [--output-dir DIR]")
        print()
        print("Downloads YouTube transcript with 3-method fallback chain.")
        print("Default output: ./transcripts/<video_title>/")
        return 0 if args else 1

    url_or_id = args[0]
    output_base = "./transcripts"

    i = 1
    while i < len(args):
        if args[i] == '--output-dir' and i + 1 < len(args):
            output_base = args[i + 1]
            i += 2
        else:
            i += 1

    video_id = extract_video_id(url_or_id)
    print(f"Video ID: {video_id}", file=sys.stderr)

    title = get_safe_title(video_id)
    output_dir = os.path.join(output_base, title)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}", file=sys.stderr)

    entries = download_transcript(video_id, output_dir, title=title)

    if not entries:
        return 1

    # Compute word count from clean text
    clean_path = os.path.join(output_dir, f"{title}_clean_text.txt")
    word_count = 0
    if os.path.isfile(clean_path):
        with open(clean_path) as f:
            word_count = len(f.read().split())

    files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]

    report = {
        "title": title,
        "video_id": video_id,
        "output_dir": os.path.abspath(output_dir),
        "files": sorted(files),
        "word_count": word_count,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
