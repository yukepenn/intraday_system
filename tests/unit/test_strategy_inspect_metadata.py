"""Phase19 immediate fix: strategy inspect CLI metadata authority tests."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest
from intraday.cli.strategy_cmds import cmd_strategies_inspect
from intraday.strategies.registry import register_builtin_strategies
from intraday.strategies.setup_codes import SETUP_CODES

REPO = Path(__file__).resolve().parents[2]

CURRENT10_WITH_BASES = (
    ("pa_buy_sell_close_trend", "configs/strategies/base/pa_buy_sell_close_trend.yaml"),
    ("orb_continuation", "configs/strategies/base/orb_continuation.yaml"),
    ("orb_retest_continuation", "configs/strategies/base/orb_retest_continuation.yaml"),
    ("failed_orb", "configs/strategies/base/failed_orb.yaml"),
    ("gap_acceptance_failure", "configs/strategies/base/gap_acceptance_failure.yaml"),
    ("vwap_trend_pullback", "configs/strategies/base/vwap_trend_pullback.yaml"),
    ("vwap_reclaim_reject", "configs/strategies/base/vwap_reclaim_reject.yaml"),
    ("prior_day_level_trap", "configs/strategies/base/prior_day_level_trap.yaml"),
    ("cci_extreme_snapback", "configs/strategies/base/cci_extreme_snapback.yaml"),
    ("stochastic_oversold_cross", "configs/strategies/base/stochastic_oversold_cross.yaml"),
)

PHASE19_WITH_BASES = (
    ("pa_second_entry_pullback", "configs/strategies/base/phase19/pa_second_entry_pullback.yaml"),
    ("pa_trading_range_bls_hs", "configs/strategies/base/phase19/pa_trading_range_bls_hs.yaml"),
    ("pa_failed_breakout_trap", "configs/strategies/base/phase19/pa_failed_breakout_trap.yaml"),
    ("pa_opening_reversal_sr", "configs/strategies/base/phase19/pa_opening_reversal_sr.yaml"),
    (
        "pa_breakout_pullback_continuation",
        "configs/strategies/base/phase19/pa_breakout_pullback_continuation.yaml",
    ),
    ("pa_tight_channel_pullback", "configs/strategies/base/phase19/pa_tight_channel_pullback.yaml"),
    ("pa_broad_channel_zone", "configs/strategies/base/phase19/pa_broad_channel_zone.yaml"),
)


@pytest.fixture(scope="module", autouse=True)
def _registry():
    register_builtin_strategies()


def _inspect(strategy: str, cfg: str) -> dict:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cmd_strategies_inspect(strategy=strategy, config=cfg)
    assert rc == 0
    return json.loads(buf.getvalue())


@pytest.mark.parametrize("strategy,cfg", CURRENT10_WITH_BASES + PHASE19_WITH_BASES)
def test_inspect_reports_nonempty_setup_codes(strategy: str, cfg: str) -> None:
    payload = _inspect(strategy, cfg)
    codes = payload["setup_codes"]
    assert codes, f"{strategy}: inspect must report non-empty setup_codes"
    spec = SETUP_CODES[strategy]
    assert int(codes["long"]) == spec.long_code
    assert int(codes["short"]) == spec.short_code


@pytest.mark.parametrize("strategy,cfg", CURRENT10_WITH_BASES + PHASE19_WITH_BASES)
def test_inspect_reports_nonempty_required_feature_columns(strategy: str, cfg: str) -> None:
    payload = _inspect(strategy, cfg)
    cols = payload["required_feature_columns"]
    assert cols, f"{strategy}: inspect must report non-empty required_feature_columns"


@pytest.mark.parametrize("strategy,cfg", CURRENT10_WITH_BASES + PHASE19_WITH_BASES)
def test_inspect_reports_allowed_side_modes_and_default(strategy: str, cfg: str) -> None:
    payload = _inspect(strategy, cfg)
    assert "long_only" in payload["allowed_side_modes"]
    assert payload["default_side_mode"] == "long_only"


@pytest.mark.parametrize("strategy,cfg", CURRENT10_WITH_BASES + PHASE19_WITH_BASES)
def test_inspect_metadata_setup_codes_match_strategydef(strategy: str, cfg: str) -> None:
    payload = _inspect(strategy, cfg)
    meta_codes = payload["metadata_setup_codes"]
    runtime_codes = payload["setup_codes"]
    assert int(meta_codes["long"]) == int(runtime_codes["long"])
    assert int(meta_codes["short"]) == int(runtime_codes["short"])
