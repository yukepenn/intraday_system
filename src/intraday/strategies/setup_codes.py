"""Authoritative runtime setup-code registry.

This module is the single source of truth for per-strategy long/short setup
codes. Strategy modules, ``StrategyDef`` metadata, configuration YAMLs, and
review artifacts must all align to the values defined here.

Setup codes are stable audit identifiers. They are not optimization parameters
and they are not grid axes. See ``docs/SETUP_CODE_REGISTRY.md`` for the full
governance policy.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from intraday.core.errors import ConfigError
from intraday.core.types import Side


@dataclass(frozen=True)
class SetupCodeSpec:
    """Per-strategy long/short setup-code spec.

    ``long_code`` and ``short_code`` are stable int16 identifiers. ``short_code``
    is ``None`` only for strategies that have no defined short-side identifier.
    """

    strategy_name: str
    family: str
    long_code: int
    short_code: int | None
    status: str
    notes: str = ""


_INT16_MIN = -32_768
_INT16_MAX = 32_767


def _fits_int16(value: int) -> bool:
    return _INT16_MIN <= int(value) <= _INT16_MAX


# Approved registry. Order is informational only; uniqueness/int16 enforced below.
_SPECS: tuple[SetupCodeSpec, ...] = (
    # Current-10 (long codes are historical; short codes added in Phase19 immediate fix).
    SetupCodeSpec(
        strategy_name="pa_buy_sell_close_trend",
        family="pa",
        long_code=1001,
        short_code=8001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="orb_continuation",
        family="orb",
        long_code=2001,
        short_code=9001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="orb_retest_continuation",
        family="orb",
        long_code=2002,
        short_code=9002,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="failed_orb",
        family="orb",
        long_code=2003,
        short_code=9003,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="gap_acceptance_failure",
        family="gap",
        long_code=3001,
        short_code=10001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="vwap_trend_pullback",
        family="vwap",
        long_code=4001,
        short_code=11001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="vwap_reclaim_reject",
        family="vwap",
        long_code=4002,
        short_code=11002,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="prior_day_level_trap",
        family="levels",
        long_code=5001,
        short_code=12001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="cci_extreme_snapback",
        family="cci",
        long_code=6001,
        short_code=13001,
        status="current10",
    ),
    SetupCodeSpec(
        strategy_name="stochastic_oversold_cross",
        family="stochastic",
        long_code=6002,
        short_code=13002,
        status="current10",
    ),
    # Phase19 core strategies 11-17.
    SetupCodeSpec(
        strategy_name="pa_second_entry_pullback",
        family="pa",
        long_code=7101,
        short_code=7201,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_trading_range_bls_hs",
        family="pa",
        long_code=7102,
        short_code=7202,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_failed_breakout_trap",
        family="pa",
        long_code=7103,
        short_code=7203,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_opening_reversal_sr",
        family="pa",
        long_code=7104,
        short_code=7204,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_breakout_pullback_continuation",
        family="pa",
        long_code=7105,
        short_code=7205,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_tight_channel_pullback",
        family="pa",
        long_code=7106,
        short_code=7206,
        status="phase19_core",
    ),
    SetupCodeSpec(
        strategy_name="pa_broad_channel_zone",
        family="pa",
        long_code=7107,
        short_code=7207,
        status="phase19_core",
    ),
    # Phase19 diagnostic reservations 18-20 (not implemented).
    SetupCodeSpec(
        strategy_name="pa_mtr_reversal_diagnostic",
        family="pa",
        long_code=7108,
        short_code=7208,
        status="phase19_diagnostic_reserved",
        notes="Reserved for Phase19 diagnostic strategy 18; not implemented in this phase.",
    ),
    SetupCodeSpec(
        strategy_name="pa_wedge_reversal_diagnostic",
        family="pa",
        long_code=7109,
        short_code=7209,
        status="phase19_diagnostic_reserved",
        notes="Reserved for Phase19 diagnostic strategy 19; not implemented in this phase.",
    ),
    SetupCodeSpec(
        strategy_name="pa_climax_reversal_diagnostic",
        family="pa",
        long_code=7110,
        short_code=7210,
        status="phase19_diagnostic_reserved",
        notes="Reserved for Phase19 diagnostic strategy 20; not implemented in this phase.",
    ),
)


def _build_lookup() -> dict[str, SetupCodeSpec]:
    lookup: dict[str, SetupCodeSpec] = {}
    seen_codes: dict[int, str] = {}
    for spec in _SPECS:
        if spec.strategy_name in lookup:
            raise ConfigError(f"duplicate strategy in setup-code registry: {spec.strategy_name!r}")
        for code in (spec.long_code, spec.short_code):
            if code is None:
                continue
            if not _fits_int16(code):
                raise ConfigError(
                    f"setup code {code} for {spec.strategy_name!r} does not fit int16"
                )
            if code in seen_codes:
                raise ConfigError(
                    f"setup code {code} reused by {spec.strategy_name!r} "
                    f"(already used by {seen_codes[code]!r})"
                )
            seen_codes[code] = spec.strategy_name
        lookup[spec.strategy_name] = spec
    return lookup


SETUP_CODES: Mapping[str, SetupCodeSpec] = _build_lookup()
"""Mapping ``strategy_name -> SetupCodeSpec``. Built and validated at import time."""

# Future reservation ranges (not yet assigned to specific strategy names).
FUTURE_RESERVED_RANGES: Mapping[str, Mapping[str, tuple[int, int]]] = {
    "strategies_21_30": {"long": (7301, 7310), "short": (7401, 7410)},
    "strategies_31_40": {"long": (7501, 7510), "short": (7601, 7610)},
    "strategies_41_50": {"long": (7701, 7710), "short": (7801, 7810)},
}


def all_setup_code_specs() -> tuple[SetupCodeSpec, ...]:
    """Return all known specs, registry-order."""
    return _SPECS


def get_setup_codes(strategy_name: str) -> SetupCodeSpec:
    """Return the spec for ``strategy_name`` or raise ``ConfigError``."""
    try:
        return SETUP_CODES[strategy_name]
    except KeyError as exc:
        raise ConfigError(f"no setup-code spec for strategy {strategy_name!r}") from exc


def setup_code_for_side(strategy_name: str, side: int | Side) -> int:
    """Return the long or short setup code for ``strategy_name``."""
    spec = get_setup_codes(strategy_name)
    side_int = int(side)
    if side_int == int(Side.LONG):
        return int(spec.long_code)
    if side_int == int(Side.SHORT):
        if spec.short_code is None:
            raise ConfigError(f"strategy {strategy_name!r} has no short setup code defined")
        return int(spec.short_code)
    raise ConfigError(f"side must be Side.LONG or Side.SHORT, got {side!r}")
