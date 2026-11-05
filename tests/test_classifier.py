"""Classifier: state labelling from source columns ONLY; unlogged is a state."""
from __future__ import annotations

from tests.conftest import FIXTURES

from signoff.engine.classifier import classify
from signoff.ingest.csv_normaliser import normalise_csv


def classify_export(name: str):
    return classify(normalise_csv(FIXTURES / name, relative_to=FIXTURES))


def states_of(name, field="state"):
    return [getattr(e, field) for e in classify_export(name)]


def rows(name):
    return classify_export(name)


# ------------------------------------------------------------------ qa review
def test_qa_accepted_becomes_human_approved():
    qa = rows("qa_review_export.csv")
    r2 = qa[0]  # C-1001 accepted by Reviewer_A
    assert r2.state == "human-approved"
    assert r2.actor_identity == "Reviewer_A"
    assert r2.action == "auto_score:accepted"


def test_qa_edited_becomes_gate_blocked():
    qa = rows("qa_review_export.csv")
    assert qa[1].state == "gate-blocked"
    assert qa[1].actor_identity == "Reviewer_B"


def test_qa_missing_ai_identity_is_unlogged():
    qa = rows("qa_review_export.csv")
    assert qa[5].state == "unlogged"   # C-1006: reviewer present, ai_identity blank


def test_qa_no_review_record_is_unlogged():
    qa = rows("qa_review_export.csv")
    assert qa[4].state == "unlogged"   # C-1005: no human_action, no reviewer

# --------------------------------------------------------------- approval gate
def test_approval_blocked_and_approved():
    ap = rows("approval_events.csv")
    assert [e.state for e in ap] == ["AI-proposed", "gate-blocked", "human-approved"]
    assert ap[0].actor_identity == "unknown"    # ai_proposed with no approver
    assert ap[1].actor_identity == "Supervisor_2"


def test_approval_unknown_decision_is_unlogged():
    from signoff.engine.classifier import _classify_row

    state, actor, _ = _classify_row(
        type("R", (), {"kind": "approval_events",
                       "canonical": {"decision": "pending", "approver_id": "A",
                                     "gate": "g"},
                       "policy_rule": "", "source_file": "f", "source_row": 1,
                       "ts": "2026-01-01T00:00:00+00:00"})(), frozenset())
    assert state == "unlogged" and actor == "A"

# --------------------------------------------------------------- escalation
def test_escalation_only_authorised_roster_may_escalate():
    # roster + escalation log together, exactly as a build supplies them
    rows = (normalise_csv(FIXTURES / "rolespec_export.csv", relative_to=FIXTURES)
            + normalise_csv(FIXTURES / "escalation_log.csv", relative_to=FIXTURES))
    events = classify(rows)
    role = [e for e in events if e.source_file == "rolespec_export.csv"]
    roster = {e.actor_identity.lower() for e in role
              if e.action.endswith("named_accountable=no")}
    esc = [e for e in events if e.source_file == "escalation_log.csv"]
    escalated = [e.actor_identity for e in esc if e.state == "escalated"]
    # Supervisor_1 + Supervisor_3 are on the roster; TeamLead_9 is not
    assert escalated == ["Supervisor_1", "Supervisor_3"]
    assert all(a.lower() in roster for a in escalated)
    assert esc[1].state == "unlogged"   # T-2: TeamLead_9 not authorised
    assert "not-authorised" in esc[1].action

# --------------------------------------------------------------- audit events
def test_audit_event_types_map_to_states():
    aud = rows("audit_events.csv")
    assert aud[0].state == "gate-blocked"       # kill_switch
    assert aud[1].state == "gate-blocked"       # access_revoked
    assert aud[2].state == "human-approved"     # pii_log_check
    assert aud[2].action == "audit:pii_log_check"


def test_audit_unknown_event_type_is_unlogged():
    from signoff.engine.classifier import _classify_row

    state, actor, _ = _classify_row(
        type("R", (), {"kind": "audit_events",
                       "canonical": {"event_type": "mystery", "actor": "X"},
                       "policy_rule": "", "source_file": "f", "source_row": 1,
                       "ts": "x"})(), frozenset())
    assert state == "unlogged" and actor == "X"

# --------------------------------------------------------------- role export
def test_rolespec_names_accountable_and_roster_flags():
    role = rows("rolespec_export.csv")
    assert role[0].state == "human-approved"
    assert role[0].actor_identity == "Demo_Exec_Signatory"
    assert ";named_accountable=yes" in role[0].action
    assert "named_accountable=no" in role[3].action

# --------------------------------------------------------------- ai inventory
def test_contract_term_requires_clause_and_signer():
    inv = rows("ai_inventory.csv")
    assert inv[0].state == "human-approved"     # provider registered by a name
    assert inv[1].state == "human-approved"     # signed contract term with clause
    assert inv[1].action == "inventory[contract_term]:Client_Demo_Bank"


def test_inventory_row_without_registration_is_unlogged():
    from signoff.engine.classifier import _classify_row

    state, _, _ = _classify_row(
        type("R", (), {"kind": "ai_inventory",
                       "canonical": {"row_type": "provider",
                                     "provider_name": "V", "registered_by": "",
                                     "signed_by": "", "clause": ""},
                       "policy_rule": "", "source_file": "f", "source_row": 1,
                       "ts": "x"})(), frozenset())
    assert state == "unlogged"

# ------------------------------------------------------------------ training
def test_training_unverified_row_is_unlogged():
    trn = rows("training_register.csv")
    assert [e.state for e in trn] == ["human-approved", "human-approved", "unlogged"]
    assert trn[0].actor_identity == "Trainer_1"

# ------------------------------------------------------------------ incident
def test_incident_sla_miss_is_unlogged_not_dropped():
    inc = rows("incident_register.csv")
    assert inc[0].state == "human-approved"
    assert inc[1].state == "unlogged"     # SLA missed; stays in the pack
    assert "sla=no" in inc[1].action
