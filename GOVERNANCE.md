# GOVERNANCE.md — Operating Policy & Repo Map for Signoff

> Companion to `CONSTITUTION.md` (the *why* — philosophy and clean-code policy, which
> this file enforces operationally) and `AGENTS.md` (the agent charter + ledger).
> Read all three before acting. This file may be updated by any agent **as a logged
> governance change**; the CONSTITUTION itself is owner-only.

## 1. Repository map

Authoritative directory map for **Signoff**. Any file you add, move, rename, or
delete gets reflected here in the same landing.

| Path | Purpose (one line) |
|---|---|
| `src/signoff/` | The application: ingest, mapping, engine, render, util, CLI. Standard library plus one pinned pure-Python PDF library; no network in the evidence path. |
| `scripts/` | The gates: `check-scaffold.py`, `check-offline.py`, `check-determinism.py`, `verify_agent_instruction_files.py`, `run-all-checks.sh`, and the shared root-document gate. |
| `tests/` | The pytest suite. |
| `examples/` | A runnable demo pack. |
| `OWNER/` | Owner-only decision files, including the signed mapping table and pricing. |
| `docs/` | Standing documentation: architecture, decision log, verification log, data contract, threat model, offline guarantee, owner hand-off. |
| `docs/archive/` | One-off and historical reports — the shipment-readiness record. |
| `assets/` | Brand and page assets. |
| `.github/` | CI workflows. |
| `Dockerfile`, `docker-compose.yml` | The offline container run (`--network none`). |

## 2. Documentation policy (what belongs where)

**Root holds only the requested set** — nothing else:

| File | State | Purpose |
|---|---|---|
| `README.md` | required | The single source of truth: what this is, why it's here, how to use it — in simple English for a professional reader. Carries the Helix Solutions logo. |
| `AGENTS.md` | required | Agent charter + sign-in/out ledger. |
| `CONSTITUTION.md` | required | The owner's engineering philosophy and clean-code policy (unified across every repo). |
| `GOVERNANCE.md` | required | This file: repo map, documentation policy, sync policy, archiving rules. |
| `CHANGELOG.md` | standard | Dated user-visible changes. |
| `LICENSE` / `LICENSE.md` | standard | MIT, unless the repo states otherwise. |
| `SECURITY.md` | standard | Threat model summary and vulnerability reporting; the full model is `docs/SECURITY.md`. |
| `CONTRIBUTING.md` | required | Contribution rules — including the rule that the mapping table is not contributor-editable. It stays at the root because `scripts/check-scaffold.py` requires it there as part of its phased contract. |
| `REPORT.md` | required | The committed report artifact. It stays at the root for the same reason: `scripts/check-scaffold.py` requires `REPORT.md` and `REPORT.json`. |

**Two of these are exceptions worth knowing about.** The portfolio standard places
one-off reports — including contributor notes and shipment reports — in `docs/archive/`.
`CONTRIBUTING.md` and `REPORT.md` are kept at the root here only because this
repository's own scaffold contract pins them there. Moving them is a one-line change to
the phase map in `scripts/check-scaffold.py` plus the links in `README.md`, and it is the
owner's call rather than an agent's, because the scaffold check is a verification gate
and weakening a gate during a documentation landing is exactly the wrong moment.

**Everything else lives in `docs/`** — reports, audit logs, execution plans, research
notes, ADRs, runbooks, anything dated or one-off. No stray `.md`/`.txt` at the root.
If a document at the root is not in the table above, move it to `docs/` (or
`docs/archive/` if it is historical) and record the move in the `AGENTS.md` ledger.

## 3. Synchronization & harmony policy

The owner's rule: **the repository's actual status must match its README at all times,
locally and remotely.**

1. `README.md` is the canonical account. `index.html` mirrors it; it never forks it.
2. When reality changes, update `README.md` **first**, then mirror it to the page.
3. Every sanctioned change is committed **and pushed** to the default branch, so the
   GitHub copy, the local working copy, and any local platform that reads the repo
   all show the same truth.
4. A number published anywhere (README, page, badge) must be reproducible from this
   repository. A stale figure is removed, not left to rot.

## 4. Archiving rule

- Archive (move to `docs/archive/`), never delete: historical reports, superseded plans,
  dated audits, and one-off execution logs.
- Delete outright only regenerable artifacts: caches, build output, coverage files.
- Record every move in the `AGENTS.md` ledger with date and time.

## 5. Engineering philosophy & clean-code policy (operational summary)

The full text is `CONSTITUTION.md`. The operational reminders, enforced here:

- **Fail closed.** Missing input or missing authority is a refusal, never a default.
- **Evidence before claims.** Published numbers carry a command, a date, and an artifact.
- **No duplicates, no temp files, one file one job, every file explains itself.**
- **Secrets never enter the tree.**
- **Simple English** in code, docs, and UI, so a non-technical professional reader
  (recruiter, partner) can follow.
- **One brand mark:** the Helix Solutions logo, everywhere.

## 6. Definition of done

It works; it has a test or a documented manual check; the `AGENTS.md` ledger has an
entry; the docs reflect the new reality; no temporary file was left behind; and every
published number can be re-run to reproduce itself.
