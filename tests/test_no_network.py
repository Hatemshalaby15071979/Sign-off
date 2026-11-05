"""No-network proof: socket is ripped out and the full build still completes.

The product must work with the socket module monkeypatched to raise on ANY
use. In addition an AST census proves the runtime imports no network modules.
"""
from __future__ import annotations

import ast
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

import pytest

from tests.conftest import AS_OF, DEMO_DATA_FILES, FIXTURES

from signoff import cli
from signoff.engine import builder as builder_mod


def _loud_socket(*args, **kwargs):
    raise ConnectionError("network attempted during a build")


@pytest.fixture()
def no_network(monkeypatch):
    """Every plausible network object becomes a live landmine."""
    monkeypatch.setattr(socket, "socket", _loud_socket)
    monkeypatch.setattr(socket, "create_connection", _loud_socket)
    monkeypatch.setattr(socket, "getaddrinfo", _loud_socket)
    monkeypatch.setattr(socket, "socketpair", _loud_socket)
    monkeypatch.setattr(urllib.request, "urlopen", _loud_socket, raising=False)


def test_pack_under_blackhole_socket(no_network):
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    artifacts = cli._render_artifacts(pack, pack.as_of)
    assert set(artifacts) == set(cli.cfg.OUTPUT_FILES.values())
    assert all(len(data) for data in artifacts.values())


def test_cli_demo_under_blackhole_socket(no_network, tmp_path, monkeypatch):
    from signoff import cli

    out = tmp_path / "demo"
    ns = type("NS", (), {"out": str(out), "as_of": "2026-11-05T00:00:00+00:00"})
    assert cli.cmd_demo(ns) == 0
    assert (out / "pack.json").exists()
    assert "SIMULATION_DISCLOSURE" in (out / "dossier.html").read_text("utf-8")


BANNED_ROOTS = {
    "socket", "ssl", "urllib", "http", "httpx", "requests", "aiohttp",
    "ftplib", "smtplib", "telnetlib", "ftp", "poplib", "imaplib", "sftp",
    "asyncio", "subprocess",
}


def test_source_imports_are_network_free():
    src_root = Path(__file__).resolve().parent.parent / "src" / "signoff"
    hits = []
    for path in sorted(src_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in BANNED_ROOTS:
                        hits.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or "").split(".")[0]
                if root in BANNED_ROOTS:
                    hits.append(f"{path.name}: from {node.module} import ...")
    assert hits == []


def test_uuid4_and_random_never_used():
    src_root = Path(__file__).resolve().parent.parent / "src" / "signoff"
    hits = []
    for path in sorted(src_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in ("uuid.uuid4", "random.random", "os.random", "secrets.token"):
            if token in text:
                hits.append(f"{path.name}: {token}")
    assert hits == []


def test_scripts_may_use_subprocess_but_runtime_may_not():
    src_root = Path(__file__).resolve().parent.parent / "src" / "signoff"
    hits = [p.name for p in sorted(src_root.rglob("*.py"))
            if "subprocess" in p.read_text(encoding="utf-8")]
    assert hits == []
