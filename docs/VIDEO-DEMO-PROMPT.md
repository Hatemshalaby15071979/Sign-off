# Autonomous demo-video prompt — Signoff 2-minute animated demo

> **What this file is:** a complete, self-contained prompt. Paste it (or point
> an agent at this file) and it can produce the full 2-minute marketing video
> with no further input. It uses only files in this repository plus a
> synthetic demo pack it generates itself.
>
> **Owner decision (2026-11-06):** a public demo video is wanted for external
> visitors before the repo ships. **Owner decision (2026-11-06):** runtime cut
> from 3 minutes to 2 minutes (120 s ±5 s) for social-first distribution.

---

## THE PROMPT (start here)

You are an autonomous video-production agent. Your job: render a **2-minute
(120 s ±5 s), high-quality, animated demo video** for the Signoff project,
using only the files in this repository. Follow every rule. Do not ask
questions; when a rule and a shortcut conflict, the rule wins.

### Mission

Explain, in plain human language, (1) the real problem Signoff solves, (2) how
it solves it, shown with real screenshots of the software running, (3) why it
is worth the money, (4) the engineering philosophy behind it. The video must
be honest: every number and claim must be traceable to a file in this repo.

### Hard rules (violating any = failed job)

1. **No client data, ever.** Screenshots and screen recordings come only
   from a *synthetic* pack you build yourself with `python -m signoff demo`.
   Never open, display, or reference anything outside this repository — no
   operator scratch directories in `/tmp`, no `~/Downloads`, no real export
   anywhere. Anonymized *statistics* already committed to this repo (e.g.
   "10/10 questions evidenced, 0 gaps") may be shown as text — never the
   underlying rows, answer-level detail, or the real dossier, and never any
   client organization or contact name.
2. **No fabricated claims.** Every on-screen number, price, and capability
   must appear in one of: `README.md`, `SHIPMENT_READINESS.md`,
   `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `OWNER/offer-and-pricing.md`.
   Cite the source file in your scene notes (not on screen).
3. **No compliance overclaiming.** Always keep the disclaimer idea visible
   where a pack is shown: an evidence pack proves internal consistency of
   supplied records — it is *not* a certification. Do not say "compliant",
   "certified", or "guaranteed".
4. **Offline by design is the hero message.** Never imply the tool phones
   home. No cloud/AI-service logos in a way that suggests the tool uses them.
5. **Deterministic render.** Fixed seed, injected clock, no network access
   during production. Re-running the pipeline must reproduce byte-identical
   frames where the tooling allows.

### Inputs (read these first, in order)

| # | File | Why |
| - | ---- | --- |
| 1 | `README.md` | product definition, 60-second demo commands, status |
| 2 | `index.html` | the marketing narrative and copy you are animating |
| 3 | `SHIPMENT_READINESS.md` | verified facts, pilot results, honest gaps |
| 4 | `CHANGELOG.md` | pilot story + operator lessons (the refusal moments) |
| 5 | `docs/ARCHITECTURE.md` | pipeline stages for the flow animation |
| 6 | `docs/OFFLINE-GUARANTEE.md` + `docs/SECURITY.md` | the offline/security claims you may make |
| 7 | `OWNER/offer-and-pricing.md` | the three price bands (decided 2026-11-06) |
| 8 | `OWNER/mapping-table.csv` | what a signed mapping rule looks like (structure only) |
| 9 | `scripts/demo` + `src/signoff/demo.py` | how to generate the synthetic pack you will screenshot |

### Step 1 — build your visual assets (synthetic only)

```bash
cd <repo-root>
python -m signoff demo --out out/demo          # synthetic pack
python -m signoff verify-pack --pack out/demo  # must print VERIFIED
```

Capture, at 1920×1080 (or 2× for 4K), these shots (PNG, transparent where
useful): (a) terminal: `demo` build output ending `VERIFIED`; (b) terminal:
`verify-pack` output; (c) `out/demo/dossier.html` rendered in a headless
browser — hero header, evidence table, gap list, oversight statement with its
**blank signature line**; (d) `questionnaire-answers.csv` and `gap-list.csv`
opened in a spreadsheet view; (e) a single signed mapping row from
`OWNER/mapping-table.csv` (crop to one row); (f) the `SIMULATION_DISCLOSURE`
stamp zoomed. Use a headless Chromium (`--screenshot`) or Playwright; if none
is available, render the HTML to PNG with the lightest local tool that exists
and note the substitution in the scene notes.

### Step 2 — scene script (verbatim narration + visual direction)

Total runtime **120 s**. Narration below is the script — read it aloud
verbatim (TTS or human). Timings are targets; ±2 s per scene is fine if the
total stays 120 ±5 s.

**S1 · 0:00–0:15 · The hook**
Narration: *"Your client sends an AI governance questionnaire.
Every answer must point to a real record. Your team has the records — across
spreadsheets. So what happens? Manual copy-pasting. A stale PDF. And one day,
an answer you can't back up."*
Visual: kinetic typography on dark navy; questionnaire pages stacking; a
redacted answer with a shaky question mark; clock spinning. Ends on the words
"an answer you can't back up" in amber.

**S2 · 0:15–0:35 · What Signoff is**
Narration: *"Signoff is an offline document factory. You give it the
questionnaire you already received, and the CSV exports you already own. It
gives back a signed, hash-chained evidence pack that says exactly what you
can prove — and names the gaps you can't. It runs on your own machine. Nothing
leaves the building."*
Visual: five blocks fly in and connect — Parse → Sign mapping → Build → Pack
→ Verify (this is the `docs/ARCHITECTURE.md` pipeline); a padlock closes over
a laptop; a "0 network calls" badge (source: `docs/OFFLINE-GUARANTEE.md`).

**S3 · 0:35–0:57 · Live walkthrough (screenshots)**
Narration: *"Here it is running. One command parses the questionnaire — every
question gets an ID, nothing is paraphrased. You sign the mapping: a human
decides, per question, which file and which columns count as proof. The
machine never writes that table. Then: build. Offline. One command later you
have a dossier, an answered questionnaire, a gap list, and a hash-chained set
of evidence events. Verify replays the chain — every artifact matches its
digest, or the pack is rejected."*
Visual: screen-recording style, sped up 2×, with zoom-pans on: parse output,
the signed mapping row (Hatem Shalaby, date, verified=yes), the build
terminal ending in a pack ID, the dossier rendering, then `verify-pack`
printing `VERIFIED` — hold on that word for 1 s with a subtle glow.

**S4 · 0:57–1:19 · Proof: the first real pilot**
Narration: *"This isn't a toy. In November 2026, a real call center answered
a ten-question form and handed over eight anonymized exports. Signoff built
the pack offline and verified it: ten of ten questions evidenced, zero gaps.
And it pushed back along the way — stale audit rows from last year scored No,
because they were outside the ninety-day window. The refusal behavior is the
product."*
Visual: big counters animating 10/10 and 0 gaps (text only — no client rows);
two "refusal moment" cards sliding in: `No — outside 90-day window` and
`GAP — provider contract` then flipping to `Yes — remediated`. Cite
`SHIPMENT_READINESS.md` in scene notes. **Show no exports, no dossier from
the real pack.**

**S5 · 1:19–1:39 · Engineering philosophy + why it's worth the money**
Narration: *"Four rules shaped it. One: fail closed, never guess — an
unmapped question stays unmapped; a missing timestamp is a refusal, not an
invention. Two: humans sign, machines prove — every rule carries a name, a
date, a verification, and the oversight statement ships blank, because a
machine must never produce a signature. Three: determinism is a feature —
injected clock, canonical JSON, SHA-256 hash chain; the same inputs always
produce byte-identical output, in front of an auditor. Four: small and
auditable — Python standard library plus one pinned PDF library, every
dependency hash-locked. It is a two-week fixed-price engagement —
questionnaire in, signed pack out."*
Visual: four numbered cards, each with a one-line icon animation (guillotine
for fail-closed, pen for humans-sign, gears for determinism, feather for
small). Keep this scene typographic and calm — it is the credibility beat.
Then a calendar marking the two-week engagement.

**S6 · 1:39–1:55 · Pricing**
Narration: *"One price, per assessment, fixed: in Egypt, sixty to ninety
thousand pounds. Across the Gulf, twenty-five hundred to four thousand
dollars. For EU and UK buyers, three to six thousand. Fifty percent up
front, fifty on delivery."*
Visual: three market cards (EGP / USD Gulf / USD Global) rising in sequence
with the bands from `OWNER/offer-and-pricing.md`; terms line beneath. Cards
must match the decided bands exactly — no other numbers on screen.

**S7 · 1:55–2:00 · Close**
Narration: *"Signoff. Answer the questionnaire with a signed evidence pack.
Offline by design. MIT licensed."*
Visual: logo/wordmark, the five pipeline blocks collapsing into a single
sealed-pack icon, then `index.html` URL / contact and a final frame that
holds for 2 s. Footer line small: *"Evidence packs prove internal
consistency of your records — not certification."*

### Step 3 — production spec

- **Format:** MP4, H.264 High, yuv420p, **1920×1080 @ 30 fps** (4K master
  optional), AAC-LC 192 kbps audio, faststart moov.
- **Duration:** 120 s ±5 s (hard gate).
- **Look:** dark navy `#0d1729` background, ink `#10192b`, accent `#1f6feb`,
  ok-green `#0f7b45`, warn-amber `#b45309` — the same palette as
  `index.html`. Sans-serif (system font stack), generous whitespace, 2–3
  animation motions per scene max. No stock footage, no emoji, no watermarks.
- **Audio:** narration mixed at −16 LUFS integrated; subtle ambient bed at
  −26 dB or none; one soft UI click on each terminal command.
- **Captions:** burn-in English subtitles **and** ship a sidecar `.srt`
  (accessibility + silent autoplay on social).
- **Thumbnails:** one 1280×720 PNG: the sealed-pack icon + *"10/10 evidenced.
  0 gaps. Offline."*
- **Toolchain (pick what exists locally, in this order):** Remotion (React,
  deterministic) → Motion Canvas → Manim (community) → generated SVG frames +
  ffmpeg. If only ffmpeg exists, animate with `drawtext`/`zoompan` over the
  PNGs from Step 1 and note the substitution. No cloud render services (the
  production itself should honor the offline ethos).

### Step 4 — verification gate (all must pass before you call it done)

1. `ffprobe` shows duration 115–125 s, 1920×1080, 30 fps, has audio track.
2. Every claim in the narration matches its source file (re-check S4 numbers
   against `SHIPMENT_READINESS.md`, S6 against `OWNER/offer-and-pricing.md`).
3. **Leak check:** grep the render project for any client organization
   name, contact name, operator scratch paths, and any row values from real
   exports — zero hits allowed in frames or project files. (The pilot
   *statistics* and repo-committed pilot narrative are allowed; underlying
   client rows and identities are not.)
4. Disclaimer present in S7 end frame.
5. Re-run the render: identical output hash (or document why the toolchain is
   not bit-reproducible).
6. A human has watched it once end-to-end.

### Output (definition of done)

```
out/video/signoff-demo-2min.mp4      # the master
out/video/signoff-demo-2min.srt      # captions
out/video/thumbnail.png              # 1280×720
out/video/SCENE-NOTES.md             # per-scene source citations + any substitutions
out/video/SIGNOFF.md                 # owner signoff record (template in docs/VIDEO-DEMO-2MIN-SIGNOFF.md)
```

Commit nothing under `out/` (it is git-ignored); the owner decides whether the
mp4 goes into the repo or a release later.

---

## Owner checklist (before publishing the video)

- [ ] Watch it once end-to-end (verification gate step 6).
- [x] Contact in `index.html` set to `[REDACTED_EMAIL]` (2026-11-06).
- [ ] Decide hosting: GitHub Release asset / LinkedIn / YouTube — then the
  link can be added to `index.html` and `README.md`.
- [ ] Sign off the 2-minute cut using `docs/VIDEO-DEMO-2MIN-SIGNOFF.md`.
