"""Signoff — errors.

Fail-closed exception hierarchy. Every abort of a build uses one of these;
nothing is ever swallowed into a partial pack.
"""
from __future__ import annotations


class SignoffError(Exception):
    """Base class with a stable, human-readable message prefix."""

    code = "SIGNOFF_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(f"[{self.code}] {message}")


class ParseError(SignoffError):
    code = "PARSE_ERROR"


class MappingError(SignoffError):
    code = "MAPPING_ERROR"


class ChainError(SignoffError):
    code = "CHAIN_ERROR"


class OutputError(SignoffError):
    code = "OUTPUT_ERROR"


class ConfigError(SignoffError):
    code = "CONFIG_ERROR"
