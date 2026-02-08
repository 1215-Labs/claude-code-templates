# PRP: cbass n8n Workflow Manager

**Date**: 2026-02-07
**Status**: Draft
**Complexity**: High (score 5)
**Target Repo**: cbass (multi-service AI stack)

## Summary

Build a `/cbass-workflows` command (or command group) that manages n8n workflows through the n8n API — listing, importing, exporting, validating, and syncing workflows and credentials between environments. This goes beyond simple CLI wrapping into n8n API integration with deep domain knowledge.

## Why This Is Complex

- **Multiple API calls**: n8n REST API for workflows, credentials, executions
- **Deep domain knowledge**: n8n workflow JSON structure, node types, credential references
- **Shared state**: Credential IDs differ between environments, need mapping
- **Error-prone operations**: Import can break references, export can leak secrets
- **Multi-environment**: Local dev vs VPS production with different credential IDs

## Context

### Current State
- n8n workflows stored as JSON files in `n8n-tool-workflows/` and `n8n/backup/`
- Import handled by `n8n-import` init container on startup
- Manual workflow management through n8n UI at `n8n.cbass.space`
- Credential IDs are hardcoded per environment (documented in CLAUDE.md)
- No automated workflow versioning or sync

### Pain Points (from CLAUDE.md)
- Credential management is manual — look up IDs in n8n UI
- No way to sync workflows between local and VPS
- n8n MCP returns incorrect node type information
- Workflow import can fail silently if credentials don't match

### n8n API Endpoints
```
GET  /api/v1/workflows              # List all workflows
GET  /api/v1/workflows/:id          # Get workflow by ID
POST /api/v1/workflows              # Create workflow
PUT  /api/v1/workflows/:id          # Update workflow
GET  /api/v1/credentials            # List credentials
GET  /api/v1/executions             # List executions
```
Authentication: API key via `N8N_API_KEY` env var, header `X-N8N-API-KEY`

## Proposed Commands

### `/cbass-workflows` (main)
Modes:
- `/cbass-workflows` — list all workflows with status, last execution, node count
- `/cbass-workflows "export"` — export all workflows to `n8n/backup/workflows/`
- `/cbass-workflows "import"` — import from backup with credential validation
- `/cbass-workflows "sync"` — compare local backup vs running n8n, show differences
- `/cbass-workflows "validate"` — check all workflows for broken credential refs, deprecated nodes

### Supporting Skill
Extend `cbass-context` with:
- n8n API endpoint reference
- Credential ID mapping (local ↔ VPS)
- Common node types and their credential requirements
- Workflow JSON structure reference

## Implementation Requirements

1. **API Authentication**: Read `N8N_API_KEY` from `.env` or environment
2. **Credential Mapping**: Maintain a mapping file (`n8n/credential-map.json`) between environments
3. **Safe Export**: Strip sensitive credential values from exported JSON
4. **Smart Import**: Match credentials by name (not ID), warn on mismatches
5. **Validation**: Check each workflow node has valid credential references
6. **Diff View**: Show meaningful diffs between backup and running workflows

## Dependencies

- `cbass-context` skill (for paths, API endpoints)
- n8n container must be running
- `N8N_API_KEY` must be set in `.env`
- `curl` or similar for API calls

## Estimated Effort

- Context skill extension: 30 min
- Main command with 5 modes: 2-3 hours
- Credential mapping logic: 1 hour
- Testing against live n8n: 1 hour
- Total: ~5 hours

## Acceptance Criteria

- [ ] Can list all workflows with meaningful summary
- [ ] Export preserves workflow JSON structure without secrets
- [ ] Import matches credentials by name, warns on mismatches
- [ ] Sync shows clear diff between backup and running state
- [ ] Validate catches broken credential references
- [ ] Works with both local and VPS n8n instances
