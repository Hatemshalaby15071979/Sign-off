# Security Policy

Signoff is an offline, deterministic evidence-pack builder. It makes no network
calls, holds no credentials, uses no LLM in the evidence path, and writes only
to an operator-specified output directory. The full threat model, assets, and
mitigations are in [`docs/SECURITY.md`](docs/SECURITY.md); limitations are in
[`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.1.0   | Yes — pre-production candidate; owner decisions (licence, client use) are pending, see [`OWNER/DECISIONS-TO-MAKE.md`](OWNER/DECISIONS-TO-MAKE.md) |

## Reporting a vulnerability

**Reporting contact: to be filled in by the owner.** There is no monitored
security mailbox or private reporting channel in this repository yet; do not
send vulnerability reports to any address guessed from this file.

Until the owner publishes a contact, please:

1. Do not open a public issue containing exploit details.
2. Do not include real client data, credentials, or personal data in any report.
3. The owner will add a private reporting channel (e.g. GitHub Private
   Vulnerability Reporting) before any public release; re-check this file then.

Signoff output is a document factory, not a compliance certification. Hash
chains and manifests establish internal consistency of a generated pack, not
source authenticity or real-world control effectiveness.
