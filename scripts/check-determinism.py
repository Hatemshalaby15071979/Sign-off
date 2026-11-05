#!/usr/bin/env python3
"""Determinism check: two identical demo builds must give byte-identical packs.

Runs `python -m signoff demo --out <dir1> --as-of <fixed>` and the same into
<dir2>, then compares sha256 of every artifact pair. Prints the two digest
lists; exit 0 only if every file matches. Note: PDF/HTML/JSON/CSV must be
byte-identical; the embed-as-of value comes from the injected epoch clock,
never from wall time.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AS_OF = "2026-11-04T00:00:00+00:00"


def build(out_dir: Path) -> int:
    env_cmd = [sys.executable, "-m", "signoff", "demo", "--out", str(out_dir),
               "--as-of", AS_OF]
    env = None
    return subprocess.run(env_cmd, cwd=REPO, env=env).returncode


def digest_dir(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in sorted(path.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(path))
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(REPO / "out" / "determinism"))
    args = ap.parse_args()
    base = Path(args.out)
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    d1, d2 = base / "run1", base / "run2"
    for d in (d1, d2):
        rc = build(d)
        if rc != 0:
            print(f"check-determinism: demo build failed for {d} (exit {rc})")
            return 1
    h1, h2 = digest_dir(d1), digest_dir(d2)
    identical = h1 == h2
    print("check-determinism: run1 digests:")
    for rel, h in sorted(h1.items()):
        print(f"  {h}  {rel}")
    print("check-determinism: run2 digests:")
    for rel, h in sorted(h2.items()):
        print(f"  {h}  {rel}")
    if identical:
        print("check-determinism: OK — outputs are byte-identical across runs")
        return 0
    print("check-determinism: FAIL — differing files:")
    all_keys = sorted(set(h1) | set(h2))
    for rel in all_keys:
        if h1.get(rel) != h2.get(rel):
            print(f"  - {rel}: {h1.get(rel, '<absent>')} != {h2.get(rel, '<absent>')}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
