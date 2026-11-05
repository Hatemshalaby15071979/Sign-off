"""CSV normaliser — turns Input B (a folder of the customer's CSV exports)
into raw, classifiable row records with full source traceability.

Contract (docs/DATA-CONTRACT.md):
- Every supported file kind has a hard-coded, explicit schema: required
  columns, optional columns and an alias table. Nothing is discovered by a
  model; a column name is either known or is an error.
- Missing required column -> fail closed, naming file AND column.
- Unknown column -> error, never a silent drop.
- Blank timestamps are an error (timestamps are never invented).
- Every row keeps `source_file` (relative path) + `source_row` (1-based line
  number including the header row) so an auditor can trace it back.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from signoff.errors import ParseError

# ---------------------------------------------------------------------------
# Hard-coded per-file-kind schemas. `aliases` map column name variants to one
# canonical name; the canonical name is what downstream code uses.
# ---------------------------------------------------------------------------
KIND_SPECS: dict[str, dict] = {
    "qa_review": {
        "match": re.compile(r"qa[\w\- ]*review", re.IGNORECASE),
        "description": "AI-assisted QA scoring sheet",
        "required": ["ts", "ai_action", "human_action", "reviewer_id", "agent_id"],
        "optional": ["qa_score", "ai_identity", "case_id" , "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "ai_action": ["ai_action", "ai_action_proposed", "ai_proposed_action", "auto_action", "ai_proposal"],
            "ai_identity": ["ai_identity", "ai_agent", "model_id", "ai_agent_identity"],
            "human_action": ["human_action", "review_action", "human_decision", "reviewer_action"],
            "reviewer_id": ["reviewer_id", "reviewer", "reviewedBy", "reviewed_by", "approved_by", "approver"],
            "agent_id": ["agent_id", "agent", "handled_by", "handledBy", "employee_id"],
            "qa_score": ["qa_score", "score"],
            "case_id": ["case_id", "review_id", "row_id"],
            "policy_rule": ["policy_rule", "rule", "policy", "gate"],
        },
    },
    "approval_events": {
        "match": re.compile(r"approval", re.IGNORECASE),
        "description": "human approval / AI-proposed gate log",
        "required": ["ts", "gate", "decision", "approver_id"],
        "optional": ["request_id", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "gate": ["gate", "request_type", "gate_type"],
            "decision": ["decision", "state", "result", "status"],
            "approver_id": ["approver_id", "approver", "approved_by", "reviewedBy", "reviewer", "reviewer_id", "actor"],
            "request_id": ["request_id", "req_id", "id"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "escalation_log": {
        "match": re.compile(r"escalation", re.IGNORECASE),
        "description": "escalation / override log",
        "required": ["ts", "escalated_by", "supervisor_id", "authorised"],
        "optional": ["ticket_id", "reason", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "escalated_by": ["escalated_by", "escalatedBy", "agent_id", "agent", "raised_by"],
            "supervisor_id": ["supervisor_id", "supervisor", "team_lead", "teamLead", "manager"],
            "authorised": ["authorised", "authorized", "is_authorised", "authorized_flag"],
            "ticket_id": ["ticket_id", "case_id", "id"],
            "reason": ["reason", "note", "comment"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "audit_events": {
        "match": re.compile(r"audit", re.IGNORECASE),
        "description": "audit events (kill switch, revocation, access review, retention)",
        "required": ["ts", "actor", "event_type"],
        "optional": ["detail", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "actor": ["actor", "performed_by", "performedBy", "user", "operator"],
            "event_type": ["event_type", "type", "event", "evenement"],
            "detail": ["detail", "details", "note", "description"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "rolespec_export": {
        "match": re.compile(r"role[\w\- ]*(spec|export)|roles?[\w\- ]*export", re.IGNORECASE),
        "description": "WFM / role specification export (least privilege, named accountability)",
        "required": ["ts", "role", "assigned_to", "is_authorised_supervisor"],
        "optional": ["named_accountable", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "role": ["role", "position", "job", "job_title"],
            "assigned_to": ["assigned_to", "assignedTo", "person", "owner", "assignee"],
            "is_authorised_supervisor": ["is_authorised_supervisor", "authorised_supervisor", "authorized_supervisor", "is_supervisor_authorised"],
            "named_accountable": ["named_accountable", "accountable", "accountable_named", "accountable_owner"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "ai_inventory": {
        "match": re.compile(r"ai[\w\- ]*inventory", re.IGNORECASE),
        "description": "AI inventory + contract-term register",
        "required": ["ts", "row_type", "provider_name"],
        "optional": ["clause", "signed_by", "registered_by", "model_name", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "row_type": ["row_type", "type", "kind", "entry_type"],
            "provider_name": ["provider_name", "provider", "vendor", "vendor_name"],
            "clause": ["clause", "contract_clause", "term"],
            "signed_by": ["signed_by", "signedBy", "countersigned_by"],
            "registered_by": ["registered_by", "registeredBy", "entered_by"],
            "model_name": ["model_name", "model", "service"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "training_register": {
        "match": re.compile(r"training", re.IGNORECASE),
        "description": "staff AI-training register",
        "required": ["ts", "staff_id", "module_name", "completed"],
        "optional": ["completed_by", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "staff_id": ["staff_id", "staff", "agent_id", "agent", "employee_id"],
            "module_name": ["module_name", "module", "course", "course_name", "module_title"],
            "completed": ["completed", "status", "state"],
            "completed_by": ["completed_by", "completedBy", "verifier", "certified_by"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
    "incident_register": {
        "match": re.compile(r"incident", re.IGNORECASE),
        "description": "incident register with notification SLA",
        "required": ["ts", "incident_id", "notified_within_sla", "owner"],
        "optional": ["sla_hours", "notified_by", "policy_rule"],
        "aliases": {
            "ts": ["ts", "timestamp", "time", "date", "created_at", "date_time", "datetime"],
            "incident_id": ["incident_id", "incident", "id"],
            "notified_within_sla": ["notified_within_sla", "within_sla", "notification_sla_met"],
            "owner": ["owner", "incident_owner", "responsible"],
            "sla_hours": ["sla_hours", "sla", "notification_sla_hours"],
            "notified_by": ["notified_by", "notifiedBy", "notifier"],
            "policy_rule": ["policy_rule", "rule", "policy"],
        },
    },
}

TS_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
    "%d/%m/%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S",
)


@dataclass
class RawRow:
    """One parsed export row, canonicalised, pre-classification."""
    kind: str
    canonical: dict[str, str]
    source_file: str
    source_row: int
    ts: str
    policy_rule: str
    extra_blanks: dict[str, str] = field(default_factory=dict)


def detect_kind(filename: str) -> Optional[str]:
    """Detect the file kind from its name against the hard-coded registry."""
    stem = Path(filename).name
    for kind, spec in KIND_SPECS.items():
        if spec["match"].search(stem):
            return kind
    return None


def parse_ts(raw_value: str, path: str, row: int) -> str:
    text = raw_value.strip()
    if not text:
        raise ParseError(f"{path} row {row}: blank timestamp in column "
                         f"'ts' — timestamps are never invented")
    for fmt in TS_FORMATS:
        try:
            parsed = dt.datetime.strptime(text, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc).isoformat(timespec="seconds")
        except ValueError:
            continue
    try:
        # 'Z' suffix is ISO-8601 UTC; normalise before fromisoformat
        iso_text = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
        parsed = dt.datetime.fromisoformat(iso_text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc).isoformat(timespec="seconds")
    except ValueError:
        raise ParseError(
            f"{path} row {row}: unparseable timestamp {raw_value!r} "
            f"(supported: ISO-8601, {', '.join(f.rstrip('Z') for f in TS_FORMATS if f != '%Y-%m-%dT%H:%M:%S%z')})")


def resolve_columns(header: list[str], kind: str, path: str) -> dict[str, Optional[str]]:
    """Map header names to canonical names; error on required-miss/unknowns."""
    spec = KIND_SPECS[kind]
    norm = {h.strip().lower(): h for h in header}
    resolved: dict[str, Optional[str]] = {}
    matched_header_ips: set[int] = set()
    wanted = spec["required"] + spec["optional"]
    for canonical in wanted:
        found: Optional[str] = None
        for alias in spec["aliases"][canonical]:
            h = norm.get(alias.lower())
            if h is not None and header.index(h) not in matched_header_ips:
                found = h
                break
        if found is not None:
            matched_header_ips.add(header.index(found))
            resolved[canonical] = found
        elif canonical in spec["required"]:
            raise ParseError(
                f"{path}: missing required column {canonical!r} for "
                f"{kind} rows (accepted names: {spec['aliases'][canonical]})")
        else:
            resolved[canonical] = None
    leftovers = [h for i, h in enumerate(header) if i not in matched_header_ips
                 and h.strip()]
    if leftovers:
        raise ParseError(
            f"{path}: unknown column(s) {leftovers} for {kind} — nothing is "
            "silently dropped; extend the documented schema instead")
    return resolved


def normalise_csv(path: Path, relative_to: Path | None = None) -> list[RawRow]:
    """Parse one export CSV into RawRow records. Fails closed on any problem."""
    rel = str(path.relative_to(relative_to)) if relative_to else path.name
    kind = detect_kind(path.name)
    if kind is None:
        raise ParseError(
            f"{rel}: unknown export file kind. Expected one of: "
            + ", ".join(sorted(KIND_SPECS))
            + " (file names must contain one of those keywords; rename a copy, never the original)")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ParseError(f"cannot read {rel}: {exc}") from exc
    try:
        table = list(csv.reader(text.splitlines()))
    except csv.Error as exc:
        raise ParseError(f"{rel}: malformed CSV ({exc})") from exc
    if not table:
        raise ParseError(f"{rel}: file is empty")
    header = table[0]
    resolved = resolve_columns(header, kind, rel)

    rows: list[RawRow] = []
    prev_line_num = 0
    for i, record in enumerate(table[1:], start=1):
        # 1-based source line including the header row; csv module line
        # counting is emulated: values cannot contain embedded newlines in
        # these exports, so the line number equals the record index + 1.
        line_no = i + 1  # +1 for the header row
        if line_no <= prev_line_num:
            line_no = prev_line_num + 1
        prev_line_num = line_no
        cells = {header[j]: record[j] for j in range(min(len(header), len(record)))}
        if not any(v.strip() for v in record):
            continue  # blank separator row
        col_of = lambda canon: resolved[canon]
        canonical: dict[str, str] = {}
        for canon in KIND_SPECS[kind]["required"] + KIND_SPECS[kind]["optional"]:
            header_name = col_of(canon)
            canonical[canon] = cells[header_name].strip() if header_name in cells and header_name is not None else ""
        ts = parse_ts(canonical["ts"], rel, line_no)
        rows.append(RawRow(
            kind=kind,
            canonical={c: canonical[c] for c in KIND_SPECS[kind]["required"] +
                       KIND_SPECS[kind]["optional"] if c != "ts"},
            source_file=rel,
            source_row=line_no,
            ts=ts,
            policy_rule=canonical.get("policy_rule", ""),
        ))
    return rows
