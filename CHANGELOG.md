# Changelog

All notable changes to Signoff are listed here. The mapping table is not
contributor-editable (see CONTRIBUTING.md).

## Unreleased

- **First real client pack (WE pilot, 2026-11-06).** A practitioner at a WE call centre answered a 10-question blank form and supplied anonymized exports (QA review, audit events, provider inventory, roles, agent identity, escalations, training, incidents). The owner signed 10 mapping rules (`OWNER/mapping-table.csv`, `Hatem Shalaby`, 2026-11-06) and the resulting pack built offline: **10/10 Yes with evidence, 0 gaps, `VERIFIED`** (pack `PK-278084a109d79591`, as-of 2026-11-07). Client data is held **outside** the repository and is not committed. The Oversight Statement records that the owner was authorised by the named accountable person ([REDACTED_PERSON], AI OPS Engineer) to sign on his behalf — recorded 2026-11-06.
- Scaffold/test guards retired: the pre-owner "header-only mapping table" assertion now enforces *signed* rows (named owner, date, verified=yes).
- Learned from the pilot (operator notes): exports may arrive as Excel (`.xlsx` content under `.csv` names) — convert to pure CSV first; `status` values must be `yes` (not `Completed`); escalations validate against an authorised-supervisor roster that must exist in the roles export; coverage window is 90 days, so stale exports (last year) read as No/N/A, not Yes.

- Fixed: Dockerfile could not build (missing `pyproject.toml` context and demo
  fixtures) and its offline demo step failed on a root-created output volume.
  The image now runs from `PYTHONPATH`, copies the demo fixtures, the CI
  pre-creates its output directory, and the workflow has least-privilege
  `contents: read` permissions.
- Security: upgraded pinned `fpdf2` 2.8.4 → 2.8.8. pip-audit reported
  CVE-2026-114609 (SSRF via image-resource dereferencing) and CVE-2026-114610
  (SVG `<use>` resource exhaustion) in 2.8.4; Signoff never passes user input
  to `FPDF.image()`/`write_html()`, but the fixed pin removes the exposure.
- Added: root `SECURITY.md` (GitHub-discoverable) and `SHIPMENT_READINESS.md`.

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
