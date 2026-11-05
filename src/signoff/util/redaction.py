"""Opt-in redaction.

Signoff's default is to redact nothing: the customer's own exports stay on
the customer's machine. When the operator passes `--redact`, value columns
are masked with `REDACTED` while IDs, timestamps and structural fields are
kept, so the pack remains verifiable.
"""
from __future__ import annotations

from collections import OrderedDict

# Fields that are NEVER masked (they carry no customer torso content).
KEEP = frozenset({
    "event_id", "ts", "source_file", "source_row", "state",
    "policy_rule", "evidence_ids", "prev_hash", "hash", "qid",
    "rule_id", "pattern_id", "source_qid", "answer_type", "order",
    "as_of", "coverage", "matched", "expected",
})

MASK = "REDACTED"


def redact_mapping(mapping: dict, keys_to_mask: frozenset) -> dict:
    """Return a copy with the listed keys masked (others untouched)."""
    out: OrderedDict = OrderedDict()
    for key, value in mapping.items():
        if key in keys_to_mask:
            if isinstance(value, list):
                out[key] = [MASK if isinstance(v, str) else v for v in value]
            elif isinstance(value, dict):
                out[key] = {k: MASK for k in value}
            else:
                out[key] = MASK
        else:
            out[key] = value
    return out


def mask_text(text: str) -> str:
    """Mask free text while keeping the fact that text existed."""
    return MASK if text else text


def redact_value(value: str) -> str:
    return MASK if value.strip() else value
