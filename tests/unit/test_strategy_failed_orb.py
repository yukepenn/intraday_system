"""Failed ORB strategy tests."""

import numpy as np
from intraday.strategies.orb.failed_orb import _prior_breach_below, validate_failed_orb_config

from tests.helpers import strategy_phase13 as sp13
from tests.helpers.strategy_phase13 import load_base_config


def test_base_yaml_validates() -> None:
    validate_failed_orb_config(load_base_config("failed_orb"))


def test_rejects_short_side() -> None:
    sp13.test_rejects_short_side(validate_failed_orb_config, "failed_orb")


def _prior_breach_below_slow(
    close: np.ndarray,
    orb_low: np.ndarray,
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
            if int(minute[j]) >= om - 1 and np.isfinite(close[j]) and np.isfinite(orb_low[j]):
                if close[j] < orb_low[j]:
                    out[i] = True
                    break
    return out


def test_prior_breach_below_equivalence_and_no_lookahead() -> None:
    close = np.asarray([101.0, 100.5, 99.5, 100.2, 101.0, 100.0, 99.7, 100.1])
    orb_low = np.asarray([np.nan, np.nan, 100.0, 100.0, np.nan, np.nan, 100.0, 100.0])
    minute = np.asarray([0, 1, 2, 3, 0, 1, 2, 3], dtype=np.int32)
    session_id = np.asarray([0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int32)

    old = _prior_breach_below_slow(close, orb_low, minute, session_id, 3)
    new = _prior_breach_below(close, orb_low, minute, session_id, 3)

    assert bool(new[2]) is False
    assert bool(new[3]) is True
    assert bool(new[6]) is False
    assert bool(new[7]) is True
    np.testing.assert_array_equal(new, old)
