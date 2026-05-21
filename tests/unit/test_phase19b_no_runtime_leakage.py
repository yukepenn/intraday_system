"""Phase19B no execution/runtime leakage tests."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

STRATEGY_FILES = (
    "second_entry_pullback.py",
    "trading_range_bls_hs.py",
    "failed_breakout_trap.py",
    "opening_reversal_sr.py",
    "breakout_pullback_continuation.py",
    "tight_channel_pullback.py",
    "broad_channel_zone.py",
)


def test_phase19b_strategies_do_not_import_execution_or_compute_pnl() -> None:
    base = REPO / "src" / "intraday" / "strategies" / "pa"
    forbidden = ("intraday.execution", "simulate_trade", "materialize_trade", "pnl", "target_price")
    for filename in STRATEGY_FILES:
        text = (base / filename).read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text


def test_phase19b_does_not_create_forbidden_runtime_configs() -> None:
    forbidden_roots = (
        REPO / "configs" / "candidates",
        REPO / "configs" / "layer2",
        REPO / "configs" / "layer3",
    )
    forbidden_names = {"pa_mtr_reversal_diagnostic.py", "pa_wedge_reversal_diagnostic.py"}
    for root in forbidden_roots:
        assert not any(root.glob("**/phase19b*"))
    pa_dir = REPO / "src" / "intraday" / "strategies" / "pa"
    assert not any((pa_dir / name).exists() for name in forbidden_names)
