"""Mapping-table loader — STRICTLY read-only, never modifies owner files."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from signoff.errors import MappingError
from signoff.mapping.patterns import dedup_report
from signoff.mapping.validator import validate_rules
from signoff.model.mapping_rule import COLUMNS, MappingRule
from signoff.util.sim_flag import UNVERIFIED_RULES_BANNER


def mapping_file_hash(path: Path) -> str:
    """sha256 of the mapping table bytes (traceability, read-only)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mapping(
    path: Path,
    *,
    allow_unverified: bool = False,
    echo=print,
) -> tuple[list[MappingRule], bool]:
    """Load + validate the mapping table.

    Returns (rules, unverified_flag). Refuses (fail closed) when:
    - the file is unreadable or is not the contract CSV,
    - the header is missing/wrong (the contract order is enforced),
    - there are no rules and --allow-unverified was NOT passed.
    The loader never writes to, or moves, the owner's file.
    """
    if not path.exists():
        raise MappingError(f"mapping table not found: {path}")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise MappingError(f"cannot read mapping table {path}: {exc}") from exc
    lines = [ln for ln in text.splitlines() if ln.strip()
             and not ln.lstrip().startswith("#")]
    if not lines:
        raise MappingError(
            f"{path}: mapping table is empty (not even the header). "
            "Start from OWNER/mapping-table.template.csv and sign each rule "
            "(docs/MAPPING-TABLE-GUIDE.md).")
    reader = csv.reader(lines)
    header = next(reader, None)
    header_norm = [h.strip() for h in (header or [])]
    if header_norm != COLUMNS:
        raise MappingError(
            f"{path}: header {header_norm!r} != contract header {COLUMNS!r}")
    rows = []
    for lineno, record in enumerate(reader, start=2):
        if len(record) != len(COLUMNS):
            raise MappingError(
                f"{path} line {lineno}: {len(record)} fields, expected {len(COLUMNS)}")
        rows.append(dict(zip(COLUMNS, record)))

    rules = validate_rules(rows, allow_unverified=allow_unverified)
    unverified = bool(allow_unverified) or any(r.verified != "yes" for r in rules)
    if not rules and allow_unverified:
        echo("WARNING: the mapping table has NO rules; every question will be "
             "UNMAPPED. Loud warning per docs/01-DECISION-LOG.md.")
    if allow_unverified:
        echo(f"WARNING: running with --allow-unverified. {UNVERIFIED_RULES_BANNER}")
    echo(f"mapping table: {dedup_report(rules)}" if rules else
         "mapping table: 0 signed rules")
    return rules, unverified
