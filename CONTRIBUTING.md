# Contributing

## The mapping table is not contributor-editable

`OWNER/mapping-table.csv` records **what counts as evidence**. It is signed
row by row by the owner (`decided_by`, `date`, `verified`), and an auditor
must be able to trace any mapping judgement back to one named human. No
contributor, agent, or automation may write, edit, or auto-fill rows in that
file. Contributions to anything under `OWNER/questionnaires/` and
`OWNER/real-data/` (real client forms and real client data) are also banned —
never commit such files.

## What you may contribute

- Code under `src/signoff/`, `scripts/`, `tests/` (fixtures only — synthetic,
  watermarked).
- Parser fixes (never adding interpretation of question semantics).
- Documentation under `docs/` except `docs/01-DECISION-LOG.md` owner-marked
  decisions, which stay with the owner.

## Project rules (non-negotiable in review)

1. Offline / air-gapped: no network client imports in runtime code; check
   with `python scripts/check-offline.py`.
2. No model (LLM) anywhere in the evidence path.
3. Determinism: same inputs give byte-identical outputs; IDs derive from
   content, never randomness; clocks are injected.
4. Fail closed on any parse/chain/mapping problem.
5. No placeholders: no `TODO`, no `pass` stubs, no unimplemented branches.
6. Never auto-sign anything, never claim compliance or legal classification.

Run before opening a contribution:

```console
$ python scripts/run-all-checks.sh && python -m pytest -q
```
