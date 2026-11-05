# Limitations

- Signoff does not authenticate source CSVs or prove their completeness. A valid hash chain proves internal consistency of the generated pack only.
- Coverage percentages describe the configured evidence patterns, supplied records and 90-day window. Missing exports can produce gaps or no denominator; they do not prove a control is absent or present in practice.
- The software does not make legal, regulatory, safety, or high-risk classification decisions and does not certify compliance.
- A mapping table is a human business decision. The program cannot determine whether a rule is substantively correct or authorised.
- Questionnaire parsing is structural extraction. It does not resolve ambiguity in question meaning or contractual context.
- XLSX parsing requires installing the optional `[xlsx]` extra. Other formats are handled without that extra.
- Hashes are not digital signatures, and the Oversight Statement intentionally has an unsigned signature block.
- Demo fixtures are synthetic and watermarked. They are never client evidence.
- Local filesystem permissions, backups, malware protection and secure transfer are the operator's responsibility.
