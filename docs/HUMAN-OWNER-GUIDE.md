# Human Owner Guide

Signoff is a document factory. A human owner must decide what evidence means before any client-facing use.

1. Review `OWNER/DECISIONS-TO-MAKE.md` and complete the owner-only company, pricing, legal and oversight decisions.
2. For each questionnaire question, create an explicit mapping rule. Record the deciding person, date and verification; never rely on a guessed match.
3. Validate the completed mapping table with `python -m signoff validate-mapping --mapping OWNER/mapping-table.csv`.
4. Select a client questionnaire and the exact customer exports to process. Keep data access limited to the intended files.
5. Build into a new output directory, review every answer, evidence reference, gap and disclosure, then run `verify-pack`.
6. Have the accountable human review and sign the Oversight Statement. Do not treat a generated blank statement as approval.
7. Share only after confirming the pack is appropriate for its recipient and contains no unintended data.

The repository's `OWNER/mapping-table.csv` must remain header-only until the human owner supplies decisions. Demo mappings and synthetic fixtures are examples only.
