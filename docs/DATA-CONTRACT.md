# Signoff — Data Contract

This document defines the complete, machine-readable specification of every CSV column, every hash input, every artifact schema, and the injected clock (`--as-of`).

## Input A: Client Questionnaire

The client provides a questionnaire in one of these formats:
- CSV (comma-separated values)
- DOCX (Microsoft Word)
- XLSX (Excel)
- TXT (plain text)

### CSV Format Requirements

| Column | Description | Required |
|--------|-------------|----------|
| `qid` | Question ID (unique identifier) | Yes |
| `exact_text` | Exact text of the question as presented to the client | Yes |
| `answer_type` | Type of answer expected (e.g., "text", "multiple_choice", "date") | Yes |
| `qid_source` | Source of the question (e.g., "client_provided", "internal") | Yes |
| `source_path` | Path to the original file containing this question | Yes |
| `order` | Order of the question in the questionnaire | Yes |

### XLSX Format Requirements

- Must have a sheet named "Questions"
- Each row represents one question
- Must include columns matching the CSV format above

### DOCX/TXT Format Requirements

- Must be parsed to extract questions with the same fields as CSV

## Input B: CSV Exports

The client provides 8 types of CSV exports (Input B), each with specific column requirements:

### 1. `qa_review_export.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `qid` | Question ID | Yes |
| `exact_text` | Exact text of the question | Yes |
| `answer_type` | Type of answer expected | Yes |
| `ai_proposed_action` | AI-proposed action or response | Yes |
| `ai_confidence` | Confidence score (0.0-1.0) | Yes |
| `reviewer_id` | ID of the human reviewer | Yes |
| `review_timestamp` | Timestamp of review (ISO format) | Yes |
| `status` | Review status ("pending", "completed", "rejected") | Yes |

### 2. `approval_events.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `event_id` | Event ID | Yes |
| `qid` | Question ID | Yes |
| `action` | Action taken (e.g., "approved", "rejected") | Yes |
| `actor` | Actor who took the action | Yes |
| `timestamp` | Timestamp of action (ISO format) | Yes |
| `evidence_id` | ID of evidence supporting the action | Yes |

### 3. `escalation_log.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `event_id` | Event ID | Yes |
| `qid` | Question ID | Yes |
| `escalation_level` | Level of escalation (e.g., "1", "2", "3") | Yes |
| `escalated_by` | Person who escalated | Yes |
| `timestamp` | Timestamp of escalation (ISO format) | Yes |
| `resolution_status` | Resolution status ("pending", "resolved") | Yes |

### 4. `audit_events.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `event_id` | Event ID | Yes |
| `qid` | Question ID | Yes |
| `action` | Action taken (e.g., "reviewed", "verified") | Yes |
| `actor` | Actor who took the action | Yes |
| `timestamp` | Timestamp of action (ISO format) | Yes |
| `evidence_id` | ID of evidence supporting the action | Yes |

### 5. `rolespec_export.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `rule_id` | Rule ID | Yes |
| `pattern_id` | Pattern ID | Yes |
| `source_qid` | Question ID | Yes |
| `question` | Question text | Yes |
| `answer_type` | Answer type | Yes |
| `evidence_needed` | Evidence required | Yes |
| `where_to_find_it` | Where to find evidence | Yes |
| `if_missing_gap` | What constitutes a gap | Yes |
| `decided_by` | Person who decided | Yes |
| `date` | Decision date | Yes |
| `verified` | "yes" if verified | Yes |

### 6. `ai_inventory.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `provider_id` | Provider ID | Yes |
| `provider_name` | Provider name | Yes |
| `contact_email` | Contact email | Yes |
| `contract_expiration` | Contract expiration date | Yes |
| `signed_contract` | "yes" if signed | Yes |

### 7. `training_register.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `employee_id` | Employee ID | Yes |
| `name` | Employee name | Yes |
| `role` | Employee role | Yes |
| `training_date` | Date of training completion | Yes |
| `trainer_id` | ID of trainer | Yes |
| `certification` | Certification achieved | Yes |
| `evidence_id` | ID of training evidence | Yes |

### 8. `incident_register.csv`

| Column | Description | Required |
|--------|-------------|----------|
| `incident_id` | Incident ID | Yes |
| `qid` | Question ID | Yes |
| `description` | Description of incident | Yes |
| `severity` | Severity level (e.g., "low", "medium", "high") | Yes |
| `reported_by` | Person who reported | Yes |
| `timestamp` | Timestamp of report (ISO format) | Yes |
| `resolution_status` | Resolution status ("pending", "resolved") | Yes |
| `resolution_timestamp` | Timestamp of resolution (ISO format) | Yes |
| `evidence_id` | ID of incident evidence | Yes |

## Hash Chain Specification

### Chain Genesis

```
signoff-chain-genesis: + parse_instant(as_of).isoformat()
```

### Chain Structure

Each event in the chain contains:

- `event_id` (UUID)
- `timestamp` (ISO 8601 format)
- `event_type` (e.g., "questionnaire_parsed", "mapping_applied", "coverage_calculated")
- `data` (JSON-serializable object)
- `prev_hash` (SHA-256 of previous event's canonical JSON)
- `current_hash` (SHA-256 of current event's canonical JSON)

### Hash Chain Validation

The verifier checks:
- Chain head matches genesis
- Each event's `prev_hash` matches previous event's `current_hash`
- No missing events in the chain
- All artifacts match their digests in `pack.json`

## Coverage Engine

### EVIDENCE_SPECS

| Pattern ID | Kind | Denominator | Purpose |
|------------|------|-------------|---------|
| QA-HUMAN-REVIEW | rows | QA rows with AI-proposed action | Human review of AI QA |
| KILL-SWITCH-REVOKE | fixed | 1 | Kill switch / revocation exercise |
| AGENT-IDENTITY-LOG | rows | AI-proposed decisions | Agent identity logged |
| LEAST-PRIV-QUARTERLY | fixed | 1 | Access review logged |
| AI-INVENTORY-PROVIDERS | fixed | 1 | Registered provider entry |
| CONTRACT-NO-TRAINING-DOC | fixed | 1 | Signed contract term |
| ESCALATION-AUTH-SUPERVISOR | rows | escalation rows | Authorised supervisor only |
| ACCOUNTABILITY-STATEMENT | fixed | 1 | Named accountable record |
| OVERSIGHT-METRICS | pre-pass | accepted+edited QA pairs | Monitoring data |
| TRAINING-RECORDS | rows | training rows | Completed staff training |
| INCIDENT-SLA | rows | incident rows | SLA notification |
| RETENTION-PII-LOGGING | fixed | 1 | Retention/PII check |

### Coverage Window

- Start: `--as-of` date
- End: `--as-of` date minus 90 days (inclusive)
- Events outside window are excluded from numerator AND denominator
- Zero denominator = "N/A (no events in period)" — never 100%

## Verification Requirements

The `verify_pack` tool checks:
1. Replay chain integrity
2. Artifact digest matches computed digest
3. `SIMULATION_DISCLOSURE` watermark present in demo artifacts

## Security & Threat Model

- **TCB**: Signoff itself is the Trusted Computing Base
- **No credentials**: No API keys, no secrets stored
- **No network**: `network_mode: none` in Docker
- **Non-root**: Docker container runs as non-root user
- **No telemetry**: No data sent to external services
- **Tamper detection**: `verify_pack` detects byte mutations, event body changes, genesis changes, etc.

*End of data contract.*