"""Never-guesses: unmapped/unverifiable questions are answered UNMAPPED, always.

There is no code path that invents an answer for a question with no signed
rule, and no code path that hides an unmapped question from the pack.
"""
from __future__ import annotations

import pytest

from tests.conftest import AS_OF, DEMO_DATA_FILES, FIXTURES

from signoff.config import UNMAPPED
from signoff.engine import builder as builder_mod
from signoff.errors import ParseError
from signoff.mapping.loader import load_mapping


def build_with_questionnaire(tmp_path, csv_text: str, name="qq.csv"):
    path = tmp_path / name
    path.write_text(csv_text, encoding="utf-8")
    # the demo mapping table never covers these qids -> every answer UNMAPPED
    return builder_mod.build_pack(
        questionnaire_path=path,
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=False)


CSV = "Ref,Question\nZZ-901,Do you have an AI policy document?\nZZ-902,Pricing?\n"


def test_no_signed_rule_means_LITERAL_unmapped(tmp_path):
    pack = build_with_questionnaire(tmp_path, CSV)
    for answer in pack.questions:
        assert answer.answer == UNMAPPED, answer.qid
        assert answer.trust_label == "UNMAPPED"
        assert answer.mapped_rule_id is None
        assert answer.pattern_id is None
        assert answer.evidence_id is None
    assert pack.unmapped_qids == ["ZZ-901", "ZZ-902"]


def test_unmapped_never_scores_coverage(tmp_path):
    pack = build_with_questionnaire(tmp_path, CSV)
    by_qid = {a.qid: a for a in pack.questions}
    assert by_qid["ZZ-901"].coverage_pct == "N/A (no events in period)"


def test_unmapped_show_in_the_gap_list(tmp_path):
    from signoff import cli

    pack = build_with_questionnaire(tmp_path, CSV)
    artifacts = cli._render_artifacts(pack, pack.as_of)
    text = artifacts["gap-list.csv"].decode("utf-8")
    assert "UNMAPPED: no signed rule maps question 'ZZ-901'" in text
    assert text.count("UNMAPPED: no signed rule") == 2


def test_blank_qid_is_a_parse_error_never_a_guess(tmp_path):
    path = tmp_path / "qq.csv"
    path.write_text("Ref,Question\n,What?\n", encoding="utf-8")
    with pytest.raises(ParseError, match="blank qid"):
        builder_mod.parse_questionnaire_auto(path)


def test_partial_mapping_only_covers_signed_rules(tmp_path):
    # only ZZ-901 is mapped; ZZ-902 must STILL be UNMAPPED
    rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
    mapped_qids = {r.source_qid for r in rules}
    assert "Q-117" not in mapped_qids and "Q-118" not in mapped_qids
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=False)
    by_qid = {a.qid: a for a in pack.questions}
    assert by_qid["Q-117"].answer == UNMAPPED
    assert by_qid["Q-118"].answer == UNMAPPED
    for qid in ("Q-101", "Q-114"):
        assert by_qid[qid].trust_label == "mapped"


def test_no_free_text_can_float_without_a_rule_id(tmp_path):
    pack = build_with_questionnaire(tmp_path, CSV)
    for a in pack.questions:
        if a.trust_label == "UNMAPPED":
            assert a.answer == UNMAPPED
            assert a.coverage_pct == "N/A (no events in period)"
        else:
            assert "signed rule" in a.answer or "appendix pack" in a.answer
