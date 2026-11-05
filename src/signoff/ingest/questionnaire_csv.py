"""Questionnaire CSV parser — extraction only."""
from __future__ import annotations

import csv
from pathlib import Path

from signoff.errors import ParseError
from signoff.model.question import Question, ANSWER_TYPES

QID_HEADERS = ["ref", "qid", "id", "question id", "question_id", "ref no", "question ref"]
QUESTION_HEADERS = ["question", "question text", "questiontext",
                    "question_text", "exact question", "exact question text"]
YESNO_HEADERS = ["yes", "partly", "no"]


def _pick(header: list[str], candidates: list[str]) -> str | None:
    norm = {h.strip().lower(): h for h in header}
    for cand in candidates:
        if cand in norm:
            return norm[cand]
    return None


def parse_csv_questionnaire(path: Path, relative_to: Path | None = None) -> list[Question]:
    rel = str(path.relative_to(relative_to)) if relative_to else path.name
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ParseError(f"cannot read questionnaire {rel}: {exc}") from exc
    if "\x00" in text[:1024]:
        raise ParseError(f"{rel}: binary content is not a CSV questionnaire")

    reader = csv.reader(text.splitlines())
    try:
        rows = [r for r in reader]
    except csv.Error as exc:
        raise ParseError(f"{rel}: malformed CSV ({exc})") from exc
    if not rows:
        raise ParseError(f"{rel}: questionnaire CSV is empty")
    header = rows[0]
    qid_col = _pick(header, QID_HEADERS)
    question_col = _pick(header, QUESTION_HEADERS)
    if qid_col is None:
        raise ParseError(f"{rel}: no question-id column found "
                         f"(expected one of {QID_HEADERS})")
    if question_col is None:
        raise ParseError(f"{rel}: no question column found "
                         f"(expected one of {QUESTION_HEADERS})")
    qid_idx, q_idx = header.index(qid_col), header.index(question_col)
    # Yes/Partly/No columns may exist; they define the answer_type ONLY.
    has_yesno = any(_pick(header, [h]) is not None for h in ["yes"]) and \
        any(_pick(header, [h]) is not None for h in ["partly"]) and \
        any(_pick(header, [h]) is not None for h in ["no"])

    questions: list[Question] = []
    seen_qids: set[str] = set()
    for order, row in enumerate(rows[1:]):
        if not any(cell.strip() for cell in row):
            continue  # blank separator line
        if len(row) <= max(qid_idx, q_idx):
            raise ParseError(
                f"{rel} row {order + 2}: shorter than the header row (" +
                "; ".join(row) + ")")
        qid = row[qid_idx].strip()
        exact = row[q_idx].strip()
        if not qid:
            raise ParseError(f"{rel} row {order + 2}: blank qid")
        if not exact:
            raise ParseError(f"{rel} row {order + 2}: blank question text")
        if qid in seen_qids:
            raise ParseError(f"{rel} row {order + 2}: duplicate qid {qid!r}")
        seen_qids.add(qid)
        answer_type = ANSWER_TYPES[0] if has_yesno else ANSWER_TYPES[3]
        questions.append(Question(
            qid=qid, exact_text=exact, answer_type=answer_type,
            source_path=rel, order=len(questions), qid_source="column",
        ))
    if not questions:
        raise ParseError(f"{rel}: questionnaire CSV has a header but no questions")
    return questions
