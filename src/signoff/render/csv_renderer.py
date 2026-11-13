"""CSV artefacts: machine-readable, stable row order, disclosure suffix."""
from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING

from signoff.render.disclosure import active_banners, not_proof_csv_rows
from signoff.util.csv_safe import csv_safe_row

if TYPE_CHECKING:  # pragma: no cover
    from signoff.model.evidence_pack import EvidencePack


def _rows_to_csv(header: list[str], rows: list[list[str]],
                 simulated: bool, unverified: bool) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(csv_safe_row(header))
    writer.writerows(csv_safe_row(row) for row in rows)
    for label, value in not_proof_csv_rows():
        writer.writerow(csv_safe_row([label, value]))
    for banner in active_banners(simulated, unverified):
        writer.writerow(csv_safe_row(["banners", banner]))
    buf.seek(0)
    return buf.getvalue()


def render_answers_csv(pack: "EvidencePack") -> str:
    return _rows_to_csv(
        ["qid", "question_text", "answer_type", "answer", "mapped_rule_id",
         "pattern_id", "evidence_id", "coverage", "trust_label"],
        [[q.qid, q.exact_text, q.answer_type, q.answer, q.mapped_rule_id or "",
          q.pattern_id or "", q.evidence_id or "", q.coverage_pct, q.trust_label]
         for q in pack.questions],
        pack.simulated, pack.unverified_rules)


def render_gaps_csv(pack: "EvidencePack") -> str:
    return _rows_to_csv(
        ["rule_id", "source_qid", "reason", "affected_source_files",
         "affected_row_count", "suggested_remediation"],
        [[g.rule_id, g.source_qid, g.reason,
          ";".join(g.affected_source_files), str(g.affected_row_count),
          g.suggested_remediation] for g in pack.gaps],
        pack.simulated, pack.unverified_rules)


def render_events_csv(pack: "EvidencePack") -> str:
    return _rows_to_csv(
        ["event_id", "ts", "state", "actor_identity", "action", "source_file",
         "source_row", "policy_rule", "evidence_ids", "prev_hash", "hash"],
        [[ev.event_id, ev.ts, ev.state, ev.actor_identity, ev.action,
          ev.source_file, str(ev.source_row), ev.policy_rule,
          ";".join(ev.evidence_ids), ev.prev_hash, ev.hash]
         for ev in pack.events],
        pack.simulated, pack.unverified_rules)
