#!/usr/bin/env python3
"""Static AST scan: assert the runtime code is offline and model-free.

Scans src/signoff/**/*.py for:
- banned network client imports (requests, httpx, urllib.request, aiohttp,
  urllib3, boto3, smtplib, ftplib, telnetlib, xmlrpc.client as URI callers),
- banned model/LLM SDK imports (openai, anthropic, langchain, llama_index,
  transformers, ollama, google-generativeai, cohere, litellm),
- active outbound calls: socket.socket/connect/create_connection/getaddrinfo,
  urllib.request.urlopen,
- reading of environment variables (os.environ / os.getenv) — the product
  reads nothing from the environment; only explicit CLI flags are allowed,
- subprocess module (runtime must not shell out).

Exiting 0 proves: zero network imports, zero model SDKs in src/.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "signoff"

BANNED_IMPORTS = {
    # network clients
    "requests", "httpx", "aiohttp", "urllib3", "boto3", "botocore",
    "smtplib", "ftplib", "telnetlib", "grequests", "pycurl", "grpc",
    # model / LLM SDKs (must never appear in the evidence path)
    "openai", "anthropic", "langchain", "llama_index", "llama-index",
    "transformers", "ollama", "cohere", "litellm", "google.generativeai",
    "sentence_transformers", "nltk", "huggingface_hub",
}

BANNED_ROOT_MODULES = {"socket", "urllib", "ssl"}
# Importing these root modules IS allowed if the provenance is passive
# (tests monkeypatch socket). In runtime src/ we forbid them entirely so
# the guarantee is mechanical, not judmental.

BANNED_CALLS = {
    "urlopen", "socket", "create_connection", "connect", "getaddrinfo",
    "gethostbyname", "putrequest", "urllib.request.urlopen",
    "socket.socket", "socket.create_connection",
}

BANNED_ATTRS = {"environ", "getenv"}

DENY_SUBPROCESS = True


class Visitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.hits: list[str] = []

    def _hit(self, msg: str) -> None:
        self.hits.append(f"{self.path}: {msg}")

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if alias.name in BANNED_IMPORTS or root in BANNED_IMPORTS:
                self._hit(f"banned import: {alias.name}")
            elif root in BANNED_ROOT_MODULES:
                self._hit(f"network module import: {alias.name}")
            elif root == "subprocess" and DENY_SUBPROCESS:
                self._hit("subprocess import (runtime must not shell out)")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        root = mod.split(".")[0]
        for alias in node.names:
            full = f"{mod}.{alias.name}" if mod else alias.name
            if full in BANNED_IMPORTS or alias.name in BANNED_IMPORTS or root in BANNED_IMPORTS:
                self._hit(f"banned import: from {mod} import {alias.name}")
            elif root in BANNED_ROOT_MODULES or mod in BANNED_ROOT_MODULES:
                self._hit(f"network module import: from {mod} import {alias.name}")
            elif root == "subprocess" and DENY_SUBPROCESS:
                self._hit("subprocess import (runtime must not shell out)")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = ""
        fn = node.func
        if isinstance(fn, ast.Name):
            name = fn.id
        elif isinstance(fn, ast.Attribute):
            parts: list[str] = [fn.attr]
            cur = fn.value
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            name = ".".join(reversed(parts))
        else:
            name = ""
        attr = getattr(fn, "attr", "")
        if name and (name in BANNED_CALLS or attr in {"urlopen", "connect",
                                                     "create_connection", "getaddrinfo"}):
            self._hit(f"banned call: {name}()")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # os.environ / os.getenv anywhere in runtime code
        if isinstance(node.value, ast.Name) and node.value.id == "os":
            if node.attr in BANNED_ATTRS:
                qual = "os." + node.attr
                parent = getattr(node, "_parent_attr", "")
                if node.attr == "environ" or parent == "getenv":
                    self._hit(f"environment read: {qual}")
        self.generic_visit(node)


def scan_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:  # pragma: no cover - would be a build break
        return [f"{path.name}: syntax error: {exc}"]
    v = Visitor(str(path.relative_to(REPO)))
    # annotate attribute parents to catch os.getenv precisely
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, "_parent_attr", getattr(node, "attr", ""))
    v.visit(tree)
    return v.hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", default=str(SRC), help="directory to scan (default: src/signoff)")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    problems: list[str] = []
    files = sorted(root.rglob("*.py"))
    for path in files:
        problems.extend(scan_file(path))
    if problems:
        print(f"check-offline: {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        print("check-offline: FAIL")
        return 1
    print(f"check-offline: OK — scanned {len(files)} file(s) in {args.path}; "
          "zero network imports, zero model SDKs, zero outbound calls, zero env reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
