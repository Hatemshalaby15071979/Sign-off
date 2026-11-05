# Signoff — Mapping Table Guide

The mapping table (`OWNER/mapping-table.csv`) is the **single source of truth** connecting client questionnaire questions to evidence patterns. It must be signed by the human owner before any pack can be built.

## Table Schema

| Column | Description | Example |
|--------|-------------|---------|
| `rule_id` | Unique rule identifier | `R-001` |
| `pattern_id` | Evidence pattern ID (from `EVIDENCE_SPECS`) | `QA-HUMAN-REVIEW` |
| `source_qid` | Question ID from client questionnaire | `Q-101` |
| `question` | Exact question text (for reference) | "How is human review performed?" |
| `answer_type` | Expected answer type | `text` |
| `evidence_needed` | What evidence is required | `qa_review_export.csv rows with reviewer_id` |
| `where_to_find_it` | Which export file and columns | `qa_review_export.csv: reviewer_id, review_timestamp` |
| `if_missing_gap` | Gap description if evidence missing | `No human review record for Q-101` |
| `decided_by` | Owner who signed this rule | `Hatem` |
| `date` | Date of decision (ISO format) | `2026-11-05` |
| `verified` | Must be "yes" for pack build | `yes` |

## Rules

1. **Every row must have `verified=yes`** — the CLI refuses to build without it
2. **`decided_by` and `date` are mandatory** — blank values cause validation failure
3. **`pattern_id` must match an `EVIDENCE_SPECS` entry** — unknown patterns fail validation
4. **One question = one rule** — multiple patterns for the same question need separate rules
5. **`if_missing_gap` becomes the gap text** — shown in `gap-list.csv` if coverage is 0%

## Example Row

```csv
R-001,QA-HUMAN-REVIEW,Q-101,"How is human review performed?",text,"qa_review_export.csv rows with reviewer_id","qa_review_export.csv: reviewer_id, review_timestamp","No human review record for Q-101",Hatem,2026-11-05,yes
```

## Demo Mapping Table

The demo includes `tests/fixtures/mapping-table.demo.csv` with pre-signed rules for the synthetic fixtures. This is used by `python -m signoff demo`.

## Owner Boundary

The `OWNER/mapping-table.csv` in the repo root is **header-only** — agents must not add data rows. The human owner fills it in per client.

*End of mapping table guide.*