# Control Mapping

This document maps product safeguards to the evidence-pack behavior. It is an implementation aid, not a certification or legal opinion.

| Control objective | Signoff behavior | Evidence / limit |
|---|---|---|
| Trace each answer to a human-approved rule | Requires owner-decided mapping rules; unmatched questions remain `UNMAPPED` | Mapping table and answer CSV; this repo's owner table is intentionally header-only. |
| Preserve an audit trail | Hash-chained decision events and artifact digests | `pack.json`; does not prove source records are authentic. |
| Show evidence coverage and missing records | Explicit denominators, percentages and gap list | Coverage reflects supplied exports and configured period only. |
| Keep human oversight with people | Blank-signature Oversight Statement; no automated signature | A human must review and sign where appropriate. |
| Disclose synthetic examples | Demo artifacts contain `SIMULATION_DISCLOSURE` | Demo output is not client evidence. |
| Operate without network access | No runtime network client in evidence path; Docker can use `--network none` | See `OFFLINE-GUARANTEE.md`; host/runtime integrity remains outside scope. |

No control mapping here establishes regulatory compliance or that a customer's AI system satisfies a control.
