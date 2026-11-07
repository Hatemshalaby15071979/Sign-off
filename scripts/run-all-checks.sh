#!/usr/bin/env bash
# run-all-checks.sh — scaffold + offline scan + demo determinism, in one pass.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== run-all-checks: start =="
python3 scripts/check-scaffold.py
python3 scripts/check-offline.py

echo "== demo build (determinism) =="
python3 scripts/check-determinism.py --out out/determinism

echo "== pytests =="
if python3 -c "import pytest" 2>/dev/null; then
    python3 -m pytest -q
else
    echo "NOTE pytest not importable with python3; skipping test step here (covered by CI and dev venv)"
fi

echo "== run-all-checks: OK =="
