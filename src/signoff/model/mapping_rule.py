"""MappingRule — one signed row of the operator's mapping table.

The mapping table is the authoritative, human-signed record of what counts
as evidence for a questionnaire question. Signoff only matches a question's
source_qid to a row here; it never guesses.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass

from signoff.errors import MappingError
from signoff.util.csv_safe import csv_safe

HEADER = (
    "rule_id,pattern_id,source_qid,question,answer_type,evidence_needed,"
    "where_to_find_it,if_missing_gap,decided_by,date,verified"
)
COLUMNS = [
    "rule_id", "pattern_id", "source_qid", "question", "answer_type",
    "evidence_needed", "where_to_find_it", "if_missing_gap", "decided_by",
    "date", "verified",
]


@dataclass(frozen=True)
class MappingRule:
    rule_id: str
    pattern_id: str
    source_qid: str
    question: str
    answer_type: str
    evidence_needed: str
    where_to_find_it: str
    if_missing_gap: str
    decided_by: str
    date: str
    verified: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "pattern_id": self.pattern_id,
            "source_qid": self.source_qid,
            "question": self.question,
            "answer_type": self.answer_type,
            "evidence_needed": self.evidence_needed,
            "where_to_find_it": self.where_to_find_it,
            "if_missing_gap": self.if_missing_gap,
            "decided_by": self.decided_by,
            "date": self.date,
            "verified": self.verified,
        }


def rules_to_csv(rules: list[MappingRule]) -> str:
    """Render rules back to the exact contract CSV (stable column order)."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    for rule in rules:
        writer.writerow({key: csv_safe(value)
                         for key, value in rule.to_dict().items()})
    return buf.getvalue()
