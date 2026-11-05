"""Questionnaire parsers: extraction only, no interpretation, fail closed."""
from __future__ import annotations

import pytest

from tests.conftest import FIXTURES

from signoff.engine.builder import parse_questionnaire_auto
from signoff.errors import ParseError
from signoff.ingest.questionnaire_csv import parse_csv_questionnaire
from signoff.ingest.questionnaire_docx import parse_docx_questionnaire
from signoff.ingest.questionnaire_txt import parse_txt_questionnaire


def test_csv_fixture_parses_18_questions():
    questions = parse_csv_questionnaire(FIXTURES / "questionnaire.demo.csv")
    assert len(questions) == 18
    assert [q.qid for q in questions][:3] == ["Q-101", "Q-102", "Q-103"]
    # exact text is NEVER altered
    assert questions[0].exact_text == (
        "Are AI-proposed QA actions reviewed by a named human before acceptance?")
    assert questions[0].answer_type == "yes_no"
    assert [q.order for q in questions] == list(range(18))


def test_txt_fixture_parses_inline_and_derived_qids():
    questions = parse_txt_questionnaire(FIXTURES / "questionnaire.demo.txt")
    assert questions
    inline = [q for q in questions if q.qid_source == "inline"]
    derived = [q for q in questions if q.qid_source == "derived"]
    assert inline and derived
    assert all(q.answer_type == "unknown" for q in questions)
    assert [q.order for q in questions] == list(range(len(questions)))


def test_docx_fixture_parses():  # regression: the shipped demo docx must parse
    questions = parse_docx_questionnaire(FIXTURES / "questionnaire.demo.docx")
    assert questions
    assert {q.qid_source for q in questions} <= {"inline", "derived"}


def test_csv_missing_qid_column_rejected(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_text("Question\nHow do you do this?\n", encoding="utf-8")
    with pytest.raises(ParseError, match="no question-id column"):
        parse_csv_questionnaire(path)


def test_csv_missing_question_column_rejected(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_text("Ref\nA1\n", encoding="utf-8")
    with pytest.raises(ParseError, match="no question column"):
        parse_csv_questionnaire(path)


def test_csv_blank_question_text_rejected(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_text("Ref,Question\nA1,\n", encoding="utf-8")
    with pytest.raises(ParseError, match="blank question text"):
        parse_csv_questionnaire(path)


def test_csv_duplicate_qid_rejected(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_text("Ref,Question\nA1,One?\nA1,Two?\n", encoding="utf-8")
    with pytest.raises(ParseError, match="duplicate qid"):
        parse_csv_questionnaire(path)


def test_csv_binary_content_rejected(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_bytes(b"Ref,Question\nA1,\x00bad\x00\n")
    with pytest.raises(ParseError, match="binary content"):
        parse_csv_questionnaire(path)


def test_txt_empty_rejected(tmp_path):
    path = tmp_path / "qq.txt"
    path.write_text("\n\n", encoding="utf-8")
    with pytest.raises(ParseError, match="no questions"):
        parse_txt_questionnaire(path)


def test_docx_zip_bomb_rejected(tmp_path):
    import zipfile

    path = tmp_path / "qq.docx"
    with zipfile.ZipFile(path, "w") as zf:
        for i in range(600):
            zf.writestr(f"member_{i}", "x" * 10)
    with pytest.raises(ParseError, match="member"):
        parse_docx_questionnaire(path)


def test_docx_without_document_xml_rejected(tmp_path):
    import zipfile

    path = tmp_path / "qq.docx"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/other.xml", "<x/>")
    with pytest.raises(ParseError, match="not a Word document"):
        parse_docx_questionnaire(path)


def test_unsupported_extension_rejected(tmp_path):
    path = tmp_path / "qq.pdf"
    path.write_bytes(b"%PDF-1.4")
    with pytest.raises(ParseError, match="unsupported questionnaire extension"):
        parse_questionnaire_auto(path)
