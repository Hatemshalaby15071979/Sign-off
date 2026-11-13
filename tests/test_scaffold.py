"""Scaffold + governance invariants: required tree, owner boundary, offline scan.

Runs the repo's own checkers as subprocesses — the tests must not restate
their logic; they assert the same exit codes an operator sees.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.conftest import REPO

OWNER_MARKER = "<<<OWNER — DO NOT AUTO-FILL — HUMAN DECISION REQUIRED>>>"


def run_script(script: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script)], cwd=str(REPO),
                          capture_output=True, text=True)


def test_check_scaffold_all_phases_exit_zero():
    result = run_script(REPO / "scripts" / "check-scaffold.py")
    assert result.returncode == 0, result.stdout + result.stderr


def test_check_offline_scan_exit_zero():
    result = run_script(REPO / "scripts" / "check-offline.py")
    assert result.returncode == 0, result.stdout + result.stderr


def test_owner_mapping_table_rows_are_authorised():
    """Authorised rows must carry a named owner, a date, and verified=yes."""
    import csv
    path = REPO / "OWNER" / "mapping-table.csv"
    rows = [r for r in csv.DictReader(path.read_text(encoding="utf-8").splitlines()) if any((v or "").strip() for v in r.values())]
    assert rows, "OWNER/mapping-table.csv has no authorised rows — owner decisions pending"
    for r in rows:
        assert r["decided_by"].strip() and r["decided_by"].strip() != "OWNER_PENDING", f"unauthorised row {r['rule_id']}"
        assert r["date"].strip(), f"dateless row {r['rule_id']}"
        assert r["verified"].strip() == "yes", f"unverified row {r['rule_id']}"


def test_owner_files_begin_with_marker():
    for name in ("oversight-statement.md", "offer-and-pricing.md",
                 "company-and-tax.md", "legal-review.md",
                 "mapping-table.template.csv"):
        path = REPO / "OWNER" / name
        first = path.read_text(encoding="utf-8").splitlines()[0]
        assert first == OWNER_MARKER, f"{name} lost its owner marker"


def test_no_placeholder_tokens_in_sources():
    bad_tokens = ("TODO", "FIXME", "XXX", "HACK")
    exempt = {"check-scaffold.py", "check-offline.py"}   # they carry the lists
    hits: list[str] = []
    for root in ("src", "scripts"):
        for path in (REPO / root).rglob("*.py"):
            if path.name in exempt:
                continue
            text = path.read_text(encoding="utf-8")
            for token in bad_tokens:
                if token in text:
                    hits.append(f"{path}: {token}")
    assert hits == [], "placeholder tokens must never ship recursively"


def test_ci_workflow_contains_network_none_demo():
    workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "--network none" in workflow


def test_output_files_contract_is_stable():
    from signoff import config as cfg

    assert set(cfg.OUTPUT_FILES) == {
        "dossier_html", "dossier_pdf", "pack_json", "answers_csv",
        "gaps_csv", "events_csv", "statement_txt",
    }


def test_coverage_window_is_90_days():
    from signoff import config as cfg

    assert cfg.COVERAGE_WINDOW_DAYS == 90


def test_readme_states_offline_guarantee_up_front():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    head = "\n".join(readme.splitlines()[:20]).lower()
    assert "offline" in head
