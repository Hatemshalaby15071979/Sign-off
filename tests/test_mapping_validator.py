"""Mapping-table validator + loader: every rejection names the offending rule."""
from __future__ import annotations

import pytest

from tests.conftest import VALID_RULE_ROW, rule_csv

from signoff.errors import MappingError
from signoff.mapping.loader import load_mapping
from signoff.mapping.patterns import group_by_pattern
from signoff.mapping.validator import validate_rules


def rules_from(*rows: list[str], allow_unverified: bool = False):
    columns = ("rule_id", "pattern_id", "source_qid", "question", "answer_type",
               "evidence_needed", "where_to_find_it", "if_missing_gap",
               "decided_by", "date", "verified")
    return validate_rules([dict(zip(columns, row)) for row in rows],
                          allow_unverified=allow_unverified)


def test_valid_rule_is_accepted():
    rules = rules_from(VALID_RULE_ROW)
    assert len(rules) == 1
    assert rules[0].rule_id == "R-T01"
    assert rules[0].verified == "yes"


def test_duplicate_rule_id_rejected():
    with pytest.raises(MappingError, match="duplicate rule_id 'R-T01'"):
        rules_from(VALID_RULE_ROW, VALID_RULE_ROW)


def test_duplicate_source_qid_rejected():
    second = list(VALID_RULE_ROW)
    second[0] = "R-T02"
    with pytest.raises(MappingError, match="duplicate source_qid 'Q-999'"):
        rules_from(VALID_RULE_ROW, second)


def test_vague_evidence_needed_rejected():
    row = list(VALID_RULE_ROW)
    row[5] = "human oversight exists"
    with pytest.raises(MappingError, match="vague evidence_needed"):
        rules_from(row)


def test_evidence_needed_without_concrete_file_rejected():
    row = list(VALID_RULE_ROW)
    row[5] = "The service desk keeps a record of all reviews in their tooling."
    with pytest.raises(MappingError, match="vague evidence_needed"):
        rules_from(row)


def test_owner_pending_rejected_unless_allowed():
    row = list(VALID_RULE_ROW)
    row[8] = "OWNER_PENDING"
    with pytest.raises(MappingError, match="decided_by is OWNER_PENDING"):
        rules_from(row)
    rules = rules_from(row, allow_unverified=True)
    assert rules[0].decided_by == "OWNER_PENDING"


def test_bad_answer_type_rejected():
    row = list(VALID_RULE_ROW)
    row[4] = "multiple_choice"
    with pytest.raises(MappingError, match="answer_type"):
        rules_from(row)


def test_bad_date_rejected():
    row = list(VALID_RULE_ROW)
    row[9] = "04/11/2026"
    with pytest.raises(MappingError, match="must be an ISO date"):
        rules_from(row)


def test_blank_decided_by_rejected():
    row = list(VALID_RULE_ROW)
    row[8] = ""
    with pytest.raises(MappingError, match="blank decided_by"):
        rules_from(row)


def test_verified_no_is_allowed_but_flags_unverified():
    from pathlib import Path
    import tempfile

    from signoff.mapping.loader import load_mapping

    row = list(VALID_RULE_ROW)
    row[10] = "no"
    rules = rules_from(row)
    assert rules[0].verified == "no"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "mapping-table.csv"
        path.write_text(rule_csv(row), encoding="utf-8")
        rules, unverified = load_mapping(path, allow_unverified=True)
    assert unverified is True
    assert rules[0].verified == "no"


def test_loader_missing_file():
    from pathlib import Path

    with pytest.raises(MappingError, match="mapping table not found"):
        load_mapping(Path("/nonexistent/mapping.csv"))


def test_loader_wrong_header_fails_closed(tmp_path, mapping_file_factory):
    path = mapping_file_factory(rule_csv(header="rule_id,pattern_id\n"))
    with pytest.raises(MappingError, match="!= contract header"):
        load_mapping(path)


def test_loader_empty_table_fails_closed(tmp_path, mapping_file_factory):
    path = mapping_file_factory("")
    with pytest.raises(MappingError, match="empty"):
        load_mapping(path)


def test_loader_demo_table_loads_and_flags_verified_false_is_possible():
    from tests.conftest import FIXTURES

    rules, unverified = load_mapping(FIXTURES / "mapping-table.demo.csv")
    assert len(rules) == 16
    assert unverified is False
    groups = group_by_pattern(rules)
    assert set(groups) == {
        "QA-HUMAN-REVIEW", "KILL-SWITCH-REVOKE", "AGENT-IDENTITY-LOG",
        "LEAST-PRIV-QUARTERLY", "AI-INVENTORY-PROVIDERS",
        "CONTRACT-NO-TRAINING-DOC", "ESCALATION-AUTH-SUPERVISOR",
        "ACCOUNTABILITY-STATEMENT", "OVERSIGHT-METRICS", "TRAINING-RECORDS",
        "INCIDENT-SLA", "RETENTION-PII-LOGGING",
    }
    assert groups["ESCALATION-AUTH-SUPERVISOR"] == [
        r for r in rules if r.pattern_id == "ESCALATION-AUTH-SUPERVISOR"]


def test_loader_is_read_only(tmp_path, mapping_file_factory):
    path = mapping_file_factory(rule_csv(VALID_RULE_ROW))
    before = path.read_bytes()
    load_mapping(path)
    assert path.read_bytes() == before
