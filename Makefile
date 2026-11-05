# Signoff — developer entry points.
# All commands run fully offline once dependencies are installed.

PYTHON ?= python3

.PHONY: check-scaffold check-offline check-determinism test test-cov demo verify all

check-scaffold:
	$(PYTHON) scripts/check-scaffold.py

check-offline:
	$(PYTHON) scripts/check-offline.py

check-determinism:
	$(PYTHON) scripts/check-determinism.py --out out/determinism

test:
	$(PYTHON) -m pytest -q

test-cov:
	$(PYTHON) -m pytest --cov=src/signoff --cov-report=term-missing -q

demo:
	$(PYTHON) -m signoff demo --out out/demo

verify:
	$(PYTHON) -m signoff verify-pack --pack out/demo

all: check-scaffold check-offline test demo verify check-determinism
