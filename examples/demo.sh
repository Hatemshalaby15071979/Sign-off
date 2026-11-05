#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
python3 -m signoff demo --out out/demo
python3 -m signoff verify-pack --pack out/demo
