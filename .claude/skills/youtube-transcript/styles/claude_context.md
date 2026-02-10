# Claude Context Style Guide

Transform a YouTube video transcript into a dense, structured reference document optimized for injection into an LLM context window. Maximize information density. Minimize redundancy.

## Output Format

### 1. TL;DR
2-3 sentences. What is this about, what is the main claim, what is the primary takeaway.

### 2. Facts & Definitions
Bulleted list of every factual claim, definition, and data point stated in the transcript.
- Format: `**Term/Concept**: Definition or factual statement`
- Include version numbers, measurements, benchmarks, dates
- One fact per bullet, no compound statements

### 3. Techniques & Patterns
For each technique, pattern, or methodology discussed:
- **Name**: What it is (1 sentence)
- **When**: When to use it
- **How**: Implementation steps or key details
- **Tradeoff**: What you give up

### 4. Code & Commands
Every code snippet, CLI command, file path, and configuration mentioned:
```language
exact code or command as stated
```
Mark inferred commands with `# inferred` comment.

### 5. Opinions & Recommendations
Separate the speaker's subjective claims from facts:
- **Claim**: The opinion stated
- **Evidence**: What evidence or reasoning was given (if any)
- **Strength**: Strong (data-backed) / Medium (experience-backed) / Weak (assertion only)

### 6. Gaps & Limitations
What was NOT covered, acknowledged limitations, open questions, or areas where the speaker hedged.

### 7. Action Items
Concrete, specific next steps someone could take after consuming this content.
Numbered list, imperative voice, each under 20 words.

## Rules
- Extract EVERY technical term, tool name, and concept
- Preserve exact terminology -- do not paraphrase technical terms
- Remove ALL filler: greetings, transitions, self-references, promotional content
- Do not add information not present in the transcript
- If the transcript is ambiguous, note the ambiguity rather than guessing
- Prioritize density: this document should be 10-20% of the transcript length
- No introductory or concluding paragraphs -- start with content immediately
