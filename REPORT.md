# Signoff Build Report

| Field | Value |
|---|---|
| Product | Signoff 0.1.0 |
| As-of | 2026-11-05T00:00:00+00:00 (injected deterministic clock) |
| Scope | Offline CLI and Docker evidence-pack builder for AI vendor questionnaires |

## 1. Executive summary

Signoff parses questionnaire files and local CSV exports, applies only explicit human mapping rules, and builds a deterministic evidence pack. It does not use an LLM, make runtime network calls, or sign on behalf of a person.

## 2. User problem

Teams need to respond to AI vendor questionnaires with traceable operational evidence. Signoff connects questions to owner-approved evidence patterns and identifies gaps rather than inventing answers.

## 3. Product behavior

Inputs are a questionnaire (CSV, DOCX, TXT/Markdown, or optional XLSX) and selected CSV exports. Outputs include questionnaire answers with evidence IDs, a dossier in HTML/PDF/JSON/CSV, a gap list, hash-chained events and a blank-signature Oversight Statement.

## 4. Architecture

The Python package separates ingestion, mapping validation, coverage/classification, rendering and verification. Python 3.11+ standard library is used with pinned `fpdf2==2.8.4`; XLSX support is an optional `openpyxl==3.1.5` extra. See [architecture](docs/ARCHITECTURE.md) and [data contract](docs/DATA-CONTRACT.md).

## 5. Safety and ownership boundary

The production mapping table remains header-only. Owner files retain their required human-decision marker. Demo fixtures are synthetic and disclose that status. No output is a compliance certification, and a human must review any client-facing pack.

## 6. Determinism and integrity

The build accepts an injected `--as-of` instant, hashes canonical JSON, and manifests generated artifacts. Verification replays the chain and checks artifact digests and simulation disclosure. Hashes establish internal consistency, not source authenticity.

## 7. Offline and security posture

The evidence path has no network client or LLM. The offline source scan is provided in `scripts/check-offline.py`; the Docker image supports isolated operation with `--network none`. See [offline guarantee](docs/OFFLINE-GUARANTEE.md) and [threat model](docs/THREAT-MODEL.md).

## 8. Coverage and gaps

Evidence patterns define denominators and a bounded time window. The pack reports coverage and explicit gaps based on supplied exports. Percentages do not establish actual organizational compliance.

## 9. Demo output

The repository contains a generated synthetic pack in `out/demo/`, including HTML/PDF dossier, JSON manifest, questionnaire answers, gap list, event CSV and blank-signature statement. It is marked `SIMULATION_DISCLOSURE` and is not client evidence.

## 10. Verification record

The final scaffold check and suite were run using the project build virtual environment. After adding the missing required docs and examples, results are recorded in [verification log](docs/02-VERIFICATION-LOG.md). In this workspace run, pytest reported 140 passed and 88% coverage; offline and deterministic checks passed. Docker execution was not repeated during this final verification pass.

## 11. Known limitations

Source authenticity, data completeness, legal interpretation, system risk classification, and real-world control effectiveness are outside the tool's capability. Optional XLSX support must be installed separately. See [limitations](docs/LIMITATIONS.md).

## 12. Owner handoff

Before client use, the owner must make commercial/legal decisions, sign appropriate mappings, select real inputs, decide redaction, review every artifact and arrange human oversight. See [handoff](docs/03-HANDOFF-TO-OWNER.md) and [owner guide](docs/HUMAN-OWNER-GUIDE.md).
