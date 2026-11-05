# Signoff — Handoff to Owner

This document lists the 7 decisions a human owner must make before producing any client-facing pack.

## 1. Sign Every Row in `OWNER/mapping-table.csv`

Each row needs `decided_by`, `date`, `verified=yes`. The tool refuses to build without signed rules.

## 2. Set `offer-and-pricing.md`, `company-and-tax.md`, `legal-review.md`

These three files contain the signed commercial terms that R-006 uses.

## 3. Replace `OWNER/oversight-statement.md` with the Real Signatory Details

The Oversight Statement is **blank-signature** by design. The owner must fill in the real signatory.

## 4. Choose Real Export CSVs (Input B)

The 8 kinds documented in `docs/QUESTIONNAIRE-PARSING.md`:
- `qa_review_export.csv`
- `approval_events.csv`
- `escalation_log.csv`
- `audit_events.csv`
- `rolespec_export.csv`
- `ai_inventory.csv`
- `training_register.csv`
- `incident_register.csv`

## 5. Choose Real Client Questionnaire (Input A)

CSV/DOCX/XLSX/TXT formats supported. Use `parse-questionnaire` to extract questions first.

## 6. Decide `--redact` Posture

`--redact` masks value columns while keeping IDs and timestamps. Choose per-client.

## 7. Confirm `docker run --network none` Runs in the Client Environment

The Docker image is multi-stage, non-root, `network_mode: none`.

---

*End of handoff document.*
