"""CLI surface: operator entry points, exit codes, honest failures."""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import FIXTURES, export_data_dir

from signoff import cli
from signoff.errors import SignoffError


class Args:
    pass


def test_validate_mapping_prints_rule_count():
    import contextlib
    import io

    class A(Args):
        mapping = str(FIXTURES / "mapping-table.demo.csv")
        allow_unverified = False
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert cli.cmd_validate_mapping(A()) == 0
    assert "VALID: 16 signed rule(s)" in buf.getvalue()


def test_parse_questionnaire_writes_csv(tmp_path):
    class A(Args):
        input = str(FIXTURES / "questionnaire.demo.csv")
        out = str(tmp_path / "questions.csv")
    assert cli.cmd_parse_questionnaire(A()) == 0
    text = (tmp_path / "questions.csv").read_text(encoding="utf-8")
    lines = text.strip().splitlines()
    assert lines[0] == ("qid,exact_text,answer_type,qid_source,source_path,order")
    assert "Q-101," in text


def test_build_fails_closed_when_data_folder_has_foreign_csvs(tmp_path, export_data_dir):
    # a folder whose extra CSV is not a known export kind must fail, never filter
    (export_data_dir / "random_notes.csv").write_text("foo,bar\n1,2\n", "utf-8")
    class A(Args):
        questionnaire = str(FIXTURES / "questionnaire.demo.csv")
        data = str(export_data_dir)
        mapping = str(FIXTURES / "mapping-table.demo.csv")
        out = str(tmp_path / "pack")
        as_of = None
        redact = False
        allow_unverified = False
    with pytest.raises(SignoffError, match="unknown export file kind"):
        cli.cmd_build(A())
    assert not (tmp_path / "pack").exists()      # nothing was written


def test_build_round_trip_with_clean_data_dir(tmp_path, export_data_dir):
    out = tmp_path / "pack"
    A = type("A", (), {
        "questionnaire": str(FIXTURES / "questionnaire.demo.csv"),
        "data": str(export_data_dir),
        "mapping": str(FIXTURES / "mapping-table.demo.csv"),
        "out": str(out),
        "as_of": "2026-11-05T00:00:00+00:00",
        "redact": False,
        "allow_unverified": False,
    })
    assert cli.cmd_build(A) == 0
    assert "pack.json" in {p.name for p in out.iterdir()}
    assert (out / "dossier.pdf").read_bytes()[:4] == b"%PDF"
    pack_id = json.loads((out / "pack.json").read_text(encoding="utf-8"))["pack_id"]
    assert pack_id.startswith("PK-")
    # a real build carries the UNVERIFIED banner never the simulation one
    html = (out / "dossier.html").read_text(encoding="utf-8")
    assert "SIMULATION_DISCLOSURE" not in html


def test_rejects_bad_and_naive_as_of(tmp_path, export_data_dir):
    base = dict(questionnaire=str(FIXTURES / "questionnaire.demo.csv"),
                data=str(export_data_dir),
                mapping=str(FIXTURES / "mapping-table.demo.csv"),
                out=str(tmp_path / "pack"),
                redact=False, allow_unverified=False)
    for bad in ("yesterday", "2026-11-05T09:00:00"):
        class A(Args):
            pass
        for key, value in {**base, "as_of": bad}.items():
            setattr(A, key, value)
        with pytest.raises(SignoffError):
            cli.cmd_build(A())
    assert not (tmp_path / "pack").exists()


def test_help_lists_all_commands():
    out = subprocess.run([sys.executable, "-m", "signoff", "--help"],
                         capture_output=True, text=True)
    for command in ("validate-mapping", "parse-questionnaire", "build",
                    "demo", "verify-pack"):
        assert command in out.stdout


def test_version_probe_exits():
    import pytest as _pytest

    with _pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0


def test_cli_demo_output_is_simulated(demo_written_pack):
    data = json.loads((demo_written_pack / "pack.json").read_text(
        encoding="utf-8"))
    assert data["simulated"] is True
    assert data["pack_id"].startswith("PK-")


def test_atomic_write_leaves_nothing_on_failure(tmp_path, monkeypatch):
    out_dir = tmp_path / "pack"
    broken_stage = tmp_path / "stage-broken"
    broken_stage.mkdir()
    (broken_stage / "pack.json").mkdir()      # writing bytes onto a dir -> OSError
    monkeypatch.setattr(cli.tempfile, "mkdtemp", lambda **kw: str(broken_stage))
    artifacts = {"pack.json": b"{}", "dossier.html": b"<html/>"}
    with pytest.raises(SignoffError, match="atomic artifact write failed"):
        cli._write_atomic(out_dir, artifacts)
    assert list(out_dir.iterdir()) == []
