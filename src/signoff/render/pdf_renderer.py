"""PDF renderer — pinned pure-Python library (fpdf2==2.8.8), same content
as the HTML dossier. No external fonts, no network calls, no images: this
must render inside an air-gapped container.
"""
from __future__ import annotations

import io
from typing import TYPE_CHECKING

from fpdf import FPDF

from signoff.render.appendix import APPENDIX_BANNER, appendix_rows
from signoff.render.disclosure import (
    NOT_PROOF_POINTS, NOT_PROOF_TITLE, SIMULATION_DISCLOSURE,
    UNVERIFIED_RULES_BANNER,
)
from signoff.util.clock import parse_instant

if TYPE_CHECKING:  # pragma: no cover
    from signoff.model.evidence_pack import EvidencePack

PAGE_W = 210  # A4 portrait, mm

_ASCII_MAP = {"—": "-", "–": "-", "…": "...", "’": "'", "‘": "'",
              "“": '"', "”": '"', "→": "->", "•": "-"}


def _ascii(text: str) -> str:
    """Latin-1-safe text for the pure core fonts (deterministic transposition)."""
    for src, dst in _ASCII_MAP.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class _Dossier(FPDF):
    """Fixed header/footer: no wall-clock values anywhere on the page."""

    def header(self) -> None:
        self.set_font("helvetica", "B", 11)
        self.cell(0, 8, "Signoff - AI questionnaire evidence dossier",
                  new_x="LMARGIN", new_y="NEXT")

    def footer(self) -> None:
        self.set_y(-14)
        self.set_font("helvetica", "", 8)
        self.cell(0, 8, f"offline build - page {self.page_no()}/{{nb}}",
                  align="C")


def _heading(doc: FPDF, text: str) -> None:
    doc.ln(2)
    doc.set_font("helvetica", "B", 13)
    doc.set_text_color(34, 69, 107)
    doc.multi_cell(0, 7, _ascii(text), new_x="LMARGIN", new_y="NEXT")
    doc.set_text_color(0, 0, 0)
    doc.ln(1)


def _para(doc: FPDF, text: str, size: int = 9) -> None:
    doc.set_font("helvetica", "", size)
    doc.multi_cell(0, 5, _ascii(text), new_x="LMARGIN", new_y="NEXT")


def _banner(doc: FPDF, text: str) -> None:
    doc.set_font("helvetica", "B", 9)
    doc.set_text_color(140, 60, 10)
    doc.multi_cell(0, 5, _ascii(text), new_x="LMARGIN", new_y="NEXT")
    doc.set_text_color(0, 0, 0)
    doc.ln(1)


def _kv_table(doc: FPDF, rows: list[tuple[str, str]]) -> None:
    for key, value in rows:
        doc.set_font("helvetica", "B", 8)
        doc.cell(38, 5, _ascii(key))
        doc.set_font("helvetica", "", 8)
        doc.multi_cell(0, 5, _ascii(str(value)), new_x="LMARGIN", new_y="NEXT")


def _simple_table(doc: FPDF, header: list[str], rows: list[list[str]],
                  widths: list[float]) -> None:
    col_w = [w * PAGE_W for w in widths]  # proportional widths summing to ~1.0
    doc.set_font("helvetica", "B", 7.5)
    for w, head in zip(col_w, header):
        doc.cell(w, 5, _ascii(_clip(head, w)), border=1)
    doc.ln()
    doc.set_font("helvetica", "", 7.5)
    for row in rows:
        for w, cell in zip(col_w, row):
            doc.cell(w, 5, _ascii(_clip(cell, w)), border=1)
        doc.ln()
    doc.ln(1)


def _clip(text: str, width_mm: float) -> str:
    """Clip long text so single-line table cells never overflow."""
    approx_chars = max(6, int(width_mm / 1.9))
    text = text.replace("\n", " ").strip()
    return text if len(text) <= approx_chars * 2 else text[:approx_chars * 2 - 1] + "…"


def render_pdf(pack: "EvidencePack") -> bytes:
    """Render deterministic PDF bytes using the pack's injected instant."""
    doc = _Dossier()
    doc.set_creation_date(parse_instant(pack.as_of))
    doc.set_margins(15, 15, 15)
    doc.set_auto_page_break(auto=True, margin=18)
    doc.set_title("Signoff evidence dossier")
    doc.set_author("Signoff (offline build)")
    doc.set_subject("AI questionnaire evidence pack")
    doc.set_creator("Signoff 0.1.0")
    doc.set_producer("Signoff 0.1.0 (fpdf2, offline)")
    doc.set_keywords("signoff, evidence, questionnaire")
    doc.add_page()

    if pack.simulated:
        _banner(doc, SIMULATION_DISCLOSURE)
    if pack.unverified_rules:
        _banner(doc, UNVERIFIED_RULES_BANNER)

    _heading(doc, "Pack summary")
    _kv_table(doc, [
        ("Pack id", pack.pack_id),
        ("As-of (injected)", pack.as_of),
        ("Chain head", pack.head),
        ("Questions", f"{len(pack.questions)} ({len(pack.unmapped_qids)} unmapped)"),
        ("Evidence events", str(len(pack.events))),
        ("Gap rows", str(len(pack.gaps))),
        ("Rules", str(len(pack.rules))),
    ])

    _heading(doc, "Coverage (with explicit denominators)")
    cov_rows = []
    for c in pack.coverage:
        cov_rows.append([
            c.rule_id, c.pattern_id, c.source_qid,
            "N/A" if c.pct is None else f"{c.pct}%",
            f"{c.matched}/{c.expected}",
        ])
    _simple_table(doc, ["rule", "pattern", "qid", "cov", "m/e"], cov_rows,
                  [0.14, 0.28, 0.12, 0.1, 0.1])

    _heading(doc, "Questionnaire answers")
    ans_rows = [[q.qid, q.answer_type, q.answer] for q in pack.questions]
    _simple_table(doc, ["qid", "type", "answer"], ans_rows,
                  [0.1, 0.14, 0.62])

    _heading(doc, "Gap list")
    if pack.gaps:
        gap_rows = [[g.rule_id, g.source_qid, g.reason,
                     ", ".join(g.affected_source_files) or "-", str(g.affected_row_count)]
                    for g in pack.gaps]
        _simple_table(doc, ["rule", "qid", "gap", "files", "unmet"], gap_rows,
                      [0.09, 0.09, 0.46, 0.26, 0.08])
    else:
        _para(doc, "No coverage gaps in window; see unmapped-question rows if any.")

    _heading(doc, "Evidence events")
    ev_rows = []
    for ev in pack.events:
        ev_rows.append([
            ev.event_id or "-", ev.ts, ev.state, ev.actor_identity,
            f"{ev.source_file}:{ev.source_row}",
        ])
    if ev_rows:
        _simple_table(doc, ["event", "ts", "state", "actor", "source"], ev_rows,
                      [0.18, 0.2, 0.16, 0.16, 0.26])

    _heading(doc, NOT_PROOF_TITLE)
    for point in NOT_PROOF_POINTS:
        _para(doc, "- " + point)

    _heading(doc, "Appendix — control cross-reference (informational)")
    _para(doc, APPENDIX_BANNER, size=8)
    app_rows = [[row[0], row[1], row[2]] for row in appendix_rows()]
    _simple_table(doc, ["area", "EU AI Act", "ISO/IEC 42001"], app_rows,
                  [0.4, 0.32, 0.26])

    _heading(doc, "Oversight Statement (for human signature)")
    _para(doc, "Statement: I confirm that the oversight evidence summarised in "
               "this pack was reconstructed from records our organisation "
               "supplied, that nothing has been generated that we cannot point "
               "to in our own records, and that the gaps listed are accurate "
               "at the as-of date.")
    _kv_table(doc, [
        ("Pack", pack.pack_id),
        ("As-of", pack.as_of),
        ("Accountable person (name)", "____________________________"),
        ("Role", "____________________________"),
        ("Signature", "____________________________"),
        ("Date", "____________________________"),
    ])
    _para(doc, "This statement is signed by a human. Signoff never signs on "
               "anyone's behalf.")

    return bytes(doc.output())
