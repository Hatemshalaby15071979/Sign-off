"""Questionnaire TXT / Markdown parser — one question per non-empty line."""
from __future__ import annotations

import re
from pathlib import Path

from signoff.errors import ParseError
from signoff.model.question import Question

# Inline id forms we accept: "A7", "Q12", "Q-12", "3.", "5)", "Ref 12:",
# followed by the question text. Anything else is assigned a derived id.
INLINE = re.compile(
    r"^\s*(?P<qid>(?:[A-Za-z]{1,6}[-_.]?)?\d{1,4})\s*(?P<sep>[).\]:-])\s+(?P<text>\S.*)$"
)
HEADING = re.compile(r"^\s*#+\s*(?P<text>\S.*)$")


def parse_txt_questionnaire(path: Path, relative_to: Path | None = None) -> list[Question]:
    rel = str(path.relative_to(relative_to)) if relative_to else path.name
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ParseError(f"cannot read questionnaire {rel}: {exc}") from exc
    if "\x00" in text[:1024]:
        raise ParseError(f"{rel}: binary content is not a TXT questionnaire")

    questions: list[Question] = []
    seen_qids: set[str] = set()
    for raw_line in text.splitlines():
        m = HEADING.match(raw_line)
        if m:
            # Markdown heading: recorded as a question line only if it
            # follows the one-question-per-line shape (len>?). Headings are
            # skipped: they are structure, not questions.
            continue
        line = raw_line.strip()
        if not line:
            continue
        inline = INLINE.match(line)
        if inline:
            qid = inline.group("qid").upper().replace(" ", "")
            exact = inline.group("text").strip()
            qid_source = "inline"
        else:
            qid = f"TXT-P{len(questions) + 1:03d}"
            exact = line
            qid_source = "derived"
        if not exact:
            raise ParseError(f"{rel}: question text missing for {qid!r}")
        if qid in seen_qids:
            raise ParseError(f"{rel}: duplicate qid {qid!r}")
        seen_qids.add(qid)
        questions.append(Question(
            qid=qid, exact_text=exact, answer_type="unknown",
            source_path=rel, order=len(questions), qid_source=qid_source,
        ))
    if not questions:
        raise ParseError(f"{rel}: questionnaire has no questions")
    return questions
