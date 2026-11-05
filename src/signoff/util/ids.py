"""Stable, content-derived IDs.

No random sources anywhere. Every ID is a short sha256 prefix over a
canonical serialisation of the labelled content it names, so identical
inputs always produce identical IDs and different inputs never collide in
practice (16 hex characters).

Prefix scheme:
- `E-`  : DecisionEvent chain id
- `EV-` : evidence entry inside the pack (one per rule/per pattern answer)
- `PK-` : pack id (whole-manifest hash)
- `B-`  : build (questionnaire+data+mapping+as_of) id
"""
from __future__ import annotations

from signoff.engine.hash_chain import canonical_json, sha256_text


def make_id(prefix: str, payload: object, length: int = 16) -> str:
    """`<prefix><16 hex chars>` derived from canonical(sha256(payload))."""
    return prefix + sha256_text(canonical_json(payload))[:length]


def evidence_id(rule_id: str, pattern_id: str, source_qid: str, as_of: str) -> str:
    """Deterministic evidence entry id for one answered rule."""
    return make_id(
        "EV-",
        {"rule_id": rule_id, "pattern_id": pattern_id,
         "source_qid": source_qid, "as_of": as_of},
        length=12,
    )


def pack_id(manifest_hash: str) -> str:
    return "PK-" + manifest_hash[:16]
