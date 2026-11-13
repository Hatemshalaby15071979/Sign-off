"""HI-08: CSV formula-injection defence on every export path."""
from __future__ import annotations

import csv
import io

import pytest

from signoff.model.mapping_rule import MappingRule, rules_to_csv
from signoff.render.csv_renderer import _rows_to_csv
from signoff.util.csv_safe import csv_safe


@pytest.mark.parametrize("prefix", ["=", "+", "-", "@", "\t", "\r"])
def test_each_dangerous_prefix_is_neutralised(prefix: str) -> None:
    assert csv_safe(f"{prefix}SUM(A1)") == f"'{prefix}SUM(A1)"


def test_leading_spaces_do_not_hide_a_formula() -> None:
    assert csv_safe("  =1+1") == "'  =1+1"


@pytest.mark.parametrize("value", ["", "hello", "0", "2026-11-06", "a=b", "x+y", "A@b"])
def test_safe_values_are_unchanged(value: str) -> None:
    assert csv_safe(value) == value


@pytest.mark.parametrize("value", ["-", "-5", "-3.25", "+5"])
def test_signed_numbers_and_sentinel_are_not_escaped(value: str) -> None:
    assert csv_safe(value) == value


def _parse(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text)))


def test_renderer_escapes_every_cell() -> None:
    text = _rows_to_csv(
        ["qid", "answer"],
        [["Q-1", "=HYPERLINK(\"http://evil\")"], ["Q-2", "\tcmd"]],
        simulated=False,
        unverified=False,
    )
    rows = _parse(text)
    assert rows[1] == ["Q-1", "'=HYPERLINK(\"http://evil\")"]
    assert rows[2] == ["Q-2", "'\tcmd"]
    for row in rows:
        for cell in row:
            assert not cell.startswith(("=", "+", "-", "@", "\t", "\r"))


def test_mapping_table_export_escapes_rules() -> None:
    rule = MappingRule(
        rule_id="R-T01", pattern_id="QA-HUMAN-REVIEW", source_qid="Q-1",
        question="@SUM(A1:A9)", answer_type="yes_no", evidence_needed="x",
        where_to_find_it="y", if_missing_gap="z", decided_by="=cmd|' /C calc'!A0",
        date="2026-11-06", verified="yes",
    )
    rows = _parse(rules_to_csv([rule]))
    assert rows[1][3] == "'@SUM(A1:A9)"
    assert rows[1][8] == "'=cmd|' /C calc'!A0"
