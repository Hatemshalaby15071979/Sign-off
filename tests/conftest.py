"""Shared test fixtures: fixture paths, pack builders, small canonical CSVs."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURES = REPO / "tests" / "fixtures"

# Subprocess-based tests (`python -m signoff`) must import the package from a
# fresh checkout too. pyproject's `pythonpath = ["src"]` only covers the
# in-process interpreter, so export it for children as well (CR-05).
_SRC = str(REPO / "src")
_existing = os.environ.get("PYTHONPATH")
os.environ["PYTHONPATH"] = _SRC + (os.pathsep + _existing if _existing else "")

AS_OF = "2026-11-05T00:00:00+00:00"
DEMO_AS_OF = "2026-11-05T00:00:00+00:00"

DEMO_DATA_FILES = (
    "qa_review_export.csv", "approval_events.csv", "escalation_log.csv",
    "audit_events.csv", "rolespec_export.csv", "ai_inventory.csv",
    "training_register.csv", "incident_register.csv",
)


@pytest.fixture()
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture()
def mapping_csv() -> Path:
    return FIXTURES / "mapping-table.demo.csv"


@pytest.fixture()
def questionnaire_csv() -> Path:
    return FIXTURES / "questionnaire.demo.csv"


@pytest.fixture()
def demo_build(tmp_path: Path):
    """Build the demo pack once; share it across chained artifacts."""
    from signoff.engine import builder as builder_mod

    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / name for name in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF,
        simulated=True,
    )
    return pack


@pytest.fixture()
def demo_artifacts(demo_build):
    """Rendered demo pack bytes in memory (nothing on disk)."""
    from signoff import cli

    return cli._render_artifacts(demo_build, demo_build.as_of)


@pytest.fixture()
def written_pack(tmp_path: Path, demo_artifacts) -> Path:
    """Demo pack rendered + written + verified VERIFIED."""
    from signoff import cli

    out = tmp_path / "pack"
    cli._write_atomic(out, demo_artifacts)
    return out


@pytest.fixture()
def real_pack(tmp_path: Path):
    """A non-simulated pack built from the demo fixtures (real-build mode)."""
    from signoff import cli
    from signoff.engine import builder as builder_mod

    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / name for name in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF,
        simulated=False,
    )
    artifacts = cli._render_artifacts(pack, pack.as_of)
    out = tmp_path / "real"
    cli._write_atomic(out, artifacts)
    return out


VALID_RULE_ROW = [
    "R-T01", "QA-HUMAN-REVIEW", "Q-999", "Does a named human review AI QA actions?",
    "yes_no", "qa_review_export.csv columns reviewer_id + human_action",
    "qa_review_export.csv rows", "Gap: no reviewer rows.",
    "Test_Signer", "2026-11-04", "yes",
]


def rule_csv(*rows: list[str], header: str | None = None) -> str:
    from signoff.model.mapping_rule import HEADER

    lines = [header or HEADER]
    for row in rows:
        quoted = []
        for cell in row:
            text = cell.replace('"', '""')
            quoted.append(f'"{text}"' if any(c in text for c in ',"\n') else text)
        lines.append(",".join(quoted))
    return "\n".join(lines) + "\n"


@pytest.fixture()
def mapping_file_factory(tmp_path: Path):
    """Write a mapping-table.csv into tmp storage; returns its Path."""
    def _write(text: str, name: str = "mapping-table.csv") -> Path:
        path = tmp_path / name
        path.write_text(text, encoding="utf-8")
        return path
    return _write


def run_cli(*args: str, cwd: Path = REPO) -> subprocess.CompletedProcess:
    """Run the CLI exactly like an operator would (subprocess, honest exit code)."""
    return subprocess.run(
        [sys.executable, "-m", "signoff", *args],
        cwd=str(cwd), capture_output=True, text=True, env=None)


@pytest.fixture()
def export_data_dir(tmp_path: Path) -> Path:
    """A clean Input-B folder with ONLY the eight export CSVs."""
    out = tmp_path / "data"
    out.mkdir()
    for name in DEMO_DATA_FILES:
        out.joinpath(name).write_bytes((FIXTURES / name).read_bytes())
    return out


def pdf_stream_text(pdf_bytes: bytes) -> str:
    """Extract human-readable text out of PDF object streams (may be zlib)."""
    import re
    import zlib

    chunks = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.S)
    text = bytearray()
    for chunk in chunks:
        try:
            text += zlib.decompress(chunk)
        except zlib.error:
            text += chunk
    return bytes(text).decode("latin-1", "replace")


@pytest.fixture()
def demo_written_pack(tmp_path: Path) -> Path:
    """Full demo built via the CLI subprocess (operator path)."""
    out = tmp_path / "demo"
    result = run_cli("demo", "--out", str(out))
    assert result.returncode == 0, result.stderr + result.stdout
    return out
