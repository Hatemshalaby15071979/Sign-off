"""Simulation watermark and honesty banners.

Any pack built from `tests/fixtures/` demo data is, permanently, a
simulation and must say so on every artifact it produces. Likewise, the
"No rules verified" banner stamps every artifact of an
`--allow-unverified` real build.
"""
from __future__ import annotations

SIMULATION_DISCLOSURE = (
    "SIMULATION_DISCLOSURE: Synthetic demonstration data. Not evidence. "
    "Not a client record. Not for submission."
)

UNVERIFIED_RULES_BANNER = (
    "UNVERIFIED RULES: this pack was built with unverified mapping rules "
    "(no human-authorised decision_by/date/verified=yes). It has no evidential value "
    "until the operator signs the mapping table and rebuilds."
)

NOT_PROOF_TITLE = "What this pack does NOT prove"

NOT_PROOF_POINTS = [
    "It does not prove compliance with any law, regulation or standard.",
    "It does not prove that a system is or is not high-risk; it never "
    "classifies anyone's system, and no classification is taken from this pack.",
    "It does not prove the absence of incidents; it proves only that the "
    "supplied CSVs do or do not contain the records the authorised rules ask for.",
    "It does not replace a signed policy, contract, SOP or human decision — "
    "the Oversight Statement must still be signed by a named human.",
    "It does not cover periods for which no exports were supplied; coverage "
    "windows with no rows are reported N/A, never as 100%.",
    "It does not verify the authenticity of supplied CSVs; a hash chain proves "
    "internal consistency of the pack, not the truth of the source exports.",
    "It contains no generative-model output in the evidence path; nothing here "
    "was summarised or written by a model.",
]


def banner(simulated: bool, unverified: bool) -> str:
    parts: list[str] = []
    if simulated:
        parts.append(SIMULATION_DISCLOSURE)
    if unverified:
        parts.append(UNVERIFIED_RULES_BANNER)
    return "\n".join(parts)
