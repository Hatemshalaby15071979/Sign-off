# Signoff — Security

## Threat Model

Signoff itself is the **Trusted Computing Base (TCB)** — the only code that runs on the customer's machine.

### Assets Protected

1. **Client questionnaire data** (Input A) — potentially sensitive
2. **Customer export data** (Input B) — internal operational data
3. **Mapping table** (`OWNER/mapping-table.csv`) — signed business decisions
4. **Evidence pack artifacts** — delivered to client

### Threats

| Threat | Mitigation |
|--------|------------|
| Supply chain compromise | Pinned deps, no network, stdlib-only |
| Data exfiltration | No network calls; `network_mode: none` |
| Tampering with pack | Hash chain + `verify-pack` |
| Guessing / hallucination | No LLM in evidence path; `UNMAPPED` for unknown |
| Secrets leakage | No credentials, no API keys, no telemetry |

### Attack Surface

- **Input parsing**: CSV/DOCX/XLSX/TXT → validated schemas, fail-closed
- **File I/O**: Atomic writes, no partial artifacts on failure
- **Docker**: Multi-stage, non-root, `network_mode: none`

## Security Controls

### Dependency Security

- Pinned `fpdf2==2.8.8`, `openpyxl==3.1.5` (optional)
- Dev deps: `pytest==9.1.1`, `pytest-cov==7.1.0`
- No unpinned or floating dependencies

### Runtime Security

- **No network**: AST scan in `check-offline.py` bans socket/urllib/requests/LLM SDKs
- **No LLM**: No AI model in evidence path
- **No guessing**: Every mapping is a signed human decision
- **Fail closed**: All parsers/validators raise on missing/unknown columns

### Data Handling

- **Atomic writes**: `_write_atomic` stages artifacts, removes on failure
- **No partial artifacts**: Failed builds leave nothing behind
- **Deterministic output**: Byte-identical across runs

## Compliance

- **Offline guarantee**: Documented in `docs/OFFLINE-GUARANTEE.md`
- **Determinism**: Verified by `check-determinism.py`
- **No telemetry**: Verified by code inspection

*End of security document.*