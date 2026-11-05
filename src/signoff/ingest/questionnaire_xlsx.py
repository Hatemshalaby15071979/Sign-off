"""Questionnaire XLSX parser — optional `signoff[xlsx]` extra (openpyxl).

If openpyxl is missing the parser fails with a clear message telling the
operator to install the extra; it never silently skips a format.
"""
from __future__ import annotations

from pathlib import Path

from signoff.errors import ParseError
from signoff.model.question import Question, ANSWER_TYPES

from signoff.ingest.questionnaire_csv import QID_HEADERS, QUESTION_HEADERS

MAX_ROWS = 50_000


def parse_xlsx_questionnaire(path: Path, relative_to: Path | None = None) -> list[Question]:
    rel = str(path.relative_to(relative_to)) if relative_to else path.name
    try:
        import openpyxl  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - exercised when extra missing
        raise ParseError(
            f"{rel}: parsing .xlsx questionnaires requires the optional "
            "'xlsx' extra — install with: pip install \"signoff[xlsx]\"") from exc

    try:
        # read_only: streams rows; data_only: values, not formulas
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001 - openpyxl raises many types
        raise ParseError(f"{rel}: unopenable XLSX ({exc})") from exc

    try:
        sheet = workbook[workbook.sheetnames[0]]
        rows: list[list[object]] = []
        for row in sheet.iter_rows(values_only=True):
            rows.append(list(row))
            if len(rows) > MAX_ROWS:
                raise ParseError(f"{rel}: more than {MAX_ROWS} sheet rows")
    except ParseError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ParseError(f"{rel}: cannot read worksheet ({exc})") from exc
    finally:
        workbook.close()

    if not rows:
        raise ParseError(f"{rel}: worksheet is empty")
    header_norm = {str(c).strip().lower(): i for i, c in enumerate(rows[0])
                   if c is not None and str(c).strip()}
    qid_idx = next((header_norm[h] for h in QID_HEADERS if h in header_norm), None)
    q_idx = next((header_norm[h] for h in QUESTION_HEADERS if h in header_norm), None)
    if qid_idx is None or q_idx is None:
        raise ParseError(
            f"{rel}: first sheet needs a qid column ({QID_HEADERS}) and a "
            f"question column ({QUESTION_HEADERS}); none found in the header row")
    has_yesno = all(h in header_norm for h in ("yes", "partly", "no"))

    questions: list[Question] = []
    seen_qids: set[str] = set()
    for order, row in enumerate(rows[1:]):
        qid = row[qid_idx] if len(row) > qid_idx else None
        exact = row[q_idx] if len(row) > q_idx else None
        qid_s = str(qid).strip() if qid is not None else ""
        exact_s = str(exact).strip() if exact is not None else ""
        if not any(str(c).strip() for c in row if c is not None):
            continue
        if not qid_s:
            raise ParseError(f"{rel} row {order + 2}: blank qid")
        if not exact_s:
            raise ParseError(f"{rel} row {order + 2}: blank question text")
        if qid_s in seen_qids:
            raise ParseError(f"{rel} row {order + 2}: duplicate qid {qid_s!r}")
        seen_qids.add(qid_s)
        questions.append(Question(
            qid=qid_s, exact_text=exact_s,
            answer_type=ANSWER_TYPES[0] if has_yesno else ANSWER_TYPES[3],
            source_path=rel, order=len(questions), qid_source="column",
        ))
    if not questions:
        raise ParseError(f"{rel}: worksheet has a header but no questions")
    return questions
