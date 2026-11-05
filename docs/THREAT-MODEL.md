# Signoff Threat Model

## Scope and trust boundary

Signoff is a local document builder. The executable and its pinned dependencies form the trusted computing base. Inputs are untrusted questionnaire files and CSV exports; outputs are files in the selected destination. The tool has no service, account, credential store, telemetry, or network dependency at runtime.

## Assets and threats

| Asset | Threat | Control and limitation |
|---|---|---|
| Questionnaire and exports | Accidental disclosure | Processing remains local; choose a protected input/output location. The tool does not encrypt files. |
| Mapping decisions | Unauthorised or accidental rule | Owner-only signed mapping table; it remains header-only in this repository. |
| Generated evidence pack | Undetected modification | Canonical SHA-256 chain and artifact manifest checked by `verify-pack`; hashes do not establish source authenticity. |
| Build environment | Dependency compromise | Runtime dependency set is small and pinned; installation integrity remains the operator's responsibility. |
| Output correctness | Guessing or unsupported claims | Unmapped questions stay `UNMAPPED`; gaps and limitations are disclosed. Human review remains necessary. |

## Attack surface

Parsers accept CSV, DOCX (ZIP/XML), TXT/Markdown and optional XLSX. They validate expected structure and fail closed on malformed or unexpected input. Output writing is staged to avoid partial packs. Run the offline scanner and tests before distributing a build. Docker is configured for non-root operation and can be run with `--network none`.

## Residual risks

Malicious files can still target Python or dependency vulnerabilities, consume excessive disk/CPU, or exploit the host's document viewers. Hash chains detect changes after construction, not fabricated or incomplete source records. Protect the machine and inspect outputs before sharing.
