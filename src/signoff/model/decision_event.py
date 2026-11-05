"""Signoff — DecisionEvent: the single internal evidence representation.

See docs/DATA-CONTRACT.md for the full contract. All IDs are content-derived
(sha256 over canonical serialisations); no random UUIDs; no wall clock.
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from signoff.engine.hash_chain import canonical_json, sha256_text

State = Literal[
    "AI-proposed", "gate-blocked", "human-approved", "escalated", "unlogged"
]

STATES: tuple[str, ...] = (
    "AI-proposed", "gate-blocked", "human-approved", "escalated", "unlogged",
)

# Canonical serialisation key order is fixed by sorted keys; the field set
# below is the contract. Extra fields are a contract violation.
CONTRACT_FIELDS = (
    "event_id", "ts", "actor_identity", "action", "state",
    "source_file", "source_row", "policy_rule", "evidence_ids",
    "prev_hash", "hash",
)


class DecisionEvent:
    """One reconstructed oversight decision, traceable to a source row."""

    __slots__ = CONTRACT_FIELDS + ("_identity_key",)

    def __init__(
        self,
        *,
        ts: str,
        actor_identity: str,
        action: str,
        state: State,
        source_file: str,
        source_row: int,
        policy_rule: str,
        event_id: str = "",
        evidence_ids: Optional[list[str]] = None,
        prev_hash: str = "",
        hash: str = "",
    ) -> None:
        self.ts = ts
        self.actor_identity = actor_identity
        self.action = action
        self.state = state
        self.source_file = source_file
        self.source_row = int(source_row)
        self.policy_rule = policy_rule
        self.event_id = event_id
        self.evidence_ids = list(evidence_ids or [])
        self.prev_hash = prev_hash
        self.hash = hash
        # Stable sort key derived from content (used for chain order).
        self._identity_key = canonical_json(
            {"ts": ts, "source_file": source_file, "source_row": self.source_row,
             "action": action, "actor_identity": actor_identity, "state": state})

    # ---------------------------------------------------------------- ordinal
    @property
    def identity_key(self) -> str:
        """Deterministic sort key; identical rows keep a stable tie-break."""
        return self._identity_key

    def __lt__(self, other: "DecisionEvent") -> bool:
        return self._identity_key < other._identity_key
    __le__ = __lt__.__le__  # type: ignore[attr-defined]
    __gt__ = __lt__.__gt__  # type: ignore[attr-defined]

    # ---------------------------------------------------------- serialisation
    def body(self) -> dict:
        """Chain payload: everything except the derived id and hashes."""
        return {
            "ts": self.ts,
            "actor_identity": self.actor_identity,
            "action": self.action,
            "state": self.state,
            "source_file": self.source_file,
            "source_row": self.source_row,
            "policy_rule": self.policy_rule,
            "evidence_ids": self.evidence_ids,
        }

    def compute_ids(self, prev_hash: str) -> str:
        """Derive event_id and hash; return the new hash for chaining."""
        payload = dict(self.body())
        self.event_id = "E-" + sha256_text(canonical_json(payload))[:16]
        payload["prev_hash"] = prev_hash
        self.prev_hash = prev_hash
        self.hash = sha256_text(canonical_json(payload))
        return self.hash

    def to_dict(self) -> dict:
        out = {k: getattr(self, k) for k in CONTRACT_FIELDS}
        return out

    @classmethod
    def from_dict(cls, data: dict) -> "DecisionEvent":
        missing = [k for k in CONTRACT_FIELDS if k not in data]
        if missing:
            raise ValueError(f"DecisionEvent serialisation missing fields: {missing}")
        ev = cls(
            ts=data["ts"], actor_identity=data["actor_identity"],
            action=data["action"], state=data["state"],
            source_file=data["source_file"], source_row=data["source_row"],
            policy_rule=data["policy_rule"], event_id=data["event_id"],
            evidence_ids=list(data["evidence_ids"]),
            prev_hash=data["prev_hash"], hash=data["hash"],
        )
        # stored id must match content exactly — catches hand-edited packs
        intended = canonical_json(dict(ev.body(), prev_hash=data["prev_hash"]))
        if data["hash"] != sha256_text(intended) or data["event_id"] != "E-" + \
                sha256_text(canonical_json(ev.body()))[:16]:
            raise ValueError("DecisionEvent serialisation failed content check")
        return ev

    def json(self) -> str:
        return canonical_json(self.to_dict())
