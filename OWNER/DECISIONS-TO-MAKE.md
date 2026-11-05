# Decision checklist for the owner (Hatem)

These are the decisions an autonomous agent must never make. Each entry names
the owner-only file, a conservative default already shipped in the code, and
whom to consult. Work top to bottom; items 1–4 gate real client work.

## 1. What counts as evidence — `OWNER/mapping-table.csv`
- Decision: for each question in a real client questionnaire, which file +
  columns + condition constitute proof.
- Conservative default shipped: header-only file; template examples all
  `decided_by=OWNER_PENDING`, `verified=no`.
- Hard rule: sign each rule with your own name in `decided_by` and a real
  date; set `verified=yes` only after you verified the columns named in
  `evidence_needed` exist in the actual export. Never let a model write a
  rule. Guide: `docs/MAPPING-TABLE-GUIDE.md`.

## 2. Real client questionnaires — `OWNER/questionnaires/`
- Decision: pick the first payer (a 50–500 seat BPO/CX outsourcer with an
  EU/UK bank, telco or insurer client), collect their actual AI
  questionnaire.
- Conservative default shipped: folder contains only instructions.
- No market data, no test count, no architecture work substitutes for a real
  client document.

## 3. Signed oversight statement — `OWNER/oversight-statement.md`
- Decision: name the accountable human (this is your product differentiator:
  a named, signed statement a machine will never produce).
- Conservative default shipped: `statement.py` renders a blank named-person
  field, signature line, date line. Signoff never signs.

## 4. Price and scope — `OWNER/offer-and-pricing.md`
- Conservative default shipped by the agent: **none**. The agent set no
  price, no terms, no T&A. Only the owner sets price.
- Note for the owner: the fixed-price, two-week, offline, no-integration
  assessment shape comes from the product strategy; the number is yours.

## 5. Company / tax — `OWNER/company-and-tax.md`
- A **local Egyptian accountant** must confirm: exported-services vs software
  product treatment, VAT registration threshold and the 30-day registration
  window after crossing it, invoicing format for foreign clients.
- The agent gives no tax advice, only the pointer.

## 6. Legal review — `OWNER/legal-review.md`
- NDA, liability cap, data-handling terms between you and the client. Draft
  nothing with an agent; have a lawyer review before first client contact.

## 7. Licence — `LICENSE`
- Conservative default shipped: proprietary, all rights reserved. Choosing
  MIT/Apache/etc. is an owner decision. If you sell to enterprises, the
  proprietary default is usually the safe start.

## 8. First 15 discovery calls, first invoice, first signed pack
- See `docs/03-HANDOFF-TO-OWNER.md` steps 1–5. These cannot be automated and
  no amount of code, docs, or tests substitutes for them.
