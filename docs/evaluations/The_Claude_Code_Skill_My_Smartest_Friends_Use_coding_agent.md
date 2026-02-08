---
type: tutorial
category: development
domain:
  - youtube-transcript
  - coding_agent
source: youtube-transcript-transform
created: 2026-02-05
status: inbox-triage
tags:
  - tutorial
  - coding_agent
  - transformed-transcript
summary: Transformed YouTube transcript using coding_agent style guide.
enriched_at: ""
---

# Coding Agent Style Guide: Last 30 Days for Claude Code

## 1. Overview
This guide teaches how to integrate the "Last 30 Days" skill into Claude Code to enhance prompting and development workflows. It leverages real-time trending data from X (Twitter), Reddit, and the web to provide "superpowers" for competitive research, software architecture planning, and content generation. This is designed for developers, founders, and solopreneurs operating at a mid-to-advanced level with AI coding agents.

## 2. Prerequisites
- **Claude Code**: Access to the Anthropic terminal-based coding agent ($20/month tier minimum recommended).
- **OpenAI API Key**: Required for Reddit data access (via OpenAI’s data partnership).
- **XAI API Key**: Required for searching X (Twitter).
- **Terminal Access**: A standard shell account or a Mac environment.

## 3. Key Concepts

| Concept | Definition |
|---------|------------|
| **Last 30 Days** | A specialized skill for Claude Code that searches X, Reddit, and the web for data limited to the previous month. |
| **Prompt Priming** | The technique of running research first to feed the LLM context before asking it to perform a specific task or build software. |
| **Compound Engineering** | A workflow planning skill used to transition from research data to technical software architecture and PRDs. |
| **Skill** | A modular functionality or plugin that can be called within the Claude Code environment. |
| **Shell Account** | A hosted terminal environment (e.g., a $4/month solution) used to run agents when local Mac hardware is unavailable. |

## 4. Steps

### Step 1: Initialize Research
**Action**: Execute a research query to gather recent trends or technical data to ground the agent's knowledge.
**Command**: 
```bash
last 30 days [topic_to_research]
```
**Expected Result**: Claude Code searches Reddit, X, and the web, returning a summary of findings including specific threads, posts, and web results from the last 30 days.

### Step 2: Architecture & Workflow Planning
**Action**: Use current research to generate a technical implementation plan or business strategy.
**Command**:
```bash
# Workflow setup using Compound Engineering
workflows plan 
```
**Expected Result**: The agent proposes a structural plan (e.g., an enterprise SAS platform architecture) based on the context from Step 1.
**Notes**: User recommends asking the agent to keep it simple initially.

### Step 3: View & Edit Strategy
**Action**: Review the generated plan in a text editor to ensure technical components align with requirements.
**Command**:
```bash
bbedit [filename] # inferred
```
**Expected Result**: The plan opens in BBEdit (or the user's preferred editor) for inspection.

### Step 4: Execute Build or POC
**Action**: Instruct the agent to build the software based on the validated plan.
**Command**:
```bash
build # inferred
```
**Expected Result**: Claude Code begins creating repository structures, setting up environments (e.g., TypeScript, NodeJS, Postgres), and writing code.

### Step 5: Visual Content Refinement (Optional)
**Action**: Request design specifications or specific framework prompts based on trending aesthetics.
**Command**:
```bash
last 30 days what webpage designs are getting the most love right now?
```
**Expected Result**: A detailed design prompt or implementation strategy (e.g., "Anti-grid composition," "Nature distilled warm cream background") derived from current trends.

## 5. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| General technical errors in terminal | Complex shell environment or syntax errors | Take a screenshot and upload it to a separate ChatGPT (o1/Thinking) window for debugging. |
| Unable to paste screenshots into terminal | Operating system keyboard shortcut conflict | Use `Control+V` instead of `Command+V` within the terminal window. |
| Missing recent data | Lack of API authorization | Ensure XAI and OpenAI API keys are correctly configured in the skill settings. |

## 6. Technical Reference

**Tools/Commands**
| Tool | Description |
|------|-------------|
| `last 30 days` | The primary skill command for time-limited research. |
| `workflows plan` | Command for triggering the planning agent (Compound Engineering). |
| `Claude Code` | The CLI-based agent from Anthropic. |
| `OpenAI API` | Used for accessing Reddit data. |
| `XAI API` | Used for accessing X (Twitter) data. |

**File Paths**
- No specific file paths mentioned, though the user referenced opening a "plan" file via `BBEdit`.

**Code Snippets**

*Figma/Design Prompt (derived from trends):*
```text
Design that feels warm and human, not cold sass. 
Layout: Anti-grid composition. 
Hero section: Use asymmetrical balance, headline left, product screenshots floating right at angle. 
Sections: Flow organic with varied spacing (not rigid 12 column uniformity). 
Typography: One oversized display headline paired with small body text. 
Add a single handdrawn underline or circle accent. 
Colors: Warm cream background, charcoal text, one muted accent (avoid harsh pure white).
```

## 7. Key Takeaways
- **The "Kung Fu" Hack**: Run research on high-level frameworks (like "best prompting techniques for tool X") even if you don't plan to read the results; the agent uses that context to drastically improve its output quality.
- **API Synergy**: The "Last 30 Days" tool effectively bundles Reddit, X, and Web APIs into a single prompt-priming workflow.
- **Context over Complexity**: Simple, short prompts (e.g., "I'm a former smart oven entrepreneur") are sufficient if the agent is first primed with trending data about the target audience or industry.
- **Interactive Debugging**: For non-engineers, using a separate LLM window (like ChatGPT) specifically to interpret terminal errors via screenshots is a critical workflow move.

## 8. Resources
- **Last 30 Days Skill**: [Link provided in tutorial description]
- **Matt Van Horn on X**: @mattvanhorn
- **Claude Code**: Anthropic’s official CLI tool.
- **Compound Engineering**: Planning skill for Claude Code.