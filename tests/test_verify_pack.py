"""Pack verifier: VERIFIED on a clean pack; TAMPERED on every mutation class."""
from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import written_pack

from signoff.verify.verify_pack import verify_pack


def flip_pack_json(pack_dir: Path, mutate) -> None:
    data = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    mutate(data)
    (pack_dir / "pack.json").write_text(
        json.dumps(data, sort_keys=True, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")


def test_clean_demo_pack_is_verified(written_pack):
    status, messages = verify_pack(written_pack)
    assert status == "VERIFIED"
    assert any("replays cleanly" in m for m in messages)
    assert any("match their manifest digests" in m for m in messages)


def test_artifact_tamper_detected_must_report_tampered(written_pack):
    target = written_pack / "dossier.html"
    data = bytearray(target.read_bytes())
    i = data.index(b"Signoff")
    data[i] = ord("X")
    target.write_bytes(bytes(data))
    status, messages = verify_pack(written_pack)
    assert status == "TAMPERED"
    assert any("digest mismatch" in m for m in messages)


def test_event_body_tamper_detected(written_pack):
    def mutate(data):
        data["events"][2]["policy_rule"] = \
            data["events"][2]["policy_rule"] + "-edited"

    flip_pack_json(written_pack, mutate)
    status, messages = verify_pack(written_pack)
    assert status == "TAMPERED"


def test_head_tamper_detected(written_pack):
    def mutate(data):
        data["head"] = "0" * 64

    flip_pack_json(written_pack, mutate)
    assert verify_pack(written_pack)[0] == "TAMPERED"


def test_chain_genesis_tamper_detected(written_pack):
    def mutate(data):
        gen = data["chain_genesis"]
        data["chain_genesis"] = gen[:-1] + ("X" if gen[-1] != "X" else "Y")

    flip_pack_json(written_pack, mutate)
    assert verify_pack(written_pack)[0] == "TAMPERED"


def test_missing_artifact_detected(written_pack):
    (written_pack / "gap-list.csv").unlink()
    status, messages = verify_pack(written_pack)
    assert status == "TAMPERED"
    assert any("missing on disk" in m for m in messages)


def test_missing_pack_json_detected(written_pack):
    (written_pack / "pack.json").unlink()
    status, messages = verify_pack(written_pack)
    assert status == "TAMPERED"
    assert any("pack.json missing" in m for m in messages)


def test_malformed_pack_json_detected(written_pack):
    (written_pack / "pack.json").write_text("{not json", encoding="utf-8")
    assert verify_pack(written_pack)[0] == "TAMPERED"


def test_path_shaped_artifact_names_refused(written_pack):
    def mutate(data):
        name = "dossier.pdf"
        data["artifacts"][name]["sha256"] = data["artifacts"][name]["sha256"]

    # instead inject a malicious manifest entry on a copy
    data = json.loads((written_pack / "pack.json").read_text(encoding="utf-8"))
    data["artifacts"]["../evil/bin"] = {"sha256": "0", "bytes": 1}
    (written_pack / "pack.json").write_text(
        json.dumps(data, sort_keys=True, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    status, _ = verify_pack(written_pack)
    assert status == "TAMPERED"


def test_verify_is_reproducible(written_pack):
    assert verify_pack(written_pack) == verify_pack(written_pack)


def test_cli_verify_feedback_codes(tmp_path):
    from tests.conftest import run_cli

    out = tmp_path / "vv"
    assert run_cli("demo", "--out", str(out)).returncode == 0
    ok = run_cli("verify-pack", "--pack", str(out))
    assert ok.returncode == 0 and ok.stdout.strip().endswith("VERIFIED")
    (out / "questionnaire-answers.csv").write_text("tampered\n", encoding="utf-8")
    bad = run_cli("verify-pack", "--pack", str(out))
    assert bad.returncode == 1
