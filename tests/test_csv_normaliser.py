"""CSV normaliser: hard-coded schemas, fail-closed on every surprise."""
from __future__ import annotations

import pytest

from tests.conftest import FIXTURES

from signoff.errors import ParseError
from signoff.ingest.csv_normaliser import (
    detect_kind, normalise_csv, parse_ts, resolve_columns,
)


def test_detect_kind_registry_complete():
    assert detect_kind("qa_review_export.csv") == "qa_review"
    assert detect_kind("approval_events.csv") == "approval_events"
    assert detect_kind("escalation_log.csv") == "escalation_log"
    assert detect_kind("audit_events.csv") == "audit_events"
    assert detect_kind("rolespec_export.csv") == "rolespec_export"
    assert detect_kind("ai_inventory.csv") == "ai_inventory"
    assert detect_kind("training_register.csv") == "training_register"
    assert detect_kind("incident_register.csv") == "incident_register"
    assert detect_kind("mapping-table.demo.csv") is None
    assert detect_kind("questionnaire.demo.csv") is None


def test_normalise_demo_exports_count_and_traceability():
    rows = []
    for name in ("qa_review_export.csv", "incident_register.csv"):
        rows.extend(normalise_csv(FIXTURES / name, relative_to=FIXTURES))
    qa = [r for r in rows if r.kind == "qa_review"]
    assert len(qa) == 6
    assert all(r.source_file == "qa_review_export.csv" for r in qa)
    # 1-based line numbers, header row included, in file order
    assert [r.source_row for r in qa] == [2, 3, 4, 5, 6, 7]
    assert all(r.ts.startswith("2026-") for r in qa)


def test_missing_required_column_fails_closed(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text("ts,actor\ntoo, few\n", encoding="utf-8")   # event_type missing
    with pytest.raises(ParseError, match="missing required column 'event_type'"):
        normalise_csv(path)


def test_unknown_column_never_silently_dropped(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text(
        "ts,actor,event_type,whoops\n2026-01-01,Admin_1,kill_switch,extra\n",
        encoding="utf-8")
    with pytest.raises(ParseError, match="unknown column"):
        normalise_csv(path)


def test_blank_timestamp_never_invented(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text(
        "ts,actor,event_type\n,Admin_1,kill_switch\n", encoding="utf-8")
    with pytest.raises(ParseError, match="blank timestamp"):
        normalise_csv(path)


def test_unparseable_timestamp_fails_closed(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text(
        "ts,actor,event_type\nnot-a-date,Admin_1,kill_switch\n", encoding="utf-8")
    with pytest.raises(ParseError, match="unparseable timestamp"):
        normalise_csv(path)


def test_blank_separator_rows_are_skipped(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text(
        "ts,actor,event_type\n2026-01-01,Admin_1,kill_switch\n,,,,\n"
        "2026-01-02,Admin_2,access_revoked\n", encoding="utf-8")
    rows = normalise_csv(path)
    assert [r.source_row for r in rows] == [2, 4]


def test_aliases_accept_renamed_headers(tmp_path):
    path = tmp_path / "audit_events.csv"
    path.write_text(
        "timestamp,performed_by,type\n2026-11-01T09:00:00+02:00,Admin_1,kill_switch\n",
        encoding="utf-8")
    rows = normalise_csv(path)
    assert rows[0].canonical["event_type"] == "kill_switch"
    assert rows[0].canonical["actor"] == "Admin_1"


def test_timestamps_normalised_to_utc_iso():
    assert parse_ts("2026-11-05 10:00", "f.csv", 2) == "2026-11-05T10:00:00+00:00"
    assert parse_ts("2026-11-05Z", "f.csv", 2) == "2026-11-05T00:00:00+00:00"
    assert parse_ts("05/11/2026 09:00", "f.csv", 2) == "2026-11-05T09:00:00+00:00"
    assert parse_ts("2026-11-05T12:30:00+02:00", "f.csv", 2) == "2026-11-05T10:30:00+00:00"


def test_resolve_columns_errors_name_the_file():
    with pytest.raises(ParseError, match="audit"):
        resolve_columns(["ts", "actor"], "audit_events", "audit_events.csv")
