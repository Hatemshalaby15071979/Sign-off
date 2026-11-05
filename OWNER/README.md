# OWNER folder — this is Hatem's folder

The `OWNER/` directory is the human boundary of this project. Every file in
here is either (a) a placeholder the owner (Hatem) must fill personally, or
(b) an explanation written by the build agent to make the boundary clear.
No autonomous agent ever writes owner content.

## What belongs to the owner only

| File / folder                            | Belongs to | Why it cannot be automated                                        |
| ---------------------------------------- | ---------- | ----------------------------------------------------------------- |
| `mapping-table.csv`                      | Owner      | Deciding what counts as evidence for each question is a human, dated, signed judgement. The validator refuses blank `decided_by`, blank `date`, or `verified != yes`. |
| `mapping-table.template.csv`             | Owner      | Example rows marked `OWNER_PENDING` / `verified=no`; examples, not approvals. |
| `questionnaires/`                        | Owner      | Real client questionnaires are real client documents. Fabricating one would be inventing evidence. |
| `oversight-statement.md`                 | Owner      | The signed statement needs a real named accountable human and a real signature. Signoff never signs. |
| `offer-and-pricing.md`                   | Owner      | Only the owner sets price and commercial terms.                   |
| `company-and-tax.md`                     | Owner      | Egypt entity, VAT registration, exported-services treatment — must be confirmed by a local accountant. |
| `legal-review.md`                        | Owner      | NDA / liability / data-handling terms require real legal review.  |
| `real-data/`                             | Owner      | Real client CSV exports are used on the customer's machine only. Never commit them. |

## Why the boundary exists

The product's promise is: *evidence is reconstructed from your records, and
every judgement about what counts as evidence is traceable to a named human,
a rule ID, and a date.* If any of those judgements were made by a model or an
agent, the pack could never be defended in front of an auditor. The rule in
the codebase is: `decided_by` is always a person, and the machine never
decides what counts as evidence.

## Three files the agent DID write, in full

- `OWNER/README.md` (this file) — explains the boundary.
- `OWNER/DECISIONS-TO-MAKE.md` — the owner's decision checklist with
  conservative defaults.
- `OWNER/real-data/README.md` — rules for handling real client data.

Everything else under `OWNER/` starts with the marker line
`<<<OWNER — DO NOT AUTO-FILL — HUMAN DECISION REQUIRED>>>` and is untouched
placeholder until the owner writes it.
