"""Canonical serialisation + sha256 - the hashing core.

Canonical rule (docs/DATA-CONTRACT.md): `json.dumps(obj, sort_keys=True,
separators=(",", ":"), ensure_ascii=False)`, UTF-8 encoded. Every hash in a
pack is sha256 over such a canonical JSON document. Nothing else is hashed.
"""
from __future__ import annotations

import hashlib
import json


def canonical_json(obj: object) -> str:
    """Canonical, stable serialisation: sorted keys, no whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    """sha256 hex digest of a UTF-8 string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """sha256 hex digest of raw bytes (used for artifact integrity)."""
    return hashlib.sha256(data).hexdigest()
