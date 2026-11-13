# Signoff GitHub shipment readiness

**Assessment date:** 2026-11-06
**Local branch:** `audit/shipment-candidate`
**Base HEAD before this audit's commit:** `dbcb8d7` (see `git log` for the
shipment commit SHA; this file is committed together with the fixes below)
**GitHub destination:** <https://github.com/Hatemshalaby15071979/Sign-off>

This is a local repository shipment assessment. No push, tag, GitHub release,
or deployment was made. It does not assert production readiness, legal or
compliance approval, customer validation, or a production security approval.

## Status vocabulary (binding)

These terms are used precisely throughout the repository:

- **hash-consistent pack** — a pack whose artifact digests and hash chain
  replay. `VERIFIED` means only this. It does not authenticate the source
  records, prove completeness, or establish who produced them.
- **human-authorised rule** — a row in `OWNER/mapping-table.csv` with a named
  `decided_by`, a real `date`, and `verified=yes`, entered by a human. This is
  an authorisation record, **not** a cryptographic signature.
- **signed pack** — a pack carrying a digital signature made with a
  human-supplied private key. **No such key exists in this repository and
  Signoff does not produce one.** No document may describe a pack as signed
  until a human supplies a key and a signing step is implemented and tested.


## Initial state (2026-11-06)

- Checkout: `cloned_repos/signoff`, branch `audit/shipment-candidate`,
  HEAD `dbcb8d7`, remote `origin` = the destination above, clean working tree.
- No `SHIPMENT_READINESS.md` existed; `docs/history-secret-scan-2026-11-05.json`
  recorded a prior scan (1 commit, 5,846 lines, 0 hard hits).

## Findings and fixes made in this audit

1. **Dockerfile could not build (blocker, fixed).** The runtime stage copied
   only `src/`/`scripts/` and then ran `pip install -e /app`, which fails
   without `pyproject.toml`; the builder also masked wheel-download failures
   with `|| true` and downloaded unnecessary pytest wheels. The image now runs
   from `PYTHONPATH=/app/src` (no build backend needed offline), copies the
   demo fixtures the `demo` command resolves via its `/app` fallback, and the
   builder downloads only the two runtime wheels without error masking.
2. **CI offline-demo step would fail on a root-created volume (fixed).**
   Docker creates a missing bind-mount source as root, which the non-root
   `signoff` user cannot write to. CI now pre-creates `out/ci-demo`.
3. **CI triggers/permissions (fixed).** Pushes previously triggered only on
   `main`, so this audit branch would never run CI; now all branches trigger.
   Added least-privilege `permissions: contents: read`. Third-party actions
   remain tag-pinned (`checkout@v4`, `setup-python@v5`) — SHA pinning was not
   applied because the SHAs could not be verified from this environment;
   recorded as a remaining hardening item, not claimed as done.
4. **Known-vulnerable dependency pin (fixed).** `pip-audit` reported
   CVE-2026-114609 (SSRF via image-resource dereferencing) and CVE-2026-114610
   (SVG `<use>` resource exhaustion) in pinned `fpdf2==2.8.4`. Signoff never
   passes user-controlled input to `FPDF.image()`/`write_html()` (PDF output
   is generated from internal templates only), so exposure was limited, but
   the pin is upgraded to `fpdf2==2.8.8` in `pyproject.toml`, `Dockerfile`,
   CI, `src/signoff/config.py`, renderers, tests, and current-state docs.
   The 0.1.0 CHANGELOG entry retains the historical 2.8.4 reference.
5. **Security policy discoverability (added).** Added root `SECURITY.md`
   pointing to `docs/SECURITY.md`. It honestly states that no monitored
   reporting contact exists yet — no address was invented.

`LICENSE` was a proprietary placeholder at audit time; the owner chose **MIT**
on 2026-11-06 and the file now carries the MIT text (commit `b782541`).

## Checks run (exact outcomes)

All commands run from the repository root on 2026-11-06:

| Check | Command | Outcome |
| --- | --- | --- |
| Tests | `PYTHONPATH=src python3 -m pytest` | **140 passed** |
| Coverage | `PYTHONPATH=src python3 -m pytest --cov=src/signoff --cov-report=term-missing -q` | **88%** total (1485 stmts, 181 missed) |
| Offline scan | `python3 scripts/check-offline.py` | OK — 41 files, zero network imports/calls/env reads |
| Scaffold | `python3 scripts/check-scaffold.py` | OK — 116 required files |
| Determinism | `PYTHONPATH=src python3 scripts/check-determinism.py --out /tmp/signoff-det` | OK — byte-identical |
| Demo + verify (host) | `python3 -m signoff demo --out /tmp/signoff-demo`, then `verify-pack` | Pack built (7 artifacts), `VERIFIED` |
| Docker build | `docker build -t signoff:shipment-audit .` | **Built** (after fix; failed before) |
| Docker offline demo | `docker run --rm --network none --read-only -v ... signoff:shipment-audit demo --out /out/demo` | Pack built (7 artifacts) |
| Docker verify | `docker run --rm --network none --read-only ... verify-pack --pack /data` | `VERIFIED` |
| Dependency audit | `pip-audit -r` on pinned runtime set | Before: 2 CVEs in fpdf2 2.8.4. After upgrade to 2.8.8: **No known vulnerabilities found** |
| pip check | `python3 -m pip check` | No broken requirements |

Note: the host environment has `fpdf2` installed at a different version than
the pin; tests were run with `PYTHONPATH=src` against the installed library
(2.8.8 after the audit upgrade) rather than a fresh venv install of the pin.
The Docker image installs the exact pinned wheels offline and was verified
separately. `pip-audit` was installed with `--user --break-system-packages`
into the operator's user site, not into the repository.

## Secret-history scan

- Scope: full reachable history (`git log --all -p`, 2 commits, 138 objects)
  plus `git grep` over tracked files, for private-key blocks, AWS access keys,
  GitHub tokens, Google API keys, and generic credential assignments.
- Result: **no hits**; new/modified files in this audit were also grepped with
  no hits. The prior recorded scan (`docs/history-secret-scan-2026-11-05.json`)
  likewise reported 0 hard hits. This is a pattern scan, not proof that no
  secret ever existed. No secret values are printed in this report.
- Tracked-file audit: no `.env`, private keys, databases, logs, customer data,
  or build outputs are tracked; `out/`, `.coverage`, `__pycache__/`, and
  `OWNER/` real-data paths are gitignored and Docker-ignored.

## Remaining limitations (not waived)

- Hosted GitHub Actions, branch protection, repository visibility, and remote
  state were **not verified** (no push was made or authorized). The workflow
  must be run on GitHub after the owner pushes.
- Third-party Actions are tag-pinned, not SHA-pinned; base images are now
  digest-pinned (`python:3.11-slim@sha256:07d48…`). Action SHA pinning remains
  open.
- Licence choice, security reporting contact, client use, and the authorisation
  of mapping rules remain owner decisions (`OWNER/DECISIONS-TO-MAKE.md`).
- This is a pre-production document factory: no real client data is committed,
  no client has an authorised mapping table in this repository, and no
  compliance certification exists.

**Status: locally shipment-ready** (tests, offline, determinism, Docker,
and dependency checks pass; fixes above committed locally), with
hosted-only verifications to run at first push. The owner authorised the
GitHub push on 2026-11-06; no version tag or GitHub release exists yet.

### Owner decisions since the audit (2026-11-06)

- **MIT licence adopted** (`LICENSE`) — licence risk cleared before any sale.
- **Pricing decided** (`OWNER/offer-and-pricing.md`): Egypt EGP 60–90k ·
  Gulf $2,500–4,000 · Global $3,000–6,000 per assessment; 50/50 terms,
  annual re-run at 40%. Recorded in `OWNER/DECISIONS-TO-MAKE.md` item 4.
- **Second client: not required now** (owner decision) — production readiness
  is proven by the first pilot; a second client is a post-launch goal.
- **Legal/tax deferred to first-sale income** (owner is a solo builder with
  no company yet) — push to GitHub is held until the owner closes this.
- **Hosted CI:** GitHub Actions is free and unlimited on public repos —
  verification happens at first push, no paid tier needed.

### Visitor-facing assets (ready for launch)

- `index.html` — single-file marketing page (problem, solution, value,
  engineering philosophy, decided pricing). Contact placeholder
  `index.html` (contact set 2026-11-06, replacing the example placeholder).
- `docs/VIDEO-DEMO-PROMPT.md` — autonomous-agent prompt for the 2-minute
  animated demo video; uses only repo files + a self-generated synthetic
  pack, with a hard rule against any real client data on screen.

## First real pilot pack — anonymized MENA call centre (2026-11-06)

After the audit above, the owner completed the human-owner track with a real
practitioner at a MENA call centre:

- The practitioner answered a 10-question blank form (4 Yes, 3 Partly, 2 No in
  the gaps round, then the remaining exports arrived) and supplied anonymized
  exports: QA review, audit events, provider inventory, roles/accountability,
  agent-identity log, escalations, training records, incident SLA log.
- The owner entered 10 mapping rules in `OWNER/mapping-table.csv`
  (`decided_by=Hatem Shalaby`, `date=2026-11-06`, `verified=yes` for all).
  These are human authorisations, **not cryptographic signatures**. The
  scaffold/test guards were updated accordingly: the pre-owner "header-only"
  assertion now requires named, dated, verified rows. Full suite: **140 passed**.
- Resulting pack (built offline, as-of 2026-11-07) reported **10/10 Yes with
  evidence, 0 gap rows**, and the verifier returned `VERIFIED`
  (`PK-278084a109d79591`). `VERIFIED` means the artifact digests and hash chain
  replay; it does **not** authenticate the source exports. Intermediate states
  were honest: stale 2025 audit rows read No (outside the 90-day window),
  `Completed` training statuses read No, and a 3-provider no-training gap
  (Provider C) was flagged until the client remediated it.
- **Oversight Statement:** it remains unsigned. No signature, key, or
  independent authorisation record is present in this repository.
- **Data boundary:** all client questionnaire data and exports are held
  **outside** this repository (operator's local `/tmp` only) and are not
  committed. `incident_register` was reconstructed from the dossier's evidence
  source table because the original file never arrived on disk. It is not a
  source record, so the 10/10 result above is **not valid source evidence** and
  must not be shown to a client or used in a release claim. Rebuild only from
  the client's original export.
- Production scope is unchanged: this pack evidences one pilot
  organization's records, subject to the reconstructed-record caveat above.
  Licence choice, pricing, legal/tax review, and a second client remain open
  (`OWNER/DECISIONS-TO-MAKE.md` items 2–8).

### Launch sequence (owner-authorised 2026-11-06)

Company/tax papers are deferred to first-sale income by owner decision
(`OWNER/DECISIONS-TO-MAKE.md` item 5). Push authorised; steps run in order
at launch:

```console
$ # 1. contact email already set in index.html ([REDACTED_EMAIL])
$ # 2. final sweep (all green as of 2026-11-06):
$ python3 scripts/check-scaffold.py && python3 scripts/check-offline.py
$ PYTHONPATH=src python3 -m pytest -q          # 140 passed
$ docker build -t signoff:latest .             # builds clean
$ # 3. push the branch, let hosted CI verify (free on public repos):
$ git push -u origin audit/shipment-candidate
$ # 4. tag + release once CI is green:
$ git tag -a v0.1.0 -m "v0.1.0 — hash-consistent pilot pack (not signed)"
$ git push origin v0.1.0
$ gh release create v0.1.0 --title "Signoff v0.1.0" --notes-file SHIPMENT_READINESS.md
$ # 5. optional: attach the 2-min video (out/video/signoff-demo-2min.mp4)
$ #    produced by following docs/VIDEO-DEMO-PROMPT.md
```

Nothing above has been executed as part of this assessment. A remote (`origin` →
`github.com/Hatemshalaby15071979/Sign-off`) is configured. The repository was
later published (private) on 2026-11-13; check `git ls-remote` and the hosted
CI run before assuming any tag, release, or green build exists.
