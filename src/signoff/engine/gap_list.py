"""Gap list — the most valuable page: what a client audit will find missing.

One row per missing proof, with rule_id, source_qid, reason (quantified),
affected source files, row counts, and a plain-text suggested remediation.
No legal claims anywhere. Deterministic in (coverage, events, unmapped).
"""
from __future__ import annotations

from signoff.ingest.csv_normaliser import detect_kind
from signoff.model.evidence_pack import CoverageResult, Gap

# Every pattern's narrative "where the evidence should live" file kind.
KIND_FOR_PATTERN: dict[str, str] = {
    "QA-HUMAN-REVIEW": "qa_review",
    "KILL-SWITCH-REVOKE": "audit_events",
    "AGENT-IDENTITY-LOG": "approval_events",
    "LEAST-PRIV-QUARTERLY": "audit_events",
    "AI-INVENTORY-PROVIDERS": "ai_inventory",
    "CONTRACT-NO-TRAINING-DOC": "ai_inventory",
    "ESCALATION-AUTH-SUPERVISOR": "escalation_log",
    "ACCOUNTABILITY-STATEMENT": "rolespec_export",
    "OVERSIGHT-METRICS": "qa_review",
    "TRAINING-RECORDS": "training_register",
    "INCIDENT-SLA": "incident_register",
    "RETENTION-PII-LOGGING": "audit_events",
}

_COV_REMEDIATION = ("Collect the missing records named above for the coverage "
                    "window and re-run `signoff build` with the same signed "
                    "mapping table.")

_UNMAPPED_REMEDIATION = (
    "Add a signed rule to the mapping table for this qid "
    "(docs/MAPPING-TABLE-GUIDE.md), or answer the client manually outside "
    "Signoff. Do not paraphrase an answer into the pack.")


def gap_header() -> list[str]:
    return ["rule_id", "source_qid", "reason", "affected_source_files",
            "affected_row_count", "suggested_remediation"]


def build_gaps(
    coverage: list[CoverageResult],
    events: list,
    unmapped: list[tuple[str, str]],
    questionnaire_rel: str,
) -> list[Gap]:
    """Coverage below 100% plus questions no signed rule covers (UNMAPPED)."""
    files_by_kind: dict[str, set[str]] = {}
    for ev in events:
        if not ev.event_id:
            continue
        kind = detect_kind(ev.source_file)
        if kind:
            files_by_kind.setdefault(kind, set()).add(ev.source_file)

    gaps: list[Gap] = []
    for c in coverage:
        if c.pct is None or c.pct >= 100.0:
            continue
        affected = sorted(files_by_kind.get(KIND_FOR_PATTERN.get(c.pattern_id, ""), set()))
        gaps.append(Gap(
            rule_id=c.rule_id,
            source_qid=c.source_qid,
            reason=(f"{c.pattern_id}: coverage {c.matched}/{c.expected} "
                    f"({c.denominator_label})"),
            affected_source_files=affected,
            affected_row_count=c.expected - c.matched,
            suggested_remediation=_COV_REMEDIATION,
        ))

    for qid, exact_text in unmapped:
        short = exact_text[:60] + ("…" if len(exact_text) > 60 else "")
        gaps.append(Gap(
            rule_id="-",
            source_qid=qid,
            reason=(f"UNMAPPED: no signed rule maps question '{qid}' "
                    f"('{short}'); no answer may be generated"),
            affected_source_files=[questionnaire_rel],
            affected_row_count=0,
            suggested_remediation=_UNMAPPED_REMEDIATION,
        ))
    return gaps
