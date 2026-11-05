# Changelog

All notable changes to Signoff are listed here. The mapping table is not
contributor-editable (see CONTRIBUTING.md).

## 0.1.0 — 2026-11-05

Initial release (autonomous build for the owner).

- Added: questionnaire parsers for CSV, DOCX (stdlib XML), XLSX (optional
  `openpyxl` extra), TXT/Markdown.
- Added: hard-coded alias-table CSV normaliser producing `DecisionEvent`s
  with full source traceability (`source_file` + `source_row`).
- Added: mapping-table loader and strict validator (duplicate rule IDs,
  blank signed fields, vague evidence sentences, `OWNER_PENDING` in real
  builds all fail closed).
- Added: deterministic classifier for the five oversight states
  (`AI-proposed`, `gate-blocked`, `human-approved`, `escalated`,
  `unlogged`).
- Added: sha256 hash chain over canonical serialisations, verified by
  `signoff verify-pack`.
- Added: coverage computation with explicit denominators (`N/A` when there
  is no denominator).
- Added: gap list (missing approvals, unlogged identities, missing retention
  and SLA proof, unmapped questions).
- Added: renderers — self-contained HTML (no external resources), PDF
  (fpdf2 == 2.8.4), JSON, CSV; Appendix cross-reference (Art. 12 / 14 /
  26(6), ISO/IEC 42001, NIST AI RMF, OWASP Agentic Top 10); "What this pack
  does NOT prove" section on every artifact; blank-signature Oversight
  Statement.
- Added: `signoff demo` (synthetic fixtures, `SIMULATION_DISCLOSURE`
  watermark on every artifact) and `signoff verify-pack`.
- Added: offline static scan (`scripts/check-offline.py`), determinism check
  (`scripts/check-determinism.py`), socket-monkeypatch test suite, Docker
  multi-stage image tested with `--network none`.
- Owner boundary: `OWNER/` placeholders only; `decided_by`, price, entity,
  licence, real questionnaires and first invoice all deferred to the owner.
