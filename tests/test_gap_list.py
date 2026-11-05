"""Gap list: every sub-100% coverage and UNMAPPED question becomes a gap row."""
from __future__ import annotations

from tests.conftest import FIXTURES

from signoff.engine import builder as builder_mod
from signoff.engine.gap_list import gap_header, build_gaps
from signoff.ingest.csv_normaliser import detect_kind
from signoff.mapping.loader import load_mapping


def demo_gaps_and_unmapped():
    pack = None
    from tests.conftest import AS_OF
    questions, _ = builder_mod.parse_questionnaire_auto(
        FIXTURES / "questionnaire.demo.csv")
    rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
    events, files = builder_mod.load_events(
        FIXTURES, file_paths=None or [
            FIXTURES / n for n in (
                "qa_review_export.csv", "approval_events.csv",
                "escalation_log.csv", "audit_events.csv",
                "rolespec_export.csv", "ai_inventory.csv",
                "training_register.csv", "incident_register.csv")])
    coverage = builder_mod.compute_coverage(
        builder_mod.group_by_pattern(rules), events, AS_OF)
    coverage_by_qid = {c.source_qid: c for c in coverage}
    builder_mod.attach_evidence_ids(coverage, events, AS_OF)
    builder_mod.chain_events(events, AS_OF)   # derive event ids before gaps
    answers, unmapped = builder_mod.build_answers(
        questions, {r.source_qid: r for r in rules}, coverage_by_qid, AS_OF, False)
    return build_gaps(coverage, events, unmapped, "questionnaire.demo.csv"), answers


def test_gap_header_matches_contract():
    assert gap_header() == ["rule_id", "source_qid", "reason",
                            "affected_source_files", "affected_row_count",
                            "suggested_remediation"]


def test_sub_100_becomes_gap_naming_file_and_denominator():
    gaps, _ = demo_gaps_and_unmapped()
    qa = next(g for g in gaps if g.rule_id == "R-001")
    assert qa.reason.startswith("QA-HUMAN-REVIEW: coverage 4/6")
    assert qa.affected_source_files == ["qa_review_export.csv"]
    assert qa.affected_row_count == 2
    assert qa.suggested_remediation


def test_100percent_patterns_never_produce_gaps():
    gaps, _ = demo_gaps_and_unmapped()
    assert all(g.rule_id != "R-002" for g in gaps)      # kill switch 100%
    assert all(g.rule_id != "R-006" for g in gaps)      # contract term 100%
    assert all(g.rule_id != "R-011" for g in gaps)      # oversight metrics 100%


def test_unmapped_questions_gap_no_answer_may_be_generated():
    gaps, answers = demo_gaps_and_unmapped()
    by_qid = {a.qid: a for a in answers}
    assert by_qid["Q-117"].answer == "UNMAPPED"
    assert by_qid["Q-118"].answer == "UNMAPPED"
    assert by_qid["Q-117"].trust_label == "UNMAPPED"
    unmapped_gaps = [g for g in gaps if g.rule_id == "-"]
    assert {g.source_qid for g in unmapped_gaps} == {"Q-117", "Q-118"}
    assert all("no signed rule" in g.reason for g in unmapped_gaps)
    assert all(g.affected_source_files == ["questionnaire.demo.csv"]
               for g in unmapped_gaps)


def test_previous_pattern_kinds_map_to_real_files():
    from signoff.engine.gap_list import KIND_FOR_PATTERN

    for pattern, kind in KIND_FOR_PATTERN.items():
        assert detect_kind(kind + "_export.csv") == kind or kind in (
            "ai_inventory",), pattern


def test_signoff_never_guessed_any_answer_text():
    # Every mapped answer must quote its signed rule, never invent prose.
    _, answers = demo_gaps_and_unmapped()
    for a in answers:
        if a.trust_label != "UNMAPPED":
            assert a.mapped_rule_id and a.pattern_id and a.evidence_id
            # the rule id itself (a signed table reference) is quoted in the text
            assert a.mapped_rule_id in a.answer
            assert a.evidence_id in a.answer
