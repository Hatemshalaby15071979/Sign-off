"""Mandatory disclosures: simulation watermark + "What this pack does NOT prove".

Every artifact (HTML, PDF, JSON, CSV, statement) carries these. Renderers
import the functions here — there is exactly one copy of the wording.
"""
from __future__ import annotations

from signoff.util.sim_flag import (
    NOT_PROOF_POINTS, NOT_PROOF_TITLE, SIMULATION_DISCLOSURE,
    UNVERIFIED_RULES_BANNER,
)


def active_banners(simulated: bool, unverified: bool) -> list[str]:
    out: list[str] = []
    if simulated:
        out.append(SIMULATION_DISCLOSURE)
    if unverified:
        out.append(UNVERIFIED_RULES_BANNER)
    return out


def not_proof_text() -> str:
    lines = [NOT_PROOF_TITLE, ""]
    for i, point in enumerate(NOT_PROOF_POINTS, start=1):
        lines.append(f"{i}. {point}")
    return "\n".join(lines)


def not_proof_html() -> str:
    import html as _h
    items = "".join(f"<li>{_h.escape(p)}</li>" for p in NOT_PROOF_POINTS)
    return (
        "<section class=\"noproof\"><h2>"
        + _h.escape(NOT_PROOF_TITLE) + "</h2><ol>" + items + "</ol></section>"
    )


def not_proof_json() -> list[str]:
    return list(NOT_PROOF_POINTS)


def not_proof_csv_rows() -> list[tuple[str, str]]:
    rows = [("disclosure", NOT_PROOF_TITLE)]
    rows += [("disclosure", p) for p in NOT_PROOF_POINTS]
    return rows
