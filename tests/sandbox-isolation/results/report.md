# Sandbox Isolation Test Report

**Date:** 2026-02-10T04:32:18.671557+00:00
**Environment:** E2B sandbox (fullstack-vue-fastapi-node22)

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 18 |
| Passed | 18 |
| Failed | 0 |
| Errors | 0 |
| Pass Rate | 100.0% |

## Results by Component

### ruff-validator

| Test | Status | Detail |
|------|--------|--------|
| clean file -> allow | PASS | rc=0, output={} |
| lint errors -> block | PASS | rc=0, output={'decision': 'block', 'reason': 'Lint check failed:\nF401 [*] `os`  |
| non-.py -> skip | PASS | rc=0, output={} |
| empty stdin -> allow | PASS | rc=0, output={} |
| missing uvx -> graceful | PASS | rc=0, output={} |

### ty-validator

| Test | Status | Detail |
|------|--------|--------|
| clean file -> allow | PASS | rc=0, output={} |
| type errors -> block | PASS | rc=0, output={'decision': 'block', 'reason': 'Type check failed:\nerror[invalid- |
| non-.py -> skip | PASS | rc=0, output={} |
| empty stdin -> allow | PASS | rc=0, output={} |
| missing uvx -> graceful | PASS | rc=0, output={} |

### meta-agent

| Test | Status | Detail |
|------|--------|--------|
| frontmatter schema | PASS | all checks passed |
| body sections | PASS | all checks passed |

### team-builder

| Test | Status | Detail |
|------|--------|--------|
| frontmatter schema | PASS | all checks passed |
| body sections | PASS | all checks passed |

### team-validator

| Test | Status | Detail |
|------|--------|--------|
| frontmatter schema | PASS | all checks passed |
| body sections | PASS | all checks passed |
| no write/edit tools (read-only) | PASS | all checks passed |

### hooks.json

| Test | Status | Detail |
|------|--------|--------|
| ruff/ty registered correctly | PASS | both registered with Write\|Edit matcher |
