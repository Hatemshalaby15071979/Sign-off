"""HTML renderer — one self-contained HTML file.

Inline CSS only: no external fonts, scripts, stylesheets or images; it must
work opened with `file://` while offline. All data comes from the pack; all
text is HTML-escaped.
"""
from __future__ import annotations

import html as _h
from typing import TYPE_CHECKING

from signoff.render.appendix import appendix_html
from signoff.render.disclosure import active_banners, not_proof_html

if TYPE_CHECKING:  # pragma: no cover
    from signoff.model.evidence_pack import EvidencePack

CSS = """
:root{--ink:#1b2430;--muted:#5b6470;--rule:#d5dbe3;--ok:#1a6b3a;--warn:#8a5a00;--bad:#8a1f1f;--accent:#22456b}
*{box-sizing:border-box}
body{font-family:"Segoe UI",system-ui,-apple-system,sans-serif;color:var(--ink);margin:0;background:#f7f8fa}
main{max-width:1080px;margin:0 auto;padding:24px}
h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:28px 0 8px;color:var(--accent)}
h3{font-size:15px;margin:18px 0 6px}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fff}
th,td{border:1px solid var(--rule);padding:6px 8px;text-align:left;vertical-align:top}
th{background:#eef2f6}
code{background:#eef1f4;padding:1px 4px;border-radius:3px;font-size:12px}
.banner{border:2px solid #b3621f;background:#fdf3e7;padding:10px 12px;font-weight:600;margin:10px 0}
.noproof ol{margin:6px 0 0 18px;padding:0}
.noproof li{margin-bottom:6px}
.meta td{font-size:12px}
.pct-full{color:var(--ok);font-weight:700}.pct-zero{color:var(--bad);font-weight:700}.pct-part{color:var(--warn);font-weight:700}
.small{color:var(--muted);font-size:12px}
.unmapped td{background:#fff8e6}
.gap td{background:#fff2f2}
footer{margin-top:30px;border-top:1px solid var(--rule);padding-top:10px;color:var(--muted);font-size:12px}
.sig td{height:34px}
""".strip()


def _pct_class(pct: float) -> str:
    if pct >= 100.0:
        return "pct-full"
    if pct <= 0.0:
        return "pct-zero"
    return "pct-part"


def _coverage_table(pack: "EvidencePack") -> str:
    seen: set[tuple] = set()
    rows = []
    for c in pack.coverage:
        key = (c.pattern_id, c.rule_id, c.source_qid)
        if key in seen:
            continue
        seen.add(key)
        if c.pct is None:
            pct_text = "N/A (no events in period)"
            cls = ""
        else:
            pct_text = f"{c.pct}%"
            cls = _pct_class(c.pct)
        rows.append(
            f"<tr><td>{_h.escape(c.rule_id)}</td><td>{_h.escape(c.pattern_id)}</td>"
            f"<td>{_h.escape(c.source_qid)}</td>"
            f"<td class=\"{cls}\">{_h.escape(pct_text)}</td>"
            f"<td>{c.matched} / {c.expected}</td>"
            f"<td class=\"small\">{_h.escape(c.denominator_label)}</td></tr>")
    return ("<table class=\"coverage\">"
            "<tr><th>rule</th><th>pattern</th><th>qid</th><th>coverage</th>"
            "<th>matched / expected</th><th>explicit denominator</th></tr>"
            + "".join(rows) + "</table>")


def _answers_table(pack: "EvidencePack") -> str:
    rows = []
    for q in pack.questions:
        cls = "unmapped" if q.trust_label == "UNMAPPED" else ""
        rows.append(
            f"<tr class=\"{cls}\"><td>{_h.escape(q.qid)}</td>"
            f"<td>{_h.escape(q.answer_type)}</td>"
            f"<td>{_h.escape(q.answer)}</td>"
            f"<td class=\"small\">{_h.escape(q.trust_label)}"
            + (f" — {q.evidence_id}" if q.evidence_id else "")
            + f"</td></tr>")
    return ("<table class=\"answers\">"
            "<tr><th>qid</th><th>type</th><th>answer (with evidence id)</th>"
            "<th>status</th></tr>" + "".join(rows) + "</table>")


def _gaps_table(pack: "EvidencePack") -> str:
    rows = []
    for g in pack.gaps:
        files = g.affected_source_files or ["(no file of this kind supplied)"]
        rows.append(
            f"<tr class=\"gap\"><td>{_h.escape(g.rule_id)}</td>"
            f"<td>{_h.escape(g.source_qid)}</td>"
            f"<td>{_h.escape(g.reason)}</td>"
            f"<td>{'<br>'.join(_h.escape(f) for f in files)}</td>"
            f"<td>{g.affected_row_count}</td></tr>")
    if not rows:
        rows.append("<tr><td colspan=5>No coverage gaps in window; see "
                    "unmapped-question rows if any.</td></tr>")
    return ("<table class=\"gaps\">"
            "<tr><th>rule</th><th>qid</th><th>gap</th>"
            "<th>files holding these records</th><th>unmet rows</th></tr>"
            + "".join(rows) + "</table>")


def _evidence_table(pack: "EvidencePack") -> str:
    rows = []
    for ev in pack.events:
        rows.append(
            f"<tr><td><code>{_h.escape(ev.event_id)}</code></td>"
            f"<td>{_h.escape(ev.ts)}</td><td>{_h.escape(ev.state)}</td>"
            f"<td>{_h.escape(ev.actor_identity)}</td>"
            f"<td class=\"small\">{_h.escape(ev.action)}</td>"
            f"<td class=\"small\">{_h.escape(ev.source_file)}:{ev.source_row}</td>"
            f"<td class=\"small\">{_h.escape(ev.policy_rule)}</td></tr>")
    return ("<table class=\"events\">"
            "<tr><th>event id</th><th>ts (UTC)</th><th>state</th><th>actor</th>"
            "<th>action</th><th>source row</th><th>policy rule</th></tr>"
            + "".join(rows) + "</table>")


def _chain_table(pack: "EvidencePack") -> str:
    rows = []
    for ev in pack.events:
        rows.append(
            f"<tr><td><code>{_h.escape(ev.event_id)}</code></td>"
            f"<td class=\"small\" style=\"word-break:break-all\">"
            f"{_h.escape(ev.hash)}</td>"
            f"<td class=\"small\" style=\"word-break:break-all\">"
            f"{_h.escape(ev.prev_hash)}</td>"
            f"<td class=\"small\">{' '.join(_h.escape(e) for e in ev.evidence_ids) or '—'}</td></tr>")
    return ("<table><tr><th>event</th><th>hash</th><th>prev hash</th>"
            f"<th>evidence ids</th></tr>{''.join(rows)}"
            f"<tr><td colspan=4><b>chain head:</b> "
            f"<span style=\"word-break:break-all\">{_h.escape(pack.head)}</span></td></tr></table>")


def _statement_block(pack: "EvidencePack") -> str:
    return (
        "<section class=\"statement\"><h2>Oversight Statement (for human "
        "signature)</h2>"
        "<p>Statement: I confirm that the oversight evidence summarised in "
        "this pack was reconstructed from records our organisation supplied, "
        "that nothing has been generated that we cannot point to in our own "
        "records, and that the gaps listed are accurate at the as-of date.</p>"
        "<table class=\"sig\">"
        f"<tr><td>Pack</td><td><code>{_h.escape(pack.pack_id)}</code></td></tr>"
        f"<tr><td>As-of</td><td>{_h.escape(pack.as_of)}</td></tr>"
        "<tr><td>Accountable person (name)</td><td>____________________________</td></tr>"
        "<tr><td>Role</td><td>____________________________</td></tr>"
        "<tr><td>Signature</td><td>____________________________</td></tr>"
        "<tr><td>Date</td><td>____________________________</td></tr>"
        "</table>"
        "<p><b>This statement is signed by a human. Signoff never signs on "
        "anyone's behalf.</b></p></section>")


def render_html(pack: "EvidencePack") -> str:
    banners_html = "".join(
        f"<div class=\"banner\">{_h.escape(b)}</div>"
        for b in active_banners(pack.simulated, pack.unverified_rules))
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8">
<title>Signoff evidence dossier</title>
<style>{CSS}</style></head>
<body><main>
<h1>Signoff — AI questionnaire evidence dossier</h1>
<p>A signed, decision-by-decision evidence pack reconstructed from records
the customer supplied. Built fully offline; no model took any decision here.</p>
{banners_html}
<h2>Pack summary</h2>
<table class="meta">
<tr><td>Pack id</td><td><code>{_h.escape(pack.pack_id)}</code></td></tr>
<tr><td>As-of (injected)</td><td>{_h.escape(pack.as_of)}</td></tr>
<tr><td>Chain head</td><td style="word-break:break-all"><code>{_h.escape(pack.head)}</code></td></tr>
<tr><td>Questions</td><td>{len(pack.questions)} ({len(pack.unmapped_qids)} unmapped)</td></tr>
<tr><td>Evidence events (chain)</td><td>{len(pack.events)}</td></tr>
<tr><td>Gap rows</td><td>{len(pack.gaps)}</td></tr>
<tr><td>Rules / patterns</td><td>{len(pack.rules)}</td></tr>
<tr><td>Runtime</td><td class="small">Python 3.11 standard library + fpdf2 2.8.8 (offline build)</td></tr>
</table>

<h2>Coverage (with explicit denominators)</h2>
<p>A percentage is only shown with its denominator; a zero denominator is
reported N/A, never 100%.</p>
{_coverage_table(pack)}

<h2>Questionnaire answers</h2>
<p>Unmapped questions are answered with the literal <code>UNMAPPED</code>;
no inference, no paraphrase.</p>
{_answers_table(pack)}

<h2>Gap list (the page an auditor will read first)</h2>
{_gaps_table(pack)}

<h2>Evidence events (traceability: file and 1-based row)</h2>
{_evidence_table(pack)}

<h2>Hash chain (sha256 over canonical serialisation)</h2>
{_chain_table(pack) if pack.events else "<p>No events in the pack.</p>"}

{not_proof_html()}
{appendix_html()}
{_statement_block(pack)}
<footer>Rendered by Signoff (self-contained HTML — no external resources,
no network access, no fonts loaded). Simulated watermark active: {str(pack.simulated).lower()}.</footer>
</main></body></html>
"""
