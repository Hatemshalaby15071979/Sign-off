# Signoff — Verification Log (append-only)

## Run 1 — Scaffold Check
```
python scripts/check-scaffold.py
```
Result: initially reported 10 missing required paths. Added the six missing docs, report files, and example files. Final check: `check-scaffold: OK (all phases) — 116 required files present`.

## Run 2 — Determinism Check
```
python scripts/check-determinism.py
```
Result: byte-identical outputs across runs (OK).

## Run 3 — Offline Check
```
python scripts/check-offline.py
```
Result: no banned imports/calls/env reads detected (OK).

## Run 4 — Test Suite
```
pytest --cov=signoff --cov-report=term-missing
```
Result:
```
TOTAL: 1483 statements, 181 missed, 88% coverage
```

## Run 5 — Demo Build
```
python -m signoff demo --out out/demo
```
Result: 7 artifacts built, PK-e0ada980b335da26, verify-pack prints VERIFIED.

## Run 6 — CLI Commands
```
python -m signoff validate-mapping --mapping OWNER/mapping-table.demo.csv
python -m signoff parse-questionnaire --input tests/fixtures/questionnaire.demo.csv --out /tmp/questions.csv
python -m signoff build --questionnaire tests/fixtures/questionnaire.demo.csv --data tests/fixtures --mapping OWNER/mapping-table.demo.csv --out /tmp/built
python -m signoff verify-pack --pack /tmp/built
```

## Run 7 — Docker Demo
```
docker run --network none -v $(pwd)/out:/out signoff:latest python -m signoff demo --out /out/demo
```
Result: previously reported as working in the supplied build handoff; Docker was not rerun during this final pass.

---

*End of verification log.*
## Final Run — Scaffold, Determinism, Offline, Tests

Commands: `python3 scripts/check-scaffold.py`, `python3 scripts/check-determinism.py`, `python3 scripts/check-offline.py`, `PYTHONPATH=src python3 -m pytest -q`. Executed using the available project build interpreter. Scaffold passed for all phases (116 required files), determinism produced byte-identical runs, offline scan passed, and pytest passed all 140 tests. Coverage run: 88% (1483 statements, 181 missed).

## Shipment audit recheck — 2026-11-05

- `python3 scripts/check-scaffold.py`: passed; all phases, 116 required files.
- `python3 scripts/check-determinism.py --out /tmp/signoff-determinism-final`: initially found PDF creation timestamps from the host clock. Fixed `pdf_renderer` to set PDF creation metadata from the pack's injected `as_of` value. Re-run: byte-identical artifacts and stable pack ID.
- `python3 scripts/check-offline.py`: passed; 41 runtime files scanned, no network/model SDK/outbound call/environment read.
- `PYTHONPATH=src python3 -m pytest --cov=signoff --cov-report=term`: 140 passed; 88% (1,485 statements, 181 missed).
- PDF metadata no longer leaks the build host time; it is derived from the deterministic pack timestamp.
- Signoff directory is not a Git repository in this workspace. GitHub/remote CI, clean external install and current Docker runtime were not verified in this pass.
