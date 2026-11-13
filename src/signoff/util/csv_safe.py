"""CSV formula-injection defence (HI-08).

Spreadsheet programs treat a cell beginning with ``=``, ``+``, ``-``, ``@``,
a tab or a carriage return as a formula. Questionnaires, mapping tables and
exported source records are untrusted input, so every CSV export path must
neutralise those prefixes.

The standard mitigation is to prefix the cell with a single quote, which
Excel/LibreOffice treat as "this is literal text". Plain signed numbers and the
gap-list "-" sentinel are left alone: they cannot form a formula.
"""
from __future__ import annotations

from typing import Any

DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


def csv_safe(value: Any) -> str:
    """Return *value* as text that cannot start a spreadsheet formula."""
    text = "" if value is None else str(value)
    # Leading spaces do not stop Excel from evaluating a formula, so inspect
    # the first non-space character.
    probe = text.lstrip(" ")
    if not probe or probe[0] not in DANGEROUS_PREFIXES:
        return text
    # A lone "-" is the gap-list sentinel, and signed numbers such as "-5" or
    # "+5" are ordinary numeric cells, not formulas. Leaving them intact keeps
    # the CSV contract and does not create an injection vector.
    if probe == "-" or (probe[0] in "+-" and _is_number(probe)):
        return text
    return "'" + text


def csv_safe_row(row: list[Any]) -> list[str]:
    return [csv_safe(cell) for cell in row]
