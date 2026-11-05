"""Injectable clock — the ONLY time source in Signoff.

No output-affecting code path may read wall-clock time. Every build receives
its `--as-of` instant, plus optional explicit context values; the wall clock
is never read. `Clock.wall_epoch()` exists ONLY for the CLI to stamp the
verification log on the operator's terminal (never into artifacts).
"""
from __future__ import annotations

import datetime as _dt

# Fixed default so implicit runs stay deterministic.
DEFAULT_AS_OF = "2026-11-05T00:00:00+00:00"


class Clock:
    """Deterministic time source. `as_of` is injected, never discovered."""

    def __init__(self, as_of: str | None = None) -> None:
        self._as_of = as_of if as_of is not None else DEFAULT_AS_OF

    def as_of(self) -> str:
        """The operator-injected pack instant (ISO-8601, UTC)."""
        return self._as_of

    def as_of_date(self) -> str:
        """Date portion of the injected instant, for the statement page."""
        return self._as_of.split("T")[0]


def parse_instant(value: str) -> _dt.datetime:
    """Parse an injected ISO-8601 instant; raises ConfigError on bad input."""
    from signoff.errors import ConfigError

    text = value.strip()
    if not text:
        raise ConfigError("--as-of must not be blank")
    if text.endswith("z") or text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError as exc:
        raise ConfigError(f"--as-of is not a valid ISO-8601 instant: {value!r} ({exc})") from exc
    if parsed.tzinfo is None:
        raise ConfigError("--as-of must include a UTC offset, e.g. 2026-11-05T00:00:00+00:00")
    return parsed
