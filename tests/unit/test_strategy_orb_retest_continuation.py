"""ORB retest continuation strategy tests."""

import numpy as np
from intraday.strategies.orb.retest_continuation import (
    _prior_breakout_above,
    validate_orb_retest_continuation_config,
)

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_orb_retest_continuation_config(load_base_config("orb_retest_continuation"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_orb_retest_continuation_config, "orb_retest_continuation")


def _prior_breakout_above_slow(
    close: np.ndarray,
    orb_high: np.ndarray,
    minute: np.ndarray,
    session_id: np.ndarray,
    om: int,
) -> np.ndarray:
    out = np.zeros(close.shape[0], dtype=bool)
    for i in range(close.shape[0]):
        if int(minute[i]) < om - 1:
            continue
        s0 = i
        while s0 > 0 and int(session_id[s0 - 1]) == int(session_id[i]):
            s0 -= 1
        for j in range(s0, i):
            if int(minute[j]) >= om - 1 and np.isfinite(close[j]) and np.isfinite(orb_high[j]):
                if close[j] > orb_high[j]:
                    out[i] = True
                    break
    return out


def _assert_prior_breakout_equivalent(
    *,
    close: list[float],
    orb_high: list[float],
    minute: list[int],
    session_id: list[int],
    om: int = 3,
) -> None:
    close_arr = np.asarray(close, dtype=np.float64)
    orb_arr = np.asarray(orb_high, dtype=np.float64)
    minute_arr = np.asarray(minute, dtype=np.int32)
    session_arr = np.asarray(session_id, dtype=np.int32)

    old = _prior_breakout_above_slow(close_arr, orb_arr, minute_arr, session_arr, om)
    new = _prior_breakout_above(close_arr, orb_arr, minute_arr, session_arr, om)
    np.testing.assert_array_equal(new, old)


def test_prior_breakout_equivalence_no_prior_breakout() -> None:
    _assert_prior_breakout_equivalent(
        close=[99.0, 99.5, 100.0, 100.1, 100.2],
        orb_high=[np.nan, np.nan, 101.0, 101.0, 101.0],
        minute=[0, 1, 2, 3, 4],
        session_id=[0, 0, 0, 0, 0],
    )


def test_prior_breakout_equivalence_breakout_before_retest() -> None:
    _assert_prior_breakout_equivalent(
        close=[99.0, 100.0, 101.5, 100.6, 101.2],
        orb_high=[np.nan, np.nan, 101.0, 101.0, 101.0],
        minute=[0, 1, 2, 3, 4],
        session_id=[0, 0, 0, 0, 0],
    )


def test_prior_breakout_current_bar_does_not_count() -> None:
    close = np.asarray([99.0, 100.0, 101.5, 100.6], dtype=np.float64)
    orb_high = np.asarray([np.nan, np.nan, 101.0, 101.0], dtype=np.float64)
    minute = np.asarray([0, 1, 2, 3], dtype=np.int32)
    session_id = np.asarray([0, 0, 0, 0], dtype=np.int32)

    out = _prior_breakout_above(close, orb_high, minute, session_id, 3)

    assert bool(out[2]) is False
    assert bool(out[3]) is True
    np.testing.assert_array_equal(
        out, _prior_breakout_above_slow(close, orb_high, minute, session_id, 3)
    )


def test_prior_breakout_equivalence_session_reset_and_multi_session() -> None:
    _assert_prior_breakout_equivalent(
        close=[99.0, 100.0, 101.5, 100.5, 99.0, 100.0, 100.2, 100.4],
        orb_high=[np.nan, np.nan, 101.0, 101.0, np.nan, np.nan, 101.0, 101.0],
        minute=[0, 1, 2, 3, 0, 1, 2, 3],
        session_id=[0, 0, 0, 0, 1, 1, 1, 1],
    )


def test_prior_breakout_equivalence_nan_close_or_orb_high_ignored() -> None:
    _assert_prior_breakout_equivalent(
        close=[99.0, 100.0, np.nan, 101.5, 100.8, 101.2],
        orb_high=[np.nan, np.nan, 101.0, np.nan, 101.0, 101.0],
        minute=[0, 1, 2, 3, 4, 5],
        session_id=[0, 0, 0, 0, 0, 0],
    )


def test_prior_breakout_equivalence_different_orb_open_minutes() -> None:
    _assert_prior_breakout_equivalent(
        close=[99.0, 100.0, 100.4, 100.8, 101.5, 100.9, 101.1],
        orb_high=[np.nan, np.nan, np.nan, np.nan, 101.0, 101.0, 101.0],
        minute=[0, 1, 2, 3, 4, 5, 6],
        session_id=[0, 0, 0, 0, 0, 0, 0],
        om=5,
    )
