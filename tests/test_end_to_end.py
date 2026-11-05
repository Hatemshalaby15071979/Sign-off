"""End-to-end: real questionnaire -> pack -> artifacts -> verifier -> gaps."""
from __future__ import annotations

import csv
import io
import json

from tests.conftest import AS_OF, DEMO_DATA_FILES, FIXTURES

from signoff import cli
from signoff.engine import builder as builder_mod
from signoff.verify.verify_pack import verify_pack


def build_demo(tmp_path):
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    artifacts = cli._render_artifacts(pack, pack.as_of)
    out = tmp_path / "demo"
    cli._write_atomic(out, artifacts)
    return pack, artifacts, out


def test_full_pipeline(tmp_path):
    pack, artifacts, out = build_demo(tmp_path)
    assert set(p.name for p in out.iterdir()) == {
        "dossier.html", "dossier.pdf", "pack.json",
        "questionnaire-answers.csv", "gap-list.csv",
        "evidence-events.csv", "oversight-statement.txt"}
    assert verify_pack(out)[0] == "VERIFIED"


def test_pack_json_is_self_describing(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    data = json.loads((out / "pack.json").read_text(encoding="utf-8"))
    assert data["schema"] == "signoff-pack/0.1"
    assert data["pack_id"].startswith("PK-")
    assert data["as_of"] == AS_OF
    assert data["simulated"] is True
    assert data["chain_genesis"].startswith("signoff-chain-genesis:")
    # manifest never contains pack.json itself
    assert "pack.json" not in data["artifacts"]
    assert set(data["artifacts"]) == {
        "dossier.html", "dossier.pdf", "questionnaire-answers.csv",
        "gap-list.csv", "evidence-events.csv", "oversight-statement.txt"}
    for meta in data["artifacts"].values():
        assert len(meta["sha256"]) == 64 and meta["bytes"] > 0
    assert data["runtime"]["fpdf2"] == "2.8.4"
    assert data["not_prove"] and len(data["not_prove"]) >= 6
    assert data["appendix"]["banner"].startswith("Informational cross-reference only")


def test_answers_csv_fidelity(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    text = (out / "questionnaire-answers.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    answers = {r["qid"]: r for r in rows if r["qid"].startswith("Q-")}
    assert len(answers) == 18
    a = answers["Q-101"]
    assert a["mapped_rule_id"] == "R-001"
    assert a["pattern_id"] == "QA-HUMAN-REVIEW"
    assert a["coverage"] == "66.7%"
    assert a["evidence_id"].startswith("EV-")
    assert "4/6" in a["answer"]
    assert answers["Q-117"]["answer"] == "UNMAPPED"
    # every row of every CSV carries the machine disclosure suffix
    assert any(r["qid"] == "disclosure" for r in rows)


def test_events_csv_exports_the_chain(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    text = (out / "evidence-events.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    events = [r for r in rows if r["event_id"].startswith("E-")]
    assert len(events) == 26
    assert all(r["prev_hash"] for r in events)
    assert all(r["hash"] for r in events)
    headers = list(events[0])
    assert headers[0] == "event_id" and "evidence_ids" in headers


def test_gap_list_csv_content(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    text = (out / "gap-list.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    rows = [r for r in rows if r.get("reason")]          # minus disclosure rows
    rules = [r["rule_id"] for r in rows]
    assert "R-004" in rules            # LEAST-PRIV gap: 0/1
    assert "R-001" in rules            # QA gap: 4/6
    assert rows and all(r["reason"] for r in rows)
    unmapped = [r for r in rows if r["rule_id"] == "-"]
    assert {r["source_qid"] for r in unmapped} == {"Q-117", "Q-118"}


def test_statement_is_never_pre_signed(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    text = (out / "oversight-statement.txt").read_text(encoding="utf-8")
    assert "FOR HUMAN SIGNATURE" in text
    assert "Accountable person (name) : ______" in text
    assert all("_" * 10 in line for line in text.splitlines()
               if line.startswith(("Accountable person", "Role / organisation",
                                   "Signature", "Date")))
    assert "Signoff never signs" in text


def test_html_dossier_is_self_contained(tmp_path):
    _pack, _artifacts, out = build_demo(tmp_path)
    html = (out / "dossier.html").read_text(encoding="utf-8")
    for banned in ("<script", "https://", "http://", 'src="', "@import"):
        assert banned not in html
    assert "What this pack does NOT prove" in html
    assert "SIMULATION_DISCLOSURE" in html
    assert html.count("<h2>") >= 4          # sections per decision-log D-009


def test_redacted_build_keeps_ids_masks_values(tmp_path, export_data_dir):
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=export_data_dir,
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, redact=True, simulated=False)
    assert any(ev.actor_identity == "REDACTED" for ev in pack.events)
    assert all(ev.ts for ev in pack.events)                  # ids/ts kept
    assert pack.events[0].source_file                        # traceability kept


def test_real_data_demo_roundtrip_via_cli(tmp_path):
    from tests.conftest import run_cli

    out = tmp_path / "demo"
    result = run_cli("demo", "--out", str(out), "--as-of", AS_OF)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "SIMULATION_DISCLOSURE" in result.stdout
    verification = run_cli("verify-pack", "--pack", str(out))
    assert verification.returncode == 0
    assert "VERIFIED" in verification.stdout
