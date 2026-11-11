"""Determinism: identical inputs -> byte-identical artifacts, no wall clock involved."""
from __future__ import annotations

import time

from tests.conftest import AS_OF, DEMO_DATA_FILES, FIXTURES

from signoff import cli
from signoff.engine import builder as builder_mod
from signoff.engine.hash_chain import sha256_bytes
from signoff.util.clock import Clock


def build_rendered_artifacts() -> dict[str, bytes]:
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF,
        simulated=True,
    )
    return cli._render_artifacts(pack, pack.as_of)


def test_two_builds_are_byte_identical():
    run1 = build_rendered_artifacts()
    run2 = build_rendered_artifacts()
    assert set(run1) == set(run2)
    for name in run1:
        assert run1[name] == run2[name], f"{name} is not deterministic"


def test_build_survives_a_wall_clock_tick():
    pack1 = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    time.sleep(1.1)                      # wall clock would advance >= 1 s
    pack2 = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    assert pack1.head == pack2.head
    d1 = cli._render_artifacts(pack1, pack1.as_of)
    d2 = cli._render_artifacts(pack2, pack2.as_of)
    assert d1 == d2


def test_injected_clock_controls_output():
    later = "2026-12-05T00:00:00+00:00"
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=later, simulated=True)
    assert pack.as_of == later
    assert pack.chain_genesis.startswith("signoff-chain-genesis:2026-12-05")
    pack_early = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    assert pack.head != pack_early.head          # different window -> different chain


def test_clock_default_is_the_documented_constant():
    assert Clock(None).as_of() == "2026-11-05T00:00:00+00:00"


def test_rendered_pdf_bytes_stable():
    arts = build_rendered_artifacts()
    pdf = arts["dossier.pdf"]
    assert pdf.startswith(b"%PDF")
    again = build_rendered_artifacts()["dossier.pdf"]
    assert sha256_bytes(pdf) == sha256_bytes(again)


def test_unverified_rules_pack_renders_with_the_banner():
    """Regression: the PDF renderer used the banner without importing it.

    An unverified-rules pack is exactly what a real client build produces
    before the owner signs the mapping, so this path must render rather than
    raise NameError. It must also SAY it is unverified on every artifact.
    """
    import dataclasses

    pack = dataclasses.replace(
        builder_mod.build_pack(
            questionnaire_path=FIXTURES / "questionnaire.demo.csv",
            data_dir=FIXTURES,
            data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
            mapping_path=FIXTURES / "mapping-table.demo.csv",
            as_of=AS_OF,
            simulated=False,
        ),
        unverified_rules=True,
    )
    arts = cli._render_artifacts(pack, pack.as_of)
    assert arts["dossier.pdf"].startswith(b"%PDF")
    assert "UNVERIFIED RULES" in arts["dossier.html"].decode("utf-8")
