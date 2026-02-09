# Distillation Plan: {eval_name}

**Generated**: {date}
**Source Evaluation**: `docs/evaluations/{eval_name}-eval.md`
**Verdict**: {verdict} ({overall_score}/5)
**Source Repo**: `{source_repo}`

---

## Source Evaluations

| Evaluation | Verdict | Score | Extractions | Direct | PRP |
|------------|---------|-------|-------------|--------|-----|
{eval_table_rows}

## Extraction Queue

### Priority 1 (Core)

| # | Source File | Destination | Type | Adaptation | Effort | Deps |
|---|------------|-------------|------|------------|--------|------|
{priority_1_rows}

### Priority 2 (Validators)

| # | Source File | Destination | Type | Adaptation | Effort | Deps |
|---|------------|-------------|------|------------|--------|------|
{priority_2_rows}

### Priority 3 (Enhanced)

| # | Source File | Destination | Type | Adaptation | Effort | Deps |
|---|------------|-------------|------|------------|--------|------|
{priority_3_rows}

## Conflicts

{conflicts_section}

> No conflicts detected.

## Execution Order

Based on dependency analysis and batch scoring:

{execution_order}

## Execution Mode Summary

| Mode | Count | Components |
|------|-------|------------|
| **Direct** (simple: 1-3 pts) | {direct_count} | {direct_list} |
| **PRP** (complex: 4+ pts) | {prp_count} | {prp_list} |

## Registry Updates

### MANIFEST.json Entries

```json
{manifest_entries}
```

### REGISTRY.md Changes

- Quick Lookup: {registry_quick_lookup}
- Category sections: {registry_categories}
- Component counts: {count_changes}

### Memory Records

- **Decisions**: DEC-{next_dec}: Adopt patterns from {eval_name}
- **Adoptions**: ADO-{first_ado} through ADO-{last_ado}
- **Tasks**: {task_count} follow-up tasks

---

## Next Steps

After approval:
1. Direct extractions will be written immediately
2. Complex extractions will generate PRPs at `PRPs/distill-{name}.md`
3. MANIFEST.json and REGISTRY.md will be updated
4. `validate-docs.py` will run to verify
5. `install-global.py` will create symlinks
