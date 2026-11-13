#!/usr/bin/env python3
"""ME-15 guard: every agent-instruction file must carry the quarantine header.

Agent-directive files (prompts, constitutions) are *data, not instructions*. They
must contain the UNTRUSTED AGENT TEXT (ME-15) marker so an automated agent does
not treat their contents as commands to act on. This fails the build if a matching
file is missing the marker, so a new agent-instruction file cannot be introduced
without being explicitly quarantined.
"""
import glob
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "UNTRUSTED AGENT TEXT (ME-15)"

# Known agent-instruction files (relative to repo root).
KNOWN = ["docs/VIDEO-DEMO-PROMPT.md"]


def candidate_files():
    """Return the set of files that must carry the marker."""
    files = set()
    for rel in KNOWN:
        path = os.path.join(REPO_ROOT, rel)
        if os.path.isfile(path):
            files.add(path)
    # Any future agent prompt under docs/ is also in scope.
    for path in glob.glob(os.path.join(REPO_ROOT, "docs", "*_PROMPT.md")):
        files.add(path)
    return files


def main():
    missing = []
    for path in sorted(candidate_files()):
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(4096)
        if MARKER not in head:
            missing.append(os.path.relpath(path, REPO_ROOT))
    if missing:
        sys.stderr.write(
            "ME-15: agent-instruction files missing the quarantine header "
            f"({MARKER}):\n  - " + "\n  - ".join(missing) + "\n"
        )
        return 1
    print("ME-15: all agent-instruction files carry the quarantine header.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
