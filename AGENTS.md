# AGENTS.md — Agent Charter & Ledger for Signoff

> **Read order (mandatory, every landing):** `AGENTS.md` → `CONSTITUTION.md` →
> `GOVERNANCE.md` → `README.md`. Then **sign in** to the ledger below, do the work,
> **sign out**. No entry, no trust: an unlogged session's work is treated as unverified
> until someone checks it.

## 1. Who agents are here

An "agent" is any entity that reads or writes this repository — an AI model, an
automation script, or a human acting as operator. There is exactly **one supreme
authority**: the repository owner (**Hatem Shalaby**). An agent acts only on the
owner's instruction and records every landing.

## 2. The mandatory sign-in / sign-out rule

Every agent, on **every landing** (a landing = one session that ends with the agent
stopping, whether the task is finished or not), must:

1. **SIGN IN** before any write action — who, why, what will be touched, sensitive or
   network actions planned, and the **date and time from the system clock**.
2. **SIGN OUT** when the landing's work is complete or stopped — what changed, why,
   the files touched, evidence of verification, and **the current status when leaving**,
   written so the next agent can continue without re-discovery.

Fail closed: if a task cannot be completed, still sign out and state exactly what is
incomplete. Never claim verification that did not happen.

### Entry format

```
## [YYYY-MM-DD HH:MM TZ] — <agent name / model>
Task: <what was assigned>
Touched: <files created / modified / deleted / moved>
Why: <the reasoning, not just the diff>
Verification: <what was actually checked and the observed result>
Left undone: <what is incomplete, needs review, or is deferred — or "nothing">
Sensitive: <any remote writes, secrets, or destructive actions, or "none">
```

## 3. Environment facts

- **Repo:** Signoff — an offline, deterministic evidence-pack builder that answers an AI questionnaire from a client's own exports, with a signed mapping table, a hash-chained pack and a coverage/gap list. Version 0.1.0, a pre-production candidate.
- **Owner account:** https://github.com/Hatemshalaby15071979
- **Default branch:** main
- **Where it runs:** fully offline by construction. The pack is built with no network access, under `--network none` in CI. No credentials, no LLM in the evidence path.
- **Verification commands:** `python3 scripts/check-scaffold.py`, `python3 scripts/check-offline.py`, `python3 scripts/check-determinism.py --out out/determinism`, `python3 scripts/verify_agent_instruction_files.py`, `python3 -m pytest -q`, and the root-document gate `python3 scripts/check_root_docs.py` (`--self-test` proves it fails closed). `bash scripts/run-all-checks.sh` runs the first four in one pass.
- **The scaffold check has a forbidden-token scan** over `src/**/*.py` and `scripts/**/*.py`: a literal `TODO`, `FIXME`, `XXX`, `HACK`, `NotImplementedError` or `left as an exercise`, or a bare `pass` / `...` body, fails the build. Do not leave placeholders; if a task cannot be finished, say so in the ledger instead.

## 4. Rules this agent must follow

- Read and obey **CONSTITUTION.md** (philosophy + clean-code policy). On conflict, it
  wins over this file.
- Follow **GOVERNANCE.md** for the repo map, documentation policy, and archiving rules.
- Keep `README.md` the single source of truth; `index.html` mirrors it.
- Keep local and remote in harmony: after a sanctioned change, commit and push so the
  GitHub copy matches the working copy.
- Sign in and sign out every landing, with the real clock time.
- Owner-only files under `OWNER/` are decisions, not drafts. Never auto-fill one; the
  scaffold check looks for the human-decision marker and will fail if it is removed.
- Do not describe this repository as free of customer data and do not claim production
  readiness: data provenance is unverified and the pack is a pre-production candidate.

## 5. Ledger (sign-in / sign-out)

## [2026-11-27 05:22 EET] — sami (OpenMausBot), owner-authorised governance landing

STATUS: SIGN-IN (work in progress)

Task: Bring this repository onto the portfolio governance standard, as the owner approved in chat on 2026-11-27 ("bring the remaining eleven onto the same governance standard"). Add the missing `AGENTS.md`, `CONSTITUTION.md` and `GOVERNANCE.md`; move the dated shipment report out of the root; land the shared root-document gate and wire it into CI.

Touched: Will add `AGENTS.md`, `CONSTITUTION.md`, `GOVERNANCE.md`, `scripts/check_root_docs.py`; move `SHIPMENT_READINESS.md` to `docs/archive/` and repoint its eleven references across five files; add one job to `.github/workflows/ci.yml`. Nothing is deleted, and the two files this repository's own scaffold contract pins at the root (`CONTRIBUTING.md`, `REPORT.md`) stay where they are.

Why: The repository had a strong verification culture — scaffold, offline and determinism gates — but no agent charter, no portfolio constitution and no written policy for the root, and a dated shipment report sat at the root. The root-document rule is now stated and enforced; the existing gates are untouched.

Verification: Planned — `scripts/check_root_docs.py` and `--self-test`, then `check-scaffold.py`, `check-offline.py`, `check-determinism.py`, `verify_agent_instruction_files.py` and `pytest`, then the GitHub Actions run on the landing commit.

Left undone: Nothing at sign-in.

Sensitive: `git push origin main` (owner's instruction in chat, 2026-11-27). No force push, no history rewrite, no secrets.
