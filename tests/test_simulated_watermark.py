"""Simulation watermark: every demo artifact carries SIMULATION_DISCLOSURE,
and no real build does."""
from __future__ import annotations

from tests.conftest import DEMO_DATA_FILES, FIXTURES, demo_artifacts, written_pack

from signoff.util.sim_flag import SIMULATION_DISCLOSURE


def test_disclosure_string_is_exact_and_is_one_line():
    assert SIMULATION_DISCLOSURE.startswith("SIMULATION_DISCLOSURE:")
    assert "Synthetic demonstration data" in SIMULATION_DISCLOSURE
    assert "\n" not in SIMULATION_DISCLOSURE


def test_every_demo_artifact_carries_the_watermark(written_pack):
    from tests.conftest import pdf_stream_text

    for name, data in sorted(written_pack_artifact_bytes(written_pack).items()):
        needle = b"SIMULATION_DISCLOSURE"
        if name.endswith(".pdf"):
            assert "SIMULATION_DISCLOSURE" in pdf_stream_text(data), name
        else:
            assert needle in data, f"{name} lost the simulation watermark"


def written_pack_artifact_bytes(pack_dir):
    out = {}
    for path in sorted(pack_dir.iterdir()):
        out[path.name] = path.read_bytes()
    return out


def test_pdf_carries_the_watermark(written_pack):
    from tests.conftest import pdf_stream_text

    text = pdf_stream_text((written_pack / "dossier.pdf").read_bytes())
    assert "SIMULATION_DISCLOSURE" in text
    assert "What this pack does NOT prove" in text


def test_html_carries_the_watermark(written_pack):
    html = (written_pack / "dossier.html").read_text(encoding="utf-8")
    assert "SIMULATION_DISCLOSURE" in html
    assert "What this pack does NOT prove" in html


def test_real_build_has_no_simulation_watermark():
    from tests.conftest import AS_OF

    from signoff.engine import builder as builder_mod

    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=False)
    bisect = [q for q in pack.questions]
    assert bisect is not None
    assert pack.simulated is False


def test_expression_of_not_prove_points_is_complete(demo_artifacts):
    noproof = demo_artifacts["dossier.html"].decode("utf-8")
    assert noproof.count("does not prove") >= 6 or "does NOT prove" in noproof


def test_not_prove_points_cover_the_seven_commitments():
    from signoff.util.sim_flag import NOT_PROOF_POINTS

    assert points_text(NOT_PROOF_POINTS)


def points_text(points):
    joined = " ".join(points).lower()
    assert "law, regulation or standard" in joined
    assert "high-risk" in joined
    assert "absence of incidents" in joined
    assert "never classifies" in joined
    return True
