"""Builder — orchestrates a full pack build. Deterministic and atomic in
effect: all artifact bytes are prepared in memory; the CLI writes them in
one pass at the end, so a failure never leaves a partial pack.

Order of operations is fixed and important: classify first, then compute
coverage (identity-based matching), attach EV ids, THEN hash-chain (so the
chain covers the evidence ids), then answers and gaps.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from signoff import config as cfg
from signoff.engine.classifier import classify
from signoff.engine.coverage import compute_coverage
from signoff.engine.gap_list import build_gaps
from signoff.engine.hash_chain import sha256_text
from signoff.errors import ParseError
from signoff.ingest import csv_normaliser
from signoff.ingest.questionnaire_csv import parse_csv_questionnaire
from signoff.ingest.questionnaire_docx import parse_docx_questionnaire
from signoff.ingest.questionnaire_txt import parse_txt_questionnaire
from signoff.ingest.questionnaire_xlsx import parse_xlsx_questionnaire
from signoff.mapping.loader import load_mapping
from signoff.mapping.patterns import group_by_pattern
from signoff.model.decision_event import DecisionEvent
from signoff.model.evidence_pack import Answer, CoverageResult, EvidencePack
from signoff.model.question import Question
from signoff.util import redaction
from signoff.util.clock import parse_instant
from signoff.util.ids import evidence_id

PARSERS = {
    ".csv": parse_csv_questionnaire,
    ".docx": parse_docx_questionnaire,
    ".xlsx": parse_xlsx_questionnaire,
    ".txt": parse_txt_questionnaire,
    ".md": parse_txt_questionnaire,
}


def parse_questionnaire_auto(path: Path) -> tuple[list[Question], str]:
    """Dispatch a questionnaire file to its parser by extension."""
    ext = path.suffix.lower()
    parser = PARSERS.get(ext)
    if parser is None:
        raise ParseError(
            f"{path.name}: unsupported questionnaire extension {ext!r} "
            "(supported: .csv, .docx, .xlsx, .txt, .md)")
    return parser(path), ext.lstrip(".")


def window_bounds(as_of: str) -> tuple[dt.datetime, dt.datetime]:
    """The explicit, documented coverage window: --as-of minus 90 days."""
    end = parse_instant(as_of)
    return end - dt.timedelta(days=cfg.COVERAGE_WINDOW_DAYS), end


def load_events(data_dir: Path, file_paths: list[Path] | None = None) -> tuple[list[DecisionEvent], list[str]]:
    """Normalise + classify the export CSVs of the data folder.

    With `file_paths` given (demo fixture mode), exactly those files are
    parsed; otherwise every `*.csv` in `data_dir` is parsed and any file
    that fails kind detection aborts the build (fail closed).
    """
    if file_paths is None:
        csvs = sorted(p for p in data_dir.iterdir() if p.suffix.lower() == ".csv")
    else:
        csvs = sorted(file_paths)
    raw_rows: list[csv_normaliser.RawRow] = []
    for path in csvs:
        raw_rows.extend(csv_normaliser.normalise_csv(path, relative_to=data_dir))
    return classify(raw_rows), [p.name for p in csvs]


def chain_genesis(as_of: str) -> str:
    return "signoff-chain-genesis:" + parse_instant(as_of).isoformat()


def chain_events(events: list[DecisionEvent], as_of: str) -> str:
    """Hash-chain in stable identity order; return the head hash.

    Sorting is by identity_key (content-derived), not arrival order, so the
    chain is reproducible on identical inputs.
    """
    events.sort(key=lambda e: e.identity_key)
    prev = sha256_text(chain_genesis(as_of))
    for ev in events:
        prev = ev.compute_ids(prev)
    return prev


def attach_evidence_ids(coverage: list[CoverageResult],
                        events: list[DecisionEvent], as_of: str) -> None:
    """EV ids attach to events BEFORE chaining so the chain covers them."""
    by_key = {(ev.source_file, ev.source_row, ev.identity_key): ev for ev in events}
    for c in coverage:
        ev_id = evidence_id(c.rule_id, c.pattern_id, c.source_qid, as_of)
        for ev in c.matched_events:
            target = by_key.get((ev.source_file, ev.source_row, ev.identity_key))
            if target is not None and ev_id not in target.evidence_ids:
                target.evidence_ids.append(ev_id)
        c.event_ids = [e.event_id for e in c.matched_events]


def build_answers(
    questions: list[Question],
    rule_by_qid: dict[str, object],
    coverage_by_qid: dict[str, object],
    as_of: str,
    unverified: bool,
) -> tuple[list[Answer], list[tuple[str, str]]]:
    """Deterministic answer text per answer_type; UNMAPPED never guessed."""
    answers: list[Answer] = []
    unmapped: list[tuple[str, str]] = []
    for q in questions:
        rule = rule_by_qid.get(q.qid)
        if rule is None:
            unmapped.append((q.qid, q.exact_text))
            answers.append(Answer(
                qid=q.qid, exact_text=q.exact_text, answer_type=q.answer_type,
                answer=cfg.UNMAPPED, mapped_rule_id=None, pattern_id=None,
                evidence_id=None, coverage_pct="N/A (no events in period)",
                trust_label="UNMAPPED",
            ))
            continue
        cov: CoverageResult = coverage_by_qid[q.qid]
        pct = cov.pct
        ev_id = evidence_id(rule.rule_id, rule.pattern_id, rule.source_qid, as_of)
        cov_text = "N/A (no events in period)" if pct is None else f"{pct}%"
        denominator = f"{cov.matched}/{cov.expected} {cov.denominator_label}"
        if q.answer_type == "yes_no":
            if pct is None:
                core = "N/A (no events in period)"
            elif pct >= 100.0:
                core = cfg.ANSWER_YES
            elif pct <= 0.0:
                core = cfg.ANSWER_NO
            else:
                core = cfg.ANSWER_PARTLY
            text = (f"{core} — signed evidence: rule {rule.rule_id} "
                    f"(decided by {rule.decided_by}, {rule.date}); "
                    f"coverage {cov_text} ({denominator}); evidence {ev_id}")
        elif q.answer_type == "free_text":
            text = (f"Evidence required by signed rule {rule.rule_id} "
                    f"({rule.decided_by}, {rule.date}): {rule.evidence_needed}. "
                    f"Coverage: {cov_text} ({denominator}); evidence {ev_id}.")
        else:  # attachment
            text = (f"See the appendix pack for rule {rule.rule_id}: "
                    f"{rule.evidence_needed}. Coverage {cov_text} "
                    f"({denominator}); evidence {ev_id}.")
        answers.append(Answer(
            qid=q.qid, exact_text=q.exact_text, answer_type=q.answer_type,
            answer=text, mapped_rule_id=rule.rule_id,
            pattern_id=rule.pattern_id, evidence_id=ev_id,
            coverage_pct=cov_text,
            trust_label="UNVERIFIED RULES" if unverified else "mapped",
        ))
    return answers, unmapped


def build_pack(
    questionnaire_path: Path,
    data_dir: Path,
    mapping_path: Path,
    as_of: str,
    data_files: list[Path] | None = None,
    redact: bool = False,
    allow_unverified: bool = False,
    simulated: bool = False,
    echo=print,
) -> EvidencePack:
    """Assemble the whole pack in memory. Nothing is written to disk here."""
    questions, _ext = parse_questionnaire_auto(questionnaire_path)
    q_rel = questionnaire_path.name
    rules, unverified = load_mapping(mapping_path, allow_unverified=allow_unverified,
                                     echo=echo)
    events, data_files_list = load_events(data_dir, file_paths=data_files)

    if redact:
        for ev in events:
            if ev.actor_identity not in ("", "unknown"):
                ev.actor_identity = redaction.mask_text(ev.actor_identity)
            ev.action = redaction.mask_text(ev.action)
        questions = [
            Question(qid=q.qid, exact_text=redaction.mask_text(q.exact_text),
                     answer_type=q.answer_type, source_path=q.source_path,
                     order=q.order, qid_source=q.qid_source)
            for q in questions
        ]

    rules_by_pattern = group_by_pattern(rules)
    rule_by_qid = {r.source_qid: r for r in rules}
    coverage = compute_coverage(rules_by_pattern, events, as_of)
    coverage_by_qid: dict[str, object] = {c.source_qid: c for c in coverage}
    attach_evidence_ids(coverage, events, as_of)
    head = chain_events(events, as_of)

    answers, unmapped = build_answers(questions, rule_by_qid, coverage_by_qid,
                                      as_of, unverified)
    gaps = build_gaps(coverage, events, unmapped, q_rel)

    return EvidencePack(
        pack_id="PENDING",
        as_of=as_of,
        simulated=simulated,
        unverified_rules=unverified,
        runtime=dict(cfg.RUNTIME_DEPENDENCIES),
        questions=answers,
        rules=[r.to_dict() for r in rules],
        events=events,
        coverage=coverage,
        gaps=gaps,
        unmapped_qids=[qid for qid, _ in unmapped],
        head=head,
        chain_genesis=chain_genesis(as_of),
        data_files=data_files_list,
    )
