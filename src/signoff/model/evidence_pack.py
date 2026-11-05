"""EvidencePack — the complete, self-verifying pack model.

A pack is everything needed to re-render all artifacts byte-identically and
to re-verify the hash chain without the original data folder: the pack id,
the injected as-of instant, the banners, the questionnaire questions with
mapped rules and answers, the amber-verified events, coverage results, gaps,
and the manifest of tool versions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PACK_SCHEMA_VERSION = "signoff-pack/0.1"


@dataclass
class CoverageResult:
    pattern_id: str
    rule_id: str
    source_qid: str
    matched: int
    expected: int
    denominator_label: str     # explicit, human-readable denominator
    pct: float | None          # None => N/A window
    event_ids: list[str] = field(default_factory=list)
    matched_events: list = field(default_factory=list)  # DecisionEvent objects (transient)

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "rule_id": self.rule_id,
            "source_qid": self.source_qid,
            "matched": self.matched,
            "expected": self.expected,
            "denominator": self.denominator_label,
            "percentage": self.pct if self.pct is not None else "N/A (no events in period)",
            "event_ids": list(self.event_ids),
        }


@dataclass
class Gap:
    rule_id: str
    source_qid: str
    reason: str
    affected_source_files: list[str]
    affected_row_count: int
    suggested_remediation: str

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "source_qid": self.source_qid,
            "reason": self.reason,
            "affected_source_files": list(self.affected_source_files),
            "affected_row_count": self.affected_row_count,
            "suggested_remediation": self.suggested_remediation,
        }


@dataclass
class Answer:
    qid: str
    exact_text: str
    answer_type: str
    answer: str
    mapped_rule_id: str | None
    pattern_id: str | None
    evidence_id: str | None
    coverage_pct: str            # e.g. "83.3%" or "N/A (no events in period)"
    trust_label: str             # "mapped" | "UNMAPPED"

    def to_dict(self) -> dict:
        return {
            "qid": self.qid,
            "question": self.exact_text,
            "answer_type": self.answer_type,
            "answer": self.answer,
            "mapped_rule_id": self.mapped_rule_id,
            "pattern_id": self.pattern_id,
            "evidence_id": self.evidence_id,
            "coverage": self.coverage_pct,
            "status": self.trust_label,
        }


@dataclass
class EvidencePack:
    pack_id: str
    schema_version: str = PACK_SCHEMA_VERSION
    as_of: str = ""
    simulated: bool = True
    unverified_rules: bool = False
    head: str = ""                     # hash-chain head
    chain_genesis: str = ""            # labelled genesis constant (documented)
    data_files: list[str] = field(default_factory=list)
    questions: list[Answer] = field(default_factory=list)
    events: list[Any] = field(default_factory=list)      # DecisionEvent serialisations
    coverage: list[CoverageResult] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    rules: list[dict] = field(default_factory=list)
    unmapped_qids: list[str] = field(default_factory=list)
    artifacts: dict[str, dict[str, str]] = field(default_factory=dict)  # name -> {sha256, bytes}
    runtime: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema": self.schema_version,
            "pack_id": self.pack_id,
            "as_of": self.as_of,
            "simulated": self.simulated,
            "unverified_rules": self.unverified_rules,
            "head": self.head,
            "chain_genesis": self.chain_genesis,
            "data_files": list(self.data_files),
            "runtime": dict(self.runtime),
            "questions": [q.to_dict() for q in self.questions],
            "rules": list(self.rules),
            "coverage": [c.to_dict() for c in self.coverage],
            "gaps": [g.to_dict() for g in self.gaps],
            "unmapped_qids": list(self.unmapped_qids),
            "events": [e.to_dict() for e in self.events],
            "artifacts": {
                name: {"sha256": meta["sha256"], "bytes": meta["bytes"]}
                for name, meta in sorted(self.artifacts.items())
            },
        }
