# Signoff — Architecture

## Overview

Signoff is a **deterministic, offline, signable evidence-pack builder** for AI vendor questionnaires. It answers a client's questionnaire from the customer's own CSV exports, producing:

- A completed questionnaire with evidence IDs (`questionnaire-answers.csv`)
- A signable dossier (HTML, PDF, JSON, CSV)
- A gap list of what is **not** provable from the supplied records
- An Oversight Statement with a **blank human signature block**

The tool makes **no network calls**, **uses no LLM** in the evidence path, and **never guesses** — every mapping is a signed human decision in `OWNER/mapping-table.csv`.

## Key Components

| Layer | Files | Responsibility |
|-------|-------|----------------|
| `ingest/` | 5 parsers + normaliser | CSV/DOCX/XLSX/TXT questionnaires; 8 hard-coded export schemas |
| `mapping/` | loader + validator + patterns | Owner-signed mapping table; fail-closed validation |
| `engine/` | classifier + coverage + gaps + hash_chain + builder | State labels, coverage %, gap rows, hash chain, pack assembly |
| `render/` | 6 renderers + appendix + disclosure | HTML, PDF (fpdf2), JSON, CSV, Oversight Statement |
| `verify/` | `verify_pack.py` | Replay chain + artifact digests + banner checks |
| `cli.py` | single command surface | `validate-mapping`, `parse-questionnaire`, `build`, `demo`, `verify-pack` |

## Deterministic Guarantees

- **Offline**: `check-offline.py` AST scan bans socket/urllib/requests/LLM SDKs
- **Deterministic**: `check-determinism.py` byte-identical outputs across runs
- **No guessing**: `UNMAPPED` literal for every question without a signed rule
- **Fail closed**: Every parser/validator raises on missing/unknown columns
- **Byte-identical PDF**: fpdf2 core fonts + ASCII normaliser (`_ascii()`)
- **Hash chain**: SHA-256 over canonical JSON; head derived from genesis + events
- **Owner boundary**: `OWNER/` files begin with marker; mapping-table.csv header-only

## Data Flow

1. **Input**: CSV/DOCX/XLSX/TXT questionnaire (Input A) + CSV exports (Input B)
2. **Parsing**: Extract questions and data
3. **Mapping**: Apply signed mapping table
4. **Coverage**: Calculate coverage % based on `--as-of` window (90 days)
5. **Hash Chain**: Create SHA-256 chain of canonical JSON artifacts
6. **Build**: Assemble pack with all artifacts
7. **Render**: Generate HTML, PDF, JSON, CSV, Oversight Statement
8. **Verify**: Check chain integrity and banner presence

## Versioning

- Version: 0.1.0
- Generated: 2026-11-05T00:00:00+00:00 (injected `--as-of`)
- Author: Autonomous build (no human typing, no LLM in evidence path)

## Documentation

See `docs/00-IMPLEMENTATION-REPORT.md`, `docs/DATA-CONTRACT.md`,
`docs/MAPPING-TABLE-GUIDE.md`, `docs/QUESTIONNAIRE-PARSING.md`,
`docs/SECURITY.md`, `docs/THREAT-MODEL.md`, `docs/OFFLINE-GUARANTEE.md`,
`docs/CONTROL-MAPPING.md`, `docs/HUMAN-OWNER-GUIDE.md`,
`docs/LIMITATIONS.md`, `docs/FAQ.md`.

*End of architecture document.*