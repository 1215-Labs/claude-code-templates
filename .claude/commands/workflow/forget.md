---
name: forget
description: |
  Remove a fact, preference, or decision from persistent memory.

  Usage:
  /forget "DEC-002"           - Remove a specific decision
  /forget "my email address"  - Search and remove matching entries
  /forget "bun"               - Remove entries mentioning bun
argument-hint: "<ID or search term to remove>"
user-invocable: true
related:
  commands: [remember, memory]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Forget

**Remove from persistent memory**: $ARGUMENTS

## Steps

1. **Search**: Search across ALL memory files for the specified term:
   - `~/.claude/memory/*.md` (global memory)
   - `.claude/memory/*.md` (project memory)
   - `.claude/memory/sessions/*.md` (session logs)

   Use Grep to find matching lines. The search term could be:
   - A decision ID like "DEC-002" (exact section match)
   - A keyword like "bun" (line-level match)
   - A phrase like "my email address" (fuzzy match)

2. **Show Matches**: Display ALL matches found with:
   - Which file they're in
   - The matching line(s) with surrounding context
   - Line numbers for reference

3. **Confirm**: Ask the user which matches to remove. Options:
   - Remove all matches
   - Remove specific matches by number
   - Cancel

4. **Remove**: Delete the matching lines or sections from the memory files. For decision entries (DEC-NNN), remove the entire `### DEC-NNN` section including all sub-items.

5. **Confirm Removal**: Tell the user what was removed and from which files.

## Notes

- Never remove section headings (## lines) - only content within them
- If removing the last entry under a section, leave the section heading
- For session logs: remove the entire session file if requested
- If no matches found, inform the user and suggest checking with `/memory "search term"`
