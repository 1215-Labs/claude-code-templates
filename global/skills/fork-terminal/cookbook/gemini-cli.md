# Purpose

Create a new Gemini CLI agent to execute the command.

## Variables

DEFAULT_MODEL: gemini-3-flash
HEAVY_MODEL: gemini-3-pro
BASE_MODEL: gemini-3-flash
FAST_MODEL: gemini-3-flash

## Gemini Strengths

- 1M token context window (massive codebase understanding)
- 78% SWE-bench with Flash model
- Best for: Codebase exploration, architecture analysis, pattern discovery
- Use Pro for: Complex multi-step reasoning, architecture decisions

## Model Selection

| Task | Model | Thinking Level |
|------|-------|----------------|
| Quick exploration | gemini-3-flash | minimal |
| Codebase analysis | gemini-3-flash | medium |
| Complex reasoning | gemini-3-pro | high |
| Architecture review | gemini-3-pro | high |

## Instructions

- Before executing the command, run `gemini --help` to understand the command and its options.
- Always use interactive mode with the -i flag as the last flag, right before the prompt (e.g., `gemini --model gemini-3-flash -y -i "prompt here"`)
- For the --model argument, use the DEFAULT_MODEL if not specified. If 'fast' is requested, use the FAST_MODEL. If 'heavy' is requested, use the HEAVY_MODEL.
- Always run with `--yolo` (or `-y` for short)
- For complex tasks, add `--thinking-level medium` or `--thinking-level high`
