# Compound Engineering Plugin Structural Review

**Executive Summary**
Overall score: **3.65 / 5.00**. The codebase is modular and readable, with a clear separation between parsing, conversion, and target-specific writers. The test suite covers CLI flows, conversion logic, and edge cases such as path traversal guards. Documentation is extensive (README, CLAUDE.md, AGENTS.md, docs site), but multiple component-count and version references are inconsistent across files, which is a reliability risk for adopters.

**Scorecard**
| Dimension | Score (1-5) | Weight | Weighted |
| --- | --- | --- | --- |
| Code Architecture | 4 | 25% | 1.00 |
| Documentation Quality | 3 | 20% | 0.60 |
| Testing | 4 | 20% | 0.80 |
| Metadata & Distribution | 3 | 15% | 0.45 |
| Code Quality Signals | 4 | 20% | 0.80 |
| **Total** | **3.65** | **100%** | **3.65** |

**Detailed Findings**

**Code Architecture (4/5)**
- Clear separation of concerns: CLI commands are isolated in `src/commands/*` with a thin entrypoint in `src/index.ts:1-20`, conversions live in `src/converters/*`, and target writers are in `src/targets/*`. This keeps parsing, conversion, and output responsibilities isolated. `src/index.ts:1-20`, `src/commands/convert.ts:11-119`, `src/converters/claude-to-opencode.ts:64-187`, `src/converters/claude-to-codex.ts:10-181`, `src/targets/index.ts:1-29`.
- Parser and filesystem utilities are centralized, reducing duplication. `src/parsers/claude.ts:16-247`, `src/utils/files.ts:4-63`.
- Minor duplication in CLI logic between `convert` and `install` (target validation, permission parsing, option building). This is manageable but a candidate for shared helpers to reduce drift risk. `src/commands/convert.ts:57-118`, `src/commands/install.ts:59-121`.

**Documentation Quality (3/5)**
- Strong baseline documentation: root README covers install paths and CLI usage, AGENTS.md includes workflow and provider checklist, and CLAUDE.md documents repository structure and update workflows. `README.md:1-68`, `AGENTS.md:1-48`, `CLAUDE.md:1-200`.
- The plugin reference README is detailed, enumerating agents, commands, skills, and operational notes. `plugins/compound-engineering/README.md:1-199`.
- Documentation inconsistency risk: component counts and MCP server counts disagree across docs and metadata. `plugins/compound-engineering/README.md:7-12`, `plugins/compound-engineering/.claude-plugin/plugin.json:2-32`, `docs/index.html:6-199`, `CLAUDE.md:20-23`.
- README states OpenCode output defaults to `~/.opencode`, but install defaults to `~/.config/opencode` per implementation and comments. `README.md:33-35`, `src/commands/install.ts:173-180`.

**Testing (4/5)**
- Parser tests include positive fixture coverage and explicit path traversal rejection cases. `tests/claude-parser.test.ts:12-88`, `src/parsers/claude.ts:117-247`.
- Conversion tests validate permission mapping, model normalization, hooks conversion, and MCP translation. `tests/converter.test.ts:9-170`, `src/converters/claude-to-opencode.ts:64-392`.
- Codex conversion tests cover prompt/skill generation, Task syntax rewriting, slash command rewrite rules, and description truncation. `tests/codex-converter.test.ts:44-203`, `src/converters/claude-to-codex.ts:10-167`.
- CLI tests exercise install, convert, list, and GitHub fetch paths, which is good end-to-end coverage. `tests/cli.test.ts:29-248`, `src/commands/install.ts:135-223`.

**Metadata & Distribution (3/5)**
- Package metadata is present with a public bin entry, scripts, and minimal dependency surface. `package.json:1-26`.
- Plugin metadata is defined for marketplace distribution. `plugins/compound-engineering/.claude-plugin/plugin.json:1-32`, `.claude-plugin/marketplace.json:1-36`.
- Version drift risk: CLI package version `0.1.1` does not align with plugin marketplace version `2.28.0`, and docs reference `2.28.0` in the site. This may be intentional (CLI vs plugin), but should be clarified in docs or release notes to avoid confusion for adopters. `package.json:1-26`, `plugins/compound-engineering/.claude-plugin/plugin.json:1-32`, `docs/index.html:156-165`.

**Code Quality Signals (4/5)**
- Error handling is explicit for unknown targets, invalid permissions, and git clone failures. `src/commands/convert.ts:58-71`, `src/commands/install.ts:60-222`.
- Path traversal is guarded when loading custom component and MCP paths, preventing escape from the plugin root. `src/parsers/claude.ts:177-247`, `tests/claude-parser.test.ts:72-88`.
- Type coverage is explicit with typed plugin structures and bundles, improving maintainability. `src/types/claude.ts:1-64`, `src/types/opencode.ts:1-40`, `src/types/codex.ts:1-21`.

**Critical Files**
| File | Why It Matters | Notes |
| --- | --- | --- |
| `src/index.ts:1-20` | CLI entrypoint and subcommand wiring | High-level UX surface for conversions. |
| `src/commands/convert.ts:57-118` | Core conversion flow | Target selection, permissions, output, extra targets. |
| `src/commands/install.ts:59-223` | Install flow including GitHub fetch | Cleanup safety and default output root behavior. |
| `src/parsers/claude.ts:16-247` | Claude plugin loader | Parsing logic and path safety checks. |
| `src/converters/claude-to-opencode.ts:64-392` | OpenCode conversion and permissions | Tool mapping, hooks, permission policies. |
| `src/converters/claude-to-codex.ts:10-167` | Codex conversion | Prompt/skill generation and syntax transforms. |
| `src/targets/opencode.ts:5-52` | OpenCode output writer | Output layout and file copy rules. |
| `src/targets/codex.ts:6-91` | Codex output writer | Prompts/skills/config TOML generation. |
| `plugins/compound-engineering/.claude-plugin/plugin.json:1-32` | Plugin metadata | Versioning and description for marketplace. |
| `.claude-plugin/marketplace.json:1-36` | Marketplace catalog | Distribution metadata for plugins. |

**Red Flags**
- Component counts and MCP server counts are inconsistent across the doc site, plugin README, and CLAUDE.md. This risks user confusion and undermines trust in release metadata. `docs/index.html:6-199`, `plugins/compound-engineering/README.md:7-12`, `CLAUDE.md:20-23`, `plugins/compound-engineering/.claude-plugin/plugin.json:2-32`.
- README states default OpenCode output is `~/.opencode`, but install defaults to `~/.config/opencode`. This will produce incorrect expectations for CLI users. `README.md:33-35`, `src/commands/install.ts:173-180`.
- Version identifiers differ between CLI package (`0.1.1`) and plugin (`2.28.0`) without explicit explanation, which can complicate release tracking. `package.json:1-4`, `plugins/compound-engineering/.claude-plugin/plugin.json:2-4`, `docs/index.html:156-165`.

**Green Flags**
- Strong modularity and explicit typing across parsers, converters, targets, and utilities. `src/parsers/claude.ts:16-247`, `src/converters/claude-to-opencode.ts:64-392`, `src/targets/index.ts:1-29`, `src/types/claude.ts:1-64`.
- Defensive parsing with path containment checks and negative tests for traversal. `src/parsers/claude.ts:241-247`, `tests/claude-parser.test.ts:72-88`.
- CLI integration tests cover install, convert, list, and GitHub fetch workflows. `tests/cli.test.ts:29-248`.
