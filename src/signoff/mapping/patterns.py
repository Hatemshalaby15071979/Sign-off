"""pattern_id groupings — run one code path through many duplicate questions."""
from __future__ import annotations

from signoff.model.mapping_rule import MappingRule


def group_by_pattern(rules: list[MappingRule]) -> dict[str, list[MappingRule]]:
    """pattern_id -> rules sharing it (sorted by rule_id)."""
    groups: dict[str, list[MappingRule]] = {}
    for rule in rules:
        groups.setdefault(rule.pattern_id, []).append(rule)
    return {pid: sorted(g, key=lambda r: r.rule_id) for pid, g in sorted(groups.items())}


def dedup_report(rules: list[MappingRule]) -> str:
    """Human-readable dedup summary printed by loader/build, e.g. the count."""
    groups = group_by_pattern(rules)
    questions = sum(len(g) for g in groups.values())
    return (f"{len(rules)} signed rule(s), {len(groups)} pattern(s); "
            f"{questions} question(s) answered by {len(rules)} distinct rules "
            f"({questions - len(rules)} duplicate(s) collapsed by pattern_id)")
