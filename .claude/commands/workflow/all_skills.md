---
name: workflow:all_skills
description: |
  List all available skills from your system prompt.

  Usage: /all_skills

  Use for: Discovering what skills are available in the current session
user-invocable: true
---

# List All Skills

Display all available skills that can be used in the current session.

## What It Does

Scans the system prompt and lists:
- Skill names
- Brief descriptions
- When to invoke each skill

## When to Use

- **Discovering capabilities** - see what's available
- **Finding the right skill** - when you're not sure which skill fits your task
- **Documentation** - understanding the skill library

## When NOT to Use

- **You know the skill name** - just invoke it directly
- **Need detailed skill docs** - invoke the specific skill to see full documentation
