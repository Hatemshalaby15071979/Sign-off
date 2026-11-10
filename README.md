<div align="center">

# Signoff

<!-- badges:start -->

![licence](https://img.shields.io/badge/licence-MIT-blue)
![local verification](https://img.shields.io/badge/local%20verification-140%20passed-brightgreen)
![shipment status](https://img.shields.io/badge/shipment-locally%20ready-yellow)

*Local verification measured 2026-11-06 on `main`; hosted GitHub Actions has not run on this candidate. Data provenance is unverified; this repository is not claimed to be free of customer data.*

<!-- badges:end -->

**An offline evidence-pack builder that answers *"how did AI touch our customers?"* with a signed, decision-by-decision dossier — not adjectives.**

![Status](https://img.shields.io/badge/status-v0.1.0-blue)
![Licence](https://img.shields.io/badge/licence-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)

</div>

## GitHub shipment status (2026-11-06)

<!-- docs-sync:start -->
**Signoff 0.1.0 — pre-production evidence factory, verified locally only.** 140 automated tests pass, the code is 88.0% covered. Hosted GitHub Actions has not yet run on this candidate, and data provenance is unverified.
<!-- docs-sync:end -->

The intended public repository is [Hatemshalaby15071979/Sign-off](https://github.com/Hatemshalaby15071979/Sign-off). This checkout has been pushed to `main`; hosted GitHub Actions verification has not yet been observed on the pushed SHA. Local CI-equivalent checks pass: **140 tests**, **88% coverage**, offline scan OK, scaffold OK, determinism OK, Docker build + offline demo + verify all `VERIFIED`, and `pip-audit` clean after the `fpdf2==2.8.8` upgrade. See [`SHIPMENT_READINESS.md`](SHIPMENT_READINESS.md) for the exact check outcomes and remaining hosted-only verification.

## One-line identity

Signoff is an offline, signable AI questionnaire evidence-pack builder for contact-centre and back-office operations. It takes a client's AI questionnaire and a folder of the customer's own CSV exports, and produces a completed questionnaire with evidence IDs, a signable dossier (HTML / PDF / JSON / CSV), a gap list of what is *not* provable, and a one-page Oversight Statement with a blank signature block for a human.

> [!IMPORTANT]
> **Positioning.** Pre-production evidence factory. Signoff organises and surfaces gaps in evidence; it does not authenticate source CSVs, prove their completeness, or upgrade synthetic data into real evidence. A valid hash chain proves internal consistency of the pack only. The source and anonymization of repository examples have not been independently verified. Treat their provenance as unverified; this repository does not establish compliance certification.

> [!NOTE]
> **Operating principle.** Signoff runs **100% offline**. It makes no network calls, holds no credentials, touches no production systems, uses no LLM anywhere in the evidence path, and writes only to the output directory you give it. What counts as evidence for any question is decided **only by the human owner (Hatem)**, recorded in a signed mapping table (`OWNER/mapping-table.csv`). The machine never guesses, never paraphrases an answer, never auto-signs, and never classifies anyone's system as high-risk. Unmapped questions are reported as `UNMAPPED`, never answered. `OWNER/` cannot be auto-filled — see `OWNER/README.md`.

## What it does

1. **Input A** — the client's AI questionnaire (`.csv`, `.docx`, `.xlsx`, `.txt`/`.md`).
2. **Input B** — a folder of the customer's existing CSV exports (QA scoring sheets, approval logs, escalation logs, WFM/role exports, audit events, AI inventory, training and incident registers).
3. **Output** — a completed questionnaire with evidence IDs, a signable dossier (HTML / PDF / JSON / CSV), a gap list of what is *not* provable, and a one-page Oversight Statement with a blank signature block for a human.

The owner boundary is structural: `OWNER/` holds the signed mapping table and is owner-decided territory; Signoff only enforces the rule shape (exactly one `named_accountable=yes` in `role_spec.csv`, `completed` values of `yes`, etc.).

## How it fits Helix Codex

Signoff is part of the Helix Codex / Helix Prime body of work — the same author and the same design philosophy (offline, explainable, auditable, no generative model in the evidence path). It is an **independent repository with no shared codebase or runtime infrastructure** with Helix Prime, live-support-assistant, CompliProof, or CreateLee; portfolio membership, not technical integration.

Signoff's eight export shapes are the same shapes CreateLee rehearses (QA reviews, audit events, approvals, escalations, role spec, AI inventory, training records, incident notifications). CreateLee supplies *simulated-shaped* exports so the gate can be rehearsed end to end before real client exports arrive — Signoff then produces the pack verdicts that Helix-Codex's production gates consume as *content only* (the signature itself is an external, owner-supplied act).

## Architecture

- `src/signoff/` — the governed pack builder (parser, classifier, renderer, verifier).
- `OWNER/` — owner decisions only: signed mapping table, offer-and-pricing, decisions-to-make. Not auto-fillable by the machine.
- `docs/` — architecture, decision log, handoff-to-owner, limitations.
- `index.html` — single-file, self-contained marketing landing page with decided pricing bands.
- `out/` — gitignored output directory for demo and real packs.
- `scripts/` — scaffold, offline, and determinism checks.
- `tests/` — 140 tests covering the pack build, verification, and mapping guards.

## Production status & verification

> [!WARNING]
> This is a pre-production document factory, not a compliance determination. **Locally shipment-ready; hosted-only verifications remain open.** The provenance of the demo pack and any referenced pilot materials has not been independently verified from this checkout. Do not treat those references as proof that committed data is synthetic or anonymized, or that no personal data is present.

| Check | Result | Source |
| --- | --- | --- |
| Tests | **140 passed** (5.51s) | `PYTHONPATH=src python3 -m pytest -q` |
| Coverage | **88%** (1485 stmts, 181 missed) | `pytest --cov=src/signoff --cov-report=term-missing -q` |
| Scaffold check | **OK** — 116 required files present | `python3 scripts/check-scaffold.py` |
| Offline scan | **OK** — zero network imports/calls/env reads | `python3 scripts/check-offline.py` |
| Determinism | **OK** — byte-identical across runs | `scripts/check-determinism.py --out ...` |
| Demo + verify | **VERIFIED** — 7 artifacts, hash chain replays cleanly | `python3 -m signoff demo ...` then `verify-pack` |
| Docker build | **Built** — image runs read-only, non-root, `--network none` | `docker build -t signoff:shipment-audit .` |
| Dependency audit | **No known vulnerabilities found** — `fpdf2==2.8.8` | `pip-audit -r` on pinned runtime set |
| pip check | **No broken requirements** | `python3 -m pip check` |

**Limitations (not waived):** hosted GitHub Actions, branch protection, repository visibility, and remote state were not verified until the push; third-party Actions are tag-pinned, not SHA-pinned; base images are tag-pinned, not digest-pinned; licence choice, security reporting contact, client use, and signed mapping rules remain owner decisions (`OWNER/DECISIONS-TO-MAKE.md`).

## Run it

```bash
# Install
python3 -m venv .venv && . .venv/bin/activate
pip install ".[xlsx]"        # runtime: stdlib + pinned fpdf2 (+ openpyxl extra)
pip install ".[dev]"         # dev only: pytest, pytest-cov

# 60-second demo
python -m signoff demo --out out/demo
python -m signoff verify-pack --pack out/demo
# -> VERIFIED

# Full local gate
python3 scripts/check-scaffold.py && python3 scripts/check-offline.py
PYTHONPATH=src python3 -m pytest -q          # 140 passed
PYTHONPATH=src python3 scripts/check-determinism.py --out out/determinism
docker build -t signoff:latest .
```

`.xlsx` parsing needs the optional `[xlsx]` extra; `.csv`, `.docx`, `.txt`, `.md` work from the standard library alone (`.docx` uses `zipfile` + XML).

## Documentation

- Full implementation report: [`REPORT.md`](REPORT.md)
- Architecture: `docs/ARCHITECTURE.md`
- Owner handoff: `docs/03-HANDOFF-TO-OWNER.md`
- Decision log: `docs/01-DECISION-LOG.md`
- Shipment readiness record: [`SHIPMENT_READINESS.md`](SHIPMENT_READINESS.md)

## Runbook (owner-authorised launch sequence)

Contact email is set in `index.html` (`[REDACTED_EMAIL]`). Final sweep (all green as of 2026-11-06), then:

```console
$ git push -u origin audit/shipment-candidate   # or main; let hosted CI verify
$ git tag -a v0.1.0 -m "v0.1.0 — first real pilot pack (10/10 evidenced, VERIFIED)"
$ git push origin v0.1.0
$ gh release create v0.1.0 --title "Signoff v0.1.0" --notes-file SHIPMENT_READINESS.md
```

No tag or release exists yet. Attach the 2-minute demo video (optional) produced by following `docs/VIDEO-DEMO-PROMPT.md`.

## Related work

- [CreateLee — Signoff rehearsal library](https://github.com/Hatemshalaby15071979/createlee)
- [Portfolio and wider work](https://github.com/Hatemshalaby15071979)

## Author

Built by Hatem Shalaby, Contact Centre Operations & AI Implementation Lead | WFM & CX Transformation. Background: https://github.com/Hatemshalaby15071979

## Licence

MIT
