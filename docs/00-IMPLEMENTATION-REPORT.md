# Signoff — Implementation Report

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Generated | 2026-11-05T00:00:00+00:00 (injected `--as-of`) |
| Author | Autonomous build (no human typing, no LLM in evidence path) |

---

## 1. Purpose

Signoff is an **offline, deterministic, signable evidence-pack builder** for AI vendor
questionnaires. It answers a client's questionnaire from the customer's own CSV
exports, producing:

- A completed questionnaire with evidence IDs (`questionnaire-answers.csv`)
- A signable dossier (HTML, PDF, JSON, CSV)
- A gap list of what is **not** provable from the supplied records
- An Oversight Statement with a **blank human signature block**

The tool makes **no network calls**, **uses no LLM** in the evidence path, and
**never guesses** — every mapping is a signed human decision in
`OWNER/mapping-table.csv`.

---

## 2. Architecture Summary

| Layer | Files | Responsibility |
|-------|-------|----------------|
| `ingest/` | 5 parsers + normaliser | CSV/DOCX/XLSX/TXT questionnaires; 8 hard-coded export schemas |
| `mapping/` | loader + validator + patterns | Owner-signed mapping table; fail-closed validation |
| `engine/` | classifier + coverage + gaps + hash_chain + builder | State labels, coverage %, gap rows, hash chain, pack assembly |
| `render/` | 6 renderers + appendix + disclosure | HTML, PDF (fpdf2), JSON, CSV, Oversight Statement |
| `verify/` | `verify_pack.py` | Replay chain + artifact digests + banner checks |
| `cli.py` | single command surface | `validate-mapping`, `parse-questionnaire`, `build`, `demo`, `verify-pack` |

All modules are pure Python 3.11+ stdlib + pinned `fpdf2==2.8.4` (+ optional
`openpyxl==3.1.5` for XLSX questionnaires).

---

## 3. Key Invariants (enforced by tests)

| Invariant | How |
|-----------|-----|
| **Offline** | `check-offline.py` AST scan bans socket/urllib/requests/LLM SDKs |
| **Deterministic** | `check-determinism.py` byte-identical outputs across runs |
| **No guessing** | `UNMAPPED` literal for every question without a signed rule |
| **Fail closed** | Every parser/validator raises on missing/unknown columns |
| **Byte-identical PDF** | fpdf2 core fonts + ASCII normaliser (`_ascii()`) |
| **Hash chain** | SHA-256 over canonical JSON; head derived from genesis + events |
| **Owner boundary** | `OWNER/` files begin with marker; mapping-table.csv header-only |
| **Simulation watermark** | `SIMULATION_DISCLOSURE` on every demo artifact |
| **Not-prove section** | 7 mandatory points on every artifact |

---

## 4. Data Contract

See `docs/DATA-CONTRACT.md` for the complete, machine-readable specification
of every CSV column, every hash input, every artifact schema, and the
injected clock (`--as-of`).

---

## 5. Coverage Engine

`EVIDENCE_SPECS` defines **12 evidence patterns** with explicit denominators:

| Pattern ID | Kind | Denominator | Purpose |
|------------|------|-------------|---------|
| QA-HUMAN-REVIEW | rows | QA rows with AI-proposed action | Human review of AI QA |
| KILL-SWITCH-REVOKE | fixed | 1 | Kill switch / revocation exercise |
| AGENT-IDENTITY-LOG | rows | AI-proposed decisions | Agent identity logged |
| LEAST-PRIV-QUARTERLY | fixed | 1 | Access review logged |
| AI-INVENTORY-PROVIDERS | fixed | 1 | Registered provider entry |
| CONTRACT-NO-TRAINING-DOC | fixed | 1 | Signed contract term |
| ESCALATION-AUTH-SUPERVISOR | rows | escalation rows | Authorised supervisor only |
| ACCOUNTABILITY-STATEMENT | fixed | 1 | Named accountable record |
| OVERSIGHT-METRICS | pre-pass | accepted+edited QA pairs | Monitoring data |
| TRAINING-RECORDS | rows | training rows | Completed staff training |
| INCIDENT-SLA | rows | incident rows | SLA notification |
| RETENTION-PII-LOGGING | fixed | 1 | Retention/PII check |

Coverage window = `--as-of` minus **90 days** (both ends inclusive). Events
outside the window are excluded from numerator **and** denominator. A zero
denominator is `N/A (no events in period)` — **never 100%**.

---

## 6. Verification Results (from `pytest --cov`)

```
TOTAL: 1485 statements, 189 missed, 87% coverage
```

- Uncovered lines are almost entirely in optional `questionnaire_xlsx.py`
  (the `[xlsx]` extra) and `redaction.py` (invoked only under `--redact`).
- All runtime paths hit 86–100%.

---

## 7. Build Artifacts (demo pack `PK-e0ada980b335da26`)

| Artifact | Size | SHA-256 (first 16) | Watermark |
|----------|------|--------------------|-----------|
| `dossier.html` | 33 KB | `6a8d...` | ✓ SIMULATION_DISCLOSURE |
| `dossier.pdf` | 10 KB | `3c2f...` | ✓ SIMULATION_DISCLOSURE |
| `pack.json` | 44 KB | `e0ad...` | manifest only |
| `questionnaire-answers.csv` | 6.6 KB | `8b1e...` | ✓ |
| `gap-list.csv` | 3.8 KB | `f4d7...` | ✓ |
| `evidence-events.csv` | 8.8 KB | `2a5c...` | ✓ |
| `oversight-statement.txt` | 1.1 KB | `9f33...` | ✓ |

`verify-pack` returns **VERIFIED**.

---

## 8. Tamper Detection

`verify_pack` detects and reports `TAMPERED` on:

- Artifact byte mutation (any file)
- Event body mutation in `pack.json`
- Chain genesis mutation
- Chain head mismatch
- Missing artifact
- Malformed `pack.json`
- Path-traversal artifact names

---

## 9. Decision Log Summary

See `docs/01-DECISION-LOG.md` for the complete D-001..D-012 entries. Key
decisions:

- D-001: chain genesis = `signoff-chain-genesis:` + ISO instant
- D-002: PDF core fonts + `_ascii()` normaliser for determinism
- D-003: `build_pack()` signature extended with `data_files` for demo mode
- D-004: QA `human_action=edited` → `gate-blocked`
- D-005: Evidence IDs attach **before** hash-chain
- D-006: `pack.json` manifest excludes itself
- D-007: R-006 uses `clause` column for signed contract term
- D-008: `OVERSIGHT-METRICS` pre-pass (accepted+edited QA pairs)
- D-009: 7 mandatory "What this pack does NOT prove" points
- D-010: `SIMULATION_DISCLOSURE` watermark on every demo artifact
- D-011: State machine states (`AI-proposed`, `gate-blocked`, `human-approved`, `escalated`, `unlogged`)
- D-012: 12 `EVIDENCE_SPECS` with explicit denominators

---

## 10. Handoff to Owner

See `docs/03-HANDOFF-TO-OWNER.md` for the 7 decisions the human owner
(Hatem) must make before any client-facing pack is produced:

1. Sign every row in `OWNER/mapping-table.csv` (`decided_by`, `date`, `verified=yes`)
2. Set `offer-and-pricing.md`, `company-and-tax.md`, `legal-review.md`
3. Replace `OWNER/oversight-statement.md` with the real signatory details
4. Choose real export CSVs (Input B) — the 8 kinds documented
5. Choose real client questionnaire (Input A) — CSV/DOCX/XLSX/TXT
6. Decide `--redact` posture
7. Confirm `docker run --network none` runs in the client environment

---

## 11. Known Limitations

See `docs/LIMITATIONS.md`. Key items:

- Does not verify CSV authenticity (hash chain = internal consistency only)
- Does not classify any system as high-risk under EU AI Act
- Does not replace signed policies/contracts/SOPs
- Does not cover periods without exported CSVs (N/A, not 100%)
- XLSX questionnaires require the `[xlsx]` extra at install time

---

## 12. Security / Threat Model

See `docs/THREAT-MODEL.md`. Signoff itself is the TCB — the only code that
runs on the customer's machine. No credentials, no network, no server, no
telemetry. The Docker image is multi-stage, non-root, `network_mode: none`.

---

*End of implementation report.*