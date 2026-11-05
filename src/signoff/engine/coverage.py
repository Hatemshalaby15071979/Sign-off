"""Coverage engine — evidence coverage % per questionnaire item.

Every percentage carries an explicit denominator. A zero denominator is
reported as `N/A (no events in period)`, never 100%.

Coverage window: the 90 days ending at the injected `--as-of` instant
(both ends inclusive). Events outside the window are excluded from both
numerator and denominator.

The per-pattern evidence requirements below are hand-written engineering
constants (decision log D-012): they state what the signed rules in the
mapping table must be able to point at. The mapping table remains the
authority for WHICH patterns a question needs; these specs define how a
pattern's evidence is counted. Deterministic function of (events, as_of).
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass

from signoff.config import COVERAGE_WINDOW_DAYS
from signoff.errors import ConfigError
from signoff.model.decision_event import DecisionEvent
from signoff.model.evidence_pack import CoverageResult
from signoff.util.clock import parse_instant
from signoff.ingest.csv_normaliser import detect_kind

NA_LABEL = "N/A (no events in period)"


def _part_a(action: str) -> str:
    return action.split(":", 1)[0]


def _part_b(action: str) -> str:
    return action.split(":", 1)[1] if ":" in action else ""


def _kind_is(ev: DecisionEvent, kind: str) -> bool:
    return detect_kind(ev.source_file) == kind


@dataclass(frozen=True)
class EvidenceSpec:
    pattern_id: str
    objective: str            # human-readable: what this pattern proves
    denominator_kind: str     # "rows" | "fixed"
    matcher: Callable[[DecisionEvent], bool]
    premise: Callable[[DecisionEvent], bool] | None = None   # rows kind
    fixed_expected: int = 1   # fixed kind
    denominator_label: str = ""


def _qa_ai_premise(ev: DecisionEvent) -> bool:
    return _kind_is(ev, "qa_review") and _part_a(ev.action) != "none"


EVIDENCE_SPECS: dict[str, EvidenceSpec] = {
    "QA-HUMAN-REVIEW": EvidenceSpec(
        pattern_id="QA-HUMAN-REVIEW",
        objective="every AI-proposed QA action has a recorded human review by a named reviewer",
        denominator_kind="rows",
        premise=_qa_ai_premise,
        matcher=lambda ev: ev.state in ("human-approved", "gate-blocked"),
        denominator_label="QA rows with an AI-proposed action in the coverage window",
    ),
    "KILL-SWITCH-REVOKE": EvidenceSpec(
        pattern_id="KILL-SWITCH-REVOKE",
        objective="at least one exercised kill switch or access revocation is logged",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "audit_events")
        and ev.action.startswith("audit:")
        and _part_b(ev.action) in ("kill_switch", "access_revoked"),
        fixed_expected=1,
        denominator_label="1 required kill-switch / revocation exercise in the coverage window",
    ),
    "AGENT-IDENTITY-LOG": EvidenceSpec(
        pattern_id="AGENT-IDENTITY-LOG",
        objective="every AI-proposed decision names the agent identity that produced it",
        denominator_kind="rows",
        premise=lambda ev: ev.state == "AI-proposed",
        matcher=lambda ev: ev.actor_identity not in ("", "unknown"),
        denominator_label="AI-proposed decisions in the coverage window",
    ),
    "LEAST-PRIV-QUARTERLY": EvidenceSpec(
        pattern_id="LEAST-PRIV-QUARTERLY",
        objective="at least one logged access review exists",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "audit_events") and ev.action == "audit:access_review",
        fixed_expected=1,
        denominator_label="1 required access review in the coverage window",
    ),
    "AI-INVENTORY-PROVIDERS": EvidenceSpec(
        pattern_id="AI-INVENTORY-PROVIDERS",
        objective="at least one provider entry, registered by a named person",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "ai_inventory")
        and ev.action.startswith("inventory[provider]")
        and ev.state == "human-approved",
        fixed_expected=1,
        denominator_label="1 required registered provider entry in the coverage window",
    ),
    "CONTRACT-NO-TRAINING-DOC": EvidenceSpec(
        pattern_id="CONTRACT-NO-TRAINING-DOC",
        objective="a data-use contract term exists: signed by a named person (a document, not a log)",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "ai_inventory")
        and ev.action.startswith("inventory[contract_term]")
        and ev.state == "human-approved",
        fixed_expected=1,
        denominator_label="1 required signed data-use contract term in the coverage window",
    ),
    "ESCALATION-AUTH-SUPERVISOR": EvidenceSpec(
        pattern_id="ESCALATION-AUTH-SUPERVISOR",
        objective="escalations go ONLY to an authorised supervisor on the declared roster",
        denominator_kind="rows",
        premise=lambda ev: _kind_is(ev, "escalation_log"),
        matcher=lambda ev: ev.state == "escalated",
        denominator_label="escalation rows in the coverage window",
    ),
    "ACCOUNTABILITY-STATEMENT": EvidenceSpec(
        pattern_id="ACCOUNTABILITY-STATEMENT",
        objective="a named accountable person is recorded",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "rolespec_export")
        and ";named_accountable=yes" in ev.action,
        fixed_expected=1,
        denominator_label="1 required named-accountable record in the coverage window",
    ),
    "OVERSIGHT-METRICS": EvidenceSpec(
        pattern_id="OVERSIGHT-METRICS",
        objective="accepted-vs-edited monitoring data is being collected",
        denominator_kind="fixed",
        matcher=lambda ev: True,   # evaluated as a pre-pass; see compute_coverage
        fixed_expected=1,
        denominator_label="accepted-and-edited QA pairs present in the coverage window",
    ),
    "TRAINING-RECORDS": EvidenceSpec(
        pattern_id="TRAINING-RECORDS",
        objective="completed, verified staff AI-training records exist",
        denominator_kind="rows",
        premise=lambda ev: _kind_is(ev, "training_register"),
        matcher=lambda ev: ev.state == "human-approved",
        denominator_label="training rows in the coverage window",
    ),
    "INCIDENT-SLA": EvidenceSpec(
        pattern_id="INCIDENT-SLA",
        objective="incident notifications within SLA are recorded with a named owner",
        denominator_kind="rows",
        premise=lambda ev: _kind_is(ev, "incident_register"),
        matcher=lambda ev: ev.state == "human-approved",
        denominator_label="incident rows in the coverage window",
    ),
    "RETENTION-PII-LOGGING": EvidenceSpec(
        pattern_id="RETENTION-PII-LOGGING",
        objective="at least one retention / PII logging check is logged",
        denominator_kind="fixed",
        matcher=lambda ev: _kind_is(ev, "audit_events")
        and _part_b(ev.action) in ("retention_check", "pii_log_check"),
        fixed_expected=1,
        denominator_label="1 required retention / PII-logging check in the coverage window",
    ),
}


def compute_coverage(
    rules_by_pattern: dict[str, list],
    events: list[DecisionEvent],
    as_of: str,
) -> list[CoverageResult]:
    """One CoverageResult per (pattern, rule) pair; deterministic."""
    window_end = parse_instant(as_of)
    window_start = window_end - dt.timedelta(days=COVERAGE_WINDOW_DAYS)
    in_window = [e for e in events
                 if window_start <= parse_instant(e.ts) <= window_end]
    in_window.sort(key=lambda e: e.identity_key)

    accepted = any(_kind_is(e, "qa_review") and _part_b(e.action) == "accepted"
                   for e in in_window)
    edited = any(_kind_is(e, "qa_review") and _part_b(e.action) == "edited"
                 for e in in_window)
    monitor_ok = accepted and edited

    results: list[CoverageResult] = []
    for pattern_id, rules in sorted(rules_by_pattern.items()):
        spec = EVIDENCE_SPECS.get(pattern_id)
        if spec is None:
            raise ConfigError(
                f"pattern {pattern_id!r} has no evidence spec; "
                "add it to EVIDENCE_SPECS with an owner decision")
        if spec.denominator_kind == "fixed":
            matched_events = [e for e in in_window if spec.matcher(e)]
            matched = min(len(matched_events), spec.fixed_expected)
            expected = spec.fixed_expected
            label = spec.denominator_label
        else:
            assert spec.premise is not None
            premise = [e for e in in_window if spec.premise(e)]
            matched_events = [e for e in premise if spec.matcher(e)]
            matched = len(matched_events)
            expected = len(premise)
            label = f"{expected} × {spec.denominator_label}"
        if pattern_id == "OVERSIGHT-METRICS":
            matched = 1 if monitor_ok else 0
            matched_events = list(in_window) if monitor_ok else []
        pct = (round(matched / expected * 100, 1) if expected else None)
        for rule in rules:
            results.append(CoverageResult(
                pattern_id=pattern_id,
                rule_id=rule.rule_id,
                source_qid=rule.source_qid,
                matched=int(matched),
                expected=int(expected),
                denominator_label=label,
                pct=pct,
                matched_events=list(matched_events),
            ))
    return results
