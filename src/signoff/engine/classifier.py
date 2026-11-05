"""Classifier — deterministic state labelling from source columns ONLY.

Every rule below is an explicit, hand-maintained mapping (provenance:
docs/01-DECISION-LOG.md D-011). `unlogged` is a first-class state produced
whenever a required human record is absent — it is never dropped and never
inferred away. No model is consulted at any point.
"""
from __future__ import annotations

from signoff.model.decision_event import DecisionEvent, State
from signoff.ingest.csv_normaliser import RawRow


def _rule_of(a: str, b: str) -> str:
    return f"{a}:{b}"


def classify(rows: list[RawRow]) -> list[DecisionEvent]:
    """Produce DecisionEvents (unclassified content is an error upstream)."""
    # Pass 1: collect the authorised-supervisor set from the roles export,
    # so escalation rows are validated against an actually declared roster.
    authorised_supervisors: set[str] = set()
    for row in rows:
        if row.kind == "rolespec_export":
            if (row.canonical.get("is_authorised_supervisor", "").lower() == "yes"
                    and row.canonical.get("assigned_to", "")):
                authorised_supervisors.add(row.canonical["assigned_to"].lower())

    events: list[DecisionEvent] = []
    for row in rows:
        c = row.canonical
        state, actor, action = _classify_row(row, authorised_supervisors)
        policy = row.policy_rule or "(none)"
        events.append(DecisionEvent(
            ts=row.ts,
            actor_identity=actor,
            action=action,
            state=state,
            source_file=row.source_file,
            source_row=row.source_row,
            policy_rule=policy,
        ))
    return events


def _classify_row(row: RawRow, supervisors: set[str]) -> tuple[State, str, str]:
    c = row.canonical
    kind = row.kind

    if kind == "qa_review":
        ai_action = c.get("ai_action", "")
        human_action = c.get("human_action", "").lower()
        reviewer = c.get("reviewer_id", "")
        ai_identity = c.get("ai_identity", "")
        action = _rule_of(f"{ai_action or 'none'}", human_action or "none")
        state_overrides = {
            "accepted": "human-approved",
            "edited": "gate-blocked",      # proposal blocked, replaced by human edit
        }
        if human_action in state_overrides and reviewer:
            if ai_identity:
                return state_overrides[human_action], reviewer, action
            return "unlogged", reviewer, action   # AI identity on the row unlogged
        if human_action in state_overrides and not reviewer:
            return "unlogged", "unknown", action   # review happened, reviewer unlogged
        if ai_action and not human_action:
            return "unlogged", "unknown", action   # proposal with no review record
        return "unlogged", "unknown", action

    if kind == "approval_events":
        decision = c.get("decision", "").lower()
        approver = c.get("approver_id", "")
        gate = c.get("gate", "")
        action = _rule_of(f"approval[{gate}]", decision)
        if decision == "approved" and approver:
            return "human-approved", approver, action
        if decision in ("blocked", "rejected") and approver:
            return "gate-blocked", approver, action
        if decision == "ai_proposed":
            return "AI-proposed", approver or "unknown", action
        return "unlogged", approver or "unknown", action

    if kind == "escalation_log":
        authorised = c.get("authorised", "").lower() == "yes"
        supervisor = c.get("supervisor_id", "")
        action = _rule_of(f"escalation[{ticket_of(c)}]", "authorised" if authorised else "not-authorised")
        if authorised and supervisor and supervisor.lower() in supervisors:
            return "escalated", supervisor, action
        return "unlogged", supervisor or "unknown", action

    if kind == "audit_events":
        etype = c.get("event_type", "").lower()
        actor = c.get("actor", "")
        action = _rule_of("audit", etype or "none")
        blocking = {"kill_switch", "access_revoked", "override_block"}
        approving = {"access_review", "retention_check", "pii_log_check", "monitoring_event"}
        if etype in blocking:
            return "gate-blocked", actor or "unknown", action
        if etype in approving:
            return "human-approved", actor or "unknown", action
        return "unlogged", actor or "unknown", action

    if kind == "rolespec_export":
        role = c.get("role", "")
        assigned = c.get("assigned_to", "")
        accountable = c.get("named_accountable", "")
        action = (_rule_of("role", role or "none")
                  + ";named_accountable=" + ("yes" if accountable else "no"))
        actor = accountable or assigned or "unknown"
        if assigned:
            return "human-approved", actor, action
        return "unlogged", "unknown", action

    if kind == "ai_inventory":
        row_type = c.get("row_type", "").lower()
        provider = c.get("provider_name", "")
        signed = c.get("signed_by", "")
        registered = c.get("registered_by", "")
        action = _rule_of(f"inventory[{row_type or '?'}]", provider)
        if row_type == "provider" and registered:
            return "human-approved", registered, action
        if row_type == "contract_term" and signed and c.get("clause", ""):
            return "human-approved", signed, action
        return "unlogged", signed or registered or "unknown", action

    if kind == "training_register":
        completed = c.get("completed", "").lower() == "yes"
        completer = c.get("completed_by", "")
        staff = c.get("staff_id", "")
        action = _rule_of(f"training[{c.get('module_name', '')}]", "yes" if completed else "no")
        if completed and completer:
            return "human-approved", completer, action
        return "unlogged", completer or "unknown", action

    if kind == "incident_register":
        within = c.get("notified_within_sla", "").lower()
        owner = c.get("owner", "")
        action = _rule_of(f"incident[{c.get('incident_id', '')}]", f"sla={within or 'unrecorded'}")
        if within == "yes" and owner:
            return "human-approved", owner, action
        return "unlogged", owner or "unknown", action

    raise AssertionError(f"unhandled kind {kind!r}")  # unreachable; registry-complete


def ticket_of(c: dict) -> str:
    return c.get("ticket_id", "") or "unlabelled"
