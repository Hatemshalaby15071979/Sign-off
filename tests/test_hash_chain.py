"""Hash chain: canonical JSON, deterministic ordering, tamper-sensitive head."""
from __future__ import annotations

from signoff.engine.hash_chain import canonical_json, sha256_bytes, sha256_text
from signoff.model.decision_event import DecisionEvent
from signoff.util.clock import parse_instant

from tests.conftest import AS_OF


def make_event(**overrides) -> DecisionEvent:
    fields = dict(
        ts="2026-09-14T10:00:00+00:00", actor_identity="Reviewer_A",
        action="auto_score:accepted", state="human-approved",
        source_file="qa_review_export.csv", source_row=2,
        policy_rule="DEMO-QA-1")
    fields.update(overrides)
    return DecisionEvent(**fields)


def test_canonical_json_sorts_keys_and_is_stable():
    a = canonical_json({"b": 1, "a": [2, 3]})
    b = canonical_json({"a": [2, 3], "b": 1})
    assert a == b == '{"a":[2,3],"b":1}'


def test_sha256_helpers():
    assert sha256_text("abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    assert sha256_bytes(b"abc") == sha256_text("abc")


def test_chain_genesis_has_documented_prefix():
    from signoff.engine.builder import chain_genesis

    assert chain_genesis(AS_OF) == ("signoff-chain-genesis:"
                                    + parse_instant(AS_OF).isoformat())


def test_event_ids_are_content_derived_not_random():
    ev1, ev2 = make_event(), make_event()
    ev1.compute_ids("genesis")
    ev2.compute_ids("different-genesis")
    assert ev1.event_id == ev2.event_id       # body does not include prev_hash
    assert ev1.hash != ev2.hash               # the hash chains the previous link


def test_compute_ids_links_forward():
    ev = make_event()
    h1 = ev.compute_ids("genesis")
    assert ev.prev_hash == "genesis"
    assert ev.hash == h1


def test_chain_head_deterministic_in_content_not_order():
    from signoff.engine.builder import chain_events

    events = [make_event(source_row=n, ts=f"2026-09-14T10:0{n}:00+00:00")
              for n in (2, 3, 4)]
    head_a = chain_events(list(events), AS_OF)
    head_b = chain_events(list(reversed(events)), AS_OF)
    assert head_a == head_b
    assert all(e.event_id and e.prev_hash for e in events)


def test_chain_head_tamper_sensitive():
    from signoff.engine.builder import chain_events

    events = [make_event(source_row=n, ts=f"2026-09-14T10:0{n}:00+00:00")
              for n in (2, 3)]
    original = chain_events([e for e in events], AS_OF)
    events[0].action += "x"
    for e in events:
        e.event_id = ""
        e.evidence_ids = []
        e.prev_hash = ""
        e.hash = ""
    mutated = chain_events(events, AS_OF)
    assert original != mutated


def test_serde_roundtrip_and_content_check():
    ev = make_event()
    ev.compute_ids("genesis")
    restored = DecisionEvent.from_dict(ev.to_dict())
    assert restored.hash == ev.hash
    assert restored.event_id == ev.event_id


def test_from_dict_rejects_hand_edited_body():
    ev = make_event()
    ev.compute_ids("genesis")
    data = ev.to_dict()
    data["action"] = "auto_score:accepted-but-changed"
    import pytest

    with pytest.raises(ValueError, match="failed content check"):
        DecisionEvent.from_dict(data)


def test_from_dict_rejects_missing_fields():
    import pytest

    with pytest.raises(ValueError, match="missing fields"):
        DecisionEvent.from_dict({"ts": "x"})


def test_demo_build_chain_replays_head(demo_build):
    pack = demo_build
    expected_prev = sha256_text(pack.chain_genesis)
    replay = ""
    for ev in pack.events:
        assert ev.prev_hash == expected_prev
        expected_prev = ev.hash
        replay = ev.hash
    assert replay == pack.head
    assert len(pack.events) == 26
