"""Signoff — configuration.

No environment variables are read. Every tunable is either an explicit CLI
flag or one of the fixed constants below.
"""
from __future__ import annotations

from pathlib import Path
from signoff.util.clock import DEFAULT_AS_OF

SRC_ROOT = Path(__file__).resolve().parent

# Coverage window: the 90 days ending at the --as-of instant (both ends
# included). Documented in docs/DATA-CONTRACT.md.
COVERAGE_WINDOW_DAYS = 90

# Answer labels derived from coverage (deterministic formulas).
ANSWER_YES = "Yes"
ANSWER_PARTLY = "Partly"
ANSWER_NO = "No"

# Literal answer produced when no signed rule matches a question's source_qid.
UNMAPPED = "UNMAPPED"

# Owner-table rejection sentinel.
OWNER_PENDING = "OWNER_PENDING"

OUTPUT_FILES = {
    "dossier_html": "dossier.html",
    "dossier_pdf": "dossier.pdf",
    "pack_json": "pack.json",
    "answers_csv": "questionnaire-answers.csv",
    "gaps_csv": "gap-list.csv",
    "events_csv": "evidence-events.csv",
    "statement_txt": "oversight-statement.txt",
}

# Known runtime dependency versions, echoed into every pack for traceability.
RUNTIME_DEPENDENCIES = {
    "python_standard_library": "3.11+",
    "fpdf2": "2.8.4",
    "openpyxl_optional_extra": "3.1.5 (optional; only for .xlsx questionnaires)",
}

__all__ = [
    "ANSWER_NO", "ANSWER_PARTLY", "ANSWER_YES", "COVERAGE_WINDOW_DAYS",
    "DEFAULT_AS_OF", "OUTPUT_FILES", "OWNER_PENDING", "RUNTIME_DEPENDENCIES",
    "SRC_ROOT", "UNMAPPED",
]
