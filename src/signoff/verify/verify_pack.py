"""Pack verification — recomputes the hash chain + artifact digests.

`verify_pack()` rebuilds everything from pack.json (never trusting it) and
returns ("VERIFIED"|"TAMPERED", diagnostics). Verified == every artifact
matches its manifest digest AND every event hash matches its content AND
the chain links consitently AND the head matches.
"""
from __future__ import annotations

import json
from pathlib import Path

from signoff.engine.hash_chain import canonical_json, sha256_bytes, sha256_text
from signoff.model.decision_event import DecisionEvent
from signoff.render.appendix import appendix_json  # noqa: F401 (kept for parity)
from signoff.render.disclosure import not_proof_json  # noqa: F401


def verify_pack(pack_dir: Path) -> tuple[str, list[str]]:
    """Returns (status, messages). status is 'VERIFIED' or 'TAMPERED'."""
    messages: list[str] = []
    status = "VERIFIED"

    manifest_path = pack_dir / "pack.json"
    if not manifest_path.exists():
        return "TAMPERED", [f"pack.json missing in {pack_dir.name}"]
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "TAMPERED", [f"pack.json unreadable: {exc}"]

    # 1) events: content-identical reconstruction + forward chain check
    prev_seen = ""
    chain_ok = True
    for i, raw in enumerate(data.get("events", [])):
        try:
            ev = DecisionEvent.from_dict(raw)
        except (ValueError, KeyError) as exc:
            messages.append(f"event[{i}] fails content check: {exc}")
            status = "TAMPERED"
            continue
        if i == 0:
            expected_prev = sha256_text(str(data.get("chain_genesis", "")))
            if ev.prev_hash != expected_prev:
                messages.append("event[0] prev hash does not match the genesis")
                chain_ok = False
        elif ev.prev_hash != prev_seen:
            messages.append(f"event[{i}] prev hash link broken")
            chain_ok = False
        prev_seen = ev.hash
    if chain_ok is False:
        status = "TAMPERED"
    else:
        messages.append("hash chain replays cleanly under canonical serialisation")

    if data.get("head") and prev_seen != data.get("head"):
        messages.append("chain head does not match last event hash")
        status = "TAMPERED"

    # 2) artifacts against the manifest (pack.json itself is the manifest)
    manifest = data.get("artifacts")
    if not isinstance(manifest, dict):
        return "TAMPERED", messages + ["pack.json has no artifacts manifest"]
    for name, meta in sorted(manifest.items()):
        if not isinstance(meta, dict) or "sha256" not in meta:
            messages.append(f"artifact {name} manifest entry malformed")
            status = "TAMPERED"
            continue
        target = pack_dir / name
        if ".." in name or name != Path(name).name:
            messages.append(f"artifact {name} path-shaped name; refusing")
            status = "TAMPERED"
            continue
        if not target.exists():
            messages.append(f"artifact {name} missing on disk")
            status = "TAMPERED"
            continue
        digest = sha256_bytes(target.read_bytes())
        if digest != meta.get("sha256"):
            messages.append(f"artifact {name} digest mismatch (bytes differ)")
            status = "TAMPERED"
        elif target.stat().st_size != meta.get("bytes"):
            messages.append(f"artifact {name} size mismatch")
            status = "TAMPERED"
    if status == "VERIFIED":
        messages.append("all artifacts match their manifest digests")

    # 3) banners expected on artifacts
    if data.get("simulated"):
        html_path = pack_dir / "dossier.html"
        if html_path.exists():
            if "SIMULATION_DISCLOSURE" not in html_path.read_text(encoding="utf-8"):
                messages.append("simulated pack is missing the SIMULATION_DISCLOSURE")
                status = "TAMPERED"
    return status, messages
