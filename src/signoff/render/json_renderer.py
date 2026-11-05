"""JSON artefact: full machine-readable pack description."""
from __future__ import annotations

from typing import TYPE_CHECKING

from signoff.render.appendix import appendix_json
from signoff.render.disclosure import active_banners, not_proof_json

if TYPE_CHECKING:  # pragma: no cover
    from signoff.model.evidence_pack import EvidencePack


def render_json(pack: "EvidencePack") -> dict:
    """Stable key order (sort_keys at write time); bytes → pack_id hash."""
    data = {
        "schema": pack.schema_version,
        "pack_id": pack.pack_id,
        "as_of": pack.as_of,
        "simulated": pack.simulated,
        "unverified_rules": pack.unverified_rules,
        "banners": active_banners(pack.simulated, pack.unverified_rules),
        "head": pack.head,
        "chain_genesis": pack.chain_genesis,
        "data_files": list(pack.data_files),
        "runtime": dict(pack.runtime),
        "questions": [q.to_dict() for q in pack.questions],
        "rules": list(pack.rules),
        "coverage": [c.to_dict() for c in pack.coverage],
        "gaps": [g.to_dict() for g in pack.gaps],
        "unmapped_qids": list(pack.unmapped_qids),
        "events": [e.to_dict() for e in pack.events],
        "not_prove": not_proof_json(),
        "appendix": appendix_json(),
        "artifacts": {
            name: {"sha256": meta["sha256"], "bytes": meta["bytes"]}
            for name, meta in sorted(pack.artifacts.items())
        },
    }
    return data
