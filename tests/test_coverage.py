"""Coverage engine: explicit denominators, window bounds, never a fake 100%."""
from __future__ import annotations

import pytest

from tests.conftest import AS_OF, FIXTURES

from signoff.engine import builder as builder_mod
from signoff.engine.classifier import classify
from signoff.engine.coverage import EVIDENCE_SPECS, compute_coverage
from signoff.errors import ConfigError
from signoff.ingest.csv_normaliser import normalise_csv
from signoff.mapping.loader import load_mapping
from signoff.mapping.patterns import group_by_pattern


def demo_coverage():
    rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
    events, _files = builder_mod.load_events(
        FIXTURES,
        file_paths=[FIXTURES / n for n in (
            "qa_review_export.csv", "approval_events.csv", "escalation_log.csv",
            "audit_events.csv", "rolespec_export.csv", "ai_inventory.csv",
            "training_register.csv", "incident_register.csv")])
    by_pattern = group_by_pattern(rules)
    return compute_coverage(by_pattern, events, AS_OF)


def pct_by_rule():
    return {c.rule_id: (c.matched, c.expected, c.pct) for c in demo_coverage()}


def test_every_pattern_in_the_mapping_has_a_spec():
    rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
    for pattern in group_by_pattern(rules):
        assert pattern in EVIDENCE_SPECS


def test_unknown_pattern_fails_closed():
    with pytest.raises(ConfigError, match="no evidence spec"):
        compute_coverage({"NOT-A-PATTERN": [("r", "x", "Q-0")]}, [], AS_OF)


def test_fixture_scores_are_exact():
    scores = pct_by_rule()
    assert scores["R-001"] == (4, 6, 66.7)      # QA-HUMAN-REVIEW
    assert scores["R-002"] == (1, 1, 100.0)     # KILL-SWITCH-REVOKE
    assert scores["R-003"] == (0, 1, 0.0)       # AGENT-IDENTITY-LOG
    assert scores["R-004"] == (0, 1, 0.0)       # LEAST-PRIV-QUARTERLY
    assert scores["R-005"] == (1, 1, 100.0)     # AI-INVENTORY-PROVIDERS
    assert scores["R-006"] == (1, 1, 100.0)     # CONTRACT-NO-TRAINING-DOC
    assert scores["R-007"] == (2, 3, 66.7)      # ESCALATION-AUTH-SUPERVISOR
    assert scores["R-008"] == (2, 3, 66.7)
    assert scores["R-009"] == (1, 1, 100.0)     # ACCOUNTABILITY-STATEMENT
    assert scores["R-011"] == (1, 1, 100.0)     # OVERSIGHT-METRICS pre-pass
    assert scores["R-012"] == (2, 3, 66.7)      # TRAINING-RECORDS
    assert scores["R-013"] == (2, 3, 66.7)
    assert scores["R-014"] == (1, 2, 50.0)      # INCIDENT-SLA
    assert scores["R-015"] == (1, 1, 100.0)     # RETENTION/PII via pii_log_check
    assert scores["R-016"] == (1, 1, 100.0)


def test_zero_denominator_is_na_not_100():
    # audit_events only (no qa/training/escalation/incident rows in window)
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "audit_events.csv"
        data.write_text("ts,actor,event_type\n2026-10-01,Admin_1,monitoring_event\n",
                        encoding="utf-8")
        rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
        events = classify(normalise_csv(data))
        coverage = compute_coverage(group_by_pattern(rules), events, AS_OF)
        pcts = {c.rule_id: c.pct for c in coverage}
        assert pcts["R-002"] == 0.0                 # kill switch absent => No
        # "rows"-kind patterns have an EMPTY denominator here: never 100%,
        # reported as None and rendered "N/A (no events in period)"
        assert pcts["R-001"] is None                # QA premise rows = 0
        assert pcts["R-012"] is None                # training premise rows = 0
        assert pcts["R-014"] is None                # incident premise rows = 0
        assert all(p != 100.0 for p in pcts.values())


def test_events_outside_coverage_window_excluded():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "audit_events.csv"
        # one kill switch INSIDE the 90-day window, one OUTSIDE (>90d before AS_OF)
        data.write_text(
            "ts,actor,event_type\n"
            "2026-10-01,Admin_1,kill_switch\n"
            "2026-07-01,Admin_1,kill_switch\n",
            encoding="utf-8")
        rules, _ = load_mapping(FIXTURES / "mapping-table.demo.csv")
        events = classify(normalise_csv(data))
        coverage = compute_coverage(group_by_pattern(rules), events, AS_OF)
        r2 = next(c for c in coverage if c.rule_id == "R-002")
        assert (r2.matched, r2.expected, r2.pct) == (1, 1, 100.0)

        late = "2026-09-01"           # inside window boundary check
        data.write_text(
            "ts,actor,event_type\n" + f"{late},Admin_1,kill_switch\n",
            encoding="utf-8")
        events = classify(normalise_csv(data))
        coverage = compute_coverage(group_by_pattern(rules), events, AS_OF)
        r2 = next(c for c in coverage if c.rule_id == "R-002")
        assert (r2.matched, r2.expected, r2.pct) == (1, 1, 100.0)


def test_window_bounds_are_as_of_minus_90_days_inclusive():
    from signoff.engine.builder import window_bounds
    from signoff.util.clock import parse_instant

    start, end = window_bounds(AS_OF)
    import datetime
    assert end == parse_instant(AS_OF)
    assert start == end - datetime.timedelta(days=90)
