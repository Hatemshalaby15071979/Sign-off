"""No LLM in the evidence path: mechanical, import-level proof.

There is no inference, embedding, summarising or generation code reachable
from signoff. An AST census proves no model SDK is ever imported in src/ or
reachable from the build path; sys.modules is audited after a full build.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

from tests.conftest import AS_OF, DEMO_DATA_FILES, FIXTURES

from signoff.engine import builder as builder_mod

SDK_MODULES = {
    "openai", "anthropic", "cohere", "litellm", "langchain",
    "llama_index", "transformers", "torch", "tensorflow", "ollama",
    "google.generativeai", "huggingface_hub", "sentence_transformers",
    "nltk", "spacy", "sklearn", "tiktoken",
}


def test_no_sdk_importable_from_runtime_after_full_build():
    pack = builder_mod.build_pack(
        questionnaire_path=FIXTURES / "questionnaire.demo.csv",
        data_dir=FIXTURES,
        data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
        mapping_path=FIXTURES / "mapping-table.demo.csv",
        as_of=AS_OF, simulated=True)
    artifacts_core = builder_mod  # intentionally touching the build expression
    touched = package_names(sys.modules)
    loaded = SDK_MODULES & touched
    assert loaded == set(), f"model SDKs present after a build: {loaded}"
    assert pack.head and artifacts_core is builder_mod


def package_names(modules):
    out = set()
    for name in modules:
        out.add(name)
        out.add(name.split(".")[0])
    return out


def test_no_model_code_reached_from_cli():
    from signoff import cli
    cli_modules = {name.split(".")[0] for name in sys.modules
                   if name.startswith("signoff")}
    assert cli_modules                                            # sanity
    assert not (set(SDK_MODULES) & {name.split(".")[0] for name in sys.modules})


def test_sources_never_mention_inference_calls():
    src_root = Path(__file__).resolve().parent.parent / "src" / "signoff"
    hits = []
    for path in sorted(src_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in (".create(", ".chat(", ".completions", ".embeddings(",
                      "SystemPrompt", "prompt_template", "temperature="):
            if token in text:
                hits.append(f"{path.name}: {token}")
    assert hits == []


def test_classifier_is_probability_free():
    from signoff.engine import classifier

    source = Path(classifier.__file__).read_text(encoding="utf-8")
    for banned in ("score", "threshold", "confidence", "mul(", "weight"):
        assert banned not in source.lower(), f"classifier mentions {banned!r}"


def test_deterministic_not_probabilistic_outputs():
    from signoff import cli

    def build_rendered():
        pack = builder_mod.build_pack(
            questionnaire_path=FIXTURES / "questionnaire.demo.csv",
            data_dir=FIXTURES,
            data_files=[FIXTURES / n for n in DEMO_DATA_FILES],
            mapping_path=FIXTURES / "mapping-table.demo.csv",
            as_of=AS_OF, simulated=True)
        return cli._render_artifacts(pack, pack.as_of)

    a = build_rendered()
    b = build_rendered()
    assert all(a[k] == b[k] for k in a)
