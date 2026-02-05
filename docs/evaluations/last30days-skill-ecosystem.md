# Ecosystem Analysis: last30days-skill

**Date:** February 4, 2026
**Target:** `references/last30days-skill/`
**Analyst:** Ecosystem Sub-Agent

## 1. Executive Summary

The `last30days-skill` introduces a high-value, distinct capability to the Claude Code ecosystem: **Social Trend Analysis & Prompt Engineering**. Unlike existing researchers (`technical-researcher`, `library-researcher`) that focus on official documentation and architectural stability, this skill mines ephemeral community knowledge (Reddit, X) to surface "what is working right now."

It fills a critical gap in **LSP-aware development** by providing the "vibe check" for tools that change faster than their documentation (e.g., AI models, new frameworks). Its ability to generate "copy-paste ready prompts" makes it an accelerator for the `codebase-analyst` and `new-developer` workflows.

**Recommendation:** **Strong Fit**. The skill compliments the existing robust engineering tools with agile, community-driven insights.

## 2. Scorecard

| Dimension | Score (1-5) | Justification |
| :--- | :---: | :--- |
| **Novelty** | **5** | Introduces social listening (Reddit/X) and recency-weighted synthesis, which is entirely absent in the current agent set. |
| **Gap Analysis** | **4** | Fills the need for "undocumented best practices" and "prompt engineering" support, a growing requirement for AI-native development. |
| **Overlap** | **1** | Minimal overlap. Existing researchers explicitly prioritize "official docs" and "peer-reviewed content," whereas this targets "community sentiment." |
| **Leverage** | **5** | High combinatorial potential. Can feed "latest bugs" to `code-reviewer` or "newest library features" to `library-researcher`. |

## 3. Novelty Map

| Capability | Existing Ecosystem | `last30days-skill` | Status |
| :--- | :--- | :--- | :--- |
| **Source Material** | Official Docs, GitHub, StackOverflow (`library-researcher`) | Reddit, X (Twitter), Viral Trends | **New** |
| **Time Horizon** | Historical, Stable, "Timely" | Strictly < 30 Days (Recency Bias) | **New** |
| **Output Type** | Technical Reports, Code Snippets | Prompt Packs, Trend Summaries | **New** |
| **Primary Goal** | Correctness, Stability, Feasibility | "What works now", "Vibe", "Community Consensus" | **New** |

## 4. Overlap Matrix

| Component | Potential Overlap | Resolution / Distinction |
| :--- | :--- | :--- |
| `technical-researcher` | Both perform "research" and "synthesis". | `technical-researcher` produces formal architectural reports. `last30days` produces fast, informal trend summaries. They address different questions (Why? vs. What's trending?). |
| `library-researcher` | Both look for "how to use X". | `library-researcher` looks for *correct* usage via docs. `last30days` looks for *hacky/clever* usage via community discussions. |
| `agent-browser` | Can browsing Reddit/X manually. | `last30days` automates the *synthesis* and *ranking* of social data, which would be tedious to do manually with `agent-browser`. |

## 5. Gap Analysis

**Unmet Needs Filled:**
1.  **Prompt Engineering Support:** Developers often struggle to prompt AI tools effectively. `last30days` generates optimized prompts based on community success.
2.  **Zero-Day Discovery:** Official docs lag behind releases. Community chatter (X/Reddit) is the only source for bugs/features < 1 week old.
3.  **Opinion/Sentiment Mining:** "Is library X dead?" or "Are people hating the new React feature?" are questions existing agents cannot answer reliably.

**Importance:**
In an "LSP-aware" environment where dependencies change weekly, having a sensor for "breaking changes" or "new meta" is crucial for maintaining developer velocity.

## 6. High-Value Combinations

| Combination | Workflow | Value Proposition |
| :--- | :--- | :--- |
| **`last30days` + `library-researcher`** | **"The Reality Check"** | `library-researcher` fetches the docs. `last30days` fetches the bugs people are complaining about *this week*. Prevents using "correct" code that is currently broken. |
| **`last30days` + `skill-evaluator`** | **"Meta-Skill Evolution"** | Use `last30days` to find "best new Claude Code skills" or "MCP servers", then use `skill-evaluator` to install and test them. |
| **`last30days` + `code-reviewer`** | **"Trend-Aware Review"** | `code-reviewer` checks style. `last30days` checks if the patterns used are considered "outdated" or "harmful" by the community recently (e.g., "Don't use X, it was deprecated last week"). |
| **`last30days` + `new-developer`** | **"Onboarding Vibe"** | Helps new devs understand *current* best practices and terminology that might not be in the 3-year-old `README.md`. |

## 7. Workflow Integration Points

*   **Command:** `/last30days` (Direct usage for ad-hoc queries).
*   **Workflow:** Add as a step in `workflows/feature-development.md` -> "Research Phase":
    *   *Step 1:* `library-researcher` (Docs)
    *   *Step 2:* `last30days` (Community Pitfalls)
*   **Agent Tool:** Give `codebase-analyst` the ability to call `last30days` to explain "weird" modern code patterns it encounters (e.g., "Why is this code using this weird React hook pattern?" -> Search Reddit).
