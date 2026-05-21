"""Tests for the authoritative runtime setup-code registry."""

from __future__ import annotations

from pathlib import Path

import pytest
from intraday.core.config import load_yaml
from intraday.core.errors import ConfigError
from intraday.core.types import Side
from intraday.strategies.setup_codes import (
    FUTURE_RESERVED_RANGES,
    SETUP_CODES,
    all_setup_code_specs,
    get_setup_codes,
    setup_code_for_side,
)

REPO = Path(__file__).resolve().parents[2]

CURRENT10_EXPECTED: tuple[tuple[str, int, int], ...] = (
    ("pa_buy_sell_close_trend", 1001, 8001),
    ("orb_continuation", 2001, 9001),
    ("orb_retest_continuation", 2002, 9002),
    ("failed_orb", 2003, 9003),
    ("gap_acceptance_failure", 3001, 10001),
    ("vwap_trend_pullback", 4001, 11001),
    ("vwap_reclaim_reject", 4002, 11002),
    ("prior_day_level_trap", 5001, 12001),
    ("cci_extreme_snapback", 6001, 13001),
    ("stochastic_oversold_cross", 6002, 13002),
)

PHASE19_CORE_EXPECTED: tuple[tuple[str, int, int], ...] = (
    ("pa_second_entry_pullback", 7101, 7201),
    ("pa_trading_range_bls_hs", 7102, 7202),
    ("pa_failed_breakout_trap", 7103, 7203),
    ("pa_opening_reversal_sr", 7104, 7204),
    ("pa_breakout_pullback_continuation", 7105, 7205),
    ("pa_tight_channel_pullback", 7106, 7206),
    ("pa_broad_channel_zone", 7107, 7207),
)

PHASE19_DIAGNOSTIC_EXPECTED: tuple[tuple[str, int, int], ...] = (
    ("pa_mtr_reversal_diagnostic", 7108, 7208),
    ("pa_wedge_reversal_diagnostic", 7109, 7209),
    ("pa_climax_reversal_diagnostic", 7110, 7210),
)

WRONG_PHASE19B_CODES: frozenset[int] = frozenset(
    {1101, 1102, 1201, 1202, 1301, 1302, 1401, 1402, 1501, 1502, 1601, 1602, 1701, 1702}
)


def _all_codes() -> list[int]:
    codes: list[int] = []
    for spec in all_setup_code_specs():
        codes.append(int(spec.long_code))
        if spec.short_code is not None:
            codes.append(int(spec.short_code))
    return codes


def test_registry_codes_unique() -> None:
    codes = _all_codes()
    assert len(codes) == len(set(codes))


def test_registry_codes_fit_int16() -> None:
    for code in _all_codes():
        assert -32_768 <= code <= 32_767


@pytest.mark.parametrize(("strategy", "long_code", "short_code"), CURRENT10_EXPECTED)
def test_current10_codes_match(strategy: str, long_code: int, short_code: int) -> None:
    spec = get_setup_codes(strategy)
    assert spec.long_code == long_code
    assert spec.short_code == short_code


@pytest.mark.parametrize(("strategy", "long_code", "short_code"), PHASE19_CORE_EXPECTED)
def test_phase19_core_codes_match(strategy: str, long_code: int, short_code: int) -> None:
    spec = get_setup_codes(strategy)
    assert spec.long_code == long_code
    assert spec.short_code == short_code


@pytest.mark.parametrize(("strategy", "long_code", "short_code"), PHASE19_DIAGNOSTIC_EXPECTED)
def test_phase19_diagnostic_codes_reserved(strategy: str, long_code: int, short_code: int) -> None:
    spec = get_setup_codes(strategy)
    assert spec.long_code == long_code
    assert spec.short_code == short_code
    assert spec.status == "phase19_diagnostic_reserved"


def test_get_setup_codes_rejects_unknown_strategy() -> None:
    with pytest.raises(ConfigError):
        get_setup_codes("not_a_real_strategy")


def test_setup_code_for_side_returns_long_and_short() -> None:
    spec = get_setup_codes("pa_second_entry_pullback")
    assert setup_code_for_side("pa_second_entry_pullback", Side.LONG) == spec.long_code
    assert setup_code_for_side("pa_second_entry_pullback", Side.SHORT) == spec.short_code
    with pytest.raises(ConfigError):
        setup_code_for_side("pa_second_entry_pullback", Side.FLAT)


def test_no_current_source_uses_wrong_phase19b_codes() -> None:
    """Phase19B placeholder codes 1101-1702 must not appear in current source."""
    src_root = REPO / "src" / "intraday" / "strategies" / "pa"
    offenders: list[str] = []
    for path in src_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for code in WRONG_PHASE19B_CODES:
            if str(code) in text:
                offenders.append(f"{path}: {code}")
    assert offenders == [], f"wrong Phase19B codes present in source: {offenders}"


def test_no_current_metadata_uses_wrong_phase19b_codes() -> None:
    meta_root = REPO / "configs" / "strategies" / "metadata" / "phase19"
    offenders: list[str] = []
    for path in meta_root.glob("*.yaml"):
        meta = load_yaml(path)
        codes = meta.get("setup_codes") or {}
        for value in codes.values():
            try:
                value_int = int(value)
            except (TypeError, ValueError):
                continue
            if value_int in WRONG_PHASE19B_CODES:
                offenders.append(f"{path}: {value_int}")
    assert offenders == [], f"wrong Phase19B codes present in metadata: {offenders}"


def test_future_reservation_ranges_present() -> None:
    assert FUTURE_RESERVED_RANGES["strategies_21_30"]["long"] == (7301, 7310)
    assert FUTURE_RESERVED_RANGES["strategies_21_30"]["short"] == (7401, 7410)
    assert FUTURE_RESERVED_RANGES["strategies_31_40"]["long"] == (7501, 7510)
    assert FUTURE_RESERVED_RANGES["strategies_41_50"]["short"] == (7801, 7810)


def test_all_eleven_to_seventeen_strategies_in_registry() -> None:
    for name, _, _ in (*CURRENT10_EXPECTED, *PHASE19_CORE_EXPECTED):
        assert name in SETUP_CODES
