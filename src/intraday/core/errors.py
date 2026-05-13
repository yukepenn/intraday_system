"""Project-wide exception hierarchy."""

from __future__ import annotations


class IntradaySystemError(Exception):
    """Base class for all intraday_system errors."""


class ConfigError(IntradaySystemError):
    """Raised when a YAML config violates its contract."""


class DataContractError(IntradaySystemError):
    """Raised when raw/curated data violates the data contract."""


class CandidateContractError(IntradaySystemError):
    """Raised when a Layer1 candidate YAML violates its schema."""
