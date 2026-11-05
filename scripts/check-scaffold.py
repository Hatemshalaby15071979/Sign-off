#!/usr/bin/env python3
"""Scaffold assertion for the Signoff repository.

Checks, progressively by phase (phase 1 builds the skeleton; later phases add
code), and for the completed tree when run with no argument:

1. Every required path exists and is non-empty (except files explicitly
   allowing an empty body).
2. No forbidden placeholder tokens in src/ or scripts/ (TODO, FIXME, pass,
   NotImplementedError, bare ellipsis markers).
3. Every OWNER-only file begins with the exact ownership marker line.
4. OWNER/mapping-table.csv is header-only (no data rows).
5. Optional-binary-path files that depend on an extra are only demanded when
   present-checkable fixtures exist.

Run: python scripts/check-scaffold.py [--phase N]
Exit 0 = ok, exit 1 = problem (with a printed list).
"""
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The exact marker line that begins every owner-only text file.
OWNER_MARKER = "<<<OWNER — DO NOT AUTO-FILL — HUMAN DECISION REQUIRED>>>"

# Files owned by the human owner: agent must leave them marked/empty.
OWNER_FILES = [
    "OWNER/oversight-statement.md",
    "OWNER/offer-and-pricing.md",
    "OWNER/company-and-tax.md",
    "OWNER/legal-review.md",
    "OWNER/mapping-table.template.csv",
]

# NOTE: scripts/check-scaffold.py is excluded from the token scan because it
# must contain the forbidden-token list itself; that is the one legitimate use.

# Files the agent may legitimately write in full (these EXPLAIN the boundary).
OWNER_DOCS = [
    "OWNER/README.md",
    "OWNER/DECISIONS-TO-MAKE.md",
    "OWNER/real-data/README.md",
]

# Files that may be empty or contain only structured emptiness.
ALLOW_EMPTY = {"OWNER/mapping-table.csv"}

FORBIDDEN_TOKENS = [
    "TODO", "FIXME", "NotImplementedError", "XXX", "HACK", "left as an exercise",
]


def phase_map() -> dict[int, list[str]]:
    """Files that must exist by the given phase (cumulative)."""
    root_cfg = [
        "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md",
        "pyproject.toml", "Makefile", ".gitignore", ".editorconfig",
        ".dockerignore", "Dockerfile", "docker-compose.yml",
    ]
    owner_early = OWNER_FILES + OWNER_DOCS + ["OWNER/real-data/README.md"]
    scripts_all = [
        "scripts/check-scaffold.py", "scripts/check-offline.py",
        "scripts/check-determinism.py", "scripts/run-all-checks.sh",
    ]
    docs_all = [
        "docs/00-IMPLEMENTATION-REPORT.md", "docs/01-DECISION-LOG.md",
        "docs/02-VERIFICATION-LOG.md", "docs/03-HANDOFF-TO-OWNER.md",
        "docs/ARCHITECTURE.md", "docs/DATA-CONTRACT.md",
        "docs/MAPPING-TABLE-GUIDE.md", "docs/QUESTIONNAIRE-PARSING.md",
        "docs/SECURITY.md", "docs/THREAT-MODEL.md",
        "docs/OFFLINE-GUARANTEE.md", "docs/CONTROL-MAPPING.md",
        "docs/HUMAN-OWNER-GUIDE.md", "docs/LIMITATIONS.md", "docs/FAQ.md",
        "REPORT.md", "REPORT.json", "examples/README.md", "examples/demo.sh",
    ]
    src = {
        "core": ["src/signoff/__init__.py", "src/signoff/__main__.py",
                 "src/signoff/cli.py", "src/signoff/config.py", "src/signoff/errors.py"],
        "model": ["src/signoff/model/__init__.py", "src/signoff/model/decision_event.py",
                  "src/signoff/model/question.py", "src/signoff/model/mapping_rule.py",
                  "src/signoff/model/evidence_pack.py"],
        "util": ["src/signoff/util/__init__.py", "src/signoff/util/clock.py",
                 "src/signoff/util/ids.py", "src/signoff/util/redaction.py",
                 "src/signoff/util/sim_flag.py"],
        "ingest": ["src/signoff/ingest/__init__.py", "src/signoff/ingest/questionnaire_csv.py",
                   "src/signoff/ingest/questionnaire_docx.py", "src/signoff/ingest/questionnaire_xlsx.py",
                   "src/signoff/ingest/questionnaire_txt.py", "src/signoff/ingest/csv_normaliser.py"],
        "mapping": ["src/signoff/mapping/__init__.py", "src/signoff/mapping/loader.py",
                    "src/signoff/mapping/patterns.py", "src/signoff/mapping/validator.py"],
        "engine": ["src/signoff/engine/__init__.py", "src/signoff/engine/classifier.py",
                   "src/signoff/engine/hash_chain.py", "src/signoff/engine/coverage.py",
                   "src/signoff/engine/gap_list.py", "src/signoff/engine/builder.py"],
        "render": ["src/signoff/render/__init__.py", "src/signoff/render/html_renderer.py",
                   "src/signoff/render/pdf_renderer.py", "src/signoff/render/json_renderer.py",
                   "src/signoff/render/csv_renderer.py", "src/signoff/render/statement.py",
                   "src/signoff/render/appendix.py", "src/signoff/render/disclosure.py"],
        "verify": ["src/signoff/verify/__init__.py", "src/signoff/verify/verify_pack.py"],
    }
    tests = [
        "tests/conftest.py", "tests/fixtures/mapping-table.demo.csv",
        "tests/fixtures/questionnaire.demo.csv", "tests/fixtures/questionnaire.demo.docx",
        "tests/fixtures/questionnaire.demo.txt", "tests/fixtures/qa_review_export.csv",
        "tests/fixtures/approval_events.csv", "tests/fixtures/audit_events.csv",
        "tests/fixtures/escalation_log.csv", "tests/fixtures/rolespec_export.csv",
        "tests/fixtures/ai_inventory.csv", "tests/fixtures/training_register.csv",
        "tests/fixtures/incident_register.csv",
        "tests/test_scaffold.py", "tests/test_mapping_validator.py",
        "tests/test_questionnaire_parsers.py", "tests/test_csv_normaliser.py",
        "tests/test_classifier.py", "tests/test_hash_chain.py", "tests/test_coverage.py",
        "tests/test_gap_list.py", "tests/test_determinism.py", "tests/test_no_network.py",
        "tests/test_no_llm.py", "tests/test_never_guesses.py",
        "tests/test_simulated_watermark.py", "tests/test_verify_pack.py",
        "tests/test_cli.py", "tests/test_end_to_end.py",
    ]
    return {
        1: root_cfg + ["OWNER/mapping-table.csv", "OWNER/README.md",
                       "OWNER/DECISIONS-TO-MAKE.md"] + owner_early + scripts_all,
        2: src["core"] + src["model"] + src["util"],
        3: src["ingest"] + tests,
        4: src["mapping"],
        5: src["engine"],
        6: src["render"] + src["verify"],
        7: [],  # scripts already listed in phase 1
        8: docs_all,
    }


def required_for_phase(phase: int | None) -> list[str]:
    m = phase_map()
    if phase is None:
        out: list[str] = []
        for p in sorted(m):
            out += m[p]
        return out
    out = []
    for p in sorted(m):
        if p <= phase:
            out += m[p]
    return out


def check_forbidden_tokens(problems: list[str]) -> None:
    targets = list((REPO / "src").rglob("*.py")) + list((REPO / "scripts").rglob("*.py"))
    targets += list((REPO / "scripts").rglob("*.sh"))
    for path in sorted(targets):
        if path == Path(__file__).resolve():
            continue  # the scanner necessarily contains the token literals
        rel = path.relative_to(REPO)
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_TOKENS:
            if token in text:
                problems.append(f"{rel}: forbidden placeholder token {token!r}")
        # bare `pass` statement or naked `...` as a body
        for line_no, line in enumerate(text.splitlines(), start=1):
            s = line.strip().rstrip(":")
            if s == "pass" or s == "...":
                problems.append(f"{rel}:{line_no}: stub body ({s.strip()})")


def check_owner_markers(problems: list[str]) -> None:
    for rel in OWNER_FILES:
        path = REPO / rel
        if not path.exists():
            problems.append(f"{rel}: owner file missing")
            continue
        first = path.read_text(encoding="utf-8").splitlines()[:1]
        if not first or first[0].strip() != OWNER_MARKER:
            problems.append(f"{rel}: does not begin with the owner marker line")


def check_mapping_table_header_only(problems: list[str]) -> None:
    path = REPO / "OWNER" / "mapping-table.csv"
    header = "rule_id,pattern_id,source_qid,question,answer_type,evidence_needed,where_to_find_it,if_missing_gap,decided_by,date,verified"
    if not path.exists():
        problems.append("OWNER/mapping-table.csv missing")
        return
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        problems.append("OWNER/mapping-table.csv is empty (expected header row)")
        return
    if lines[0].strip() != header:
        problems.append("OWNER/mapping-table.csv header does not match the data contract")
    if len(lines) > 1:
        problems.append(
            f"OWNER/mapping-table.csv has {len(lines) - 1} data rows — owner-only; agents must not fill it")


def check_pyproject_pins(problems: list[str]) -> None:
    path = REPO / "pyproject.toml"
    if not path.exists():
        return
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        problems.append(f"pyproject.toml unparseable: {exc}")
        return
    deps = " ".join(data.get("project", {}).get("dependencies", []))
    if "fpdf2==" not in deps:
        problems.append("pyproject.toml does not pin fpdf2")
    if data.get("project", {}).get("requires-python") != ">=3.11":
        problems.append("pyproject.toml requires-python must be >=3.11")


def check_ci_workflow(problems: list[str]) -> None:
    path = REPO / ".github" / "workflows" / "ci.yml"
    if path.exists() and "--network none" not in path.read_text(encoding="utf-8"):
        problems.append(".github/workflows/ci.yml missing the documented --network none demo run")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--phase", type=int, default=None,
                    help="only enforce requirements up to this phase (default: all)")
    args = ap.parse_args()

    problems: list[str] = []
    for rel in required_for_phase(args.phase):
        path = REPO / rel
        if not path.exists():
            problems.append(f"missing: {rel}")
            continue
        if rel in ALLOW_EMPTY:
            continue
        if path.is_file() and path.stat().st_size == 0:
            problems.append(f"empty: {rel}")

    check_forbidden_tokens(problems)
    if args.phase is None or args.phase >= 1:
        check_owner_markers(problems)
        check_mapping_table_header_only(problems)
        check_pyproject_pins(problems)
        check_ci_workflow(problems)

    if problems:
        print(f"check-scaffold: {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    scope = "all phases" if args.phase is None else f"phases up to {args.phase}"
    print(f"check-scaffold: OK ({scope}) — {len(required_for_phase(args.phase))} required files present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
