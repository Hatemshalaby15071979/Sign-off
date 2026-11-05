"""Questionnaire DOCX parser — stdlib zipfile + xml.etree.ElementTree ONLY.

No python-docx dependency. Safety limits protect against hostile DOCX files
(zip bombs, nested-path probes): a total decompressed-size cap, a member
count cap, and the mandatory `word/document.xml` member.
"""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from signoff.errors import ParseError
from signoff.model.question import Question

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DOCUMENT_MEMBER = "word/document.xml"
MAX_DECOMPRESSED = 32 * 1024 * 1024   # 32 MiB total decompressed XML
MAX_MEMBERS = 512
MAX_PARAGRAPHS = 50_000

INLINE = re.compile(
    r"^\s*(?P<qid>(?:[A-Za-z]{1,6}[-_.]?)?\d{1,4})\s*(?P<sep>[).\]:-])\s+(?P<text>\S.*)$"
)


def _read_document_xml(raw: zipfile.ZipFile, rel: str) -> str:
    info = raw.getinfo(DOCUMENT_MEMBER)
    if info.file_size > MAX_DECOMPRESSED:
        raise ParseError(
            f"{rel}: {DOCUMENT_MEMBER} decompresses to {info.file_size} bytes, "
            f"exceeding the {MAX_DECOMPRESSED}-byte safety cap")
    return raw.read(DOCUMENT_MEMBER).decode("utf-8")


def parse_docx_questionnaire(path: Path, relative_to: Path | None = None) -> list[Question]:
    rel = str(path.relative_to(relative_to)) if relative_to else path.name
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if len(names) > MAX_MEMBERS:
                raise ParseError(
                    f"{rel}: {len(names)} zip members exceeds the {MAX_MEMBERS}-member safety cap")
            if DOCUMENT_MEMBER not in names:
                raise ParseError(f"{rel}: not a Word document (no {DOCUMENT_MEMBER})")
            xml_text = _read_document_xml(zf, rel)
    except zipfile.BadZipFile as exc:
        raise ParseError(f"{rel}: unreadable DOCX ({exc})") from exc
    except ParseError:
        raise
    except OSError as exc:
        raise ParseError(f"{rel}: cannot read DOCX ({exc})") from exc

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise ParseError(f"{rel}: malformed document XML ({exc})") from exc

    paragraphs: list[str] = []
    for para in root.iter(f"{W_NS}p"):
        if len(paragraphs) >= MAX_PARAGRAPHS:
            raise ParseError(f"{rel}: more than {MAX_PARAGRAPHS} paragraphs")
        runs = [t.text or "" for t in para.iter(f"{W_NS}t")]
        joined = "".join(runs).strip()
        if joined:
            paragraphs.append(joined)

    questions: list[Question] = []
    seen_qids: set[str] = set()
    for para in paragraphs:
        inline = INLINE.match(para)
        if inline:
            qid = inline.group("qid").upper()
            exact = inline.group("text").strip()
            qid_source = "inline"
        else:
            qid = f"DOCX-P{len(questions) + 1:03d}"
            exact = para
            qid_source = "derived"
        if qid in seen_qids:
            raise ParseError(f"{rel}: duplicate qid {qid!r}")
        seen_qids.add(qid)
        questions.append(Question(
            qid=qid, exact_text=exact, answer_type="unknown",
            source_path=rel, order=len(questions), qid_source=qid_source,
        ))
    if not questions:
        raise ParseError(f"{rel}: document has no non-empty paragraphs")
    return questions
