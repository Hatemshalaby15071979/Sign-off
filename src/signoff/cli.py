"""Signoff CLI — one command surface, fully offline.

    python -m signoff validate-mapping     --mapping PATH [--allow-unverified]
    python -m signoff parse-questionnaire  --input PATH --out PATH
    python -m signoff build --questionnaire PATH --data DIR --mapping PATH
                            --out DIR [--as-of ISO] [--redact] [--allow-unverified]
    python -m signoff demo                 --out DIR [--as-of ISO]
    python -m signoff verify-pack          --pack DIR
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from signoff import __version__, config as cfg
from signoff.engine import builder as builder_mod
from signoff.render import csv_renderer, json_renderer, pdf_renderer
from signoff.render import html_renderer, statement
from signoff.engine.hash_chain import canonical_json, sha256_bytes, sha256_text
from signoff.errors import SignoffError
from signoff.util.ids import pack_id


def _as_of(args) -> str:
    from signoff.util.clock import Clock
    return Clock(args.as_of).as_of()


def cmd_validate_mapping(args) -> int:  # pragma: no cover - thin shell over loader
    from signoff.mapping.loader import load_mapping
    rules, unverified = load_mapping(Path(args.mapping),
                                     allow_unverified=args.allow_unverified)
    print(f"VALID: {len(rules)} authorised rule(s){' (UNVERIFIED)' if unverified else ''}")
    return 0


def cmd_parse_questionnaire(args) -> int:
    from signoff.engine.builder import parse_questionnaire_auto
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    questions, _ = parse_questionnaire_auto(Path(args.input))
    header = "qid,exact_text,answer_type,qid_source,source_path,order\n"
    body = "".join(
        f"{q.qid},{csv_field(q.exact_text)},{q.answer_type},{q.qid_source},"
        f"{q.source_path},{q.order}\n"
        for q in questions)
    out_path.write_text(header + body, encoding="utf-8")
    print(f"parsed {len(questions)} question(s) -> {out_path}")
    return 0


def csv_field(value: str) -> str:
    return '"' + value.replace('"', '""') + '"' if any(ch in value for ch in ',"\n') else value


def _render_artifacts(pack, as_of: str) -> dict[str, bytes]:
    """Build every artifact's bytes in memory (nothing written yet)."""
    artifacts: dict[str, bytes] = {}
    html_doc = html_renderer.render_html(pack)
    artifacts[cfg.OUTPUT_FILES["dossier_html"]] = html_doc.encode("utf-8")

    artifacts[cfg.OUTPUT_FILES["answers_csv"]] = \
        csv_renderer.render_answers_csv(pack).encode("utf-8")
    artifacts[cfg.OUTPUT_FILES["gaps_csv"]] = \
        csv_renderer.render_gaps_csv(pack).encode("utf-8")
    artifacts[cfg.OUTPUT_FILES["events_csv"]] = \
        csv_renderer.render_events_csv(pack).encode("utf-8")
    artifacts[cfg.OUTPUT_FILES["statement_txt"]] = \
        statement.render_statement_txt(pack).encode("utf-8")
    artifacts[cfg.OUTPUT_FILES["dossier_pdf"]] = pdf_renderer.render_pdf(pack)

    # Manifest = digest of every artifact except pack.json itself.
    manifest = {
        name: {"sha256": sha256_bytes(data), "bytes": len(data)}
        for name, data in sorted(artifacts.items())
    }
    pack_dict = json_renderer.render_json(pack)
    pack_dict["artifacts"] = manifest
    pack_dict["pack_id"] = pack_id(sha256_text(canonical_json(manifest)))
    pack.pack_id = pack_dict["pack_id"]
    pack.artifacts = manifest

    pack_json = (json.dumps(pack_dict, sort_keys=True, indent=1,
                            ensure_ascii=False) + "\n").encode("utf-8")
    artifacts[cfg.OUTPUT_FILES["pack_json"]] = pack_json
    return artifacts


def _write_atomic(out_dir: Path, artifacts: dict[str, bytes]) -> None:
    """Write all artifacts at the end; a failure leaves nothing behind."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".signoff-stage-", dir=str(out_dir.parent)))
    try:
        for name, data in sorted(artifacts.items()):
            target = stage / name
            if not isinstance(data, (bytes, bytearray)):
                raise SignoffError(
                    f"atomic artifact write failed: {name} is not bytes")
            target.write_bytes(data)
        for name in artifacts:
            (out_dir / name).write_bytes((stage / name).read_bytes())
    except OSError as exc:
        _abort_failed_write(out_dir, artifacts)
        raise SignoffError(f"atomic artifact write failed: {exc}") from exc
    finally:
        _remove_stage(stage)


def _remove_stage(stage: Path) -> None:
    """Best-effort staging cleanup; never masks the original failure."""
    for path in stage.iterdir():
        if path.is_dir():
            import shutil
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink(missing_ok=True)
    try:
        stage.rmdir()
    except OSError:
        # best-effort cleanup; stage contents already removed
        pass  # pragma: no cover


def _abort_failed_write(out_dir: Path, artifacts: dict[str, bytes]) -> None:
    """Remove any partially written artifacts so a failed build leaves none."""
    for name in artifacts:
        target = out_dir / name
        try:
            if target.is_dir():
                import shutil
                shutil.rmtree(target)
            else:
                target.unlink(missing_ok=True)
        except OSError:
            # any failure here is secondary; the primary error already raised
            pass  # pragma: no cover


def cmd_build(args) -> int:
    pack = builder_mod.build_pack(
        questionnaire_path=Path(args.questionnaire),
        data_dir=Path(args.data),
        mapping_path=Path(args.mapping),
        as_of=_as_of(args),
        redact=args.redact,
        allow_unverified=args.allow_unverified,
        simulated=False,
    )
    artifacts = _render_artifacts(pack, pack.as_of)
    _write_atomic(Path(args.out), artifacts)
    print(f"pack built: {pack.pack_id} ({len(artifacts)} artifacts) -> {args.out}")
    return 0


def cmd_demo(args) -> int:
    from signoff.util.sim_flag import SIMULATION_DISCLOSURE
    fixtures = _fixtures_root() / "tests" / "fixtures"
    if not (fixtures / "mapping-table.demo.csv").exists():
        raise SignoffError(
            "demo fixtures not found next to the installed package; run from "
            "the repository (they are baked into the Docker image)")
    pack = builder_mod.build_pack(
        questionnaire_path=fixtures / "questionnaire.demo.csv",
        data_dir=fixtures,
        data_files=[fixtures / name for name in
                    ("qa_review_export.csv", "approval_events.csv",
                     "escalation_log.csv", "audit_events.csv",
                     "rolespec_export.csv", "ai_inventory.csv",
                     "training_register.csv", "incident_register.csv")],
        mapping_path=fixtures / "mapping-table.demo.csv",
        as_of=_as_of(args),
        simulated=True,
    )
    artifacts = _render_artifacts(pack, pack.as_of)
    _write_atomic(Path(args.out), artifacts)
    print(SIMULATION_DISCLOSURE)
    print(f"demo pack built: {pack.pack_id} ({len(artifacts)} artifacts) -> {args.out}")
    return 0


def cmd_verify_pack(args) -> int:
    from signoff.verify.verify_pack import verify_pack
    status, messages = verify_pack(Path(args.pack))
    for message in messages:
        print(message)
    print(status)
    return 0 if status == "VERIFIED" else 1


def _fixtures_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "src" / "signoff" / "cli.py").exists() and \
                (parent / "tests" / "fixtures").exists():
            return parent
    # Docker image: the package is installed; fixtures are copied to /app
    candidates = [Path("/app"), here.parents[2] if len(here.parents) > 2 else here.parent]
    for cand in candidates:
        if (cand / "tests" / "fixtures" / "mapping-table.demo.csv").exists():
            return cand
    return here.parents[1] if len(here.parents) > 1 else here


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="signoff",
        description="Offline, signable AI questionnaire evidence-pack builder "
                    "(no network, no model in the evidence path).")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True,
                                parser_class=argparse.ArgumentParser)

    def _add_as_of(p: argparse.ArgumentParser) -> None:
        p.add_argument("--as-of", default=None, metavar="ISO",
                       help="injected pack instant, e.g. 2026-11-05T00:00:00+00:00")

    p = sub.add_parser("validate-mapping", help="validate a mapping table "
                                                "without building a pack")
    p.add_argument("--mapping", required=True)
    p.add_argument("--allow-unverified", action="store_true",
                   help="accept an unverified mapping table (packs are stamped)")
    p.set_defaults(func=cmd_validate_mapping)

    p = sub.add_parser("parse-questionnaire", help="extract questions only")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_parse_questionnaire)

    p = sub.add_parser("build", help="build a hash-consistent evidence pack (real data)")
    p.add_argument("--questionnaire", required=True)
    p.add_argument("--data", required=True, help="folder of CSV exports (Input B)")
    p.add_argument("--mapping", required=True)
    p.add_argument("--out", required=True)
    _add_as_of(p)
    p.add_argument("--redact", action="store_true",
                   help="mask value columns in the pack while keeping IDs/ts")
    p.add_argument("--allow-unverified", action="store_true")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("demo", help="build a full pack from synthetic fixtures")
    p.add_argument("--out", required=True)
    _add_as_of(p)
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("verify-pack", help="verify a built pack (hash chain)")
    p.add_argument("--pack", required=True)
    p.set_defaults(func=cmd_verify_pack)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except SignoffError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"[IO_ERROR] {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001 — last-resort honesty
        print(f"[INTERNAL] unexpected failure: {exc}", file=sys.stderr)
        return 4
