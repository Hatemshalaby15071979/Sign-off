<div align="center">

# Signoff

<!-- badges:start -->

![licence](https://img.shields.io/badge/licence-MIT-blue)
![local verification](https://img.shields.io/badge/local%20verification-140%20passed-brightgreen)
![CI](https://github.com/Hatemshalaby15071979/Sign-off/actions/workflows/ci.yml/badge.svg)

*Local verification measured 2026-11-06 on `main`; hosted GitHub Actions is green on the default branch. Data provenance is unverified; this repository is not claimed to be free of customer data.*

<!-- badges:end -->

**Offline by construction** — the pack is built with no network access (`--network none` in CI).

</div>

## What is this?

Signoff answers a question operations leaders actually ask: **"how did AI touch our customers?"** — with evidence, not adjectives.

You give it two things:

1. A client's AI questionnaire (CSV, Word, Excel, or plain text).
2. A folder of the customer's own CSV exports (QA scores, approvals, escalations, training records, and so on).

It produces a completed questionnaire where every answer points to a specific evidence ID, a signable dossier (HTML, PDF, JSON, or CSV), an honest list of what **cannot** be proven, and a one-page Oversight Statement with a blank signature block for a human.

The important part: **the machine never guesses.** Questions it can't map to evidence are reported as `UNMAPPED`, never answered. What counts as evidence is decided only by the human owner, in a human-authorised mapping table (named owner + date + `verified=yes`; there is no cryptographic signature). And the whole thing runs 100% offline — no network calls, no credentials, no AI model anywhere in the evidence path.

## Current status — read this first

**This is a pre-production evidence factory, verified locally only. It is not a compliance determination.**

<!-- docs-sync:start -->
**Signoff 0.1.0 — pre-production evidence factory, verified locally only.** 140 automated tests pass, the code is 88.0% covered. Hosted GitHub Actions is green on the default branch, and data provenance is unverified.
<!-- docs-sync:end -->

What has actually been checked (locally, 2026-11-06):

| Check | Result |
| --- | --- |
| Tests | 140 passed |
| Coverage | 88% |
| Runs fully offline | Zero network imports, calls, or environment reads |
| Determinism | Output is byte-identical across runs |
| Demo pack | Builds and verifies — hash chain replays cleanly |
| Docker | Builds; image runs read-only and non-root |
| Dependency audit | No known vulnerabilities |

What is still open:

- Hosted GitHub Actions is green on the default branch; the status above is now CI-backed, not local-only.
- The source and anonymisation of the example data has **not** been independently verified. Don't treat the demo pack as proof the committed data is synthetic or personal-data-free.
- A valid hash chain proves the pack is internally consistent — it does not authenticate the source CSVs or prove their completeness. **Packs are hash-consistent, not signed:** `VERIFIED` means the artifact digests and hash chain replay; no signing key exists and no digital signature is produced.
- A few decisions (licence confirmation, security contact, client-use terms) are deliberately left to the owner — see `OWNER/DECISIONS-TO-MAKE.md`.

Details, if you want them: [SHIPMENT_READINESS.md](SHIPMENT_READINESS.md) · [REPORT.md](REPORT.md) · docs/ (architecture, decision log, owner handoff)

## Run it

```bash
# Install
python3 -m venv .venv && . .venv/bin/activate
pip install ".[xlsx]"     # CSV/Word/text need only the standard library; Excel needs this extra

# 60-second demo
python -m signoff demo --out out/demo
python -m signoff verify-pack --pack out/demo
# -> VERIFIED
```

## Related work

- [CreateLee](https://github.com/Hatemshalaby15071979/createlee) — a synthetic rehearsal library with the same eight export shapes, so you can rehearse the whole flow before real client exports arrive.
- [Portfolio and wider work](https://github.com/Hatemshalaby15071979)

## Author

Built by Hatem Shalaby — Contact Centre Operations & AI Implementation Lead (WFM & CX transformation).

## Licence

MIT
