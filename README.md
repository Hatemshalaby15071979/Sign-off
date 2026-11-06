# Signoff

When a client asks *"how did AI touch our customers?"*, BPOs and back-office
teams answer with adjectives. **Signoff answers with a signed, decision-by-
decision evidence pack** — built offline, on the customer's own machine, from
the CSV exports they already have.

- **Input A:** the client's AI questionnaire (`.csv`, `.docx`, `.xlsx`, `.txt`/`.md`).
- **Input B:** a folder of the customer's existing CSV exports (QA scoring
  sheets, approval logs, escalation logs, WFM/role exports, audit events, AI
  inventory, training and incident registers).
- **Output:** a completed questionnaire with evidence IDs, a signable dossier
  (HTML / PDF / JSON / CSV), a gap list of what is *not* provable, and a
  one-page Oversight Statement with a **blank signature block for a human**.

## The offline guarantee (read this first)

Signoff runs **100% offline**. It makes no network calls, holds no
credentials, touches no production systems, uses no LLM anywhere in the
evidence path, and writes only to the output directory you give it. There is
no server, no API, no telemetry — the security questionnaire has no subject.
All evidence is reconstructed from the customer's own records, so it is
reproducible in front of an auditor: every mapping decision points to a named
human, a rule ID, and a date.

## The owner boundary

What counts as evidence for any question is decided **only by the human owner
(Hatem)**, recorded in a signed mapping table (`OWNER/mapping-table.csv`).
The machine never guesses, never paraphrases an answer, never auto-signs, and
never classifies anyone's system as high-risk. Unmapped questions are
reported as `UNMAPPED`, never answered. `OWNER/` cannot be auto-filled — see
`OWNER/README.md`.

## 60-second demo

```console
$ python -m signoff demo --out out/demo
$ python -m signoff verify-pack --pack out/demo
VERIFIED
$ ls out/demo/
# dossier.html  dossier.pdf  pack.json  questionnaire-answers.csv
# gap-list.csv  oversight-statement.txt  ...
```

The demo uses synthetic fixtures and every artifact is visibly stamped
`SIMULATION_DISCLOSURE` — *"Synthetic demonstration data. Not evidence. Not a
client record. Not for submission."*

## Install

```console
$ python3 -m venv .venv && . .venv/bin/activate
$ pip install ".[xlsx]"        # runtime: stdlib + pinned fpdf2 (+ openpyxl extra)
$ pip install ".[dev]"         # dev only: pytest, pytest-cov
```

`.xlsx` parsing needs the optional `[xlsx]` extra; `.csv`, `.docx`, `.txt`,
`.md` work from the standard library alone (`.docx` uses `zipfile` + XML).

## Documentation

Full implementation report: [`REPORT.md`](REPORT.md). Architecture:
`docs/ARCHITECTURE.md`. Owner handoff: `docs/03-HANDOFF-TO-OWNER.md`.
Decision log: `docs/01-DECISION-LOG.md`.

**Status: v0.1.0 — a document factory, with a first real pilot pack built 2026-11-06** (WE call centre: 10/10 questions Yes with evidence, 0 gaps, `VERIFIED`; client data kept outside this repository; Oversight Statement signed by the owner by authorisation of the named accountable person). No priced offer, licence choice, or the remaining owner decisions in `OWNER/DECISIONS-TO-MAKE.md` items 2–8 exist in this repository yet.
