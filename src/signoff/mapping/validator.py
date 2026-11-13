"""Mapping-table validator — fail-closed on anything a human signer must fix.

Rejections (all errors name the offending rule_id):
- duplicate rule_id; duplicate source_qid (1 question = 1 authorised rule)
- blank required fields (incl. question, evidence_needed, where_to_find_it,
  if_missing_gap, decided_by, date)
- answer_type outside yes_no|free_text|attachment
- verified outside yes|no
- decided_by == OWNER_PENDING in a real build
- vague evidence_needed (only boilerplate like "human oversight exists") or
  evidence_needed not naming a concrete file
- dates that are not ISO dates
"""
from __future__ import annotations

import re
import datetime as dt
from pathlib import Path

from signoff.config import OWNER_PENDING
from signoff.errors import MappingError
from signoff.model.mapping_rule import COLUMNS, MappingRule

ANSWER_TYPES_OK = {"yes_no", "free_text", "attachment"}
VERIFIED_OK = {"yes", "no"}

VAGUE_PHRASES = {
    "human oversight exists", "the vendor handles testing", "ai is monitored",
    "monitored", "provided by vendor", "see vendor policy", "vendor confirms",
    "trust the vendor", "process is compliant", "oversight in place",
    "ai under control", "no action needed",
}

FILENAME_RE = re.compile(r"[\w][\w./ -]{0,64}\.(csv|xlsx|docx|txt|md|json)\b")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _rule_is_vague(evidence_needed: str) -> bool:
    text = evidence_needed.strip().lower()
    if text in VAGUE_PHRASES:
        return True
    if not FILENAME_RE.search(evidence_needed):
        return True  # a concrete rule must reference a concrete file
    return False


def validate_rules(rows: list[dict], *, allow_unverified: bool = False) -> list[MappingRule]:
    """Validate raw mapping-table rows; return MappingRules; fail closed."""
    problems: list[str] = []
    seen_rule_ids: set[str] = set()
    seen_qids: set[str] = set()
    rules: list[MappingRule] = []

    for index, row in enumerate(rows, start=1):
        prefix = f"row {index}"
        missing = [c for c in COLUMNS if c not in row]
        if missing:
            raise MappingError(f"{prefix}: columns missing from table: {missing}")
        rule_id = (row["rule_id"] or "").strip()
        pattern_id = (row["pattern_id"] or "").strip()
        source_qid = (row["source_qid"] or "").strip()
        question = (row["question"] or "").strip()
        answer_type = (row["answer_type"] or "").strip().lower()
        evidence_needed = (row["evidence_needed"] or "").strip()
        where_to_find_it = (row["where_to_find_it"] or "").strip()
        if_missing_gap = (row["if_missing_gap"] or "").strip()
        decided_by = (row["decided_by"] or "").strip()
        date = (row["date"] or "").strip()
        verified = (row["verified"] or "").strip().lower()

        if not rule_id:
            problems.append(f"{prefix}: blank rule_id")
        if rule_id in seen_rule_ids:
            problems.append(f"{prefix}: duplicate rule_id {rule_id!r}")
        seen_rule_ids.add(rule_id)
        if not pattern_id:
            problems.append(f"{rule_id or prefix}: blank pattern_id")
        if not source_qid:
            problems.append(f"{rule_id or prefix}: blank source_qid")
        elif source_qid in seen_qids:
            problems.append(
                f"{rule_id or prefix}: duplicate source_qid {source_qid!r} "
                "(one question is answered by exactly one authorised rule)")
        seen_qids.add(source_qid)
        if not question:
            problems.append(f"{rule_id or prefix}: blank question — copy the exact "
                            "question text from the client form")
        if answer_type not in ANSWER_TYPES_OK:
            problems.append(
                f"{rule_id or prefix}: answer_type {answer_type!r} not in "
                f"{sorted(ANSWER_TYPES_OK)}")
        if _rule_is_vague(evidence_needed):
            problems.append(
                f"{rule_id or prefix}: vague evidence_needed {evidence_needed!r} — "
                "name the exact file and the exact columns that hold the evidence")
        if not where_to_find_it:
            problems.append(f"{rule_id or prefix}: blank where_to_find_it")
        if not if_missing_gap:
            problems.append(f"{rule_id or prefix}: blank if_missing_gap — write the "
                            "gap sentence shown when the evidence is missing")
        if not decided_by:
            problems.append(f"{rule_id or prefix}: blank decided_by — a rule needs a "
                            "named human signer")
        elif decided_by == OWNER_PENDING and not allow_unverified:
            problems.append(
                f"{rule_id or prefix}: decided_by is OWNER_PENDING — sign the rule "
                "with your own name and date, or rerun with --allow-unverified "
                "(the pack will be stamped UNVERIFIED RULES)")
        if not ISO_DATE_RE.match(date):
            problems.append(
                f"{rule_id or prefix}: date {date!r} must be an ISO date (YYYY-MM-DD)")
        if verified not in VERIFIED_OK:
            problems.append(f"{rule_id or prefix}: verified {verified!r} not in "
                            f"{sorted(VERIFIED_OK)}")

        rules.append(MappingRule(
            rule_id=rule_id, pattern_id=pattern_id, source_qid=source_qid,
            question=question, answer_type=answer_type,
            evidence_needed=evidence_needed, where_to_find_it=where_to_find_it,
            if_missing_gap=if_missing_gap, decided_by=decided_by, date=date,
            verified=verified,
        ))

    if problems:
        details = "\n".join(f"  - {p}" for p in problems[:10])
        more = "" if len(problems) <= 10 else f"\n  ... and {len(problems) - 10} more"
        raise MappingError(
            f"{len(problems)} problem(s) in the mapping table:\n{details}{more}\n"
            "Fix the table (docs/MAPPING-TABLE-GUIDE.md) and rebuild; "
            "Signoff never silently produces a partial pack.")
    return rules


def template_row_count_hint(template_csv: Path) -> int:
    """Number of example rows in the OWNER template (for the guide)."""
    import csv as _csv
    lines = [ln for ln in template_csv.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]
    return max(0, len(lines) - 1)
