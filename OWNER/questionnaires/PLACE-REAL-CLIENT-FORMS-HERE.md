Place REAL client AI/automation questionnaires in this folder.

What belongs here
-----------------
The actual procurement document a client (or their platform) sent the
customer: an AI vendor questionnaire, a client audit form, a due-diligence
checklist. Any of `.csv`, `.docx`, `.xlsx`, `.txt`, `.md` — the parsers
accept all five.

Why a real form is irreplaceable
--------------------------------
The mapping table is keyed to the client's own `Ref`/question IDs and the
client's exact question wording. A questionnaire you write yourself proves
nothing about what this client will actually ask, and handling a synthetic
form as if it were a client document would be exactly the "invented evidence"
failure the product exists to prevent. The trigger that pays you is *their*
document with *their* due date — collect it before promising a build.

How to handle a real form here
------------------------------
1. Copy the file as received; do not edit the client's wording.
2. If it contains client-confidential fields (client name, seat numbers,
   contacts), keep the file locally and never commit it — `OWNER/questionnaires/*`
   is git-ignored except this README, and excluded from Docker builds.
3. For your own local notes, use the relative path
   `OWNER/questionnaires/<client-demo-name>.<ext>` so no absolute host path
   ever enters an artifact.
4. When filling the mapping table, copy question text **exactly** (see
   `docs/MAPPING-TABLE-GUIDE.md`) — never paraphrase a question.
