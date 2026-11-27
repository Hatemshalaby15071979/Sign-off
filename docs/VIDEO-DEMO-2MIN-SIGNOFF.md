# Signoff record — 2-minute demo video

Companion to `docs/VIDEO-DEMO-PROMPT.md`. Complete this record before the
2-minute demo video (`out/video/signoff-demo-2min.mp4`) is published. The
3-minute cut (`signoff-demo-3min.mp4`) is superseded by this decision
(D-013, 2026-11-06).

## 1. Decision

| Item | Value |
| ---- | ----- |
| Decision ID | D-013 |
| Date | 2026-11-06 |
| Decision | Cut demo video from 3 minutes (180 s) to 2 minutes (120 s ±5 s) |
| Reason | Social-first distribution; shorter completion and retention |
| Owner | Hatem Shalaby |

## 2. Deliverables (definition of done)

| File | Purpose | Status |
| ---- | ------- | ------ |
| `out/video/signoff-demo-2min.mp4` | Master, H.264 1080p30, AAC-LC | Complete locally; owner watch pending |
| `out/video/signoff-demo-2min.srt` | Burn-in + sidecar captions | Complete locally |
| `out/video/thumbnail.png` | 1280×720 sealed-pack thumbnail | Complete locally |
| `out/video/SCENE-NOTES.md` | Per-scene source citations + substitutions | Complete locally |

## 3. Verification gate (all must pass)

| # | Gate | Evidence | Result |
| - | ---- | -------- | ------ |
| 1 | `ffprobe` duration 115–125 s, 1920×1080, 30 fps, audio present | `ffprobe out/video/signoff-demo-2min.mp4` | PASS — 120.000 s, H.264 High/yuv420p, 30 fps, AAC-LC |
| 2 | Every on-screen claim traceable to a repo file (S4 → `docs/archive/SHIPMENT_READINESS.md`, S6 → `OWNER/offer-and-pricing.md`) | `out/video/SCENE-NOTES.md` citations | PASS — unsupported duration/count claims were removed |
| 3 | Leak check: zero client org names, contact names, scratch paths, real export row values in frames or project files | Local scan of scene sources and captions; synthetic dossier visibly watermarked | PASS — no real client rows or identities in video assets |
| 4 | Disclaimer visible on end frame ("Evidence packs prove internal consistency of your records — not certification.") | Final-frame inspection | PASS |
| 5 | Render reproducible: re-run produces identical output hash (or non-reproducibility documented) | SHA-256 comparison of two final encodes from the same fixed segments | PASS — byte-identical final encodes |
| 6 | Human watched end-to-end once | Watcher name + date | PENDING — owner must watch and sign |

The cut is a captioned, silent-autoplay draft with a low-level ambient bed; it
has no spoken narration because no local TTS voice model was available. This
does not satisfy the human-watch or owner-signature gate. The master, captions,
thumbnail, and scene notes remain under gitignored `out/`; they are not a
published release asset.

## 4. Content signoff

| Element | Source file | Verified (initials/date) |
| ------- | ----------- | ------------------------ |
| Problem / hook narration | `README.md`, `docs/archive/SHIPMENT_READINESS.md` | ☐ |
| Offline pipeline visual | `docs/ARCHITECTURE.md` | ☐ |
| Pilot stats (10/10 evidenced, 0 gaps; 90-day window refusals) | `docs/archive/SHIPMENT_READINESS.md` | ☐ |
| Pricing bands (EGP 60–90k / Gulf $2,500–4,000 / Global $3,000–6,000; 50/50 terms) | `OWNER/offer-and-pricing.md` | ☐ |
| "No compliance overclaiming" disclaimer present | `docs/VIDEO-DEMO-PROMPT.md` rule 3 | ☐ |
| No real client data anywhere in video | Rule 1 + gate #3 | ☐ |

## 5. Owner sign-off

I have watched the 2-minute demo video end-to-end and confirm it is accurate,
contains no real client data, makes no compliance overclaims, and matches the
decided pricing and pilot statistics.

- **Signed by (owner):** ______________________________
- **Name:** Hatem Shalaby
- **Date:** ______________
- **Authorized by (named accountable person):** ______________________________
- **Decision recorded:** D-013 in `docs/01-DECISION-LOG.md` (2026-11-06)

## 6. Publish decision

| Item | Value |
| ---- | ----- |
| Hosting | ☐ GitHub Release asset ☐ LinkedIn ☐ YouTube ☐ Not yet decided |
| Link added to `index.html` / `README.md` | ☐ |
| Release tag | `v0.1.0` or later, per `docs/archive/SHIPMENT_READINESS.md` launch sequence |
