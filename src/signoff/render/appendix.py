"""Appendix — static, informational control cross-reference table.

Three precedent frameworks covered: EU AI Act articles, ISO/IEC 42001, NIST
AI RMF, plus the OWASP Agentic Applications Top 10. The banner below is
mandatory and travels with every appendix rendering:
"Informational cross-reference only. Not a legal determination. Nothing
here classifies your system."
"""
from __future__ import annotations

import html as _h

APPENDIX_BANNER = ("Informational cross-reference only. Not a legal "
                   "determination. Nothing here classifies your system.")

HEADERS = ["evidence area", "EU AI Act", "ISO/IEC 42001", "NIST AI RMF", "OWASP Agentic Top 10"]

# Plain-language pointers, deliberately non-normative. The EU AI Act
# references are the commonly cited sink spots for oversight, logging and
# deployer duties (Art. 12 record-keeping, Art. 14 human oversight,
# Art. 26(6) deployer monitoring duties). Nothing here "classifies" any
# customer system: classification is never claimed by Signoff.
CONTROL_MAP: list[dict[str, str]] = [
    {"area": "Human review of AI-proposed actions", "eu": "Art. 14 (human oversight); Art. 12 (record-keeping)",
     "iso": "A.7.4 human oversight", "nist": "MANAGE 3 / GOVERN 3", "owasp": "Human-in-the-loop controls"},
    {"area": "Kill switch, access revocation", "eu": "Art. 14(4) (intervention: shutdown)",
     "iso": "A.8.7 incident-type controls", "nist": "MANAGE 2", "owasp": "Tool abuse / containment"},
    {"area": "Agent-identity logging", "eu": "Art. 12 (automatically generated logs)",
     "iso": "A.8.28 secure logging", "nist": "MEASURE 2", "owasp": "Traceability categories"},
    {"area": "Least privilege & periodic access review", "eu": "Art. 14(4) (units of operation limits)",
     "iso": "A.8.2 privileged access", "nist": "GOVERN 6", "owasp": "Excessive agency"},
    {"area": "AI inventory & named providers", "eu": "Art. 13 (transparency); register-type documentation",
     "iso": "A.4.2 AI system inventory", "nist": "MAP 1", "owasp": "Supply-chain categories"},
    {"area": "Data-use / no-training clause (document, not a log)", "eu": "Art. 10 / contract terms context",
     "iso": "A.6.3 supplier terms", "nist": "MAP 3", "owasp": "Supply-chain categories"},
    {"area": "Escalation to authorised supervisor only", "eu": "Art. 14(4) (stop/comply intervention)",
     "iso": "A.7.4 escalation design", "nist": "MANAGE 3", "owasp": "Resource/connection abuse"},
    {"area": "Named accountability / signed statement", "eu": "Art. 26(6) (deployer oversight duty)",
     "iso": "A.5.3 accountability roles", "nist": "GOVERN 1", "owasp": "Organisational ownership"},
    {"area": "Monitoring metrics (accepted-vs-edited rate)", "eu": "Art. 26(6) (deployer monitoring)",
     "iso": "A.9.3 performance monitoring", "nist": "MEASURE 2", "owasp": "Human-deception categories"},
    {"area": "Staff training records", "eu": "Art. 26(2) (deployer staff literacy)",
     "iso": "A.7.2 awareness & competence", "nist": "GOVERN 4", "owasp": "Organisational ownership"},
    {"area": "Incident notification SLA", "eu": "Art. 73 (serious incident reporting context)",
     "iso": "A.8.10 event management", "nist": "MANAGE 4", "owasp": "Incident-response categories"},
    {"area": "Retention / PII logging checks", "eu": "Art. 12(3) (log retention periods)",
     "iso": "A.8.28 log retention", "nist": "MEASURE 2", "owasp": "Data-handling categories"},
]


def _row_html(row: dict[str, str]) -> str:
    cells = "".join(f"<td>{_h.escape(row[key])}</td>"
                    for key in ("area", "eu", "iso", "nist", "owasp"))
    return f"<tr>{cells}</tr>"


def appendix_html() -> str:
    rows = "".join(_row_html(r) for r in CONTROL_MAP)
    head = "".join(f"<th>{_h.escape(h)}</th>" for h in HEADERS)
    return (
        "<section class=\"appendix\"><h2>Appendix — control cross-reference "
        "(informational)</h2>"
        f"<p class=\"banner\">{_h.escape(APPENDIX_BANNER)}</p>"
        f"<table class=\"controlmap\"><thead><tr>{head}</tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def appendix_text() -> str:
    lines = ["APPENDIX — CONTROL CROSS-REFERENCE (informational)", APPENDIX_BANNER, ""]
    lines.append(" | ".join(HEADERS))
    for row in CONTROL_MAP:
        lines.append(" | ".join(row[k] for k in ("area", "eu", "iso", "nist", "owasp")))
    return "\n".join(lines)


def appendix_rows() -> list[list[str]]:
    return [[r[k] for k in ("area", "eu", "iso", "nist", "owasp")] for r in CONTROL_MAP]


def appendix_json() -> dict:
    return {"banner": APPENDIX_BANNER, "headers": HEADERS, "rows": appendix_rows()}
