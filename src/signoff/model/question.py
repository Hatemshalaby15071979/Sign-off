"""Question — one item parsed out of the client questionnaire.

Extraction only: qid, exact question text, answer type. A parser never
interprets, summarises, scores or answers a question.
"""
from __future__ import annotations

from dataclasses import dataclass

ANSWER_TYPES = ("yes_no", "free_text", "attachment", "unknown")


@dataclass(frozen=True)
class Question:
    qid: str                 # from the document, or deterministic derived id
    exact_text: str          # NEVER altered by Signoff
    answer_type: str         # one of ANSWER_TYPES
    source_path: str         # relative path of the questionnaire file
    order: int               # stable original ordering, 0-based
    qid_source: str          # "column" | "inline" | "derived"

    def to_dict(self) -> dict:
        return {
            "qid": self.qid,
            "exact_text": self.exact_text,
            "answer_type": self.answer_type,
            "source_path": self.source_path,
            "order": self.order,
            "qid_source": self.qid_source,
        }
