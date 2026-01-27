---
name: prp-any-cli-execute
description: |
  Execute PRP with any CLI agent

  Usage: /prp-any-cli-execute "PRPs/graphql-schema.md"

  Examples:
  /prp-any-cli-execute "PRPs/caching-layer.md"
  /prp-any-cli-execute "PRPs/logging-system.md"
  /prp-any-cli-execute "PRPs/feature-flags.md"

  Use for: Running PRPs with Codex, Gemini CLI, or any agentic tool
  See also: /prp-claude-code-execute (optimized for Claude Code)
argument-hint: <prp-file>
user-invocable: true
related:
  commands: [/prp-any-cli-create, /prp-claude-code-execute]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Bash(*)
  - Task
---

# Execute BASE PRP

Implement a feature using using the PRP file.

## PRP File: $ARGUMENTS

## Execution Process

1. **Load PRP**
   - Read the specified PRP file
   - Understand all context and requirements
   - Follow all instructions in the PRP and extend the research if needed
   - Ensure you have all needed context to implement the PRP fully
   - Do more web searches and codebase exploration as needed

2. **ULTRATHINK**
   - Think hard before you execute the plan. Create a comprehensive plan addressing all requirements.
   - Break down complex tasks into smaller, manageable steps using your todos tools.
   - Use the TodoWrite tool to create and track your implementation plan.
   - Identify implementation patterns from existing code to follow.

3. **Execute the plan**
   - Execute the PRP
   - Implement all the code

4. **Validate**
   - Run each validation command
   - Fix any failures
   - Re-run until all pass

5. **Complete**
   - Ensure all checklist items done
   - Run final validation suite
   - Report completion status
   - Read the PRP again to ensure you have implemented everything

6. **Reference the PRP**
   - You can always reference the PRP again if needed

Note: If validation fails, use error patterns in PRP to fix and retry.
